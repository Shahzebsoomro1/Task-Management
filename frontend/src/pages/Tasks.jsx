import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { taskService, commentService } from '../services';
import './Tasks.css';

const PAGE_SIZE = 10;

const Tasks = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [showComments, setShowComments] = useState({});
  const [formData, setFormData] = useState({ title: '', description: '', priority: 'medium' });
  const [comments, setComments] = useState({});
  const [commentText, setCommentText] = useState({});
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => { fetchTasks(page); }, [projectId, page]);

  const fetchTasks = async (currentPage = 0) => {
    try {
      const response = await taskService.getTasks(projectId, { skip: currentPage * PAGE_SIZE, limit: PAGE_SIZE });
      setTasks(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch { setError('Failed to fetch tasks'); }
  };

  const fetchComments = async (taskId) => {
    try {
      const response = await commentService.getComments(taskId);
      setComments(prev => ({ ...prev, [taskId]: response.data.items || [] }));
    } catch { setError('Failed to fetch comments'); }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      await taskService.createTask(projectId, formData);
      setFormData({ title: '', description: '', priority: 'medium' });
      setShowForm(false);
      setPage(0);
      fetchTasks(0);
    } catch (err) { setError(err.response?.data?.detail || 'Failed to create task'); }
  };

  const handleUpdateStatus = async (taskId, newStatus) => {
    try {
      await taskService.updateTask(projectId, taskId, { status: newStatus });
      fetchTasks(page);
    } catch { setError('Failed to update task'); }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await taskService.deleteTask(projectId, taskId);
      const np = tasks.length === 1 && page > 0 ? page - 1 : page;
      setPage(np);
      fetchTasks(np);
    } catch { setError('Failed to delete task'); }
  };

  const handleAddComment = async (taskId) => {
    if (!commentText[taskId]?.trim()) return;
    try {
      await commentService.createComment(taskId, { content: commentText[taskId] });
      setCommentText(prev => ({ ...prev, [taskId]: '' }));
      fetchComments(taskId);
    } catch { setError('Failed to add comment'); }
  };

  const toggleComments = (taskId) => {
    setShowComments(prev => {
      const next = { ...prev, [taskId]: !prev[taskId] };
      if (next[taskId] && !comments[taskId]) fetchComments(taskId);
      return next;
    });
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const startRow = page * PAGE_SIZE + 1;
  const endRow = Math.min(startRow + PAGE_SIZE - 1, total);

  const priorityLabel = { high: 'High', medium: 'Medium', low: 'Low' };
  const statusLabel   = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' };

  return (
    <div className="tasks-container">
      <div className="page-header">
        <div className="page-header-left">
          <button className="btn-back" onClick={() => navigate('/projects')}>← Back</button>
          <h1>📋 Project Tasks</h1>
        </div>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? '✕ Cancel' : '+ New Task'}
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {showForm && (
        <div className="create-form-panel">
          <h3>Create New Task</h3>
          <form onSubmit={handleCreateTask}>
            <div className="form-row">
              <div className="form-group">
                <label>Title *</label>
                <input
                  placeholder="Task title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  placeholder="Short description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={formData.due_date || ''}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ justifyContent: 'flex-end' }}>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </div>
          </form>
        </div>
      )}

      <div className="table-card">
        {total > 0 && (
          <div className="table-meta">
            Showing <strong>{startRow}–{endRow}</strong> of <strong>{total}</strong> tasks
          </div>
        )}
        <table className="data-table">
          <thead>
            <tr>
              <th className="td-num">#</th>
              <th>Title</th>
              <th>Description</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Due Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tasks.length === 0 ? (
              <tr className="empty-row">
                <td colSpan={7}>No tasks yet — create your first one above.</td>
              </tr>
            ) : (
              tasks.map((task, i) => (
                <React.Fragment key={task.id}>
                  <tr className="task-row">
                    <td className="td-num">{page * PAGE_SIZE + i + 1}</td>
                    <td className="td-title">{task.title}</td>
                    <td className="td-desc">
                      <span className="desc-text">{task.description || '—'}</span>
                    </td>
                    <td>
                      <span className={`badge badge-${task.priority}`}>
                        {priorityLabel[task.priority] || task.priority}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${task.status}`}>
                        {statusLabel[task.status] || task.status}
                      </span>
                    </td>
                    <td className="td-date">
                      {task.due_date ? new Date(task.due_date).toLocaleDateString() : '—'}
                    </td>
                    <td className="td-actions">
                      <div className="actions-cell">
                        <select
                          className="status-select"
                          value={task.status}
                          onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                        </select>
                        <button
                          className="btn-icon"
                          onClick={() => toggleComments(task.id)}
                          title="Comments"
                        >
                          💬 {comments[task.id]?.length ?? ''}
                        </button>
                        <button className="btn-danger" onClick={() => handleDeleteTask(task.id)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>

                  {showComments[task.id] && (
                    <tr className="comments-row">
                      <td colSpan={7}>
                        <div className="comments-drawer">
                          <h4>Comments</h4>
                          {(!comments[task.id] || comments[task.id].length === 0) ? (
                            <p className="no-comments">No comments yet.</p>
                          ) : (
                            <table className="comments-table">
                              <thead>
                                <tr>
                                  <th>#</th>
                                  <th>Comment</th>
                                  <th>Author</th>
                                  <th>Date</th>
                                </tr>
                              </thead>
                              <tbody>
                                {comments[task.id].map((c, ci) => (
                                  <tr key={c.id}>
                                    <td>{ci + 1}</td>
                                    <td>{c.content}</td>
                                    <td>{c.author_name || c.user_id}</td>
                                    <td>{new Date(c.created_at).toLocaleString()}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                          <div className="comment-add">
                            <input
                              placeholder="Write a comment…"
                              value={commentText[task.id] || ''}
                              onChange={(e) =>
                                setCommentText(prev => ({ ...prev, [task.id]: e.target.value }))
                              }
                              onKeyDown={(e) => e.key === 'Enter' && handleAddComment(task.id)}
                            />
                            <button className="btn-primary" onClick={() => handleAddComment(task.id)}>
                              Post
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>

        {totalPages > 1 && (
          <div className="pagination-bar">
            <span className="page-info">
              Page <strong>{page + 1}</strong> of <strong>{totalPages}</strong>
            </span>
            <div className="page-btns">
              <button className="btn-page" onClick={() => setPage(0)} disabled={page === 0}>«</button>
              <button className="btn-page" onClick={() => setPage(p => p - 1)} disabled={page === 0}>‹ Prev</button>
              {Array.from({ length: totalPages }, (_, idx) => (
                <button
                  key={idx}
                  className={`btn-page${page === idx ? ' active' : ''}`}
                  onClick={() => setPage(idx)}
                >
                  {idx + 1}
                </button>
              ))}
              <button className="btn-page" onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1}>Next ›</button>
              <button className="btn-page" onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1}>»</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Tasks;

