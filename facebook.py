#!/usr/bin/python
"""Facebook handler and schema mapping code.

NOTE:
eventually fb will turn phone and address back on. when they do,
add scopes:user_mobile_phone,user_address to get them.

background:
https://developers.facebook.com/blog/post/447/
https://developers.facebook.com/blog/post/446/
"""

__author__ = ['Ryan Barrett <portablecontacts-unofficial@ryanb.org>']

import collections
import datetime
import json
import logging
import pprint
import urllib
import urlparse

import appengine_config

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

ACCOUNT_DOMAIN = 'facebook.com'


# schema mapping
# TODO: addresses, IMs, follow redirects to get pictures
def to_poco(fb):
  pc = collections.defaultdict(dict)
  pc['id'] = fb['id']
  pc['accounts'] = [{'domain': ACCOUNT_DOMAIN, 'userid': fb['id']}]

  if 'username' in fb:
    pc['accounts'][0]['username'] = fb['username']

  if 'name' in fb:
    pc['displayName'] = fb['name']
    pc['name']['formatted'] = fb['name']

  if 'first_name' in fb:
    pc['name']['givenName'] = fb['first_name']

  if 'last_name' in fb:
    pc['name']['familyName'] = fb['last_name']

  if 'birthday' in fb:
    pc['birthday'] = (datetime.datetime.strptime(fb['birthday'], '%m/%d/%Y')
                        .strftime('%Y-%m-%d'))
  if 'gender' in fb:
    pc['gender'] = fb['gender']

  if 'email' in fb:
    pc['emails'] = [{'value': fb['email'], 'type': 'home', 'primary': 'true'}]

  if 'website' in fb:
    pc['urls'] = [{'value': fb['website'], 'type': 'home'}]

  for work in fb.get('work', []):
    org = {}
    pc.setdefault('organizations', []).append(org)
    if 'employer' in work:
      org['name'] = work['employer'].get('name')
    org['type'] = 'job'
    if 'position' in work:
      org['title'] = work['position']

    projects = work.get('projects')
    if 'projects' in work:
      # TODO: convert these to proper xs:date (ISO 8601)format, e.g.
      # 2008-01-23T04:56:22Z
      org['startDate'] = min(p['start_date'] for p in projects)
      org['endDate'] = max(p['end_date'] for p in projects)

  for school in fb.get('education', []):
    org = {}
    pc.setdefault('organizations', []).append(org)
    if 'school' in school:
      org['name'] = school['school'].get('name')
    org['type'] = 'school'
    if 'year' in school:
      org['endDate'] = school['year']

  if 'address' in fb:
    addr = fb['address']
    pc['addresses'] = [{
        'streetAddress': addr['street'],
        'locality': addr['city'],
        'region': addr['state'],
        'country': addr['country'],
        'postalCode': addr['zip'],
        }]
  elif 'location' in fb:
    pc['addresses'] = [{'formatted': fb['location'].get('name')}]

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

  if '' in fb:
    pc[''] = fb['']

      # ],
      # 'photos': [
      #   {
      #     'value': 'http://sample.site.org/photos/12345.jpg',
      #     'type': 'thumbnail'
      #   }
      # ],
      # 'ims': [
      #   {
      #     'value': 'plaxodev8',
      #     'type': 'aim'
      #   }
      # ],
      # 'addresses': [
      #   {
      #     'type': 'home',
      #     'streetAddress': '742 Evergreen Terrace\nSuite 123',
      #     'locality': 'Springfield',
      #     'region': 'VT',
      #     'postalCode': '12345',
      #     'country': 'USA',
      #     'formatted': '742 Evergreen Terrace\nSuite 123\nSpringfield, VT 12345 USA'
      #   }
      # ],
      # 'organizations': [
      #   {
      #     'name': 'Burns Worldwide',
      #     'title': 'Head Bee Guy'
      #   }
      # ],
      # 'accounts': [
      #   {
      #     'domain': 'plaxo.com',
      #     'userid': '2706'
      #   }
      # ]

  return dict(pc)

# # facebook api url templates. can't (easily) use urllib.urlencode() because i
# # want to keep the %(...)s placeholders as is and fill them in later in code.
# # TODO: use appengine_config.py for local mockfacebook vs prod facebook
# GET_AUTH_CODE_URL = '&'.join((
#     ('http://localhost:8000/dialog/oauth/?'
#      if appengine_config.MOCKFACEBOOK else
#      'https://www.facebook.com/dialog/oauth/?'),
#     'scope=read_stream,offline_access',
#     'client_id=%(client_id)s',
#     # redirect_uri here must be the same in the access token request!
#     'redirect_uri=%(host_url)s/facebook/got_auth_code',
#     'response_type=code',
#     'state=%(state)s',
#     ))

# GET_ACCESS_TOKEN_URL = '&'.join((
#     ('http://localhost:8000/oauth/access_token?'
#      if appengine_config.MOCKFACEBOOK else
#      'https://graph.facebook.com/oauth/access_token?'),
#     'client_id=%(client_id)s',
#     # redirect_uri here must be the same in the oauth request!
#     # (the value here doesn't actually matter since it's requested server side.)
#     'redirect_uri=%(host_url)s/facebook/got_auth_code',
#     'client_secret=%(client_secret)s',
#     'code=%(auth_code)s',
#     ))

# FQL_URL = '&'.join((
#     ('http://localhost:8000/method/fql.query?'
#      if appengine_config.MOCKFACEBOOK else
#      'https://api.facebook.com/method/fql.query?'),
#     'access_token=%(access_token)s',
#     'format=json',
#     'query=%(query)s',
#     ))


# class FacebookPage(models.Source):
#   """A facebook profile or page.

#   The key name is the facebook id.

#   Attributes:
#     comment_data: FQL results
#     link_data: FQL results
#     profile_data: FQL results
#   """

#   TYPE_NAME = 'Facebook'

#   # full human-readable name
#   name = db.StringProperty()
#   picture = db.LinkProperty()
#   type = db.StringProperty(choices=('user', 'page'))
#   # unique name used in fb URLs, e.g. facebook.com/[username]
#   username = db.StringProperty()

#   # the token should be generated with the offline_access scope so that it
#   # doesn't expire. details: http://developers.facebook.com/docs/authentication/
#   access_token = db.StringProperty()

#   def display_name(self):
#     return self.name

#   def fql(self, query):
#     return FacebookApp.get().fql(query, self.access_token)

#   @staticmethod
#   def new(handler):
#     """Creates and returns a FacebookPage for the logged in user.

#     Args:
#       handler: the current webapp.RequestHandler
#     """
#     access_token = handler.request.params['access_token']
#     results = FacebookApp.get().fql(
#       'SELECT id, name, url, pic_small, type, username FROM profile WHERE id = me()',
#       access_token)
#     result = results[0]
#     id = str(result['id'])
#     return FacebookPage(key_name=id,
#                         owner=models.User.get_current_user(),
#                         access_token=access_token,
#                         picture=result['pic_small'],
#                         **result)

#   def get_posts(self):
#     """Returns list of (link id aka post object id, link url).
#     """
#     self.comment_data = self.fql(
#       """SELECT post_fbid, time, fromid, username, object_id, text FROM comment
#          WHERE object_id IN (SELECT link_id FROM link WHERE owner = %s)
#          ORDER BY time DESC""" % self.key().name())

#     link_ids = set(str(c['object_id']) for c in self.comment_data)
#     self.link_data = self.fql('SELECT link_id, url FROM link WHERE link_id IN (%s)' %
#                        ','.join(link_ids))

#     fromids = set(str(c['fromid']) for c in self.comment_data)
#     self.profile_data = self.fql(
#       'SELECT id, name, url FROM profile WHERE id IN (%s)' % ','.join(fromids))

#     return [(l['link_id'], l['url']) for l in self.link_data]

#   def get_comments(self, posts):
#     comments_by_link_id = dict((c['object_id'], c) for c in self.comment_data)
#     profiles = dict((p['id'], p) for p in self.profile_data)
#     links = dict((l['link_id'], l['url']) for l in self.link_data)

#     comments = []
#     for link_id, dest in posts:
#       c = comments_by_link_id[link_id]
#       fromid = c['fromid']
#       profile = profiles[fromid]
#       post_url = 'https://www.facebook.com/permalink.php?story_fbid=%s&id=%s' % (
#         c['object_id'], fromid)

#       comments.append(FacebookComment(
#           key_name=c['post_fbid'],
#           source=self,
#           dest=dest,
#           source_post_url=post_url,
#           dest_post_url=links[link_id],
#           created=datetime.datetime.utcfromtimestamp(c['time']),
#           author_name=profile['name'],
#           author_url=profile['url'],
#           content=c['text'],
#           fb_fromid=fromid,
#           fb_username=c['username'],
#           fb_object_id=c['object_id'],
#           ))

#     return comments


# class FacebookComment(models.Comment):
#   """Key name is the comment's object_id.

#   Most of the properties correspond to the columns of the content table in FQL.
#   http://developers.facebook.com/docs/reference/fql/comment/
#   """

#   # user id who wrote the comment
#   fb_fromid = db.IntegerProperty(required=True)

#   # name entered by the user when they posted the comment. usually blank,
#   # generally only populated for external users. if this is provided,
#   # fb_fromid will be 0.
#   fb_username = db.StringProperty()

#   # id of the object this comment refers to
#   fb_object_id = db.IntegerProperty(required=True)


# class FacebookApp(db.Model):
#   """Stores the bridgy app credentials that we use with the API.

#   Not thread safe.
#   """
#   app_id = db.StringProperty(required=True)
#   app_secret = db.StringProperty(required=True)

#   # this will be cached in the runtime
#   __singleton = None

#   @classmethod
#   def get(cls):
#     if not cls.__singleton:
#       # TODO: check that there's only one
#       cls.__singleton = cls.all().get()
#       assert cls.__singleton
#     return cls.__singleton

#   def fql(self, query, access_token):
#     """Runs an FQL query.

#     Args:
#       access_token: string

#     Returns: string

#     TODO: error handling
#     """
#     assert access_token

#     logging.debug('Running FQL query "%s" with access token %s', query, access_token)
#     args = {
#       'access_token': access_token,
#       'query': urllib.quote(query),
#       }
#     resp = urlfetch.fetch(FQL_URL % args, deadline=999)
#     assert resp.status_code == 200, resp.status_code
#     data = json.loads(resp.content)
#     logging.debug('FQL response: %s', pprint.pformat(data))
#     assert 'error_code' not in data and 'error_msg' not in data
#     return data

#   def get_access_token(self, handler, redirect_uri):
#     """Gets an access token for the current user.

#     Actually just gets the auth code and redirects to /facebook_got_auth_code,
#     which makes the next request to get the access token.

#     Args:
#       handler: the current webapp.RequestHandler
#       redirect_uri: string, the local url to redirect to. Must begin with /.
#     """
#     assert self.app_id
#     assert self.app_secret
#     assert redirect_uri.startswith('/'), '%s does not start with /' % redirect_uri

#     url = GET_AUTH_CODE_URL % {
#       'client_id': self.app_id,
#       # TODO: CSRF protection identifier.
#       # http://developers.facebook.com/docs/authentication/
#       'host_url': handler.request.host_url,
#       'state': handler.request.host_url + redirect_uri,
#       # 'state': urllib.quote(json.dumps({'redirect_uri': redirect_uri})),
#       }
#     handler.redirect(url)

#   def _get_access_token_with_auth_code(self, handler, auth_code, redirect_uri):
#     """Gets an access token based on an auth code.

#     Args:
#       handler: the current webapp.RequestHandler
#       auth_code: string
#       redirect_uri: string, the local url to redirect to. Must begin with /.
#     """
#     assert auth_code

#     redirect_uri = urllib.unquote(redirect_uri)
#     # assert redirect_uri.startswith('http://localhost:8080/'), redirect_uri
#     assert '?' not in redirect_uri

#     # TODO: handle permission declines, errors, etc
#     url = GET_ACCESS_TOKEN_URL % {
#       'auth_code': auth_code,
#       'client_id': self.app_id,
#       'client_secret': self.app_secret,
#       'host_url': handler.request.host_url,
#       }
#     resp = urlfetch.fetch(url, deadline=999)
#     # TODO: error handling. handle permission declines, errors, etc
#     logging.debug('access token response: %s' % resp.content)
#     params = urlparse.parse_qs(resp.content)
#     access_token = params['access_token'][0]

#     url = '%s?access_token=%s' % (redirect_uri, access_token)
#     handler.redirect(url)


# class AddFacebookPage(util.Handler):
#   def post(self):
#     FacebookApp.get().get_access_token(self, '/facebook/got_access_token')


# class DeleteFacebookPage(util.Handler):
#   def post(self):
#     page = FacebookPage.get_by_key_name(self.request.params['key_name'])
#     # TODO: remove tasks, etc.
#     msg = 'Deleted %s source: %s' % (page.type_display_name(),
#                                      page.display_name())
#     page.delete()
#     self.redirect('/?msg=' + msg)


# class GotAuthCode(util.Handler):
#   def get(self):
#     FacebookApp.get()._get_access_token_with_auth_code(
#       self, self.request.params['code'], self.request.params['state'])
    

# class GotAccessToken(util.Handler):
#   def get(self):
#     FacebookPage.create_new(self)
#     self.redirect('/')


# application = webapp.WSGIApplication([
#     ('/facebook/add', AddFacebookPage),
#     ('/facebook/delete', DeleteFacebookPage),
#     ('/facebook/got_auth_code', GotAuthCode),
#     ('/facebook/got_access_token', GotAccessToken),
#     ], debug=appengine_config.DEBUG)

# def main():
#   run_wsgi_app(application)


# if __name__ == '__main__':
#   main()
