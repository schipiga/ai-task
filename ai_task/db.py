# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from ai_task.app import app
from ai_task.classifiers import classifiers
from ai_task.config import CONF


__all__ = [
    "init_db",
    "User",
    "Predict",
    "Metric",
]

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(64), nullable=False)
    predicts = db.relationship("Predict")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(CONF["secret_key"], expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def check_auth_token(token):
        s = Serializer(CONF["secret_key"])
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


class Classifier(db.Model):
    __tablename__ = "classifiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, nullable=True, unique=True)
    predicts = db.relationship("Predict")


class Predict(db.Model):
    __tablename__ = "predicts"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, index=True, nullable=False)
    toxic = db.Column(db.Float, nullable=False)
    severe_toxic = db.Column(db.Float, nullable=False)
    obscene = db.Column(db.Float, nullable=False)
    threat = db.Column(db.Float, nullable=False)
    insult = db.Column(db.Float, nullable=False)
    identity_hate = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    classifier_id = db.Column(
        db.Integer, db.ForeignKey("classifiers.id"), nullable=False)


class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    num_of_requests = db.Column(db.Integer, nullable=False)
    sum_of_toxic = db.Column(db.Float, nullable=False)
    sum_of_severe_toxic = db.Column(db.Float, nullable=False)
    sum_of_obscene = db.Column(db.Float, nullable=False)
    sum_of_threat = db.Column(db.Float, nullable=False)
    sum_of_insult = db.Column(db.Float, nullable=False)
    sum_of_identity_hate = db.Column(db.Float, nullable=False)


def init_db():

    if os.path.exists(CONF.db_path):
        print("Use existing database '%s'" % CONF.db_path)
        return

    db.create_all()
    m = Metric(num_of_requests=0,
               sum_of_toxic=0,
               sum_of_severe_toxic=0,
               sum_of_obscene=0,
               sum_of_threat=0,
               sum_of_insult=0,
               sum_of_identity_hate=0)
    db.session.add(m)

    for name in classifiers:
        c = Classifier(name=name)
        db.session.add(c)

    db.session.commit()
    print("Database '%s' is initialized" % CONF.db_path)
