# -*- coding: utf-8 -*-

from ai_task.classifiers.logistic_regression import classify as lr_classify


__all__ = [
    "classifiers",
]

classifiers = {
    "logistic_regression": lr_classify,
}
