import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Business API
export const businessAPI = {
  getBusinesses: (params = {}) => api.get('/businesses/', { params }),
  getBusiness: (id) => api.get(`/businesses/${id}`),
  createBusiness: (data) => api.post('/businesses/', data),
  updateBusiness: (id, data) => api.put(`/businesses/${id}`, data),
  deleteBusiness: (id) => api.delete(`/businesses/${id}`),
  getBusinessStats: () => api.get('/businesses/stats/summary'),
  searchBusinesses: (params) => api.get('/businesses/search/', { params }),
};

// Jobs API
export const jobsAPI = {
  getJobs: (params = {}) => api.get('/jobs/', { params }),
  getJob: (id) => api.get(`/jobs/${id}`),
  startGoogleMapsCrawl: (data) => api.post('/jobs/start-google-maps-crawl', data),
  startWebsiteCheck: (data) => api.post('/jobs/start-website-check', data),
  cancelJob: (id) => api.post(`/jobs/${id}/cancel`),
  retryJob: (id) => api.post(`/jobs/${id}/retry`),
};

// Website Checks API
export const websiteChecksAPI = {
  getWebsiteChecks: (params = {}) => api.get('/website-checks/', { params }),
  getWebsiteCheck: (id) => api.get(`/website-checks/${id}`),
  getBusinessWebsiteChecks: (businessId) => api.get(`/website-checks/business/${businessId}`),
};

// Exports API
export const exportsAPI = {
  exportBusinessesCSV: (params) => api.post('/exports/businesses/csv', params),
  exportBusinessesExcel: (params) => api.post('/exports/businesses/excel', params),
  exportZZPWithoutWebsite: () => api.get('/exports/zzp-without-website'),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: () => api.get('/dashboard/recent-activity'),
  getTopCities: () => api.get('/dashboard/top-cities'),
  getTopIndustries: () => api.get('/dashboard/top-industries'),
  getWebsiteCheckSuccessRate: () => api.get('/dashboard/website-check-success-rate'),
  getJobPerformance: () => api.get('/dashboard/job-performance'),
};

export default api;
