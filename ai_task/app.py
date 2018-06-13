from flask import Flask

__all__ = [
    "app",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = "Hello world!"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
