# -*- coding: utf-8 -*-

from flask import Flask

from user_service.config import CONF


__all__ = [
    "app",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = CONF.secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SERVER_NAME"] = CONF.host
