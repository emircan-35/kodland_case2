from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    latest_score = db.Column(db.Integer)
    best_score = db.Column(db.Integer)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    opt1_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    opt2_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    opt3_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    opt4_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    true_option = db.Column(db.Integer, nullable=False)  
    
    option1 = db.relationship('Option', foreign_keys=[opt1_id])
    option2 = db.relationship('Option', foreign_keys=[opt2_id])
    option3 = db.relationship('Option', foreign_keys=[opt3_id])
    option4 = db.relationship('Option', foreign_keys=[opt4_id])

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    quiz = db.relationship('Quiz', backref=db.backref('quiz_questions', lazy=True))
    question = db.relationship('Question', backref=db.backref('quiz_questions', lazy=True))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
