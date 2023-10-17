from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db, ma, login_manager, init_db
from routes import routes as blueprint_routes
from models import User, BlogPost, Review

import os
import subprocess
import jwt
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='../client/build', template_folder='../client/build')

# Increase the Maximum Request Header Size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Set to 16 MB or adjust as needed

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Flask Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

init_db(app)

CORS(app)
Session(app)
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "OK"}), 200)

class Users(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return make_response(jsonify(users), 200)

class BlogPosts(Resource):
    def get(self):
        blogposts = [blogpost.to_dict() for blogpost in BlogPost.query.all()]
        return make_response(jsonify(blogposts), 200)

class Reviews(Resource):
    def get(self):
        reviews = [review.to_dict() for review in Review.query.all()]
        return make_response(jsonify(reviews), 200)

@app.route('/')
@app.route('/<int:id>')
def index(id=0):
    return render_template("index.html")

api.add_resource(HealthCheck, '/healthz')
api.add_resource(Users, '/users')
api.add_resource(BlogPosts, '/blogposts')
api.add_resource(Reviews, '/reviews')

@app.route('/serve/<path:path>')
def serve(path):
    if not path:
        path = 'index.html'
    return send_from_directory('client/build', path)

@app.route('/signup', methods=['POST'])
def signup():
    # Parse the JSON from the request body
    data = request.get_json()

    # Check if data is valid
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Bad Request: Missing username or password'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first() is not None:
        return jsonify({'message': 'Conflict: User already exists'}), 409

    # Create a new user
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])  # Set the hashed password

    # Add the new user to the session and commit it to the database
    db.session.add(new_user)
    db.session.commit()

    # Return a success message
    return jsonify({'message': 'User created successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))




