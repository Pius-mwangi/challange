# from flask_login import UserMixin
# from extensions import db 

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)
#     blogposts = db.relationship('BlogPost', backref='user', lazy=True)
#     reviews = db.relationship('Review', backref='user', lazy=True)
    
#     def __repr__(self):
#         return f'<User {self.username}>'

# class BlogPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.String(1000), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     reviews = db.relationship('Review', backref='blogpost', lazy=True)  # Changed backref to 'blogpost' to match the class name
    
#     def __repr__(self):
#         return f'<BlogPost {self.title}>'
    
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "title": self.title,
#             "content": self.content
#         }


# class Review(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(500), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     blogpost_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)  # Fixed the ForeignKey reference to 'blog_post.id' to match the table name
    
#     def __repr__(self):
#         return f'<Review {self.id}>'
    
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "content": self.content,
#             "user_id": self.user_id,
#             "blogpost_id": self.blogpost_id
#         }
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    blogposts = db.relationship('BlogPost', backref='author', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
            # password is intentionally excluded to prevent it from being exposed
        }

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviews = db.relationship('Review', backref='blogpost', lazy=True)

    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id
        }

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blogpost_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)

    def __repr__(self):
        return f'<Review {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "blogpost_id": self.blogpost_id
        }
