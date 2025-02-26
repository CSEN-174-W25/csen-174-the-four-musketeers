from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # In production, store this securely!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studymate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================
#         Models
# ============================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    flashcards = db.relationship('Flashcard', backref='owner', lazy=True)
    flashcard_sets = db.relationship('FlashcardSet', backref='owner', lazy=True)
    study_guides = db.relationship('StudyGuide', backref='owner', lazy=True)

class Flashcard(db.Model):
    # Each flashcard gets a sequential integer ID.
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FlashcardSet(db.Model):
    # Each flashcard set gets its own unique UUID.
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class StudyGuide(db.Model):
    # Each study guide gets its own unique UUID.
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ============================
#    Authentication Utils
# ============================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")  # Retrieve token from cookies

        if not token:
            return redirect(url_for('login'))  # Redirect to login if no token

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise ValueError("User not found")
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))  # Redirect on expired token
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))  # Redirect on invalid token
        except Exception:
            return redirect(url_for('login'))

        return f(current_user, *args, **kwargs)

    return decorated


# ============================
#         Routes
# ============================

@app.route('/')
def index():
    token = request.cookies.get("token")
    
    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if current_user:
                return redirect(url_for('dashboard'))
        except jwt.ExpiredSignatureError:
            pass  # Expired token, stay on index page
        except jwt.InvalidTokenError:
            pass  # Invalid token, stay on index page
        except Exception:
            pass  # General failure, stay on index page

    return render_template("index.html")


# ----- Signup Endpoint (GET and POST) -----
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        token = request.cookies.get("token")
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
                if current_user:
                    return redirect(url_for('dashboard'))
            except:
                pass
        # Render the signup page (create a signup.html template or modify as needed)
        return render_template('signup.html')
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing fields'}), 400
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': 'User could not be created. Username or email might already exist.'}), 400
    return jsonify({'message': 'User created successfully!'}), 201

# ----- Login Endpoint (GET and POST) -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        token = request.cookies.get("token")
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.get(data['user_id'])
                if current_user:
                    return redirect(url_for('dashboard'))
            except:
                pass

        return render_template('login.html')

    data = request.get_json()
    
    if not data or not all(k in data for k in ('login', 'password')):
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter((User.username == data['login']) | (User.email == data['login'])).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    response = jsonify({'token': token})
    response.set_cookie("token", token, httponly=True)  # Securely set token in cookie
    return response

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    response = jsonify({'message': 'Logged out successfully!'})
    response.delete_cookie("token")
    return response, 200


@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    return render_template('dashboard.html', user=current_user)

@app.route('/get-user-info', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({'username': current_user.username})

# ============================
#     Flashcard Endpoints
# ============================
@app.route('/flashcards', methods=['GET'])
@token_required
def get_flashcards(current_user):
    flashcard_sets = FlashcardSet.query.filter_by(user_id=current_user.id).all()
    flashcards = Flashcard.query.filter_by(user_id=current_user.id).all()
    
    return render_template('flashcards.html', flashcard_sets=flashcard_sets, flashcards=flashcards, user=current_user)


@app.route('/flashcards', methods=['POST'])
@token_required
def create_flashcard(current_user):
    data = request.get_json()
    if not data or not all(k in data for k in ('question', 'answer')):
        return jsonify({'message': 'Missing question or answer'}), 400
    new_card = Flashcard(question=data['question'], answer=data['answer'], owner=current_user)
    db.session.add(new_card)
    db.session.commit()
    return jsonify({'message': 'Flashcard created!', 'flashcard_id': new_card.id}), 201

@app.route('/flashcards/<int:flashcard_id>', methods=['GET'])
@token_required
def get_flashcard(current_user, flashcard_id):
    card = Flashcard.query.filter_by(id=flashcard_id, user_id=current_user.id).first()
    if not card:
        return jsonify({'message': 'Flashcard not found'}), 404
    card_data = {
        'id': card.id,
        'question': card.question,
        'answer': card.answer,
        'created_at': card.created_at
    }
    return jsonify({'flashcard': card_data})

@app.route('/flashcards/<int:flashcard_id>', methods=['PUT'])
@token_required
def update_flashcard(current_user, flashcard_id):
    card = Flashcard.query.filter_by(id=flashcard_id, user_id=current_user.id).first()
    if not card:
        return jsonify({'message': 'Flashcard not found'}), 404
    data = request.get_json()
    if 'question' in data:
        card.question = data['question']
    if 'answer' in data:
        card.answer = data['answer']
    db.session.commit()
    return jsonify({'message': 'Flashcard updated!'})

@app.route('/flashcards/<int:flashcard_id>', methods=['DELETE'])
@token_required
def delete_flashcard(current_user, flashcard_id):
    card = Flashcard.query.filter_by(id=flashcard_id, user_id=current_user.id).first()
    if not card:
        return jsonify({'message': 'Flashcard not found'}), 404
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Flashcard deleted!'})

# ============================
#   Flashcard Set Endpoints
# ============================
@app.route('/flashcard-sets', methods=['GET'])
@token_required
def get_flashcard_sets(current_user):
    sets = FlashcardSet.query.filter_by(user_id=current_user.id).all()
    output = []
    for s in sets:
        set_data = {
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'created_at': s.created_at
        }
        output.append(set_data)
    return jsonify({'flashcard_sets': output})

@app.route('/flashcard-sets', methods=['POST'])
@token_required
def create_flashcard_set(current_user):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'message': 'Missing name field'}), 400
    new_set = FlashcardSet(name=data['name'], description=data.get('description', ''), owner=current_user)
    db.session.add(new_set)
    db.session.commit()
    return jsonify({'message': 'Flashcard set created!', 'set_id': new_set.id}), 201

@app.route('/flashcard-sets/<string:set_id>', methods=['GET'])
@token_required
def get_flashcard_set(current_user, set_id):
    s = FlashcardSet.query.filter_by(id=set_id, user_id=current_user.id).first()
    if not s:
        return jsonify({'message': 'Flashcard set not found'}), 404
    set_data = {
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'created_at': s.created_at
    }
    return jsonify({'flashcard_set': set_data})

@app.route('/flashcard-sets/<string:set_id>', methods=['PUT'])
@token_required
def update_flashcard_set(current_user, set_id):
    s = FlashcardSet.query.filter_by(id=set_id, user_id=current_user.id).first()
    if not s:
        return jsonify({'message': 'Flashcard set not found'}), 404
    data = request.get_json()
    if 'name' in data:
        s.name = data['name']
    if 'description' in data:
        s.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Flashcard set updated!'})

@app.route('/flashcard-sets/<string:set_id>', methods=['DELETE'])
@token_required
def delete_flashcard_set(current_user, set_id):
    s = FlashcardSet.query.filter_by(id=set_id, user_id=current_user.id).first()
    if not s:
        return jsonify({'message': 'Flashcard set not found'}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Flashcard set deleted!'})

# ============================
#    Study Guide Endpoints
# ============================
@app.route('/study-guides', methods=['GET'])
@token_required
def get_study_guides(current_user):
    guides = StudyGuide.query.filter_by(user_id=current_user.id).all()
    output = []
    for guide in guides:
        guide_data = {
            'id': guide.id,
            'title': guide.title,
            'content': guide.content,
            'created_at': guide.created_at
        }
        output.append(guide_data)
    return jsonify({'study_guides': output})

@app.route('/study-guides', methods=['POST'])
@token_required
def create_study_guide(current_user):
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'content')):
        return jsonify({'message': 'Missing title or content'}), 400
    new_guide = StudyGuide(title=data['title'], content=data['content'], owner=current_user)
    db.session.add(new_guide)
    db.session.commit()
    return jsonify({'message': 'Study guide created!', 'guide_id': new_guide.id}), 201

@app.route('/study-guides/<string:guide_id>', methods=['GET'])
@token_required
def get_study_guide(current_user, guide_id):
    guide = StudyGuide.query.filter_by(id=guide_id, user_id=current_user.id).first()
    if not guide:
        return jsonify({'message': 'Study guide not found'}), 404
    guide_data = {
        'id': guide.id,
        'title': guide.title,
        'content': guide.content,
        'created_at': guide.created_at
    }
    return jsonify({'study_guide': guide_data})

@app.route('/study-guides/<string:guide_id>', methods=['PUT'])
@token_required
def update_study_guide(current_user, guide_id):
    guide = StudyGuide.query.filter_by(id=guide_id, user_id=current_user.id).first()
    if not guide:
        return jsonify({'message': 'Study guide not found'}), 404
    data = request.get_json()
    if 'title' in data:
        guide.title = data['title']
    if 'content' in data:
        guide.content = data['content']
    db.session.commit()
    return jsonify({'message': 'Study guide updated!'})

@app.route('/study-guides/<string:guide_id>', methods=['DELETE'])
@token_required
def delete_study_guide(current_user, guide_id):
    guide = StudyGuide.query.filter_by(id=guide_id, user_id=current_user.id).first()
    if not guide:
        return jsonify({'message': 'Study guide not found'}), 404
    db.session.delete(guide)
    db.session.commit()
    return jsonify({'message': 'Study guide deleted!'})

# ============================
#         Main
# ============================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=False)
