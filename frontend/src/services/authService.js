import api from './api';

export const login = async (email, password) => {
  // FastAPI expects x-www-form-urlencoded data for OAuth2PasswordRequestForm
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data; // Should contain access_token
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data; // Should contain User details including role
};

export const logout = () => {
  localStorage.removeItem('token');
};
