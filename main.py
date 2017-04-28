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
import webapp2, os, jinja2
from google.appengine.ext import db


#sets up the jinja environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for the app. The other handlers inherit form this one. """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    """ Represents a blog on the site """

    title = db.StringProperty(required = True)
    blog_post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    """ Handles requests coming in to the root of the site '/' renders the main page '/blog' """

    def render_page(self, title = ""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("main-page.html", title = title, blogs = blogs)

    def get(self):
        self.render_page()

    def post(self):
        title = self.request.get("title")
        blog_post = self.request.get("blog-post")

        if title and blog_post:
            blog = Blog(title = title, blog_post = blog_post)
            blog.put()
            self.redirect("/blog")


class NewPost(Handler):
    """ handles requests coming in to the '/newpost' path and renders a page for submitting a new blog post"""

    def render_page(self, title = "", blog_post = "", error = ""):
        self.render("new-post.html", title = title, blog_post = blog_post, error = error)

    def get(self):
        self.render_page()

    def post(self):
        title = self.request.get("title")
        blog_post = self.request.get("blog-post")

        if title and blog_post:
            blog = Blog(title = title, blog_post = blog_post)
            blog.put()
            self.redirect("/blog")

        else:
            error = "form requires both a title and a blog post"
            self.render_page(title = title, blog_post = blog_post, error = error)


class SinglePost(Handler):
    """ renders a page with a single blog post based on the id of the blog post in the data store 'Blog' """

    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))
        self.render("single-post.html", blog = blog)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog', MainPage),
                               ('/newpost', NewPost),
                               webapp2.Route('/blog/<blog_id:\d+>', SinglePost)
                               ], debug = True)
