import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { taskService, commentService } from '../services';
import './Tasks.css';

const Tasks = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [showComments, setShowComments] = useState({});
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
  });
  const [comments, setComments] = useState({});
  const [commentText, setCommentText] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTasks();
  }, [projectId]);

  const fetchTasks = async () => {
    try {
      const response = await taskService.getTasks(projectId);
      setTasks(response.data.items || []);
    } catch (err) {
      setError('Failed to fetch tasks');
    }
  };

  const fetchComments = async (taskId) => {
    try {
      const response = await commentService.getComments(taskId);
      setComments({ ...comments, [taskId]: response.data });
    } catch (err) {
      setError('Failed to fetch comments');
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      await taskService.createTask(projectId, formData);
      setFormData({ title: '', description: '', priority: 'medium' });
      setShowForm(false);
      fetchTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create task');
    }
  };

  const handleUpdateStatus = async (taskId, newStatus) => {
    try {
      await taskService.updateTask(projectId, taskId, { status: newStatus });
      fetchTasks();
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Delete this task?')) {
      try {
        await taskService.deleteTask(projectId, taskId);
        fetchTasks();
      } catch (err) {
        setError('Failed to delete task');
      }
    }
  };

  const handleAddComment = async (taskId) => {
    try {
      await commentService.createComment(taskId, { content: commentText[taskId] });
      setCommentText({ ...commentText, [taskId]: '' });
      fetchComments(taskId);
    } catch (err) {
      setError('Failed to add comment');
    }
  };

  const toggleComments = (taskId) => {
    if (showComments[taskId]) {
      setShowComments({ ...showComments, [taskId]: false });
    } else {
      setShowComments({ ...showComments, [taskId]: true });
      if (!comments[taskId]) {
        fetchComments(taskId);
      }
    }
  };

  return (
    <div className="tasks-container">
      <div className="header">
        <button className="btn-back" onClick={() => navigate('/projects')}>
          ← Back to Projects
        </button>
        <h1>Project Tasks</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <button 
        className="btn-primary"
        onClick={() => setShowForm(!showForm)}
      >
        {showForm ? 'Cancel' : '+ New Task'}
      </button>

      {showForm && (
        <form className="task-form" onSubmit={handleCreateTask}>
          <input
            type="text"
            placeholder="Task Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
          <textarea
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <select
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
          >
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
          </select>
          <button type="submit">Create Task</button>
        </form>
      )}

      <div className="tasks-list">
        {tasks.map((task) => (
          <div key={task.id} className={`task-card priority-${task.priority}`}>
            <div className="task-header">
              <h3>{task.title}</h3>
              <span className={`status-badge status-${task.status}`}>
                {task.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <p>{task.description}</p>
            <div className="task-meta">
              <span className={`priority-badge priority-${task.priority}`}>
                {task.priority.toUpperCase()}
              </span>
              {task.due_date && <span>Due: {task.due_date}</span>}
            </div>
            <div className="task-actions">
              <select
                value={task.status}
                onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
                className="status-select"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
              <button 
                className="btn-comments"
                onClick={() => toggleComments(task.id)}
              >
                💬 Comments
              </button>
              <button 
                className="btn-danger"
                onClick={() => handleDeleteTask(task.id)}
              >
                Delete
              </button>
            </div>

            {showComments[task.id] && (
              <div className="comments-section">
                <h4>Comments</h4>
                <div className="comments-list">
                  {(comments[task.id] || []).map((comment) => (
                    <div key={comment.id} className="comment">
                      <p>{comment.content}</p>
                      <small>{new Date(comment.created_at).toLocaleString()}</small>
                    </div>
                  ))}
                </div>
                <div className="comment-form">
                  <input
                    type="text"
                    placeholder="Add a comment..."
                    value={commentText[task.id] || ''}
                    onChange={(e) => setCommentText({ ...commentText, [task.id]: e.target.value })}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAddComment(task.id);
                      }
                    }}
                  />
                  <button 
                    type="button"
                    onClick={() => handleAddComment(task.id)}
                  >
                    Post
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {tasks.length === 0 && !showForm && (
        <p className="empty-state">No tasks yet. Create one to get started!</p>
      )}
    </div>
  );
};

export default Tasks;
