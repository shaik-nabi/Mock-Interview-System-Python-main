
import React, { useState } from 'react';
import '../css/HomePage.css'; // Reuse styles or create new
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { toastErrorStyle } from '../components/utils/toastStyle';

function RegisterPage() {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const serverURL = process.env.REACT_APP_SERVER_URL;

    const validatePassword = (pwd) => {
        if (pwd.length < 8) return "Password must be at least 8 characters long.";
        if (!/[A-Z]/.test(pwd)) return "Password must contain at least one uppercase letter.";
        if (!/[0-9]/.test(pwd)) return "Password must contain at least one number.";
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) return "Password must contain at least one special character.";
        return null;
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        const pwdError = validatePassword(password);
        if (pwdError) {
            toast.error(pwdError, { ...toastErrorStyle(), autoClose: 3000 });
            return;
        }

        try {
            await axios.post(`${serverURL}/auth/signup`, {
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
            });
            toast.success("Registration successful! Please login.", { autoClose: 2000 });
            navigate('/login');
        } catch (error) {
            toast.error(
                error.response ? error.response.data.error : "Registration failed",
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
                    <h2>Register</h2>
                    <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '15px', width: '100%' }}>
                        <div className="input-row">
                            <input
                                type="text"
                                placeholder="First Name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                                className="auth-input"
                            />
                        </div>
                        <div className="input-row">
                            <input
                                type="text"
                                placeholder="Last Name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                                className="auth-input"
                            />
                        </div>
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
                        <button type="submit" className="StartInterviewButton" style={{ width: '100%' }}>Register</button>
                    </form>
                    <button onClick={() => navigate('/login')} className="SecondaryButton">Login</button>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
