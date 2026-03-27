import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'test-api-key';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'X-API-Key': API_KEY,
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/api/auth/login', { username, password }),
  register: (username: string, password: string) =>
    api.post('/api/auth/register', { username, password }),
  me: () => api.get('/api/auth/me'),
};

export const usersApi = {
  list: () => api.get('/api/users'),
  get: (id: number) => api.get(`/api/users/${id}`),
  create: (data: { username: string; password: string; role: string }) =>
    api.post('/api/users', data),
  update: (id: number, data: { username?: string; password?: string; role?: string }) =>
    api.put(`/api/users/${id}`, data),
  delete: (id: number) => api.delete(`/api/users/${id}`),
};

export const mappingsApi = {
  list: () => api.get('/api/mappings'),
  create: (data: { name: string; mapping: Record<string, string> }) =>
    api.post('/api/mappings', data),
  delete: (id: number) => api.delete(`/api/mappings/${id}`),
};

export const channelsApi = {
  list: () => api.get('/api/channels'),
  create: (data: { name: string; external_id: string }) =>
    api.post('/api/channels', data),
};

export const teamsApi = {
  list: () => api.get('/api/teams'),
  create: (data: { name: string }) => api.post('/api/teams', data),
};

export const agentsApi = {
  list: () => api.get('/api/agents'),
  create: (data: { name: string; external_id: string }) =>
    api.post('/api/agents', data),
};

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

export const conversationsApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/api/conversations', { params }),
  stats: {
    monthly: () => api.get(`/api/conversations/stats/monthly?year=${currentYear}&month=${currentMonth}`),
    aiVsHuman: () => api.get(`/api/conversations/stats/ai-vs-human?year=${currentYear}&month=${currentMonth}`),
  },
};

export const lifecyclesApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/api/lifecycles', { params }),
  stats: {
    pipeline: () => api.get('/api/lifecycles/stats/pipeline'),
  },
};

export const adsApi = {
  list: (params?: { skip?: number; limit?: number }) => api.get('/api/ads', { params }),
  stats: {
    byChannel: () => api.get(`/api/ads/stats/by-channel?year=${currentYear}&month=${currentMonth}`),
    topCampaigns: () => api.get(`/api/ads/stats/top-campaigns?year=${currentYear}&month=${currentMonth}`),
  },
};

export const csatApi = {
  list: (params?: { skip?: number; limit?: number }) => api.get('/api/csat', { params }),
  stats: {
    average: () => api.get(`/api/csat/stats/average?year=${currentYear}&month=${currentMonth}`),
    byAgent: () => api.get(`/api/csat/stats/by-agent?year=${currentYear}&month=${currentMonth}`),
  },
};

export const importApi = {
  import: (spreadsheetType: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/import/${spreadsheetType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  templates: (spreadsheetType: string) =>
    api.get(`/api/import/templates/${spreadsheetType}`),
};
