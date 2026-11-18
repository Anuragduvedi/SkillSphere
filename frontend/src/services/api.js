
import axios from 'axios';

const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    let url = envUrl.trim();
    if (!url.endsWith('/api/v1')) {
      url = url.replace(/\/+$/, '') + '/api/v1';
    }
    return url;
  }
  // Production default: connects to the live SkillSphere backend on Render
  if (import.meta.env.PROD) {
    return 'https://skillsphere-33s9.onrender.com/api/v1';
  }
  // Local development default: uses Vite proxy
  return '/api/v1';
};

const api = axios.create({
  baseURL: getBaseURL(),
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
      if (
        window.location.pathname !== '/login' &&
        window.location.pathname !== '/register' &&
        window.location.pathname !== '/'
      ) {
        localStorage.removeItem('skillsphere_token');
        localStorage.removeItem('skillsphere_user');
        window.location.href = '/login?expired=true';
      }
    }

    return Promise.reject(error);
  }
);

// ================= AUTH API =================

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

// ================= RESUME API =================

export const resumeAPI = {
  upload: (formData) =>
    api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getProfile: () => api.get('/resume/profile'),
  updateProfile: (data) => api.put('/resume/update-profile', data),

  analyze: (jobId, resumeId) =>
    api.post('/resume/analyze', {
      job_id: jobId,
      resume_id: resumeId,
    }),
};

// ================= JOBS API =================

export const jobsAPI = {
  list: (params) => api.get('/jobs', { params }),
  get: (id) => api.get(`/jobs/${id}`),
  create: (data) => api.post('/jobs', data),
  update: (id, data) => api.put(`/jobs/${id}`, data),
  delete: (id) => api.delete(`/jobs/${id}`),
};

// ================= APPLICATIONS API =================

export const applicationsAPI = {
  apply: (jobId, data) => api.post(`/jobs/${jobId}/apply`, data),
  list: () => api.get('/applications'),

  updateStatus: (appId, status) =>
    api.put(`/applications/${appId}/status`, { status }),

  withdraw: (appId) => api.post(`/applications/${appId}/withdraw`),
};

// ================= RECRUITER API =================

export const recruiterAPI = {
  getApplicants: (params) => api.get('/recruiter/applicants', { params }),
  getStats: () => api.get('/recruiter/stats'),
  getCompany: () => api.get('/recruiter/company'),
  updateCompany: (data) => api.put('/recruiter/company', data),

  exportCsv: (jobId) =>
    api.get('/recruiter/export-applicants', {
      params: { job_id: jobId },
      responseType: 'blob',
    }),
};

// ================= ADMIN API =================

export const adminAPI = {
  getAnalytics: () => api.get('/admin/analytics'),
  getUsers: () => api.get('/admin/users'),

  toggleUserStatus: (userId) =>
    api.put(`/admin/users/${userId}/toggle-status`),

  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  getJobs: () => api.get('/admin/jobs'),
  moderateJob: (jobId) => api.put(`/admin/jobs/${jobId}/moderate`),
};

// ================= ASSESSMENT API =================

export const assessmentAPI = {
  // Candidate Assessment
  getByToken: (token) =>
    api.get(`/assessment/by-token/${token}`),

  // Start Assessment
  // Correct backend route: /api/v1/{assessment_id}/start
  start: (assessmentId) =>
    api.post(`/${assessmentId}/start`),

  // Submit Assessment
  submit: (assessmentId, answers) =>
    api.post(`/assessment/${assessmentId}/submit`, { answers }),

  // Get Assessment Results
  getResults: (assessmentId) =>
    api.get(`/assessment/${assessmentId}/results`),

  // Get Candidate Tests
  getMyTests: () =>
    api.get('/assessment/my-tests'),

  // ================= PROCTORING =================

  // Correct backend route: /api/v1/{assessment_id}/proctoring-events
 
recordProctoringEvent: (assessmentId, eventType, details, answers, options = {}) =>
  api.post(`/${assessmentId}/proctoring-events`, {
    event_type: eventType,
    details: details,
    answers: answers,
    severity: options.severity,
    confidence: options.confidence,
    instant_terminate: options.instant_terminate || false,
    session_id: options.session_id,
  }),


  // ================= QUESTION MANAGEMENT =================

  createQuestion: (data) =>
    api.post('/assessment/questions', data),

  getQuestions: (params) =>
    api.get('/assessment/questions', { params }),

  updateQuestion: (id, data) =>
    api.put(`/assessment/questions/${id}`, data),

  deleteQuestion: (id) =>
    api.delete(`/assessment/questions/${id}`),

  getQuestionLibrary: (params) =>
    api.get('/assessment/question-library', { params }),

  importFromLibrary: (params) =>
    api.post('/assessment/questions/import-from-library', null, { params }),

  // ================= ASSESSMENT TEMPLATES =================

  createTemplate: (data) =>
    api.post('/assessment/templates', data),

  getTemplates: (params) =>
    api.get('/assessment/templates', { params }),

  getTemplateDetails: (id) =>
    api.get(`/assessment/templates/${id}`),

  updateTemplate: (id, data) =>
    api.put(`/assessment/templates/${id}`, data),

  publishTemplate: (id) =>
    api.post(`/assessment/templates/${id}/publish`),

  deleteTemplate: (id) =>
    api.delete(`/assessment/templates/${id}`),

  // ================= RECRUITER STATS =================

  getRecruiterStats: () =>
    api.get('/assessment/recruiter/stats'),

  getRecruiterCandidateResults: (params) =>
    api.get('/assessment/recruiter/candidate-results', { params }),

  // ================= RECRUITER DIRECT ASSIGNMENT & TRACKING =================

  getAssignableCandidates: (params) =>
    api.get('/assessment/recruiter/assignable-candidates', { params }),

  assignAssessment: (data) =>
    api.post('/assessment/recruiter/assign', data),

  getAssignedTracking: (params) =>
    api.get('/assessment/recruiter/assigned-tracking', { params }),

  generateQuestionsAI: (data) =>
    api.post('/assessment/generate-questions-ai', data),

  // ================= ADMIN MONITORING =================

  getAdminStats: () =>
    api.get('/assessment/admin/statistics'),

  getAdminAllTemplates: () =>
    api.get('/assessment/admin/all-templates'),

  getAdminAllQuestions: (params) =>
    api.get('/assessment/admin/all-questions', { params }),

  getAdminProctoringEvents: () =>
    api.get('/assessment/admin/proctoring-events'),

  getProctoringReports: (params) =>
    api.get('/assessment/proctoring/reports', { params }),

  getAssessmentProctoringEvents: (assessmentId) =>
    api.get(`/assessment/${assessmentId}/proctoring-events`),
};

// ================= AI CHATBOT API =================

export const chatbotAPI = {
  sendMessage: (message, history = [], context = {}) =>
    api.post('/chatbot/message', { message, history, context }),

  getStatus: () =>
    api.get('/chatbot/status'),
};

// ================= SCREENING API =================

export const screeningAPI = {
  getCandidatesForJob: (jobId) =>
    api.get(`/screening/jobs/${jobId}/candidates`),

  autoShortlist: (jobId) =>
    api.post(`/screening/jobs/${jobId}/auto-shortlist`),

  generateTest: (candidateId, jobId) =>
    api.post(
      `/screening/candidates/${candidateId}/generate-test?job_id=${jobId}`
    ),

  getStats: () =>
    api.get('/screening/dashboard-stats'),

  getAllAssessments: () =>
    api.get('/screening/all-assessments'),

  getEmails: () =>
    api.get('/screening/emails'),
};

export default api;
