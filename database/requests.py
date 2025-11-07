from werkzeug.security import generate_password_hash, check_password_hash
from database.extensions import db
from database.models import User


def register_user(username: str, password: str) -> bool:
    """
    Регистрирует нового пользователя.
    Возвращает True при успехе, False — если пользователь уже существует.
    """
    if user_exists(username):
        return False
    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return True


def user_exists(username: str) -> bool:
    """Проверяет, существует ли пользователь с данным именем."""
    return db.session.query(User).filter_by(username=username).first() is not None


def get_user_by_username(username: str):
    """
    Возвращает объект User или None, если не найден.
    """
    return db.session.query(User).filter_by(username=username).first()


def check_password(username: str, password: str) -> bool:
    """
    Проверяет пароль пользователя.
    Возвращает True, если пароль верный и пользователь существует.
    """
    user = get_user_by_username(username)
    if user is None:
        return False
    return check_password_hash(user.password_hash, password)
