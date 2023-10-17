from flask import Blueprint, request, jsonify, make_response, redirect, url_for, render_template
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators
from models import User, BlogPost, Review, db
from extensions import ma, login_manager
import jwt
from datetime import datetime, timedelta

routes = Blueprint('routes', __name__)
CORS(routes, resources={r"*": {"origins": "http://localhost:3000"}})

SECRET_KEY = 'your_secret_key'  # Store this securely, not in the code.

def generate_token_for_user(user):
    """ Generate a JWT token for the user """
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    token = jwt.encode({
        'user_id': user.id,
        'exp': expiration
    }, SECRET_KEY, algorithm='HS256')
    return token

DEFAULT_USER_ID = 0

# 3. Set Flask-Login configurations
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = "routes.login"


# FlaskForm classes
class UserForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class BlogPostForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100), validators.DataRequired()])
    content = StringField('Content', [validators.DataRequired()])

class ReviewForm(FlaskForm):
    content = StringField('Content', [validators.DataRequired()])
    blogpost_id = StringField('BlogPost ID', [validators.DataRequired()])

# Marshmallow Schemas (adjusted)
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username")

class BlogPostSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "content", "user_id")

class ReviewSchema(ma.Schema):
    class Meta:
        fields = ("id", "content", "user_id", "blogpost_id")


@routes.after_request
def apply_caching(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if 'Set-Cookie' in response.headers:
        
        response.headers["Content-Type"] = "application/json"

    return response
    


@routes.route('/', methods=['GET'])
def home():
    return "Welcome to the Blog Management System"

@routes.route('/', defaults={'path': ''})
@routes.route('/<path:path>')
def catch_all(path):
    return serve(path)



@routes.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    data = request.form if request.form else request.get_json()

 
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': f'Missing value. Username: {username}, Password: {password}'}), 400
    if len(username) < 4 or len(username) > 25:
        return jsonify({'message': f'Invalid username length: {len(username)} for username: {username}'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists!'}), 400
    new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully! Please proceed to login.'}), 201


@routes.route('/login', methods=['OPTIONS'])
def login_options():
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST,OPTIONS'
    return response


@routes.route('/login', methods=['POST'])
def login():
    # data = request.get_json() or {}
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'status': 'error', 'message': 'Invalid Username or Password!'}), 401

   
    token = generate_token_for_user(user)

    return jsonify({'status': 'success', 'message': 'Logged in successfully!', 'token': token}), 200

@routes.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user_blogposts = BlogPost.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', username=current_user.username, blogposts=user_blogposts)

@routes.route('/logout', methods=['POST', 'OPTIONS'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'}), 200


@routes.route('/logout', methods=['OPTIONS'])
def logout_options():
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST,OPTIONS'
    return response

# BlogPost Routes
@routes.route('/blogposts', methods=['GET'])
def get_blogposts():
    blogposts = BlogPost.query.all()
    blogposts_data = []

    for post in blogposts:
        post_data = post.to_dict() 
        post_data['reviews'] = [review.to_dict() for review in post.reviews]
        blogposts_data.append(post_data)
        
    return jsonify(blogposts_data), 200

@routes.route('/blogposts', methods=['POST'])
# @login_required
def create_blogpost():
    data = request.form
    print("Received data:", data)
    title = data.get('title')
    content = data.get('content')
    image = request.files.get('image')  

    if not title or not content:
        return jsonify({'message': 'Title and content are required!'}), 400

    default_user_id = 1  #

    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = default_user_id

    new_blogpost = BlogPost(title=title, content=content, user_id=user_id)
    
    db.session.add(new_blogpost)
    db.session.commit()

    blogpost_data = BlogPostSchema().dump(new_blogpost)
    
    return jsonify({'message': 'BlogPost created successfully!', 'blogPost': blogpost_data, 'success': True}), 201


@routes.route('/blogposts/<int:blogpost_id>', methods=['GET'])
def get_single_blogpost(blogpost_id):
    blogpost = BlogPost.query.get(blogpost_id)
    if blogpost:
        return BlogPostSchema().jsonify(blogpost), 200
    else:
        return jsonify({"message": "BlogPost not found!"}), 404

@routes.route('/blogposts/<int:blogpost_id>', methods=['PATCH'])
# @login_required
def modify_blogpost(blogpost_id):
    form = BlogPostForm()
    if form.validate_on_submit():
        blogpost = BlogPost.query.get(blogpost_id)

        if not blogpost:
            return jsonify({'message': 'BlogPost not found!'}), 404
        
        blogpost.title = form.title.data
        blogpost.content = form.content.data
        db.session.commit()

        return jsonify({'message': 'BlogPost updated successfully!'}), 200

    return jsonify({'message': 'Invalid Input!'}), 400

@routes.route('/blogposts/<int:blogpost_id>', methods=['DELETE'])
# @login_required
def delete_blogpost(blogpost_id):
    blogpost = BlogPost.query.get(blogpost_id)

    if not blogpost:
        return jsonify({'message': 'BlogPost not found!'}), 404
    
    db.session.delete(blogpost)
    db.session.commit()
    return jsonify({'message': 'BlogPost deleted successfully!'}), 200

# Review Routes

@routes.route('/reviews/<int:review_id>', methods=['PATCH'])
# @login_required
def modify_review(review_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review.query.get(review_id)

        if not review:
            return jsonify({'message': 'Review not found!'}), 404
        
        review.content = form.content.data
        db.session.commit()

        return jsonify({'message': 'Review updated successfully!'}), 200

    return jsonify({'message': 'Invalid Input!'}), 400

@routes.route('/reviews/<int:review_id>', methods=['DELETE'])
# @login_required
def delete_review(review_id):
    review = Review.query.get(review_id)

    if not review:
        return jsonify({'message': 'Review not found!'}), 404
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully!'}), 200


# Get all reviews for a specific blogpost
@routes.route('/blogposts/<int:blogpost_id>/reviews', methods=['GET'])
def get_reviews_for_blogpost(blogpost_id):
    blogpost = BlogPost.query.get(blogpost_id)
    if not blogpost:
        return jsonify({"message": "BlogPost not found!"}), 404

    reviews = blogpost.reviews  
    reviews_data = [ReviewSchema().dump(review) for review in reviews]
    return jsonify(reviews_data), 200


# Create a review for a specific blogpost
@routes.route('/blogposts/<int:blogpost_id>/reviews', methods=['POST'])
def add_review_to_blogpost(blogpost_id):
    blogpost = BlogPost.query.get(blogpost_id)
    if not blogpost:
        return jsonify({"message": "BlogPost not found!"}), 404

    data = request.json
    review_text = data.get('content')

    # review_text = data.get('text')
    if not review_text:
        return jsonify({"message": "Review text is required!"}), 400

    # Use current user's ID or fallback to the default user ID
    user_id = getattr(current_user, 'id', DEFAULT_USER_ID)

    new_review = Review(content=review_text, user_id=int(user_id), blogpost_id=int(blogpost_id))
# new_review = Review(content=review_text, user_id=user_id, blogpost_id=blogpost_id)
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "Review added successfully!", "review": ReviewSchema().dump(new_review)}), 201





@routes.route('/<path:actual_path>', methods=['OPTIONS'])
def catch_all_options(actual_path):
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,PATCH'
    return response
