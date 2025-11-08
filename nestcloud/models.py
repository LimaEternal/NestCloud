from nestcloud import db, manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.id


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
