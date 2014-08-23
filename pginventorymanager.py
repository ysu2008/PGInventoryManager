import os
import urllib
import math

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_DATABASE_NAME = 'default_database'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def database_key(database_name=DEFAULT_DATABASE_NAME):
    """Constructs a Datastore key for a database entity with database_name."""
    return ndb.Key('Database', database_name)

class UPC(ndb.Model):
    """Models an individual UPC entry."""
    upc_code = ndb.StringProperty()
    quantity = ndb.IntegerProperty()
    pack_size = ndb.IntegerProperty()
    name = ndb.StringProperty()
    image_url = ndb.StringProperty()
    estimated_consumption = ndb.IntegerProperty()
    vendor = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):

    def get(self):
        database_name = self.request.get('database_name',
                                          DEFAULT_DATABASE_NAME)
        upcs_query = UPC.query(
            ancestor=database_key(database_name)).order(UPC.vendor, UPC.name)
        upcs = upcs_query.fetch(None)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'upcs': upcs,
            'database_name': urllib.quote_plus(database_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Scan(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        database_name = self.request.get('database_name',
                                          DEFAULT_DATABASE_NAME)

        content_string = self.request.get('content')
        new_upcs = content_string.split("\r\n")
        
        for upc_string in new_upcs:
            upcs_query = UPC.query(ancestor=database_key(database_name)).filter(UPC.upc_code == upc_string)
            matching_upcs = upcs_query.fetch(None)

            if len(matching_upcs) > 0:
                for matching_upc in matching_upcs:
                    matching_upc.estimated_consumption += 10
                    matching_upc.quantity = int(math.ceil(float(matching_upc.estimated_consumption)/float(matching_upc.pack_size)))
                    matching_upc.put()
        query_params = {'database_name': database_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class BulkAdd(webapp2.RequestHandler):
    def post(self):
        database_name = self.request.get('database_name',
                                          DEFAULT_DATABASE_NAME)

        content_string = self.request.get('content')
        upcs = content_string.split("\r\n")
        for upc_string in upcs:
            data_list = upc_string.split(",")
            if len(data_list) == 4:
                upc = UPC(parent=database_key(database_name))
                upc.upc_code = data_list[0]
                upc.pack_size = 10
                upc.estimated_consumption = 10
                upc.quantity = int(math.ceil(float(upc.estimated_consumption)/float(upc.pack_size)))
                upc.vendor = data_list[3]
                upc.name = data_list[1]
                upc.image_url = data_list[2]
                upc.put()
        self.redirect('/')

class Update(webapp2.RequestHandler):
    def post(self):
        database_name = self.request.get('database_name', DEFAULT_DATABASE_NAME)
        upc_string = self.request.get('upc')
        quantity = int(self.request.get('quantity'))
        pack_size = int(self.request.get('pack_size'))
        upcs_query = UPC.query(ancestor=database_key(database_name)).filter(UPC.upc_code == upc_string)
        upcs = upcs_query.fetch(None)
        for upc in upcs:
            if upc.quantity != quantity and upc.pack_size != pack_size:
                upc.quantity = quantity
                upc.pack_size = pack_size
                upc.estimated_consumption = upc.quantity * upc.pack_size
            elif upc.quantity != quantity:
                upc.quantity = quantity
                upc.estimated_consumption = upc.quantity * upc.pack_size
            elif upc.pack_size != pack_size:
                upc.pack_size = pack_size
                upc.quantity = int(math.ceil(float(upc.estimated_consumption)/float(upc.pack_size)))
            upc.put()
        self.redirect('/')

class Delete(webapp2.RequestHandler):
    def post(self):
        database_name = self.request.get('database_name',
                                          DEFAULT_DATABASE_NAME)
        upc_string = self.request.get('upc')
        upcs_query = UPC.query(ancestor=database_key(database_name)).filter(UPC.upc_code == upc_string)
        upcs = upcs_query.fetch(None)
        for upc in upcs:
            upc.key.delete()
        self.redirect('/')

class DeleteAll(webapp2.RequestHandler):
    def post(self):
        database_name = self.request.get('database_name',
                                          DEFAULT_DATABASE_NAME)
        upcs_query = UPC.query(ancestor=database_key(database_name));
        upcs = upcs_query.fetch(None)
        for upc in upcs:
            upc.key.delete()
        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/scan', Scan),
    ('/update', Update),
    ('/delete', Delete),
    ('/bulk_add', BulkAdd),
    ('/delete_all', DeleteAll),
], debug=True)
