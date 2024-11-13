import logging
import os
import uuid

import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from sqlalchemy.exc import IntegrityError

from forms import UserForm
from models import User, db

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///users.db"
)
app.config["SECRET_KEY"] = "your_secret_key"
csrf = CSRFProtect(app)
csrf.init_app(app)

db.init_app(app)
ma = Marshmallow(app)

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)


@app.route("/")
def list_users():
    page = request.args.get("page", 1, type=int)
    users = User.query.paginate(page=page, per_page=5)
    for user in users.items:
        LOGGER.debug("User: %s", user)
        LOGGER.debug("User avatar URL: %s", user.avatar_url)
    return render_template("index.html", users=users)


@app.route("/add", methods=["GET", "POST"])
def add_user():
    form = UserForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        avatar_filename = os.path.join(
            "avatars", f"{form.name.data.replace(' ', '_')}_{uuid.uuid1()}.png"
        )
        avatar_path = os.path.join("static", "images", avatar_filename)
        custom_avatar = False  # Flag to check if a custom avatar was generated if not writting file of the avatar is not needed
        try:
            # Generate avatar using Robohash and save it locally
            avatar_url = f"https://robohash.org/{form.name.data.strip('')}.png?set=set5"
            response = requests.get(avatar_url, timeout=5)
            if response.status_code == 200:
                custom_avatar = True
                LOGGER.info("Avatar generated successfully")
            else:
                LOGGER.error("Failed to generate avatar")
                raise requests.RequestException("Failed to generate avatar")
        except requests.RequestException:
            LOGGER.info("Failed to generate avatar. Using default avatar instead.")
            avatar_filename = os.path.join("default_avatar", "default_avatar.png")

        avatar_url = url_for("static", filename=f"images/{avatar_filename}")
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            avatar_url=avatar_url,
        )
        try:
            db.session.add(user)
            db.session.commit()
            if custom_avatar:
                with open(avatar_path, "wb") as avatar_file:
                    avatar_file.write(response.content)
            LOGGER.info("User added successfully")
            flash("User added successfully", "success")
            return redirect(url_for("list_users"))
        except IntegrityError as e:
            db.session.rollback()  # Rollback the failed transaction
            if "user_email_key" in str(e.orig):
                LOGGER.error("A user with this email already exists")
                form.email.errors.append(
                    "A user with this email already exists. Please use a different email."
                )
            elif "user_phone_key" in str(e.orig):
                LOGGER.error("A user with this phone number already exists")
                form.phone.errors.append(
                    "A user with this phone number already exists. Please use a different phone number."
                )
            else:
                LOGGER.error("An error occurred while adding the user")
                flash(
                    "An error occurred while adding the user. Please try again.",
                    "danger",
                )

    return render_template("add_user.html", form=form)


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(request.form, obj=user)
    if request.method == "POST" and form.validate_on_submit():
        try:
            form.populate_obj(user)
            db.session.commit()
            LOGGER.info("User updated successfully")
            flash("User updated successfully")
            return redirect(url_for("list_users"))
        except IntegrityError as e:
            db.session.rollback()  # Rollback the failed transaction
            if "user_email_key" in str(e.orig):
                LOGGER.error("A user with this email already exists")
                form.email.errors.append(
                    "A user with this email already exists. Please use a different email."
                )
            elif "user_phone_key" in str(e.orig):
                LOGGER.error("A user with this phone number already exists")
                form.phone.errors.append(
                    "A user with this phone number already exists. Please use a different phone number."
                )
            else:
                LOGGER.error("An error occurred while adding the user")
                flash(
                    "An error occurred while adding the user. Please try again.",
                    "danger",
                )

    return render_template("update_user.html", form=form, user=user)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_user(id):
    user = User.query.get_or_404(id)

    try:
        if user.avatar_url:
            avatar_path = user.avatar_url.lstrip("/")
            if (
                user.avatar_url
                and "default_avatar.png" not in user.avatar_url
                and os.path.exists(avatar_path)
            ):
                os.remove(avatar_path)

        db.session.delete(user)
        db.session.commit()
        LOGGER.info("User deleted successfully")
        flash("User deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        LOGGER.error(f"An error occurred while trying to delete the user: {e}")
        flash("An error occurred while trying to delete the user.", "danger")

    return redirect(url_for("list_users"))


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    page = request.args.get("page", 1, type=int)

    users = User.query.filter(User.name.ilike(f"%{query}%")).paginate(
        page=page, per_page=5
    )

    return render_template("index.html", users=users, query=query)


@app.errorhandler(404)
def not_found(e):
    LOGGER.error("Page not found")
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
