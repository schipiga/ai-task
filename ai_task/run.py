import os
import os.path as path
import pickle

from flask import jsonify, request
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


@app.route("/api/v1.0/users")
def new_user():
    user = User(username="admin")
    user.hash_password("admin")
    db.session.add(user)
    db.session.commit()
    return jsonify({"username": user.username})


@app.route("/api/v1.0/predict")
def predict():
    comment = request.args.get("comment")
    test_text = ps.Series(comment)
    test_features = model["vectorizer"].transform(test_text)

    result = {}
    for name, clsfr in model["classifiers"].iteritems():
        result[name] = clsfr.predict_proba(test_features)[0][1]

    p = Predict(**result)
    p.user_id = db.session.query(User).first().id
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
