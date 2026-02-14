import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  refresh: () => api.post('/api/auth/refresh'),
};

export const projectsAPI = {
  list: (skip = 0, limit = 50) => api.get('/api/projects', { params: { skip, limit } }),
  create: (data) => api.post('/api/projects', data),
  get: (projectId) => api.get(`/api/projects/${projectId}`),
  update: (projectId, data) => api.put(`/api/projects/${projectId}`, data),
  delete: (projectId) => api.delete(`/api/projects/${projectId}`),
};

export const assetsAPI = {
  getPresignedUrl: (projectId, data) => api.post(`/api/assets/presigned-url?project_id=${projectId}`, data),
  confirmUpload: (projectId, storageKey, fileType, originalFilename, fileSize) =>
    api.post(`/api/assets/confirm-upload/${projectId}`, null, {
      params: { storage_key: storageKey, file_type: fileType, original_filename: originalFilename, file_size: fileSize },
    }),
  getProjectAssets: (projectId) => api.get(`/api/assets/project/${projectId}`),
  delete: (assetId) => api.delete(`/api/assets/${assetId}`),
};

export const jobsAPI = {
  startEdit: (projectId) => api.post(`/api/jobs/project/${projectId}/start-edit`, {}),
  getStatus: (jobId) => api.get(`/api/jobs/${jobId}`),
  getLatest: (projectId) => api.get(`/api/jobs/project/${projectId}/latest`),
};

export default api;
