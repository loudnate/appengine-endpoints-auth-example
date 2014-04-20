import os
from webapp2 import WSGIApplication, Route

# Make sure external paths are correctly set
import ext

# webapp2 config
config = {
    'webapp2_extras.auth': {
        'user_model': 'auth.models.User'
    }
}

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

routes = [
    Route('/oauth2/access_token', handler='auth.handlers.AuthHandler', name='auth_access_token'),
]

app = WSGIApplication(routes, config=config, debug=debug)
