import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import * as apiService from "./apiService";
import "./LogIn.css";

const LogIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogin = async () => {
    try {
      const response = await apiService.login(username, password);
      if (response && response.message === "Logged in successfully!") {
        localStorage.setItem("token", response.token);
        setLoggedIn(true);
      } else {
        alert("Login failed. Please check your credentials.");
      }
    } catch (error) {
      console.error("Error during login", error);
      alert("An error occurred during login. Please try again.");
    }
  };

  if (loggedIn) {
    return <Navigate to="/dashboard" />;
  }

  return (
    <div className="login-container">
      <h2>Login to Your Account</h2>
      <input 
        type="text" 
        placeholder="Username" 
        onChange={(e) => setUsername(e.target.value)} 
      />
      <input 
        type="password" 
        placeholder="Password" 
        onChange={(e) => setPassword(e.target.value)} 
      />
      <button onClick={handleLogin}>Log In</button>
    </div>
  );
};

export default LogIn;
