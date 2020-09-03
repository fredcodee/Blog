from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from flask_login import login_user, login_required, logout_user

forms = Blueprint('forms', __name__)


class LoginForm(FlaskForm):
  email = StringField('Email', validators=[InputRequired(), Email(message='Enter a valid email.')])
  password = PasswordField('password', validators=[InputRequired()])
  submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
  email = StringField('Email', validators=[Length(min=6), Email(
      message='Enter a valid email.'), InputRequired()])
  name = StringField('Full Name', validators=[InputRequired(), Length(min=4)])
  password = PasswordField('Password', validators=[
                           InputRequired(), Length(min=4, max=80)])
  submit = SubmitField('Register')


#login
@forms.route("/login", methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and check_password_hash(user.password, form.password.data):
      login_user(user)
      return redirect(url_for('main.home'))
    else:
      flash('email or password incorrect')
      return redirect(url_for('forms.login'))

  return render_template("login.html", form=form)

#signup
@forms.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
      hashed_password = generate_password_hash(
          form.password.data, method='sha256')
      u_name = form.name.data
      new_user = User(name=u_name.title(), email=form.email.data, password=hashed_password)
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('forms.login'))

    return render_template('signup.html', form=form)


@forms.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('main.index'))
