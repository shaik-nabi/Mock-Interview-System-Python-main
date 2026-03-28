import React, { useContext, useEffect, useState } from 'react';
import '../css/HomePage.css';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { toastErrorStyle } from '../components/utils/toastStyle';
import { FaArrowLeftLong } from "react-icons/fa6";
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { GlobalContext } from '../components/utils/GlobalState';


function HomePage() {
    const { updateGQtnGenerationData, setGValidInterview, setGValidReview, gUser, logout, setGSessionId } = useContext(GlobalContext);
    const [jobInput, setJobInput] = useState('');
    const [isVisible, setIsVisible] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const experienceLevel = 'fresher';
    const navigate = useNavigate();
    const [displayText, setDisplayText] = useState('');
    const serverURL = process.env.REACT_APP_SERVER_URL;

    useEffect(() => {
        const text = "From Practice to Perfection - Your Interview Journey Starts Here!";
        let count = 0;
        let temp = "";
        const intervalId = setInterval(() => {
            if (count >= text.length) {
                clearInterval(intervalId);
                return;
            }
            temp += text[count];
            setDisplayText(temp);
            count++;
        }, 100);
        return () => clearInterval(intervalId);
    }, []);
    //   -----------------------------------------------------------------------

    useEffect(() => {
        setGValidReview(false); // once entered homepage then cannot go to review page unless interview is done
    }, [])

    const handleGetStartedClick = () => {
        setIsVisible(false); // Hide the jobTitle-div

    };

    const handleBackClick = () => {
        setIsVisible(true); // Show the jobTitle-div
        setJobInput('');
    };

    const handleLogout = () => {
        logout();
        toast.success("Logged out successfully!", { autoClose: 2000 });
    };

    const handleStartInterviewClick = async () => {
        const sendingInput = jobInput.trim();
        if (sendingInput.length > 0) {
            try {
                setIsLoading(true);

                // Start interview session if user is logged in
                let sessionId = null;
                if (gUser) {
                    const sessionResponse = await axios.post(`${serverURL}/api/start-interview`, {
                        user_id: gUser.id,
                        job_role: sendingInput,
                        experience_level: experienceLevel
                    });
                    sessionId = sessionResponse.data.session.id;
                    setGSessionId(sessionId);
                }

                const response = await axios.post(`${serverURL}/api/get-questions`, {
                    job_role: sendingInput,
                    experience_lvl: experienceLevel,
                    session_id: sessionId,
                    question_count: 10
                });

                updateGQtnGenerationData(response.data.job_role, response.data.exp_lvl, response.data.qtns);
                setGValidInterview(true); // set as global valid interview as true
                navigate('/interview');
            } catch (error) {
                toast.error(error.response ? error.response.data.errorMsg : error.message || error,
                    { ...toastErrorStyle(), autoClose: 2000 }
                );
                console.log("Something went wrong!", error.response ? error.response.data.errorMsg : error.message || error);
            } finally {
                setIsLoading(false);
            }
        } else {
            toast.error("Please provide job title!", { ...toastErrorStyle(), autoClose: 2000 });
        }
    };


    const handleInputChange = (event) => {
        const inputValue = event.target.value;
        setJobInput(inputValue);
    };

    return (
        <div className='Home-div'>
            <div className='header-div'>
                <h1 className='header-text'>MOCK INTERVIEW</h1>
                <div style={{ position: 'absolute', right: '20px', display: 'flex', gap: '10px' }}>
                    {!gUser ? (
                        <>
                            <button onClick={() => navigate('/login')} className="NavButton">Login</button>
                            <button onClick={() => navigate('/register')} className="NavButton">Register</button>
                        </>
                    ) : (
                        <>
                            <button onClick={() => navigate('/dashboard')} className="NavButton">Dashboard</button>
                            <button onClick={handleLogout} className="NavButton">Logout</button>
                        </>
                    )}
                </div>
            </div>
            <div className='context-div'>
                <div className='text-div'>
                    <div className='Typing-effect'>
                        <p>{displayText}</p>
                    </div>

                    <button
                        className={`getStartedButton ${isVisible ? '' : 'hidden'}`}
                        onClick={handleGetStartedClick}>Get Started</button>
                </div>

                <div className='video-div'>
                    {/* <img className='image' src={'/assets/homePagePic3.jpg'} alt="Background" /> */}
                    <video className='video-tag' src={'/assets/homePageVideo1.mp4'} autoPlay muted loop />
                </div>

                <div className={`jobTitle-div ${isVisible ? 'hidden' : ''}`}>
                    <FaArrowLeftLong className='Left-arrow' onClick={!isLoading ? handleBackClick : null} />
                    <label className='joblabel'>Enter job role</label>
                    <input className='jobinput' type='text' value={jobInput} onChange={handleInputChange}
                        maxLength={35} placeholder='Eg: HR, Software Engineer' disabled={isLoading} />

                    <button className='StartInterviewButton' onClick={handleStartInterviewClick} disabled={isLoading}>
                        {isLoading ? <> Preparing Interview <FontAwesomeIcon icon={faSpinner} spin /> </>
                            : 'Start your interview'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default HomePage;
