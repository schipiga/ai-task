# -*- coding: utf-8 -*-

import json
import os.path as path

import pandas as pd
import requests

test_data_path = path.join(path.dirname(__file__), "test_data.csv")
test = pd.read_csv(test_data_path).fillna(" ")
comments = test["comment_text"]


class Request(object):

    def __init__(self):
        self._token = None
        self._username = None
        self._password = None

    def create_user(self, username, password):
        self._username = username
        self._password = password

        r = requests.post(
            "http://localhost:5000/api/v1.0/users",
            json={"username": username, "password": password})
        print("User '%s' is created" % r.json()["username"])

    def capture_token(self):
        r = requests.get("http://localhost:5000/api/v1.0/token",
                         json={"username": self._username,
                               "password": self._password})
        self._token = r.json()["token"]
        print("Auth token '%s' got" % self._token)

    def predict_comments(self, number):
        print(50 * "-")
        for comment in comments[:number]:
            r = requests.get("http://localhost:5000/api/v1.0/predict",
                             json={"token": self._token, "comment": comment})
            print(comment)
            print("")
            print(r.json())
            print(50 * "-")

    def get_statistics(self):
        r = requests.get("http://localhost:5000/api/v1.0/metrics")
        print(r.json())


if __name__ == "__main__":
  req = Request()
  req.create_user("admin", "admin")
  req.capture_token()
  req.predict_comments(1000)
  req.get_statistics()
