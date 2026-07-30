import { createContext, useState, useEffect, useContext } from 'react';
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error("Failed to fetch user:", error);
          setToken(null);
          localStorage.removeItem('token');
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, [token]);

  const login = async (email, password) => {
    const data = await apiLogin(email, password);
    const accessToken = data.access_token;
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    
    // Once we have a token, fetch the user
    const userData = await getCurrentUser();
    setUser(userData);
    return userData;
  };

  const logout = () => {
    apiLogout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
