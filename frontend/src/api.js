import axios from 'axios';

// Default to localhost, but allow overriding via environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Automatically attach the JWT token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Automatically log out if the token expires (401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Uncomment this line to force a reload to the login screen on expiration
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==========================================
// Authentication APIs
// ==========================================
export const authAPI = {
  login: async (email, password) => {
    // FastAPI's OAuth2 implementation requires Form-Urlencoded data for login, not JSON.
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }
};

// ==========================================
// Dashboard KPIs
// ==========================================
export const dashboardAPI = {
  getDealerDashboard: async () => {
    const response = await apiClient.get('/dashboards/dealer');
    return response.data;
  },
  getCustomerDashboard: async () => {
    const response = await apiClient.get('/dashboards/customer');
    return response.data;
  },
  getFleetManagerDashboard: async () => {
    const response = await apiClient.get('/dashboards/fleet-manager');
    return response.data;
  }
};

// ==========================================
// Machine APIs
// ==========================================
export const machineAPI = {
  getAll: async (params = {}) => {
    // params can include { status: 'AVAILABLE', dealer_id: 1 }
    const response = await apiClient.get('/machines/', { params });
    return response.data;
  },
  getDetails: async (equipmentId) => {
    const response = await apiClient.get(`/machines/${equipmentId}`);
    return response.data;
  },
  getTimeline: async (equipmentId) => {
    const response = await apiClient.get(`/machines/${equipmentId}/timeline`);
    return response.data;
  }
};

// ==========================================
// Rental APIs
// ==========================================
export const rentalAPI = {
  getAll: async (filters = {}) => {
    // Clean up undefined/null values
    const cleanedFilters = Object.fromEntries(Object.entries(filters).filter(([_, v]) => v != null && v !== ''));
    const params = new URLSearchParams(cleanedFilters);
    const response = await apiClient.get(`/rentals/?${params.toString()}`);
    return response.data;
  },
  getTransfers: async () => {
    const response = await apiClient.get('/rentals/transfer');
    return response.data;
  },
  getCheckins: async () => {
    const response = await apiClient.get('/rentals/check-action');
    return response.data;
  },
  createTransfer: async (transferData) => {
    const response = await apiClient.post('/rentals/transfer', transferData);
    return response.data;
  },
  create: async (data) => {
    const response = await apiClient.post('/rentals/', data);
    return response.data;
  },
  transferSite: async (data) => {
    const response = await apiClient.post('/rentals/transfer', data);
    return response.data;
  },
  checkinCheckout: async (data) => {
    const response = await apiClient.post('/rentals/check-action', data);
    return response.data;
  }
};

// ==========================================
// Operator APIs
// ==========================================
export const operatorAPI = {
  getAll: async () => {
    const response = await apiClient.get('/operators/');
    return response.data;
  },
  create: async (data) => {
    const response = await apiClient.post('/operators/', data);
    return response.data;
  }
};

// ==========================================
// Site APIs
// ==========================================
export const siteAPI = {
  getAll: async () => {
    const response = await apiClient.get('/sites/');
    return response.data;
  }
};

// ==========================================
// Usage APIs
// ==========================================
export const usageAPI = {
  getAll: async () => {
    const response = await apiClient.get('/events/usage');
    return response.data;
  }
};

// ==========================================
// Notification APIs
// ==========================================
export const notificationAPI = {
  getAll: async () => {
    const response = await apiClient.get('/notifications/');
    return response.data;
  },
  markAsRead: async (id) => {
    const response = await apiClient.put(`/notifications/${id}/read`);
    return response.data;
  }
};

// ==========================================
// Prediction APIs
// ==========================================
export const predictionAPI = {
  getDemand: async () => {
    const response = await apiClient.get('/predictions/demand');
    return response.data;
  },
  getUtilization: async () => {
    const response = await apiClient.get('/predictions/utilization');
    return response.data;
  },
  getMaintenance: async () => {
    const response = await apiClient.get('/predictions/maintenance');
    return response.data;
  },
  getAnomaly: async () => {
    const response = await apiClient.get('/predictions/anomaly');
    return response.data;
  }
};

export default apiClient;
