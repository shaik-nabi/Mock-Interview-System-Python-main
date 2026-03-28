from extensions import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(20), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('sessions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_role": self.job_role,
            "experience_level": self.experience_level,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    
    session = db.relationship('InterviewSession', backref=db.backref('questions', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_text": self.question_text
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=True) 
    feedback = db.Column(db.Text, nullable=True)
    
    question = db.relationship('Question', backref=db.backref('answer', uselist=False, lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "answer_text": self.answer_text,
            "score": self.score,
            "feedback": self.feedback
        }
class InterviewFeedback(db.Model):
    __tablename__ = 'interview_feedback'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    questions_answered = db.Column(db.Integer, nullable=False)
    questions_skipped = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship('InterviewSession', backref=db.backref('feedback', uselist=False, lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "questions_answered": self.questions_answered,
            "questions_skipped": self.questions_skipped,
            "rating": self.rating,
            "created_at": self.created_at.isoformat()
        }
