from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from loaded_dotenv import DATABASE, SECRET_KEY

app = Flask("NestCloud")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)
manager = LoginManager(app)
manager.login_view = "login_page"  # ← обязательно!
manager.login_message = "Пожалуйста, войдите в аккаунт, чтобы получить доступ."
manager.login_message_category = "info"
from nestcloud import models, routes
