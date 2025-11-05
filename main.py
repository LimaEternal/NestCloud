from flask import Flask
from pages.login import login_bp
from pages.home import home_bp
from pages.about import about_bp

app = Flask(__name__)

app.register_blueprint(login_bp)
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)


if __name__ == "__main__":
    app.run(debug=True)
