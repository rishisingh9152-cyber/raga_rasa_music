import React from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // No-auth mode: route protection disabled.
  return <>{children}</>;
};

export default ProtectedRoute;
