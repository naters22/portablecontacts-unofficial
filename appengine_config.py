"""App Engine settings.
"""

from __future__ import with_statement
import logging
import os

from google.appengine.api import app_identity

try:
  APP_ID = app_identity.get_application_id()
except AttributeError:
  # this is probably a unit test
  APP_ID = None

# app_identity.get_default_version_hostname() would be better here, but
# it doesn't work in dev_appserver since that doesn't set
# os.environ['DEFAULT_VERSION_HOSTNAME'].
HOST = os.getenv('HTTP_HOST')
SCHEME = 'https' if (os.getenv('HTTPS') == 'on') else 'http'

if not os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
  DEBUG = False
  MOCKFACEBOOK = False
  FACEBOOK_APP_ID = '235997716482623'
else:
  DEBUG = True
  MOCKFACEBOOK = False
  FACEBOOK_APP_ID = '350503391634422'

# twitter app stuff
TWITTER_APP_KEY = '1BsluYKc6dSRdI07VPTUhA'
TWITTER_APP_SECRET_FILE = 'twitter_app_secret'
if os.path.exists(TWITTER_APP_SECRET_FILE):
  with open(TWITTER_APP_SECRET_FILE) as f:
    TWITTER_APP_SECRET = f.read().strip()
else:
  logging.warning('%s file not found, cannot authenticate to twitter.' %
                  TWITTER_APP_SECRET_FILE)
