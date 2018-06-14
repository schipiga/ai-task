# -*- coding: utf-8 -*-

import os.path as path

from flask_sqlalchemy import SQLAlchemy

from predict_service.app import app
from predict_service.classifiers import classifiers
from predict_service.config import CONF


__all__ = [
    "init_db",
    "db",
    "Classifier",
    "Predict",
    "Metric",
]

db = SQLAlchemy(app)


class Classifier(db.Model):
    __tablename__ = "classifiers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, nullable=False, unique=True)
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
    username = db.Column(db.String(32), index=True, nullable=False)
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

    if path.exists(CONF.db_path):
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
