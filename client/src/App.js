import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import InterviewPage from './pages/InterviewPage';
import { GlobalProvider } from './components/utils/GlobalState';
import ReviewPage from './pages/ReviewPageNew';
import DashboardPage from './pages/DashboardPage';
import 'bootstrap/dist/css/bootstrap.min.css';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';

function App() {
  return (
    <Router>
      <GlobalProvider>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </GlobalProvider>
    </Router>
  );
}

export default App;