import React from 'react';

interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  // No-auth mode: no redirection.
  return <>{children}</>;
};

export default PublicRoute;
