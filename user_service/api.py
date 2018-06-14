 # -*- coding: utf-8 -*-

from flask import abort, jsonify, make_response, request

from user_service.app import app
import user_service.db as db


V = "v1.0"


def reject(error_message, code=400):
    """Wrapper over flask helpers to return wrong response in JSON format.

    Args:
        error_message (str): Message explaining error type.
        code (int): Status code of response.
    """
    abort(make_response(jsonify({"error": error_message}), code))


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
        return reject("username or password are invalid")

    if db.User.query.filter_by(username=username).first():
        return reject("user already exists")

    user = db.User(username="admin")
    user.hash_password("admin")

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
        return reject("username or password are invalid")

    duration = 24 * 60 * 60
    token = user.generate_auth_token(duration)
    return jsonify({"token": token.decode("ascii"), "duration": duration})


@app.route("/api/%s/tokens/check" % V)
def check_token():
    """Handler to process token validation request.

    Request options:
        - token: auth token to validate

    Response data:
        - username: name of user by token
    """
    token = request.json.get("token")
    if not token:
        return reject("no token")

    user = db.User.check_auth_token(token)
    if not user:
        return reject("invalid token")

    return jsonify({"username": user.username})


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
