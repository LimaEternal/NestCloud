from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from loaded_dotenv import DATABASE, SECRET_KEY

app = Flask("NestCloud")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)
manager = LoginManager(app)
from nestcloud import models, routes
