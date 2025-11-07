# pages/login.py
from flask import Blueprint, render_template, request, redirect, url_for
from database.requests import check_password

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if check_password(username, password):
            # TODO: установить сессию (пока просто редирект)
            return redirect(url_for("home.home_page"))
        else:
            return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")
