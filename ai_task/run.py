 # -*- coding: utf-8 -*-

import os
import os.path as path
import pickle

from flask import abort, jsonify, make_response, request
import pandas as ps

from ai_task.app import app
from ai_task.classifiers import classifiers
from ai_task.config import CONF
import ai_task.db as db


V = "v1.0"
classify = classifiers[CONF.classifier_name]


def reject(error_message, code=400):
    """Wrapper over flask helpers to return wrong response in JSON format.
    Args:
        error_message (str): Message explaining error type.
        code (int): Status code of response.
    """
    abort(make_response(jsonify({"error": error_message}), code))


@app.route("/")
def greeting():
    """Handler to process root request."""
    return jsonify({"greeting": "Hello man!"})


@app.route("/api/%s/users" % V, methods=["POST"])
def create_user():
    """Handler to process user creation request.

    Request options:
        - username: name of user
        - password: password of user

    Response data:
        - username: name of created user
    """
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return reject("invalid username or password")

    if db.User.query.filter_by(username=username).first():
        return reject("user already exists")

    user = db.User(username=username)
    user.hash_password(password)

    db.db.session.add(user)
    db.db.session.commit()

    return jsonify({"username": user.username})


@app.route("/api/%s/tokens" % V, methods=["POST"])
def create_token():
    """Handler to process auth token creation.

    Request options:
        - username: name of user
        - password: password of user

    Response data:
        - token: generated auth token
        - duration: duration of token validity
    """
    username = request.json.get("username")
    password = request.json.get("password")

    user = db.User.check_creds(username, password)
    if not user:
        return reject("invalid username or password")

    duration = 24 * 60 * 60
    token = user.generate_auth_token(duration)
    return jsonify({"token": token.decode("ascii"), "duration": duration})


@app.route("/api/%s/predict" % V, methods=["POST"])
def predict():
    """Handler to process predict request.

    Request options:
        - token: authentication token
        - comment: comment for classification

    Response data:
        weights of categories
    """
    token = request.json.get("token")

    if not token:
        return reject("no token")

    user = db.User.check_auth_token(token)
    if not user:
        return reject("token is invalid")

    comment = request.json.get("comment")
    if not comment or not comment.strip():
        return reject("comment is empty")

    c = db.Classifier.query.filter_by(name=CONF.classifier_name).first()

    classification = classify(comment)
    p = db.Predict(
        comment=comment, user_id=user.id,
        classifier_id=c.id, **classification)
    db.db.session.add(p)

    m = db.Metric.query.first()
    m.num_of_requests += 1
    m.sum_of_toxic += p.toxic
    m.sum_of_severe_toxic += p.severe_toxic
    m.sum_of_obscene += p.obscene
    m.sum_of_threat += p.threat
    m.sum_of_insult += p.insult
    m.sum_of_identity_hate += p.identity_hate

    db.db.session.add(m)
    db.db.session.commit()

    return jsonify(classification)


@app.route("/api/%s/metrics" % V)
def metrics():
    """Handler to process metrics request.

    Response data:
        requests and predicts statistics
    """
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


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
