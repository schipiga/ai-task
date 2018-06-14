 # -*- coding: utf-8 -*-

import os
import os.path as path
import pickle

from flask import abort, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_union
import pandas as ps

from ai_task.app import app
from ai_task.db import db, User, Predict, Metric


model_path = path.join(path.dirname(__file__), "model.reg")
model = pickle.load(open(model_path, "rb"))


@app.route("/")
def greeting():
    return jsonify({"greeting": "Hello man!"})


@app.route("/api/v1.0/users", methods=["POST"])
def new_user():

    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        abort(400)  # missing arguments

    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user

    user = User(username="admin")
    user.hash_password("admin")

    db.session.add(user)
    db.session.commit()

    return jsonify({"username": user.username})


def verify_user(username, password):

    if not username or not password:
        return None

    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return None

    return user


@app.route("/api/v1.0/token", methods=["POST"])
def gen_token():

    username = request.json.get("username")
    password = request.json.get("password")

    user = verify_user(username, password)
    if not user:
        abort(400)

    duration = 24 * 60 * 60
    token = user.generate_auth_token(duration)
    return jsonify({"token": token.decode("ascii"), "duration": duration})


@app.route("/api/v1.0/predict")
def predict():

    token = request.json.get("token")

    if not token:
        abort(400)

    user = User.verify_auth_token(token)
    if not user:
        abort(400)

    comment = request.json.get("comment")
    if not comment:
        abort(400)

    test_text = ps.Series(comment)
    test_features = model["vectorizer"].transform(test_text)

    result = {}
    for name, clsfr in model["classifiers"].iteritems():
        result[name] = clsfr.predict_proba(test_features)[0][1]

    p = Predict(**result)
    p.user_id = user.id
    db.session.add(p)

    m = db.session.query(Metric).first()
    m.num_of_requests += 1
    m.sum_of_toxic += p.toxic
    m.sum_of_severe_toxic += p.severe_toxic
    m.sum_of_obscene += p.obscene
    m.sum_of_threat += p.threat
    m.sum_of_insult += p.insult
    m.sum_of_identity_hate += p.identity_hate

    db.session.add(m)
    db.session.commit()

    return jsonify(result)


@app.route("/api/v1.0/metrics")
def metrics():
    m = db.session.query(Metric).first()
    return jsonify({
        "number of requests": m.num_of_requests,
        "average of toxic": m.sum_of_toxic / m.num_of_requests,
        "average of severe_toxic": m.sum_of_severe_toxic / m.num_of_requests,
        "average of obscene": m.sum_of_obscene / m.num_of_requests,
        "average of threat": m.sum_of_threat / m.num_of_requests,
        "average of insult": m.sum_of_insult / m.num_of_requests,
        "average of identity_hate": m.sum_of_identity_hate / m.num_of_requests,
    })


if __name__ == "__main__":
    if not os.path.exists("db.sqlite"):
        db.create_all()
        m = Metric(num_of_requests=0,
                   sum_of_toxic=0,
                   sum_of_severe_toxic=0,
                   sum_of_obscene=0,
                   sum_of_threat=0,
                   sum_of_insult=0,
                   sum_of_identity_hate=0)
        db.session.add(m)
        db.session.commit()
    app.run(debug=True)
