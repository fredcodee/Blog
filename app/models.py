from flask_login import UserMixin
from datetime import datetime
from app import db


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  name = db.Column(db.String(80), nullable=False)
  password = db.Column(db.String(100))
  role = db.Column(db.String(50))
  blogpost_comment = db.relationship(
      'Comment', backref='user_comment', lazy='dynamic')
  blogpost_likes = db.relationship(
      'Likes', backref='user_likes', lazy='dynamic')
  blogpost_bookmark = db.relationship(
      'Bookmark', backref='user_bookmark', lazy='dynamic')


class Blogpost(db.Model):
  __tablename__ = 'blogpost'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  subtitle = db.Column(db.String(250))
  author = db.Column(db.String(20))
  date = db.Column(db.DateTime, default=datetime.now)
  content = db.Column(db.Text,  nullable=False)
  access = db.Column(db.Boolean,  nullable = False)
  imagelink = db.Column(db.String(500))
  comments = db.relationship(
      'Comment', backref='blogpost_comments', cascade="all,delete", lazy='dynamic')
  likes = db.relationship(
      'Likes', backref='blogpost_likes', cascade="all,delete", lazy='dynamic')
  bookmarks = db.relationship('Bookmark', backref = 'blogpost_bookmarks',cascade="all,delete", lazy = 'dynamic')


class Likes(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  blogpost_id = db.Column(db.Integer, db.ForeignKey('blogpost.id'))


class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  details = db.Column(db.String(400))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  blogpost_id = db.Column(db.Integer, db.ForeignKey('blogpost.id'))
  date = db.Column(db.DateTime, default=datetime.now)

class Bookmark(db.Model):
  id=db.Column(db.Integer,primary_key =True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  blogpost_id=db.Column(db.Integer,db.ForeignKey('blogpost.id'))
