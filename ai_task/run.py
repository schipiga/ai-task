import os

from flask import jsonify

from ai_task.app import app
from ai_task.db import db, User

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
    return jsonify({"hello": "world"})

@app.route("/api/v1.0/metrics")
def metrics():
    return jsonify({"hello": "world"})

if __name__ == '__main__':
    if not os.path.exists("db.sqlite"):
        db.create_all()
    app.run(debug=True)
