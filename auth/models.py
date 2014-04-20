from datetime import datetime
from datetime import timedelta
import logging

from google.appengine.ext.ndb import model
from webapp2_extras import security
from webapp2_extras.appengine.auth.models import Unique
from webapp2_extras.appengine.auth.models import User as BaseUserExpando
from webapp2_extras.appengine.auth.models import UserToken as BaseUserToken


class UserToken(BaseUserToken):
    SUBJECT_BEARER = 'bearer'

    unique_model = Unique
    bearer_token_timedelta = timedelta(days=365)

    refresh_token = model.StringProperty()

    @classmethod
    def create(cls, user, subject, token=None):
        if subject == cls.SUBJECT_BEARER:
            user = str(user)
            token = token or security.generate_random_string(entropy=128)

            # Bearer tokens must be unique on their own, without a user scope.
            key = cls.get_key('', subject, token)
            entity = cls(
                key=key,
                user=user,
                subject=subject,
                token=token,
                refresh_token=security.generate_random_string(entropy=128)
            )

            # Refresh tokens must be unique
            ok = cls.unique_model.create(
                '%s.refresh_token:%s' % (cls.__name__, entity.refresh_token)
            )
            if ok:
                entity.put()
            else:
                logging.warning('Unable to create a unique user token for user %s', user)
                entity = None
        else:
            entity = super(UserToken, cls).create(user, subject, token)

        return entity

    def expires_at(self):
        """Returns the datetime after which this token is no longer valid

        :returns:
            A datetime object after which this token is no longer valid.
        """
        if self.subject == self.SUBJECT_BEARER:
            return self.created + self.bearer_token_timedelta

        return None

    def is_expired(self):
        """Whether the token is past its expiry time

        :returns:
            True if the token has expired
        """
        return self.expires_at() <= datetime.now()


class User(BaseUserExpando):
    token_model = UserToken

    @classmethod
    def get_by_bearer_token(cls, token):
        """Returns a user object based on a user ID and oauth bearer token.

        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        if token:
            token_obj = cls.token_model.get('', 'bearer', token)
            if token_obj and not token_obj.is_expired():
                user = cls.get_by_id(int(token_obj.user))
                if user:
                    return user, token_obj.created

        return None, None

    @classmethod
    def create_bearer_token(cls, user_id):
        """Creates a new oauth bearer token for a given user ID.

        :param user_id:
            User unique ID.
        :returns:
            A token object, or None if one could not be created.
        """
        return cls.token_model.create(user_id, 'bearer')
