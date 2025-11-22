from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from loaded_dotenv import DATABASE, SECRET_KEY
import os

app = Flask("NestCloud")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)
manager = LoginManager(app)
manager.login_view = "login_page"  # ← обязательно!
manager.login_message = "Пожалуйста, войдите в аккаунт, чтобы получить доступ."
manager.login_message_category = "info"

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024  # 16 МБ максимум
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
from nestcloud import models, routes
