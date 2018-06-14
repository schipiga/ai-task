 # -*- coding: utf-8 -*-

import os
import os.path as path
import pickle

from flask import abort, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_union
import pandas as ps

from ai_task.app import app
import ai_task.db as db


@app.route("/")
def greeting():
    return jsonify({"greeting": "Hello man!"})


@app.route("/api/v1.0/users", methods=["POST"])
def new_user():

    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        abort(400)  # missing arguments

    if not db.User.query.filter_by(username=username).first():
        abort(400)  # existing user

    user = db.User(username="admin")
    user.hash_password("admin")

    db.session.add(user)
    db.session.commit()

    return jsonify({"username": user.username})


@app.route("/api/v1.0/token", methods=["POST"])
def gen_token():

    username = request.json.get("username")
    password = request.json.get("password")

    user = db.User.check_creds(username, password)
    if not user:
        abort(400)

    duration = 24 * 60 * 60
    token = user.generate_auth_token(duration)
    return jsonify({"token": token.decode("ascii"), "duration": duration})


@app.route("/api/v1.0/predict", methods=["POST"])
def predict():

    token = request.json.get("token")

    if not token:
        abort(400)

    user = db.User.check_auth_token(token)
    if not user:
        abort(400)

    comment = request.json.get("comment")
    if not comment:
        abort(400)

    classify = classifiers.get(CONF.classifier.name)
    if not classify:
        abort(400)

    c = db.Classifier.query.filter_by(name=CONF.classifier_name).first()

    classification = classify(comment)
    p = db.Predict(
        comment=comment, user_id=user.id,
        classifier_id=c.id, **classification)
    db.session.add(p)

    m = db.Metric.query.first()
    m.num_of_requests += 1
    m.sum_of_toxic += p.toxic
    m.sum_of_severe_toxic += p.severe_toxic
    m.sum_of_obscene += p.obscene
    m.sum_of_threat += p.threat
    m.sum_of_insult += p.insult
    m.sum_of_identity_hate += p.identity_hate

    db.session.add(m)
    db.session.commit()

    return jsonify(classification)


@app.route("/api/v1.0/metrics")
def metrics():
    m = db.Metric.query.first()

    if not m.num_of_requests:
        return jsonify({})

    return jsonify({
        "number of requests": m.num_of_requests,
        "average of toxic": m.sum_of_toxic / m.num_of_requests,
        "average of severe_toxic": m.sum_of_severe_toxic / m.num_of_requests,
        "average of obscene": m.sum_of_obscene / m.num_of_requests,
        "average of threat": m.sum_of_threat / m.num_of_requests,
        "average of insult": m.sum_of_insult / m.num_of_requests,
        "average of identity_hate": m.sum_of_identity_hate / m.num_of_requests,
    })


def verify_user(username, password):

    if not username or not password:
        return None

    user = db.User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return None

    return user


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
