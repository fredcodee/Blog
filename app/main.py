from flask import Blueprint, redirect, render_template, request, flash, url_for, abort
from app.models import User
#from app.forms import 
from app import db
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc

main = Blueprint('main', __name__)


@main.route("/")
def home():
  return render_template("base.html")