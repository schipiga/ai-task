# -*- coding: utf-8 -*-

import os.path as path

from attrdict import AttrDict


__all__ = [
    "CONF",
]

CONF = AttrDict({
    "db_path": path.join(path.dirname(__file__), "db.sqlite"),
    "classifier_name": "logistic_regression",
    "secret_key": "adsh!9a=#&%10=5+1cyfiv@)_m&i0_=5@mk$2*&uyb8o=8&qy04vz#¤",
})
