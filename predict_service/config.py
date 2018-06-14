# -*- coding: utf-8 -*-

import os.path as path

from attrdict import AttrDict


__all__ = [
    "CONF",
]

CONF = AttrDict({
    "db_path": path.join(path.dirname(__file__), "db.sqlite"),
    "classifier_name": "logistic_regression",
    "secret_key": "1#eucv)rr^sdu)!7@1r2@4d@n!9w2e#ufp9b7@)=x@8stg0fj1",
    "host": "127.0.0.1:5000",
    "user_service": "http://127.0.0.1:5001",
})
