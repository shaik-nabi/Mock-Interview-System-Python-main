import React, { createContext, useState } from 'react';

export const GlobalContext = createContext();

export const GlobalProvider = ({ children }) => {
  const [gJobRole, setGJobRole] = useState('');
  const [gJobExp, setGJobExp] = useState('');
  const [gQtns, setGQtns] = useState([]);
  const [gAns, setGAns] = useState([]);
  const [gValidInterview, setGValidInterview] = useState(null); // should be null
  const [gValidReview, setGValidReview] = useState(false);
  const [gSuspiciousCount, setGSuspiciousCount] = useState(0);
  const [gSessionId, setGSessionId] = useState(null);

  const updateGQtnGenerationData = (jobRole, jobExp, questions) => {
    setGJobRole(jobRole);
    setGJobExp(jobExp);
    setGQtns(questions);
  };

  const [gUser, setGUser] = useState(JSON.parse(localStorage.getItem('user')) || null);

  const login = (userData) => {
    setGUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setGUser(null);
    localStorage.removeItem('user');
  };

  return (
    <GlobalContext.Provider value={{
      gJobRole, gJobExp, gQtns, gValidInterview,
      updateGQtnGenerationData, setGValidInterview,
      gSuspiciousCount, setGSuspiciousCount,
      gAns, setGAns,
      gValidReview, setGValidReview,
      gUser, login, logout,
      gSessionId, setGSessionId
    }}
    >
      {children}
    </GlobalContext.Provider>
  );
};