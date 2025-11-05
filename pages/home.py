from flask import Blueprint, redirect, url_for, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def root():
    return redirect(url_for("home.home_page"))


@home_bp.route("/home")
def home_page():
    return render_template("home.html")
