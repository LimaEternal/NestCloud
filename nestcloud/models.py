from nestcloud import db, manager
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    files = db.relationship("File", backref="user", lazy=True)

    def __repr__(self):
        return "<User %r>" % self.id


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    preview_path = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file_size = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime)

    def __repr__(self):
        return "<File %r>" % self.id


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
