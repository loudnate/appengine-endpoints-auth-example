import json
import logging
import webapp2
from webapp2_extras import auth

from simpleauth import SimpleAuthHandler


class AuthHandler(webapp2.RequestHandler, SimpleAuthHandler):
    """Authenticates a user to the application via a third-party provider.

    The return value of this request is an OAuth token response.

    Only a subset of the PROVIDERS specified in SimpleAuthHandler are currently supported.
    Tested providers: Facebook
    """
    def _on_signin(self, data, auth_info, provider):
        # Create the auth ID format used by the User model
        auth_id = '%s:%s' % (provider, data['id'])
        user_model = auth.get_auth().store.user_model
        user = user_model.get_by_auth_id(auth_id)

        if not user:
            ok, user = user_model.create_user(auth_id)
            if not ok:
                logging.error('Unable to create user for auth_id %s' % auth_id)
                self.abort(500, 'Unable to create user')

        return user

    def post(self):
        # TODO: Consider adding a check for a valid client ID here as well.

        access_token = self.request.get('x_access_token')
        provider = self.request.get('x_provider')

        if provider not in self.PROVIDERS or access_token is None:
            self.abort(401, 'Unknown provider or access token')

        auth_info = {'access_token': access_token}
        fetch_user_info = getattr(self, '_get_%s_user_info' % provider)
        user_info = fetch_user_info(auth_info)

        if 'id' in user_info:
            user = self._on_signin(user_info, auth_info, provider)
            token = user.create_bearer_token(user.get_id())

            self.response.content_type = 'application/json'
            self.response.body = json.dumps({
                'access_token': token.token,
                'token_type': 'Bearer',
                'expires_in': token.bearer_token_timedelta.total_seconds(),
                'refresh_token': token.refresh_token
            })
        else:
            self.abort(401, 'Access token is invalid')
