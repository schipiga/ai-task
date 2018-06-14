# -*- coding: utf-8 -*-

import argparse
import os.path as path
import pickle

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_union

cur_dir = path.dirname(__file__)
model_path = path.normpath(
    path.join(cur_dir, "../predict_service/classifiers/logistic_regression.mdl"))
train_path = path.join(cur_dir, "train_data.csv")

parser = argparse.ArgumentParser()
parser.add_argument("--size", type=int)
args = parser.parse_args()

size = args.username or 10000
split = lambda seq: seq[:size] if size else seq

class_names = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]

print("Generating regression model to '%s'..." % model_path)

train = pd.read_csv(train_path).fillna(" ")
train_text = split(train["comment_text"])

word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents="unicode",
    analyzer="word",
    token_pattern=r"\w{1,}",
    ngram_range=(1, 1),
    max_features=30000)
char_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents="unicode",
    analyzer="char",
    ngram_range=(1, 4),
    max_features=30000)
vectorizer = make_union(word_vectorizer, char_vectorizer, n_jobs=2)

vectorizer.fit(train_text)
train_features = vectorizer.transform(train_text)

scores = []
classifiers = {}
for class_name in class_names:
    train_target = split(train[class_name])
    classifier = LogisticRegression(solver="sag")

    cv_score = np.mean(cross_val_score(
        classifier, train_features, train_target, cv=3, scoring="roc_auc"))
    scores.append(cv_score)
    print("CV score for class {} is {}".format(class_name, cv_score))

    classifier.fit(train_features, train_target)
    classifiers[class_name] = classifier

print("Total CV score is {}".format(np.mean(scores)))

pickle.dump({"vectorizer": vectorizer, "classifiers": classifiers},
            open(model_path, "wb"))

print("Regression model is saved to '%s'" % model_path)
