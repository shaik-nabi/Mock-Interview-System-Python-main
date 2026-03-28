from flask import Flask, jsonify, request, g
import google.generativeai as genai
from functions.question_generation import generate_questions
from functions.review_generation import gen_review
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os
from extensions import db, bcrypt, migrate
from models import User, InterviewSession, Question, Answer, InterviewFeedback

app = Flask(__name__)
CORS(app)

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate.init_app(app, db)

genai.configure(api_key=gemini_api_key) 
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

@app.before_request
def before_request():
    g.model = model

@app.route("/")
def home():
    return "Welcome to Mock-Interview-System/Server", 200
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": 404, "message": "Not Found"}), 404

# --- Authentication Routes ---

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    if not first_name or not last_name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Password validation
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    import re
    if not re.search(r"[A-Z]", password):
        return jsonify({'error': 'Password must contain at least one uppercase letter'}), 400
    if not re.search(r"[0-9]", password):
        return jsonify({'error': 'Password must contain at least one number'}), 400
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error': 'Password must contain at least one special character'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # In a real app, return a JWT token or set a session
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

# --- Interview Routes ---

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    data = request.get_json()
    user_id = data.get('user_id') # In real app, get from token/session
    job_role = data.get('job_role')
    experience_level = data.get('experience_level') or data.get('experience_lvl', 'fresher')

    if not user_id or not job_role or not experience_level:
        return jsonify({'error': 'Missing data'}), 400
    
    user = User.query.get(user_id)
    if not user:
         return jsonify({'error': 'User not found'}), 404

    session = InterviewSession(user_id=user_id, job_role=job_role, experience_level=experience_level)
    db.session.add(session)
    db.session.commit()

    return jsonify({'message': 'Interview started', 'session': session.to_dict()}), 201

@app.route('/api/get-questions', methods=['POST'])
def ask_questions():
    try:
        data = request.get_json()
        job_role = data['job_role']
        experience_lvl = data.get('experience_lvl') or data.get('experience_level', 'fresher')
        session_id = data.get('session_id') # Optional: if provided, save questions
        question_count = data.get('question_count', 10)

        try:
            question_count = int(question_count)
            if question_count <= 0:
                return jsonify({'errorMsg': 'question_count must be a positive integer'}), 400
        except (TypeError, ValueError):
            return jsonify({'errorMsg': 'question_count must be a positive integer'}), 400

        print(f"Generating questions for {job_role} ({experience_lvl})")
        response = generate_questions(job_role, experience_lvl, question_count=question_count)

        if not isinstance(response, list):
            return jsonify({'errorMsg': response}), 400
        
        # Save questions if session_id is provided
        saved_questions = []
        if session_id:
            session = InterviewSession.query.get(session_id)
            if session:
                for q_text in response:
                    q = Question(session_id=session.id, question_text=q_text)
                    db.session.add(q)
                    saved_questions.append(q)
                db.session.commit()

        # If we saved questions, return their IDs too, but existing frontend might expect just strings.
        # Keeping response format backward compatible:
        return jsonify({'job_role' : job_role, 'exp_level' : experience_lvl, 'qtns': response}), 200
    except Exception as e:
        print(f"Error occurred while generating question: {e}")
        return jsonify({'errorMsg': "Something went wrong"}), 400

@app.route('/api/save-answer', methods=['POST'])
def save_answer():
    data = request.get_json()
    session_id = data.get('session_id')
    question_text = data.get('question_text') # If we don't have ID yet
    answer_text = data.get('answer_text')

    # This is tricky if we don't return question IDs to frontend. 
    # For now, let's assume we might need to look up the question or just create it if it wasn't pre-generated/saved.
    # A better flow: Frontend sends question_text, we find or create it.
    
    if not session_id or not question_text or not answer_text:
        return jsonify({'error': 'Missing data'}), 400

    # Find question in this session
    question = Question.query.filter_by(session_id=session_id, question_text=question_text).first()
    if not question:
        # Create it if not exists (e.g. dynamic flow)
        question = Question(session_id=session_id, question_text=question_text)
        db.session.add(question)
        db.session.commit()
    
    answer = Answer(question_id=question.id, answer_text=answer_text)
    db.session.add(answer)
    db.session.commit()

    return jsonify({'message': 'Answer saved', 'answer': answer.to_dict()}), 201

@app.route('/api/get-review', methods=['POST'])
def get_review():
    try:
        data = request.get_json()
        job_role = data['job_role']
        qns = data['qns']
        ans = data['ans']
        suspiciousCount = data.get('suspiciousCount')
        session_id = data.get('session_id')

        # get review
        review_data = gen_review(job_role, qns, ans, suspiciousCount)
        
        # Save feedback/score if possible. 
        # Since 'review' structure depends on gen_review, we might need to parse it or just save the whole text.
        # Assuming review is text or JSON. For now, we won't deep-parse to update 'Answer' table feedback unless requested.
        
        if session_id:
            from datetime import datetime
            session = InterviewSession.query.get(session_id)
            if session:
                session.completed_at = datetime.utcnow()
                
                # Check if feedback already exists
                if not InterviewFeedback.query.filter_by(session_id=session_id).first():
                    feedback = InterviewFeedback(
                        session_id=session_id,
                        questions_answered=review_data.get('answered', 0),
                        questions_skipped=review_data.get('skipped', 0),
                        rating=review_data.get('rating', 0)
                    )
                    db.session.add(feedback)

                db.session.commit()

        return jsonify(review_data)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error occurred while generating review: {e}")
        
        # Log to file
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("error_log.txt", "a") as f:
            f.write(f"[{timestamp}] Error generating review:\n{error_details}\n{'-'*50}\n")
            
        return jsonify({'errorMsg': "Something went wrong. Check server/error_log.txt for details."}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    sessions = InterviewSession.query.filter_by(user_id=user_id).order_by(InterviewSession.started_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions]), 200

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400

    try:
        # Get all sessions for user
        sessions = InterviewSession.query.filter_by(user_id=user_id).all()
        total_interviews = len(sessions)
        
        # Calculate stats
        total_rating = 0
        total_answered = 0
        total_skipped = 0
        rated_sessions_count = 0
        
        recent_performance = []

        for session in sessions:
            feedback = InterviewFeedback.query.filter_by(session_id=session.id).first()
            if feedback:
                total_rating += feedback.rating
                total_answered += feedback.questions_answered
                total_skipped += feedback.questions_skipped
                rated_sessions_count += 1
                
                # Add to recent performance for chart
                recent_performance.append({
                    'date': session.completed_at.strftime('%Y-%m-%d') if session.completed_at else session.started_at.strftime('%Y-%m-%d'),
                    'rating': feedback.rating,
                    'role': session.job_role
                })
        
        avg_rating = round(total_rating / rated_sessions_count, 1) if rated_sessions_count > 0 else 0
        
        total_questions = total_answered + total_skipped
        response_rate = round((total_answered / total_questions) * 100, 1) if total_questions > 0 else 0

        # Sort recent performance by date (if not already) - limiting to last 10
        recent_performance.sort(key=lambda x: x['date'])
        recent_performance = recent_performance[-10:]

        return jsonify({
            'totalInterviews': total_interviews,
            'averageRating': avg_rating,
            'responseRate': response_rate,
            'recentPerformance': recent_performance
        }), 200

    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({'error': 'Failed to fetch dashboard stats'}), 500

if __name__ == '__main__':
    app.run(debug=True)
