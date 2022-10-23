from sqlalchemy import ForeignKey
from flask_blog import db, app
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from itsdangerous import TimedJSONWebSignatureSerializer
import datetime

class User(UserMixin, db.Model): 
    __tablename__ = 'users'
    
    # creating columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)    
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    # creating relationships
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='comment_author')

    def get_reset_token(self, expires_sec=1800):
        s = TimedJSONWebSignatureSerializer(secret_key=app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = TimedJSONWebSignatureSerializer(secret_key=app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self) -> str:
        return f'User({self.username}, {self.email}, {self.image_file})'

class Post(db.Model):
    __tablename__ = 'user_posts'
    
    # since a post can only have one author, the author should have it's own unique ID
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime(20), nullable=False, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # creating relationships
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='parent_post')

    def __repr__(self) -> str:
        return f'Post({self.title}, {self.date_posted})'


class Comment(db.Model):
    __tablename__ = 'comments'
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    post_id = db.Column(db.Integer, ForeignKey('user_posts.id'))
    
    parent_post = relationship('Post', back_populates='comments')
    comment_author = relationship('User', back_populates='comments')

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000))

    def __repr__(self) -> str:
        return f'comment-{self.id}'

db.create_all()
    



