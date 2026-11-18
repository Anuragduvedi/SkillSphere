
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

// Safely restore user data from browser storage
const getSavedUser = () => {
  try {
    const saved = localStorage.getItem('skillsphere_user');

    if (!saved || saved === 'undefined' || saved === 'null') {
      return null;
    }

    return JSON.parse(saved);
  } catch (error) {
    console.error('Invalid saved user data. Clearing it:', error);
    localStorage.removeItem('skillsphere_user');
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getSavedUser);

  const [token, setToken] = useState(
    () => localStorage.getItem('skillsphere_token')
  );

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchUser = async () => {
      if (token) {
        try {
          const res = await authAPI.me();

          if (isMounted) {
            setUser(res.data);
            localStorage.setItem(
              'skillsphere_user',
              JSON.stringify(res.data)
            );
          }
        } catch (err) {
          console.error('Failed to restore session', err);

          if (isMounted) {
            logout();
          }
        }
      }

      if (isMounted) {
        setLoading(false);
      }
    };

    fetchUser();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });

    const { access_token, user: userData } = res.data;

    localStorage.setItem('skillsphere_token', access_token);
    localStorage.setItem('skillsphere_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);

    return userData;
  };

  const register = async (registerData) => {
    const res = await authAPI.register(registerData);

    const { access_token, user: userData } = res.data;

    localStorage.setItem('skillsphere_token', access_token);
    localStorage.setItem('skillsphere_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);

    return userData;
  };

  const logout = () => {
    localStorage.removeItem('skillsphere_token');
    localStorage.removeItem('skillsphere_user');

    setToken(null);
    setUser(null);
  };

  const refreshProfile = async () => {
    try {
      const res = await authAPI.me();

      setUser(res.data);

      localStorage.setItem(
        'skillsphere_user',
        JSON.stringify(res.data)
      );
    } catch (err) {
      console.error('Profile refresh failed', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        refreshProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
