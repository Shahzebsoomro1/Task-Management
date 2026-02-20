import api from './api';

export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

export const projectService = {
  getProjects: () => api.get('/projects'),
  getProject: (id) => api.get(`/projects/${id}`),
  createProject: (data) => api.post('/projects', data),
  updateProject: (id, data) => api.put(`/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/projects/${id}`),
};

export const taskService = {
  getTasks: (projectId, params) => 
    api.get(`/projects/${projectId}/tasks`, { params }),
  getTask: (projectId, taskId) =>
    api.get(`/projects/${projectId}/tasks/${taskId}`),
  createTask: (projectId, data) =>
    api.post(`/projects/${projectId}/tasks`, data),
  updateTask: (projectId, taskId, data) =>
    api.put(`/projects/${projectId}/tasks/${taskId}`, data),
  deleteTask: (projectId, taskId) =>
    api.delete(`/projects/${projectId}/tasks/${taskId}`),
};

export const commentService = {
  getComments: (taskId) => api.get(`/tasks/${taskId}/comments`),
  createComment: (taskId, data) =>
    api.post(`/tasks/${taskId}/comments`, data),
  updateComment: (taskId, commentId, data) =>
    api.put(`/tasks/${taskId}/comments/${commentId}`, data),
  deleteComment: (taskId, commentId) =>
    api.delete(`/tasks/${taskId}/comments/${commentId}`),
};
