# from faker import Faker
# from app import db, app  # Adjust the import here to import the app instance
# from models import User, BlogPost, Review  # Adjust as per your models
# import random

# fake = Faker()

# def seed_users(number_of_users):
#     for _ in range(number_of_users):
#         user = User(username=fake.user_name(), password='password')
#         db.session.add(user)
#     db.session.commit()

# def seed_blog_posts(number_of_posts):
#     users = User.query.all()
#     for _ in range(number_of_posts):
#         post = BlogPost(
#             title=fake.sentence(),
#             content=fake.text(),
#             user_id=random.choice(users).id
#         )
#         db.session.add(post)
#     db.session.commit()

# def seed_reviews(number_of_reviews):
#     posts = BlogPost.query.all()
#     users = User.query.all()
#     for _ in range(number_of_reviews):
#         review = Review(
#             content=fake.text(),
#             user_id=random.choice(users).id,
#             blogpost_id=random.choice(posts).id
#         )
#         db.session.add(review)
#     db.session.commit()

# if __name__ == "__main__":
#     with app.app_context():  # Use app instance to push the application context
#         seed_users(10)
#         seed_blog_posts(30)
#         seed_reviews(100)

# seed.py

from app import app, db  # Replace 'your_application' with the actual name of your application package
from models import User, BlogPost, Review  # Replace 'your_models_file' with the actual name of your models file

def seed_database():
    with app.app_context():
        # Clean existing data
        db.session.query(Review).delete()
        db.session.query(BlogPost).delete()
        db.session.query(User).delete()

        # Create new users
        alice = User(username='Alice', password='alicepassword')
        bob = User(username='Bob', password='bobpassword')

        # Create new blog posts
        post_by_alice = BlogPost(title='Alice\'s First Post', content='This is the content of Alice\'s first post.', author=alice)
        post_by_bob = BlogPost(title='Bob\'s First Post', content='This is the content of Bob\'s first post.', author=bob)

        # Create reviews
        review_for_alice = Review(content='Great post by Alice!', reviewer=bob, blogpost=post_by_alice)
        review_for_bob = Review(content='Awesome work, Bob!', reviewer=alice, blogpost=post_by_bob)

        # Add to session
        db.session.add(alice)
        db.session.add(bob)
        db.session.add(post_by_alice)
        db.session.add(post_by_bob)
        db.session.add(review_for_alice)
        db.session.add(review_for_bob)

        # Commit to database
        db.session.commit()

        print('Database seeded.')

if __name__ == "__main__":
    seed_database()
