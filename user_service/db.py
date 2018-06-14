# -*- coding: utf-8 -*-

import os.path as path

from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from user_service.app import app
from user_service.config import CONF


__all__ = [
    "init_db",
    "db",
    "User",
]

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(64), nullable=False)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(CONF.secret_key, expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def check_auth_token(token):
        s = Serializer(CONF.secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data["id"])
        return user

    @staticmethod
    def check_creds(username, password):

        if not username or not password:
            return None

        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return None

        return user


def init_db():
    if path.exists(CONF.db_path):
        print("Use existing database '%s'" % CONF.db_path)
        return

    db.create_all()
    print("Database '%s' is initialized" % CONF.db_path)
