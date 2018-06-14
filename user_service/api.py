 # -*- coding: utf-8 -*-

from flask import abort, jsonify, request

from user_service.app import app
import user_service.db as db


@app.route("/api/v1.0/users", methods=["POST"])
def create_user():

    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        abort(400)  # missing arguments

    if db.User.query.filter_by(username=username).first():
        abort(400)  # existing user

    user = db.User(username="admin")
    user.hash_password("admin")

    db.db.session.add(user)
    db.db.session.commit()

    return jsonify({"username": user.username})


@app.route("/api/v1.0/tokens", methods=["POST"])
def create_token():

    username = request.json.get("username")
    password = request.json.get("password")

    user = db.User.check_creds(username, password)
    if not user:
        abort(400)

    duration = 24 * 60 * 60
    token = user.generate_auth_token(duration)
    return jsonify({"token": token.decode("ascii"), "duration": duration})


@app.route("/api/v1.0/tokens/check")
def check_token():

    token = request.json.get("token")
    if not token:
        abort(400)

    user = db.User.check_auth_token(token)
    if not user:
        abort(400)

    return jsonify({"username": user.username})


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
