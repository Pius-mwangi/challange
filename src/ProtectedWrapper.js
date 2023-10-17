// ProtectedWrapper.js

import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedWrapper = ({ children }) => {
  const isAuthenticated = Boolean(localStorage.getItem('token'));

  if (isAuthenticated) {
    return children;
  } else {
    return <Navigate to="/login" replace />;
  }
};

export default ProtectedWrapper;
