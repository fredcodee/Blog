import stripe
from flask import Blueprint, redirect, render_template, request, flash, url_for, abort, jsonify
from app.models import User, Blogpost, Likes,Comment, Bookmark
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

#blogpost page
@main.route("/blog/<idd>")
def blog(idd):
  get_blog = Blogpost.query.get(int(idd))
  likes = Likes.query.filter(Likes.blogpost_likes.has(id=int(idd))).all()
  comments = Comment.query.filter(Comment.blogpost_comments.has(id=int(idd))).all()
  bookmarks = Bookmark.query.filter(Bookmark.blogpost_bookmarks.has(id=int(idd))).all()

  context = {
    "blog" : get_blog, 
    "discussion" : comments, 
    "likes" : len(likes), 
    "bookmarks" : len(bookmarks)
  }

  return render_template("article.html", **context)

#likes
@main.route("/likes/<idd>")
@login_required
def likes(idd):
  #check if user has like before and unlike
  check_user = Likes.query.filter(Likes.blogpost_likes.has(id=int(idd)))
  for user in check_user:
    if user.user_likes.name == current_user.name:
      db.session.delete(user)
      db.session.commit()
      return redirect(url_for("main.blog", idd = idd))
   
  get_blog = Blogpost.query.get(int(idd))
  new_like = Likes(user_likes=current_user, blogpost_likes = get_blog)

  db.session.add(new_like)
  db.session.commit()
  flash("post liked!")
  return redirect(url_for("main.blog", idd=idd))

#comments
@main.route("/comments/<idd>", methods=["POST"])
@login_required
def comments(idd):
  get_blog = Blogpost.query.get(int(idd))
  details = request.form.get("comment")
  new_comment = Comment(details=details,user_comment=current_user, blogpost_comments = get_blog )
  db.session.add(new_comment)
  db.session.commit()

  flash("comment Added")
  return redirect(url_for("main.blog", idd = idd))

#delete comment
@main.route("/delete/comment/<idd>")
@login_required
def delete_comment(idd):
  get_comment = Comment.query.get(int(idd))
  db.session.delete(get_comment)
  db.session.commit()

  flash("comment deleted")
  return redirect(url_for("main.blog", idd=idd))

#bookmark article
@main.route("/bookmark/<idd>")
@login_required
def bookmark(idd):
  #check if user has bookmarked before and unbookmark
  check_user = Bookmark.query.filter(Bookmark.blogpost_bookmarks.has(id=int(idd)))
  for user in check_user:
    if user.user_bookmark.name == current_user.name:
      db.session.delete(user)
      db.session.commit()
      flash("Removed from bookmarks")
      return redirect(url_for("main.blog", idd=idd))

  get_blog = Blogpost.query.get(int(idd))
  new_bookmark = Bookmark(user_bookmark=current_user, blogpost_bookmarks=get_blog)

  db.session.add(new_bookmark)
  db.session.commit()
  flash("Bookmarked!")
  return redirect(url_for("main.blog", idd=idd))

#bookmarked articles page
@main.route("/bookmarks")
@login_required
def bookmarks():
  get_user_bookmarks = Bookmark.query.filter(
      Bookmark.user_bookmark.has(id=current_user.id)).order_by(desc(Bookmark.id)).all()

  return render_template("bookmarks.html", bookmarks = get_user_bookmarks)


#users subcription id
def get_subscription_id(email):
  #get custormer subcription id stripe
  get_customer = stripe.Customer.list(email="test@payment.com")
  get_customer_id = get_customer["data"][0]["id"]
  customer_sub = stripe.Subscription.list(customer=get_customer_id)
  subcription_id = customer_sub["data"][0]["id"]
  return subcription_id

#view profile and payment detials
#user profile
@main.route("/<user>")
@login_required
def profile(user):
  if current_user.name == user:
    get_user = User.query.filter_by(name=user).first()
    #get all likes by user
    get_likes = Likes.query.filter(Likes.user_likes.has(id = current_user.id)).all()
    #get all comments by user
    get_comments = Comment.query.filter(Comment.user_comment.has(id = current_user.id)).all()

    context={
      'get_user': get_user,
      'get_likes': get_likes,
      'get_comments':get_comments
    }

    return render_template("profile.html",**context)
  abort(404)

#change payments
#cancel subscription 
@main.route("/cancel/subscription")
@login_required
def cancel_sub():
  sub_id = get_subscription_id(current_user.email)
  if sub_id:
    stripe.Subscription.delete(sub_id)
    get_user = User.query.get(int(current_user.id))
    db.session.delete(get_user)
    db.session.commit()

    return redirect(url_for("forms.logout"))
  abort(404)




#about me
#admin page(delete post, user or add user and view users)
#connect stripehook

