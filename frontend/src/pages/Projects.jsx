import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../services';
import './Projects.css';

const PAGE_SIZE = 8;

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => { fetchProjects(page); }, [page]);

  const fetchProjects = async (currentPage = 0) => {
    try {
      const response = await projectService.getProjects(currentPage * PAGE_SIZE, PAGE_SIZE);
      setProjects(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch {
      setError('Failed to fetch projects');
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await projectService.createProject(formData);
      setFormData({ name: '', description: '' });
      setShowForm(false);
      setPage(0);
      fetchProjects(0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this project?')) return;
    try {
      await projectService.deleteProject(id);
      const np = projects.length === 1 && page > 0 ? page - 1 : page;
      setPage(np);
      fetchProjects(np);
    } catch {
      setError('Failed to delete project');
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const startRow  = page * PAGE_SIZE + 1;
  const endRow    = Math.min(startRow + PAGE_SIZE - 1, total);

  return (
    <div className="projects-container">
      <div className="page-header">
        <h1>📁 My Projects</h1>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? '✕ Cancel' : '+ New Project'}
          </button>
          <button className="btn-logout" onClick={() => navigate('/login')}>Logout</button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {showForm && (
        <div className="create-form-panel">
          <h3>Create New Project</h3>
          <form onSubmit={handleCreate}>
            <div className="form-row">
              <div className="form-group">
                <label>Name *</label>
                <input
                  placeholder="Project name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
            Showing <strong>{startRow}–{endRow}</strong> of <strong>{total}</strong> projects
          </div>
        )}
        <table className="data-table">
          <thead>
            <tr>
              <th className="td-num">#</th>
              <th>Project Name</th>
              <th>Description</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {projects.length === 0 ? (
              <tr className="empty-row">
                <td colSpan={5}>No projects yet — create your first one above.</td>
              </tr>
            ) : (
              projects.map((p, i) => (
                <tr key={p.id}>
                  <td className="td-num">{page * PAGE_SIZE + i + 1}</td>
                  <td className="td-name">{p.name}</td>
                  <td className="td-desc">
                    <span className="desc-text">{p.description || '—'}</span>
                  </td>
                  <td className="td-date">
                    {new Date(p.created_at).toLocaleDateString()}
                  </td>
                  <td className="td-actions">
                    <div className="actions-cell">
                      <button
                        className="btn-secondary"
                        onClick={() => navigate(`/projects/${p.id}`)}
                      >
                        View Tasks
                      </button>
                      <button className="btn-danger" onClick={() => handleDelete(p.id)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
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

export default Projects;


const PAGE_SIZE = 6;

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects(page);
  }, [page]);

  const fetchProjects = async (currentPage = 0) => {
    try {
      const skip = currentPage * PAGE_SIZE;
      const response = await projectService.getProjects(skip, PAGE_SIZE);
      setProjects(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      setError('Failed to fetch projects');
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await projectService.createProject(formData);
      setFormData({ name: '', description: '' });
      setShowForm(false);
      setPage(0);
      fetchProjects(0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm('Are you sure?')) {
      try {
        await projectService.deleteProject(projectId);
        const newPage = projects.length === 1 && page > 0 ? page - 1 : page;
        setPage(newPage);
        fetchProjects(newPage);
      } catch (err) {
        setError('Failed to delete project');
      }
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="projects-container">
      <div className="header">
        <h1>My Projects</h1>
        <button onClick={() => navigate('/login')}>Logout</button>
      </div>

      {error && <div className="error">{error}</div>}

      <button
        className="btn-primary"
        onClick={() => setShowForm(!showForm)}
      >
        {showForm ? 'Cancel' : '+ New Project'}
      </button>

      {showForm && (
        <form className="project-form" onSubmit={handleCreateProject}>
          <input
            type="text"
            placeholder="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <textarea
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <button type="submit">Create Project</button>
        </form>
      )}

      <div className="projects-grid">
        {projects.map((project) => (
          <div key={project.id} className="project-card">
            <h3>{project.name}</h3>
            <p>{project.description}</p>
            <div className="project-actions">
              <button
                className="btn-secondary"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                View Tasks
              </button>
              <button
                className="btn-danger"
                onClick={() => handleDeleteProject(project.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && !showForm && (
        <p className="empty-state">No projects yet. Create one to get started!</p>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn-page"
            onClick={() => setPage((p) => p - 1)}
            disabled={page === 0}
          >
            ← Previous
          </button>
          <span className="page-info">
            Page {page + 1} of {totalPages} &nbsp;({total} total)
          </span>
          <button
            className="btn-page"
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= totalPages - 1}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default Projects;
