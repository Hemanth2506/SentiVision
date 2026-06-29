import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Crucial for httpOnly cookies
});

// Request Interceptor: Attach bearer token header if it exists in localStorage (as a fallback)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Catch auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear local auth storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Dispatch custom event to trigger redirect if outside React lifecycle
      window.dispatchEvent(new Event('auth-unauthorized'));
    }
    return Promise.reject(error);
  }
);

// ─── API Wrapper Functions ──────────────────────────────────────

export const authAPI = {
  signup: async (name, email, password) => {
    const response = await api.post('/auth/signup', { name, email, password });
    return response.data;
  },
  
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (e) {
      console.warn("Logout endpoint failed, clearing local storage anyway.", e);
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

export const analyzerAPI = {
  analyzeText: async (text) => {
    const response = await api.post('/analyze', { input_text: text });
    return response.data;
  },
  
  analyzeBatch: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/analyze/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};

export const statsAPI = {
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
  
  getHistory: async (page = 1, limit = 10, search = '', sentiment = '') => {
    const params = { page, limit };
    if (search) params.search = search;
    if (sentiment) params.sentiment = sentiment;
    const response = await api.get('/history', { params });
    return response.data;
  },

  resetData: async () => {
    const response = await api.delete('/stats/reset');
    return response.data;
  }
};

export default api;
