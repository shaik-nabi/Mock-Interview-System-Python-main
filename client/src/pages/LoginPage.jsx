
import React, { useState, useContext } from 'react';
import { GlobalContext } from '../components/utils/GlobalState';
import '../css/HomePage.css';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { toastErrorStyle } from '../components/utils/toastStyle';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const { login } = useContext(GlobalContext);
    const serverURL = process.env.REACT_APP_SERVER_URL;

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${serverURL}/auth/login`, {
                email: email,
                password: password
            });
            // Store user details if needed, for now just toast and redirect
            toast.success(`Welcome back ${response.data.user.first_name}!`, { autoClose: 2000 });
            login(response.data.user);
            navigate('/');
        } catch (error) {
            toast.error(
                error.response ? error.response.data.error : "Login failed",
                { ...toastErrorStyle(), autoClose: 3000 }
            );
        }
    };

    return (
        <div className='Home-div'>
            <div className='header-div'>
                <h1 className='header-text'>MOCK INTERVIEW</h1>
            </div>
            <div className='context-div' style={{ flexDirection: 'column', color: 'white' }}>
                <div className="auth-box">
                    <h2>Login</h2>
                    <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%' }}>
                        <div className="input-row">
                            <input
                                type="email"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="auth-input"
                            />
                        </div>
                        <div className="input-row">
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="auth-input"
                            />
                        </div>
                        <button type="submit" className="StartInterviewButton" style={{ width: '100%' }}>Login</button>
                    </form>
                    <button onClick={() => navigate('/register')} className="SecondaryButton">Register</button>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
