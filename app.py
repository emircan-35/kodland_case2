from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Quiz, Question, Option, QuizQuestion
from sqlalchemy.exc import SQLAlchemyError

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

class QuizService:
    @staticmethod
    def get_first_quiz():
        return Quiz.query.first()

    @staticmethod
    def get_quiz_questions(quiz_id):
        return QuizQuestion.query.filter_by(quiz_id=quiz_id).all()

    @staticmethod
    def get_best_user():
        return User.query.order_by(User.best_score.desc()).first()

class UserService:
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(username):
        user = User(username=username, latest_score=0, best_score=0)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user_score(user, score):
        user.latest_score = score
        if score > user.best_score:
            user.best_score = score
        db.session.commit()

@app.route('/')
def index():
    quiz = QuizService.get_first_quiz()
    if not quiz:
        return "No quiz found in the database", 404

    quiz_questions = QuizService.get_quiz_questions(quiz.id)
    best_user = QuizService.get_best_user()
    best_score = best_user.best_score if best_user else 0

    return render_template('index.html', quiz_questions=quiz_questions, best_score=best_score)

@app.route('/result/<username>', methods=['GET'])
def result(username):
    user = UserService.get_user_by_username(username)
    if not user:
        return f"No user found with the username: {username}", 404

    best_user = QuizService.get_best_user()
    return render_template('result.html', user=user, best_user=best_user)

@app.route('/quiz/<username>', methods=['GET', 'POST'])
def quiz(username):
    user = UserService.get_user_by_username(username)
    if not user:
        return redirect(url_for('start_quiz'))

    quiz = QuizService.get_first_quiz()
    quiz_questions = QuizService.get_quiz_questions(quiz.id)
    best_user = QuizService.get_best_user()
    
    highest_score = best_user.best_score if best_user else 0
    highest_scorer = best_user.username if best_user else "No one"

    if request.method == 'POST':
        try:
            score = calculate_score(quiz_questions)
            UserService.update_user_score(user, score)
            return redirect(url_for('quiz', username=username))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            return "Error processing quiz submission", 500

    return render_template(
        'quiz.html',
        username=username,
        quiz_questions=quiz_questions,
        latest_score=user.latest_score,
        best_score=user.best_score,
        highest_score=highest_score,
        highest_scorer=highest_scorer
    )

def calculate_score(quiz_questions):
    score = 0
    for quiz_question in quiz_questions:
        answer = request.form.get(f'question_{quiz_question.question.id}')
        correct_answer_index = quiz_question.question.true_option
        if int(answer) == correct_answer_index:
            score += 1
    return 100 * (score/len(quiz_questions))

@app.route('/start', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'POST':
        username = request.form['username']
        user = UserService.get_user_by_username(username)
        if not user:
            try:
                user = UserService.create_user(username)
            except SQLAlchemyError:
                db.session.rollback()
                return "Error creating user", 500
        return redirect(url_for('quiz', username=username))
    
    return render_template('start.html')

if __name__ == '__main__':
    app.run(debug=False)