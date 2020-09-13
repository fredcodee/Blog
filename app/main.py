import stripe
from flask import Blueprint, redirect, render_template, request, flash, url_for, abort, jsonify
from app.models import User, Blogpost
#from app.forms import 
from app import db
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc

#stripe payment for subscribers
stripe_keys = {"secret_key": "sk_test_51HMfihKZXGIOAX0RFNz6yGAb9VXU9cRpv1bkIxjpRjLs8NZvXg14mAYRi3E5pbqryteqdPWuKNz2Z4DLzT1zBBLq004t4Ao7Ws", "publishable_key":"pk_test_51HMfihKZXGIOAX0RySSyQ9U4BduK4lgWYka31u02pvrSAqKk0OLtzgJ9CxjH2yQLTKHK1dZeUDaHbaFmotBJ1QZy00Vw3ZggI4",
"endpoint_secret": "whsec_AlCZzWqV9PIPWpwnpFYT7snN5EmrSHfJ"}
stripe.api_key = stripe_keys["secret_key"]

main = Blueprint('main', __name__)


@main.route("/")
def home():
  #get articles
  articles = Blogpost.query.all()
  return render_template("base.html", articles = articles)


@main.route("/payment")
def payment():
  return render_template("payment.html")

#stripe ajax call
@main.route("/config")
def get_publishable_key():
  stripe_config = {"publicKey": stripe_keys["publishable_key"]}
  return jsonify(stripe_config)

#checkout session for subscribers
@main.route("/create-checkout-session/<plan>", methods=["GET", "POST"])
def create_checkout_session(plan):
  stripe.api_key = stripe_keys["secret_key"]

  try:
    #product rprice subcription id from stripe
    if plan and plan == 'yearly':
      plan = 'price_1HNjoDKZXGIOAX0RoZ2yYg7d'
    elif plan and plan == 'monthly':
      plan = 'price_1HO7guKZXGIOAX0RmSP5D0KE'

    checkout_session = stripe.checkout.Session.create(
      success_url=url_for('main.success', _external=True) +'?session_id={CHECKOUT_SESSION_ID}',
      cancel_url=url_for('main.home', _external=True),
      payment_method_types=["card"],
      mode='subscription',
      line_items=[{
          'price': plan,
          'quantity': 1,
      }]
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


#stripe webhook
@main.route("/webhook", methods=["POST"])
def stripe_webhook():
  payload = request.get_data(as_text=True)
  sig_header = request.headers.get("Stripe-Signature")

  try:
    event = stripe.Webhook.construct_event(payload, sig_header, stripe_keys["endpoint_secret"])

  except ValueError as e:
    # Invalid payload
    return "Invalid payload", 400
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return "Invalid signature", 400

    # Handle the checkout.session.completed event
  if event["type"] == "checkout.session.completed":
    print("Payment was successful.")
    #run some custom code here

  return "Success", 200



#addnew article (Author&editor)
@main.route("/new", methods=["POST","GET"])
@login_required
def new():
  if current_user.role != "Subscriber":
    if request.method == 'POST':
      title = request.form.get("title")
      content = request.form.get("content")
      imagelink = request.form.get("coverimage")
      subtitle =  content[:200]
      #post access
      access = request.form.get("access")
      if access == "T":
        access = True
      elif access == "F":
        access = False 

      #save to database
      new_post = Blogpost(title=title, subtitle =subtitle,author=current_user.name,content = content, access = access,imagelink = imagelink)

      db.session.add(new_post)
      db.session.commit()

      flash("New Post added")
      return redirect(url_for("main.home"))

    else:
      return render_template('add.html')
  else:
    abort(404)

#search articles
#bookmarked articles
#likes
#comments
#social media share
#notificaation
#view profile and payment detials
#cancel/change payments
#about me
#admin page
#connect stripehook

