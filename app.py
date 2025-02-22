import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studymate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Folder for file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# -------------------------------
# Database Models
# -------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)

class FlashcardSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcards = db.relationship('Flashcard', backref='flashcard_set', lazy=True)
    file_path = db.Column(db.String(300), nullable=True)
    
    @property
    def filename(self):
        """Return just the filename portion of file_path (e.g. '003.pdf')."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return None

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String(300), nullable=False)
    flashcard_set_id = db.Column(db.Integer, db.ForeignKey('flashcard_set.id'), nullable=False)

class StudyGuide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    
    @property
    def filename(self):
        """Return just the filename portion of file_path (e.g. 'mydoc.pdf')."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return None

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# -------------------------------
# Decorators & Context Processor
# -------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view that page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    """Inject 'user' into all templates for easy reference."""
    if 'user_id' in session:
        return {'user': User.query.get(session['user_id'])}
    return {'user': None}

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if User.query.filter_by(username=username).first():
            flash('Username already exists! Please choose another.', 'error')
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# -------------------------------
# CREATE FLASHCARDS
# -------------------------------
@app.route('/create_flashcards', methods=['GET', 'POST'])
@login_required
def create_flashcards():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash("Please provide a title for your flashcard set.", "error")
            return redirect(url_for('create_flashcards'))

        flashcard_set = FlashcardSet(title=title, user_id=session['user_id'])
        
        # Optional file upload
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flashcard_set.file_path = file_path

        db.session.add(flashcard_set)
        db.session.commit()

        # Process question/answer fields
        questions = request.form.getlist('question')
        answers = request.form.getlist('answer')
        for q, a in zip(questions, answers):
            q, a = q.strip(), a.strip()
            if q and a:
                new_card = Flashcard(question=q, answer=a, flashcard_set_id=flashcard_set.id)
                db.session.add(new_card)
        db.session.commit()

        flash('Flashcard set created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_flashcards.html')

# -------------------------------
# CREATE STUDY GUIDE
# -------------------------------
@app.route('/create_study_guide', methods=['GET', 'POST'])
@login_required
def create_study_guide():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash("Please provide both a title and content for your study guide.", "error")
            return redirect(url_for('create_study_guide'))

        study_guide = StudyGuide(title=title, content=content, user_id=session['user_id'])

        # Optional file upload
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            study_guide.file_path = file_path

        db.session.add(study_guide)
        db.session.commit()
        flash('Study guide created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_study_guide.html')

# -------------------------------
# FEEDBACK
# -------------------------------
@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        rating_str = request.form.get('rating', '').strip()
        if not comment:
            flash("Please provide feedback text.", "error")
            return redirect(url_for('feedback'))

        rating = None
        if rating_str:
            try:
                rating = int(rating_str)
            except ValueError:
                flash("Rating must be an integer (e.g., 1-5).", "error")
                return redirect(url_for('feedback'))

        fb = Feedback(comment=comment, rating=rating, user_id=session['user_id'])
        db.session.add(fb)
        db.session.commit()
        flash('Feedback submitted! Thank you.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('feedback.html')

# -------------------------------
# DARK MODE
# -------------------------------
@app.route('/toggle_dark_mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    user = User.query.get(session['user_id'])
    user.dark_mode = not user.dark_mode
    db.session.commit()
    flash('Display settings updated!', 'success')
    return redirect(url_for('dashboard'))

# -------------------------------
# DOWNLOAD ROUTES
# -------------------------------
@app.route('/download_guide/<int:guide_id>')
@login_required
def download_guide(guide_id):
    guide = StudyGuide.query.get_or_404(guide_id)
    if guide.user_id != session['user_id']:
        flash("You do not have permission to download this file.", "error")
        return redirect(url_for('my_study_guides'))
    if not guide.file_path:
        flash("No file attached to this study guide.", "error")
        return redirect(url_for('my_study_guides'))
    
    filename = os.path.basename(guide.file_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_flashcard/<int:set_id>')
@login_required
def download_flashcard(set_id):
    fset = FlashcardSet.query.get_or_404(set_id)
    if fset.user_id != session['user_id']:
        flash("You do not have permission to download this file.", "error")
        return redirect(url_for('my_flashcards'))
    if not fset.file_path:
        flash("No file attached to this flashcard set.", "error")
        return redirect(url_for('my_flashcards'))
    
    filename = os.path.basename(fset.file_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# -------------------------------
# "My Flashcards" & "My Study Guides"
# -------------------------------
@app.route('/my_flashcards')
@login_required
def my_flashcards():
    user_id = session['user_id']
    flashcard_sets = FlashcardSet.query.filter_by(user_id=user_id).all()
    return render_template('my_flashcards.html', flashcard_sets=flashcard_sets)

@app.route('/my_study_guides')
@login_required
def my_study_guides():
    user_id = session['user_id']
    study_guides = StudyGuide.query.filter_by(user_id=user_id).all()
    return render_template('my_study_guides.html', study_guides=study_guides)

# -------------------------------
# Main Entry
# -------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
