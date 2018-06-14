# -*- coding: utf-8 -*-

import requests

from predict_service.config import CONF


__all__ = [
    "check_token"
]


def check_token(token):
    """Send request to user service in order to check token validity.
    
    Args:
        token (str): Authentication token.

    Returns:
        dict: User data.
    """
    r = requests.get(
        CONF.user_service + "/api/v1.0/tokens/check", json={"token": token})
    if r.status_code != 200:
        return None
    return r.json()
