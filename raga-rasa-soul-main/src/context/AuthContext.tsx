import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  user_id: string;
  email: string;
  role: 'user';
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // No-auth mode: always initialize a guest user.
  useEffect(() => {
    const guestUser: User = {
      user_id: 'guest',
      email: 'guest@local',
      role: 'user',
    };
    setUser(guestUser);
    setToken('guest-token');
    localStorage.setItem('user', JSON.stringify(guestUser));
    localStorage.setItem('auth_token', 'guest-token');
    setIsLoading(false);
  }, []);

  const login = async (_email: string, _password: string) => {
    return;
  };

  const register = async (_email: string, _password: string) => {
    return;
  };

  const logout = () => {
    // No-auth mode keeps app accessible; reset to guest identity.
    const guestUser: User = {
      user_id: 'guest',
      email: 'guest@local',
      role: 'user',
    };
    localStorage.setItem('auth_token', 'guest-token');
    localStorage.setItem('user', JSON.stringify(guestUser));
    setToken('guest-token');
    setUser(guestUser);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
