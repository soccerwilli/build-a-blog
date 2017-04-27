#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, os, cgi, jinja2, re

from google.appengine.ext import db

# set up jinja environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app. The other handlers inherit form this one. """
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    """ Handles requests coming in to '/' (the root of our site) """

    def render_front(self, subject = "", content = "", error = ""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("main-blog.html", subject = subject, content = content, error = error, posts = posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    """ Handles requests coming in to '/newpost' """

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            c = Post(subject = subject, content = content)
            c.put()
            self.redirect('/')
        else:
            error = "We need both a subject and some content!"
            self.render_front(subject, content, error)
            #self.redirect('/newpost', error)


app = webapp2.WSGIApplication([('/', MainPage),
                               #('/blog', MainPage),
                               #('/newpost', MainPage)
                               ], debug = True)
