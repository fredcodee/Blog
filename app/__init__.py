from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_share import Share


#database
db = SQLAlchemy()
migrate = Migrate()
share = Share()

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'ASpire2begreat'
  app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://pfctfocopbwlzp:ef4b7eb3bff359c1d17ffa7f09fa0362443101bf34924671c411cb2ca95750b2@ec2-34-232-212-164.compute-1.amazonaws.com:5432/d38s5lm4gusm04"
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

  db.init_app(app)
  from app.models import User
  migrate.init_app(app, db)

  login_manager = LoginManager()
  login_manager.login_view = 'forms.login'
  login_manager.init_app(app)

  share.init_app(app)

  from app.models import User

  @login_manager.user_loader
  def load_user(user_id):
    return(User.query.get(int(user_id)))

  # blueprint for auth routes in our app
  from app.forms import forms as forms_blueprint
  app.register_blueprint(forms_blueprint)

  # blueprint for non-auth parts of app
  from app.main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  return app
