import os
from flask import Flask
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

# --- Настройка пути к БД ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DATABASE_DIR, "cloud.db")

# Создаём папку, если её нет
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH.replace(chr(92), '/')}"

# --- Инициализация Flask и БД ---
from database.extensions import db
from database.models import User, File

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Blueprints
from pages.login import login_bp
from pages.home import home_bp
from pages.about import about_bp
from pages.register import register_bp

app.register_blueprint(login_bp)
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(register_bp)

# --- Создание таблиц ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
