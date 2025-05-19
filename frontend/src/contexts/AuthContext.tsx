import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '../api/auth';
import { getCurrentUser } from '../api/auth';
import { getToken, setUser, getUser, clearToken, clearUser } from '../utils/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(getUser());
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      if (getToken() && !user) {
        setLoading(true);
        try {
          const userData = await getCurrentUser();
          setUserState(userData);
          setUser(userData);
        } catch (err) {
          console.error('Failed to fetch user:', err);
          clearToken();
          clearUser();
          setError('Failed to authenticate user');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchUser();
  }, [user]);

  const login = async (token: string) => {
    setLoading(true);
    try {
      // 保存token
      localStorage.setItem('token', token);

      // 获取用户信息
      const userData = await getCurrentUser();
      setUserState(userData);
      setUser(userData);
      setError(null);
    } catch (err) {
      console.error('Login failed:', err);
      clearToken();
      setError('Failed to authenticate user');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    clearToken();
    clearUser();
    setUserState(null);
  };

  const updateUser = (updatedUser: User) => {
    setUserState(updatedUser);
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
