from flask_login import UserMixin
from datetime import datetime
from app import db


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  name = db.Column(db.String(80), nullable=False)
  password = db.Column(db.String(100))
  role = db.Column(db.String(50))


class Blogpost(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(50))
  subtitle = db.Column(db.String(100))
  author = db.Column(db.String(20))
  date_posted = db.Column(db.DateTime)
  content = db.Column(db.Text,  nullable=False)
  access = db.Column(db.Boolean,  nullable = False)
  imagelink = db.Column(db.String(100))
