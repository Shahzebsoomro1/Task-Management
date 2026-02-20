import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService, taskService } from '../services';
import './Projects.css';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await projectService.getProjects();
      setProjects(response.data);
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
      fetchProjects();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm('Are you sure?')) {
      try {
        await projectService.deleteProject(projectId);
        fetchProjects();
      } catch (err) {
        setError('Failed to delete project');
      }
    }
  };

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
    </div>
  );
};

export default Projects;
