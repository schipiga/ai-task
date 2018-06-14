# -*- coding: utf-8 -*-

import os.path as path

import pandas as pd
import pickle


__all__ = [
    "classify",
]

model_path = path.join(path.dirname(__file__), "logistic_regression.mdl")
model = pickle.load(open(model_path, "rb"))


def classify(comment):
    test_text = pd.Series(comment)
    test_features = model["vectorizer"].transform(test_text)

    result = {}
    for name, clsfr in model["classifiers"].iteritems():
        result[name] = clsfr.predict_proba(test_features)[0][1]
    return result
