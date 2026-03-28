import React, { useEffect, useState, useContext } from 'react';
import '../css/ReviewPageNew.css';
import Markdown from 'react-markdown'
import axios from 'axios';
import { toast } from 'react-toastify';
import { toastErrorStyle } from '../components/utils/toastStyle';
import { GlobalContext } from '../components/utils/GlobalState';
import Canvas3D from '../components/utils/Canvas3D';
import { useNavigate } from 'react-router-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

function ReviewPage() {
  // access global values and functions
  const { gJobRole, gQtns, gAns, gValidReview, gSuspiciousCount, gSessionId } = useContext(GlobalContext);

  const [review, setReview] = useState('');
  const [displayText, setDisplayText] = useState('');
  const [answered, setAnswered] = useState(0);
  const [skipped, setSkipped] = useState(0);
  const [rating, setRating] = useState(0);
  const navigate = useNavigate();
  const serverURL = process.env.REACT_APP_SERVER_URL;

  // typing effect--------------
  useEffect(() => {
    let count = 0;
    let temp = "";
    let speed = review.length > 1000 ? 20 : 40;
    const intervalId = setInterval(() => {
      if (count >= review.length) {
        clearInterval(intervalId);
        return;
      }

      temp += review[count];
      setDisplayText(temp);
      count++;
    }, speed);
    return () => clearInterval(intervalId);
  }, [review]);

  // check if valid entry to review page
  useEffect(() => {
    if (!gValidReview) {
      window.location.replace('/'); // Re-direct to home page
    }
  }, []);

  // call getReview
  useEffect(() => {
    getReview();
  }, [gAns]); // call when ans data is loaded, then rest variables are assumed loaded

  const getReview = async () => {
    if (gAns.length === 0) return; // extra validation
    if (review !== '') return; // extra validation

    try {
      const response = await axios.post(`${serverURL}/api/get-review`, {
        job_role: gJobRole,
        qns: gQtns,
        ans: gAns,
        suspiciousCount: gSuspiciousCount,
        session_id: gSessionId
      });

      setReview(response.data.review);
      setAnswered(response.data.answered);
      setSkipped(response.data.skipped);
      setRating(response.data.rating);
    } catch (error) {
      toast.error(error.response ? error.response.data.errorMsg : error.message || error,
        { ...toastErrorStyle(), autoClose: 2000 }
      );
      console.log("Something went wrong!", error.response ? error.response.data.errorMsg : error.message || error);
    }
  }

  const gotoHomePage = () => {
    navigate('/', { replace: true });
  }

  return (
    <div className='review-main-div'>

      {/* Review display part */}
      <div className='left-main-div'>
        {
          review.length <= 0 ?
            <div className='loading-div'>
              <Canvas3D pos={[0, -3, 0]} scale={[6.5, 6.5, 6.5]} modelPath={'/robot1.glb'} classname={'robotloading'} />
              <center><h1>Generating Review...</h1></center>
            </div>
            :
            <div className='review-text-mainDiv'>
              <div className='robotImage-div'>
                <Canvas3D pos={[0, -3, 0]} scale={[6.7, 6.7, 6.7]} modelPath={'/robot1.glb'} classname={'robotImage'} />
                <h1>FeedBack</h1>
              </div>
              <div className="stats-container">
                <div className="stat-item">
                  <h3>Answered</h3>
                  <p>{answered}</p>
                </div>
                <div className="stat-item">
                  <h3>Skipped</h3>
                  <p>{skipped}</p>
                </div>
                <div className="stat-item">
                  <h3>Rating</h3>
                  <p>{rating}/10</p>
                </div>
              </div>
              <div className='review-text-wrapper'>
                <Markdown
                  className='review-text'
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={dark}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >{displayText}</Markdown>
              </div>
            </div>
        }
      </div>

      <div className='right-main-div'>
        <div className='right-content1-main'>
          <div className='right-content1-sub1'>
            <div className='right-content1-sub1-text'>
              <p>
                No Dream is too <br />BIG and <br /> No Dreamer is too small
              </p>
            </div>
            <div className='right-content1-sub1-model'>
              <Canvas3D pos={[0, 0, 0]} scale={[0.015, 0.015, 0.015]}
                modelPath={'/rubix_cube2.glb'} classname={'threeD_model'}
                preset={'apartment'} camControls={true} />
            </div>
          </div>
          <div className='right-content1-sub2'>
            <p>
              Hey there! Thanks for picking our Mock Interview System to help you get interview-ready.
              We're here to give you a real feel of what it's like to sit through interviews, minus the stress.
              Whether you're gearing up for your first job or just want to ace that next big opportunity, we've got you covered.
              Practice with us, get feedback, and walk into your interviews with confidence. Let's make sure you're ready to impress!
            </p>
          </div>

        </div>
        <div className='right-content2-main'>
          <p>
            Want to Test your skills again?
          </p>
          <button onClick={gotoHomePage}>Take Interview</button>
        </div>
      </div>
    </div>
  );
}

export default ReviewPage;