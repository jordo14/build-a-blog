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
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.response.write(self.render_str(template, **kw))
    
class Blog(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", post=""):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("listings.html", title=title, post=post, posts=posts)

    def get(self):
        self.render_front()

class NewPosts(Handler):
    def render_front(self, title="", post="", error=""):

        self.render("posts.html", title=title, post=post, error=error) 
    
    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            b = Blog(title = title, post = post)
            b.put()

            self.redirect("/blog/%s" % b.key().id())
        else: 
            error = "We need both a title and a post!"
            self.render_front(title, post, error)

class ViewPostHandler(Handler): 
    def render_front(self, id, title="", post="", error=""):
        id = int(id)
        posts = Blog.get_by_id(id)
        self.render("onepost.html", title=title, post=post, posts=posts)

    def get(self, id):
        self.render_front(id)
        
            
    

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', NewPosts),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
