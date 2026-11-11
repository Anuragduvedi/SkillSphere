import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('skillsphere_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle expired tokens or unauthorized access
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if invalid or expired
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        localStorage.removeItem('skillsphere_token');
        localStorage.removeItem('skillsphere_user');
        window.location.href = '/login?expired=true';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

export const resumeAPI = {
  upload: (formData) => api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getProfile: () => api.get('/resume/profile'),
  updateProfile: (data) => api.put('/resume/update-profile', data),
  analyze: (jobId, resumeId) => api.post('/resume/analyze', { job_id: jobId, resume_id: resumeId }),
};

export const jobsAPI = {
  list: (params) => api.get('/jobs', { params }),
  get: (id) => api.get(`/jobs/${id}`),
  create: (data) => api.post('/jobs', data),
  update: (id, data) => api.put(`/jobs/${id}`, data),
  delete: (id) => api.delete(`/jobs/${id}`),
};

export const applicationsAPI = {
  apply: (jobId, data) => api.post(`/jobs/${jobId}/apply`, data),
  list: () => api.get('/applications'),
  updateStatus: (appId, status) => api.put(`/applications/${appId}/status`, { status }),
  withdraw: (appId) => api.post(`/applications/${appId}/withdraw`),
};

export const recruiterAPI = {
  getApplicants: (params) => api.get('/recruiter/applicants', { params }),
  getStats: () => api.get('/recruiter/stats'),
  getCompany: () => api.get('/recruiter/company'),
  updateCompany: (data) => api.put('/recruiter/company', data),
  exportCsv: (jobId) => api.get('/recruiter/export-applicants', {
    params: { job_id: jobId },
    responseType: 'blob',
  }),
};

export const adminAPI = {
  getAnalytics: () => api.get('/admin/analytics'),
  getUsers: () => api.get('/admin/users'),
  toggleUserStatus: (userId) => api.put(`/admin/users/${userId}/toggle-status`),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  getJobs: () => api.get('/admin/jobs'),
  moderateJob: (jobId) => api.put(`/admin/jobs/${jobId}/moderate`),
};

export default api;
