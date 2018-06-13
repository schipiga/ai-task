from flask import jsonify

from .app import app

@app.route("/")
def greeting():
    return jsonify({"greeting": "Hello man!"})

@app.route("/api/v1.0/predict")
def predict():
    return jsonify({"hello": "world"})

@app.route("/api/v1.0/metrics")
def metrics():
    return jsonify({"hello": "world"})

if __name__ == '__main__':
    app.run(debug=True)
