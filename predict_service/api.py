# -*- coding: utf-8 -*-

from flask import abort, jsonify, make_response, request

from predict_service.app import app
from predict_service.classifiers import classifiers
from predict_service.config import CONF
import predict_service.db as db
import predict_service.services as ms


classify = classifiers[CONF.classifier_name]


def reject(error_message, code=400):
    abort(make_response(jsonify({"error": error_message}), code))


@app.route("/api/v1.0/predict")
def predict():

    token = request.json.get("token")

    if not token:
        return reject("no token")

    user = ms.check_token(token)
    if not user:
        return reject("invalid token")

    comment = request.json.get("comment")
    if not comment or not comment.strip():
        return reject("comment is empty")

    c = db.Classifier.query.filter_by(name=CONF.classifier_name).first()

    classification = classify(comment)
    p = db.Predict(
        comment=comment, username=user["username"],
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


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
