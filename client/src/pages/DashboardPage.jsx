import React, { useEffect, useState, useContext } from 'react';
import '../css/DashboardPage.css';
import axios from 'axios';
import { toast } from 'react-toastify';
import { toastErrorStyle } from '../components/utils/toastStyle';
import { GlobalContext } from '../components/utils/GlobalState';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Canvas3D from '../components/utils/Canvas3D';

function DashboardPage() {
    const { gUser } = useContext(GlobalContext);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const serverURL = process.env.REACT_APP_SERVER_URL;

    useEffect(() => {
        if (!gUser) {
            navigate('/login');
            return;
        }
        fetchStats();
    }, [gUser]);

    const fetchStats = async () => {
        try {
            const response = await axios.get(`${serverURL}/api/dashboard-stats`, {
                params: { user_id: gUser.id }
            });
            setStats(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching stats:", error);
            toast.error("Failed to load dashboard data", { ...toastErrorStyle(), autoClose: 2000 });
            setLoading(false);
        }
    };

    const handleBack = () => {
        navigate('/');
    };

    if (loading) {
        return (
            <div className='dashboard-loading'>
                <Canvas3D pos={[0, -3, 0]} scale={[6.5, 6.5, 6.5]} modelPath={'/robot1.glb'} classname={'robotloading'} />
                <h1>Loading Dashboard...</h1>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h1>Your Interview Performance</h1>
                <button onClick={handleBack} className="back-btn">Back to Home</button>
            </div>

            {stats && (
                <div className="dashboard-content">
                    <div className="stats-cards">
                        <div className="card">
                            <h3>Total Interviews</h3>
                            <p className="card-value">{stats.totalInterviews}</p>
                        </div>
                        <div className="card">
                            <h3>Average Rating</h3>
                            <p className="card-value">{stats.averageRating}/10</p>
                        </div>
                        <div className="card">
                            <h3>Response Rate</h3>
                            <p className="card-value">{stats.responseRate}%</p>
                        </div>
                    </div>

                    <div className="chart-section">
                        <h2>Performance Trend</h2>
                        {stats.recentPerformance.length > 0 ? (
                            <div className="chart-container">
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={stats.recentPerformance}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="date" />
                                        <YAxis domain={[0, 10]} />
                                        <Tooltip />
                                        <Bar dataKey="rating" fill="#EDC215" barSize={30} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <p className="no-data">No interview data available yet. Start your first interview!</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default DashboardPage;
