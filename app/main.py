import stripe
from flask import Blueprint, redirect, render_template, request, flash, url_for, abort, jsonify
from app.models import User
#from app.forms import 
from app import db
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc

#stripe payment for subscribers
stripe_keys = {"secret_key": "sk_test_51HMfihKZXGIOAX0RFNz6yGAb9VXU9cRpv1bkIxjpRjLs8NZvXg14mAYRi3E5pbqryteqdPWuKNz2Z4DLzT1zBBLq004t4Ao7Ws", "publishable_key":"pk_test_51HMfihKZXGIOAX0RySSyQ9U4BduK4lgWYka31u02pvrSAqKk0OLtzgJ9CxjH2yQLTKHK1dZeUDaHbaFmotBJ1QZy00Vw3ZggI4",
}
stripe.api_key = stripe_keys["secret_key"]

main = Blueprint('main', __name__)


@main.route("/")
def home():
  return render_template("base.html")


@main.route("/payment")
def payment():
  return render_template("payment.html")

#stripe ajax call
@main.route("/config")
def get_publishable_key():
  stripe_config = {"publicKey": stripe_keys["publishable_key"]}
  return jsonify(stripe_config)

#checkout session
@main.route("/create-checkout-session")
def create_checkout_session():
  stripe.api_key = stripe_keys["secret_key"]

  try:
    checkout_session = stripe.checkout.Session.create(
      success_url=url_for('main.success', _external=True) +'?session_id={CHECKOUT_SESSION_ID}',
      cancel_url=url_for('main.home', _external=True),
      payment_method_types=["card"],
      mode="payment",
      line_items=[{"name": "premium plan", "quantity": 1,
                   "currency": "usd", "amount": "1000", }]
    )
    return jsonify({"sessionId": checkout_session["id"]})
  except Exception as e:
    return jsonify(error=str(e)), 403

@main.route("/success")
def success():
  return render_template("success.html")

@main.route("/cancelled")
def cancelled():
  return render_template("cancelled.html")
