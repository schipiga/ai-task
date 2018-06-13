import os
import os.path as path
import pickle

from flask import abort, jsonify, request
import pandas as ps

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_union

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

    token = user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


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
    x = m.num_of_requests
    m.num_of_requests += 1
    y = m.num_of_requests
    
    m.avg_of_toxic = (m.avg_of_toxic * x + p.toxic) / y
    m.avg_of_severe_toxic = (m.avg_of_severe_toxic * x + p.severe_toxic) / y
    m.avg_of_obscene = (m.avg_of_obscene * x + p.obscene) / y
    m.avg_of_threat = (m.avg_of_threat * x + p.threat) / y
    m.avg_of_insult = (m.avg_of_insult * x + p.insult) / y
    m.avg_of_identity_hate = (m.avg_of_identity_hate * x + p.identity_hate) / y

    db.session.add(m)
    db.session.commit()

    return jsonify(result)


@app.route("/api/v1.0/metrics")
def metrics():
    m = db.session.query(Metric).first()
    return jsonify({
        "number of requests": m.num_of_requests,
        "average of toxic": m.avg_of_toxic,
        "average of severe toxic": m.avg_of_severe_toxic,
        "average of obscene": m.avg_of_obscene,
        "average of threat": m.avg_of_threat,
        "average of insult": m.avg_of_insult,
        "average of identity_hate": m.avg_of_identity_hate,
    })


if __name__ == '__main__':
    if not os.path.exists("db.sqlite"):
        db.create_all()
        m = Metric(num_of_requests=0,
                   avg_of_toxic=0,
                   avg_of_severe_toxic=0,
                   avg_of_obscene=0,
                   avg_of_threat=0,
                   avg_of_insult=0,
                   avg_of_identity_hate=0)
        db.session.add(m)
        db.session.commit()
    app.run(debug=True)
