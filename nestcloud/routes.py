# pages/register.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required
from nestcloud import db, app
from nestcloud.models import User


@app.route("/")
def root():
    return redirect("/home")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        if not login or not password:
            flash("Пожалуйста, заполните все поля!")
            return render_template("register.html")
        else:
            print(login, password)
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login_page"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        if not login or not password:
            flash("Пожалуйста, заполните все поля!")
            return render_template("login.html")
        else:
            user = User.query.filter_by(login=login).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Неверный логин или пароль!")

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for("login_page") + "?next" + request.url)
    return response
