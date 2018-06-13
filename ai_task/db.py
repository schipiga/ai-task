from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from ai_task.app import app


__all__ = [
    "db",
    "User",
    "Predict",
    "Metric",
]

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    predicts = db.relationship("Predict")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class Predict(db.Model):
    __tablename__ = "predicts"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    toxic = db.Column(db.Float)
    severe_toxic = db.Column(db.Float)
    obscene = db.Column(db.Float)
    threat = db.Column(db.Float)
    insult = db.Column(db.Float)
    identity_hate = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    num_of_requests = db.Column(db.Integer)
    avg_of_toxic = db.Column(db.Float)
    avg_of_severe_toxic = db.Column(db.Float)
    avg_of_obscene = db.Column(db.Float)
    avg_of_threat = db.Column(db.Float)
    avg_of_insult = db.Column(db.Float)
    avg_of_identity_hate = db.Column(db.Float)
