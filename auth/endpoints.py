import os

from .models import User


def get_current_user():
    token = os.getenv('HTTP_AUTHORIZATION')
    if token:
        try:
            token = token.split(' ')[1]
        except IndexError:
            pass

    user, _ = User.get_by_bearer_token(token)
    return user
