# -*- coding: utf-8 -*-

from predict_service.classifiers.logistic_regression import classify as lr_classify


__all__ = [
    "classifiers",
]

classifiers = {
    "logistic_regression": lr_classify,
}
