"""This module imports third-party packages which have been linked via ``git submodule``

This is necessary since most root repository directories aren't python modules themselves.
"""

import os
import sys

_modules = [
    ('httplib2','python2',),
    ('python-oauth2',),
    ('simpleauth',)
]

for module in _modules:
    sys.path.append(os.path.join(os.path.dirname(__file__), *module))
