from flask import Flask


__all__ = [
    "app",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = "adsh!9a=#&%10=5+1cyfiv@)_m&i0_=5@mk$2*&uyb8o=8&qy04vz#¤"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
