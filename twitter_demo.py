#!/usr/bin/python
"""Twitter front page and OAuth demo handlers.

Mostly copied from https://github.com/wasauce/tweepy-examples .
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import logging
from webob import exc

import app
import appengine_config
import tweepy

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

OAUTH_CALLBACK = 'http://%s/twitter_oauth_callback' % appengine_config.HOST


class OAuthToken(db.Model):
  """Datastore model class for an OAuth token.
  """
  token_key = db.StringProperty(required=True)
  token_secret = db.StringProperty(required=True)


class FrontPageHandler(app.TemplateHandler):
  """Renders and serves the front page.
  """
  template_file = 'templates/twitter_index.html'

  def get(self):
    try:
      auth = tweepy.OAuthHandler(appengine_config.TWITTER_APP_KEY,
                                 appengine_config.TWITTER_APP_SECRET,
                                 OAUTH_CALLBACK)

      self.template_vars.update({
          'authurl': auth.get_authorization_url(),
          'request_token': auth.request_token
          })
    except tweepy.TweepError, e:
      msg = 'Could not create Twitter OAuth request token: '
      logging.exception(msg)
      raise exc.HTTPInternalServerError(msg + `e`)

    # store the request token for later use in the callback page
    OAuthToken(token_key = auth.request_token.key,
               token_secret = auth.request_token.secret,
               ).put()

    super(FrontPageHandler, self).get()


class CallbackHandler(app.TemplateHandler):
  """The OAuth callback.
  """
  template_file = 'templates/twitter_oauth_callback.html'

  def get(self):
    oauth_token = self.request.get('oauth_token', None)
    oauth_verifier = self.request.get('oauth_verifier', None)
    if oauth_token is None:
      raise exc.HTTPBadRequest('Missing required query parameter oauth_token.')

    # Lookup the request token
    request_token = OAuthToken.gql('WHERE token_key=:key', key=oauth_token).get()
    if request_token is None:
      raise exc.HTTPBadRequest('Invalid oauth_token: %s' % request_token)

    # Rebuild the auth handler
    auth = tweepy.OAuthHandler(appengine_config.TWITTER_APP_KEY,
                               appengine_config.TWITTER_APP_SECRET)
    auth.set_request_token(request_token.token_key, request_token.token_secret)

    # Fetch the access token
    try:
      auth.get_access_token(oauth_verifier)
    except tweepy.TweepError, e:
      msg = 'Twitter OAuth error, could not get access token: '
      logging.exception(msg)
      raise exc.HTTPInternalServerError(msg + `e`)

    self.template_vars['access_token'] = auth.access_token

    super(CallbackHandler, self).get()


# class PostTweet(RequestHandler):
#   """Uses the retrieved access token.
#   """
#   def post(self):
#     tweettext = str(cgi.escape(self.request.get('tweettext')))
#     # Normally the key and secret would not be passed but rather
#     # stored in a DB and fetched for a user.
#     token_key = str(self.request.get('key'))
#     token_secret = str(self.request.get('secret'))

#     #Here we authenticate this app's credentials via OAuth
#     auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

#     #Here we set the credentials that we just verified and passed in.
#     auth.set_access_token(token_key, token_secret)

#     #Here we authorize with the Twitter API via OAuth
#     twitterapi = tweepy.API(auth)

#     #Here we update the user's twitter timeline with the tweeted text.
#     twitterapi.update_status(tweettext)

#     #Now we fetch the user information and redirect the user to their twitter
#     # username page so that they can see their tweet worked.
#     user = twitterapi.me()
#     self.redirect('http://www.twitter.com/%s' % user.screen_name)


def main():
  application = webapp.WSGIApplication(
      [('/', FrontPageHandler),
       ('/twitter_oauth_callback', CallbackHandler),
       ],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()