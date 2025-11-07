# pages/register.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.requests import register_user

register_bp = Blueprint("register", __name__)


@register_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("register.html", error="Логин и пароль обязательны")

        if len(username) < 3:
            return render_template(
                "register.html", error="Логин должен быть не короче 3 символов"
            )

        if len(password) < 6:
            return render_template(
                "register.html", error="Пароль должен быть не короче 6 символов"
            )

        if register_user(username, password):
            # Успешная регистрация — можно сразу перенаправить на логин
            return redirect(url_for("login.login_page"))
        else:
            return render_template(
                "register.html", error="Пользователь с таким логином уже существует"
            )

    # GET-запрос — просто показываем форму
    return render_template("register.html")
