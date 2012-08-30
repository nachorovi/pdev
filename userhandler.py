#!/usr/bin/env python
#
# Copyright 2012 Perzo Inc.
#
# Insert Perzo Inc. Copyright notice here. - TBD
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

# Python imports
import logging
import cgi
import datetime
import urllib
import webapp2
import hashlib

# Google App Engine imports
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.db import Key
from google.appengine.ext.db import polymodel

#
# Primary data model of an individual Perzo User - This is the basic user profile for 
# login verification and other typical logged in activities.
# All other profile, stream, filestore dbs are linked here via datastore keys
#
class PerzoUser(db.Model):
  # Models an individual Perzo User - This is the primary user profile for login verification
  # All other profile, stream, filestore dbs are linked here via datastore keys
  index = db.IntegerProperty()				# Unique Integer ID for each User
  email = db.StringProperty()				# Email for Signing in to Perzo
  gemail = db.UserProperty()				# Google User ID (gmail)
  firstname = db.StringProperty()			# User's proper first name(s)
  lastname = db.StringProperty()			# User's proper family name
  nickname = db.StringProperty()			# Screen name for the user
  password = db.StringProperty()			# Password for signing into Perzo
  status = db.StringProperty()				# User status (set by user)
  state = db.StringProperty()				# User state (set by Robbie: home, traveling, etc.)
  photo = db.BlobProperty()					# Quick access thumbnail photo
  mobile = db.PhoneNumberProperty()			# Mobile number required for Perzo use
  homeaddress = db.PostalAddressProperty()
  workaddress = db.PostalAddressProperty()
  shipaddress = db.PostalAddressProperty()
  currentloc = db.GeoPtProperty()
  homeloc = db.GeoPtProperty()
  workloc = db.GeoPtProperty()
  userextras = db.Key()						# Pointer to extended user data base
  robbie = db.Key()							# Pointer to Robbie data bases
  profilephotos = db.Key()					# Pointer to profile photo list
  streams = db.Key()						# Pointer to streams
  files = db.Key()							# Pointer to Perzo file store
  signals = db.Key()						# Pointer to signal filters
  contacts = db.Key							# Pointer to user contacts
  signinlog = db.Key()						# Pointer to Perzo signin history (IP, date)
  googleplussignin = db.BooleanProperty()
  googleplus = db.Key()
  facebooksignin = db.BooleanProperty()
  facebook = db.Key()
  twitterplussignin = db.BooleanProperty()
  twitter = db.Key()
  linkedinsignin = db.BooleanProperty()
  linkedin = db.Key()
  date = db.DateTimeProperty(auto_now_add=True) # Date & time of account creation
  
def perzouserlist_key(name = 'default'):
    return db.Key.from_path('PerzoUserList', name)

#
# Handler for new user register submit action 
#     expects: 'firstname', 'lastname', 'email', 'password' and 'mobile' from submit action
#     (TBD) options: 'facebook', 'google', 'twitter', 'linkedin' check box login options
#
class UserRegistrationHandler(webapp2.RequestHandler):
    def post(self):
    
        # Grab the required elements from the request form:
        email = cgi.escape(self.request.get('email'))
        password = cgi.escape(self.request.get('password'))
        firstname = cgi.escape(self.request.get('firstname'))
        lastname = cgi.escape(self.request.get('lastname'))
        mobile = cgi.escape(self.request.get('mobile'))
        
        #
        # Debug printouts for basic sanity checking;
        #
        self.response.out.write('<html><body>M.H.0.0.30: UserRegistrationHandler.get: ')
        
        self.response.out.write(' Given name: ')
        if email:
            self.response.out.write(firstname)
        else:
            self.response.write('balnk')
        
        self.response.out.write(', Family name: ')
        if email:
            self.response.out.write(lastname)
        else:
            self.response.write('blank')
        
        self.response.out.write(', Mobile number: ')
        if email:
            self.response.out.write(mobile)
        else:
            self.response.write('blank')
        
        self.response.out.write(', Email: ')
        if email:
            self.response.out.write(email)
        else:
            self.response.write('blank')
        
        self.response.out.write(', Password: ')
        if password:
            self.response.out.write(password)
        else:
            self.response.write('blank')
		

        newuser = PerzoUser(parent=perzouserlist_key('default'))
        
        # Perform any sanity checking on the provided values (TBD)
        # Check for any blank fields - they will causes problems later (TBD)
        # Normalize phone numbers and capitalization of names (TBD)
        
        
        # Check the passed in email and mobile number for duplicates in the user data base
        #
        # For now walk through the entire data base and check for either a duplicate email
        # or a duplicate mobile number. If either duplicate is found return to the register
        # new user screen with an error message.
        #
        # (TBD) - Create a hash table of all registered email addresses to speed this up
        # (TBD) - Create a hash table of all mobile numbers to speed this up
        # (TBD) - Create email and mobile fast validation methods that the front end can call
        #         once the user has completed each field (email and mobile)
        #
        # First, send the machine searching for our given email address                  
        existingusers = db.GqlQuery("SELECT * "
                            "FROM PerzoUser "
                            "WHERE email = :1 "
                            "LIMIT 1",
                            email)
        
        for returneduser in existingusers:
            # If we found a matching email log it and return to the registration page
            if returneduser.email:
                self.response.out.write('<p>Email exists: %s ' % returneduser.email)
                self.response.out.write('%s ' % cgi.escape(returneduser.firstname))
                self.response.out.write('%s ' % cgi.escape(returneduser.lastname))
                self.response.out.write('%s ' % cgi.escape(returneduser.password))
                self.response.out.write('%s ' % cgi.escape(returneduser.mobile))
                self.response.out.write(' Rejecting registraation request</p>')
                # We need for self redirect to the registration error page here
                # For now, just print and abort (TBD)
                return
                
        # Second, send the machine searching for our given mobile phone number                  
        existingusers = db.GqlQuery("SELECT * "
                            "FROM PerzoUser "
                            "WHERE mobile = :1 "
                            "LIMIT 1",
                            mobile)
        
        for returneduser in existingusers:
            # If we found a matching email log it and return to the registration page
            if returneduser.email:
                self.response.out.write('<p>Mobile number exists: %s ' % returneduser.mobile)
                self.response.out.write('%s ' % cgi.escape(returneduser.email))
                self.response.out.write('%s ' % cgi.escape(returneduser.firstname))
                self.response.out.write('%s ' % cgi.escape(returneduser.lastname))
                self.response.out.write('%s ' % cgi.escape(returneduser.password))
                self.response.out.write(' Rejecting registration request</p>')
                # We need for self redirect to the registration error page here
                # For now, just print and abort (TBD)
                return
                
        #
        # Ok, if we get here everything looks good - create a new user pending email and/or SMS validation
        #
        self.response.out.write(' Adding new user to the data base ')
        newuser.email = email
        newuser.password = password
        newuser.firstname = firstname
        newuser.lastname = lastname
        newuser.mobile = mobile
        newuser.put()
              
    def put(self):
        self.response.out.write('UserRegistrationHandler.put:')

#
# Handler for login submit action 
#     expects: 'email' and 'password' from submit action
#     options: 'rem_me' check box to drop a cookie
#
#     (TBD) Supports optional two stage login verification (SMS code to your mobile)
#
class UserLoginHandler(webapp2.RequestHandler):
    def post(self):
        email = cgi.escape(self.request.get('email'))
        password = cgi.escape(self.request.get('password'))
        rem_me = cgi.escape(self.request.get('rem_me'))
        self.response.out.write('<html><body>Ver M.H.0.0.14: UserLoginHandler.get method!')
        self.response.out.write(' Email: ')
        if email:
            self.response.out.write(email)
        else:
            self.response.write('blank')
        self.response.out.write(' Password: ')
        if password:
            self.response.out.write(password)
        else:
            self.response.write('blank')
        
        if email and password:
            existingusers = db.GqlQuery("SELECT * "
                            "FROM PerzoUser "
                            "WHERE email = :1 "
                            "LIMIT 1",
                            email)
            
            for existinguser in existingusers:
                if existinguser.password == password:
                    self.response.write(' Successful login to Perzo!')
                else:
                    self.response.write(' Invalid email and password combination')
            
        else:
            self.response.write(' Missing email and/or password')
            return


        
    def put(self):
        self.response.out.write('Hello from UserLoginHandler.put method!')
        
#
# Utility Function to test the passed in email for existence in the Perzo User data base
#     expects: email
#     options: none
#
#     Returns to login screen with "error state" on duplicate - we can use this to prompt
#     the user that she may already be registered.
#
class UserEmailExists(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<p>Entered User Email Exists</p>')
        return

#
# Debugging and Test Function to print the entire Perzo User data base (Perzouser)
#     expects: nothing
#     options: none
#
#     (TBD) Delete from operational code - we'll write this in an admin program
#
class UserdbDump(webapp2.RequestHandler):
    def get(self):
        users = db.GqlQuery("SELECT * "
                            "FROM PerzoUser "
                            "WHERE ANCESTOR IS :1 "
                            "ORDER BY date DESC ",
                            perzouserlist_key('default'))
        for user in users:
            self.response.out.write('<p>%s ' % user.email)
            self.response.out.write('%s ' % cgi.escape(user.firstname))
            self.response.out.write('%s ' % cgi.escape(user.lastname))
            self.response.out.write('%s ' % cgi.escape(user.password))
            self.response.out.write('%s </p>' % cgi.escape(user.mobile))
        
        return
        
#
# Debugging and Test Function to delete the most recent entry in the Perzo User data base (PerzoUser)
#     expects: nothing
#     options: none
#
#     (TBD) Delete from operational code - we'll write this in an admin program
#
#     WARNING - THIS OPERATES WITHOUT A WARNING AND THE RESULTS ARE FINAL (TERMINAL)
#
class UserdbDeleteLastEntry(webapp2.RequestHandler):
    def get(self):
        users = db.GqlQuery("SELECT * "
                            "FROM PerzoUser "
                            "WHERE ANCESTOR IS :1 "
                            "ORDER BY date DESC LIMIT 1",
                            perzouserlist_key('default'))
                            
        for user in users:
            self.response.out.write('<p>Deleting %s ' % user.email)
            self.response.out.write('%s ' % cgi.escape(user.firstname))
            self.response.out.write('%s ' % cgi.escape(user.lastname))
            self.response.out.write('%s ' % cgi.escape(user.password))
            self.response.out.write('%s </p>' % cgi.escape(user.mobile))
            db.delete(user)
        
        return
        
#
# Debugging and Test Function to populate some entries into the Perzo User data base (PerzoUser)
#     expects: nothing
#     options: none
#
#     (TBD) Delete from operational code - we'll write this in an admin program
#
#     WARNING - THIS OPERATES WITHOUT A WARNING AND THE RESULTS ARE FINAL (TERMINAL)
#
class UserdbPopulate(webapp2.RequestHandler):
    def get(self):
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Test",lastname="Test",email="test@perzo.com",password="test",mobile='111-222-3333')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="George",lastname="Washington",email="george@perzo.com",password="test",mobile='000-0000-0001')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="John",lastname="Adams",email="john@perzo.com",password="test",mobile='000-0000-0002')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Thomas",lastname="Jefferson",email="thomas@perzo.com",password="test",mobile='000-0000-0003')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James",lastname="Madison",email="james@perzo.com",password="test",mobile='000-0000-0004')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James",lastname="Monroe",email="jamesm@perzo.com",password="test",mobile='000-0000-0005')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="John Q",lastname="Adams",email="johnq@perzo.com",password="test",mobile='000-0000-0006')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Andrew",lastname="Jackson",email="andrew@perzo.com",password="test",mobile='000-0000-0007')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Martin",lastname="Van Buren",email="martin@perzo.com",password="test",mobile='000-0000-0008')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="William Henry",lastname="Harrison",email="william@perzo.com",password="test",mobile='000-0009-0009')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="John",lastname="Tyler",email="johnt@perzo.com",password="test",mobile='000-0000-0010')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James Knox",lastname="Polk",email="jamesp@perzo.com",password="test",mobile='000-0000-0011')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Zachary",lastname="Taylor",email="zachary@perzo.com",password="test",mobile='000-0000-0012')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Millard",lastname="Fillmore",email="millard@perzo.com",password="test",mobile='000-0000-0013')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Franklin",lastname="Pierce",email="franklin@perzo.com",password="test",mobile='000-0000-0014')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James",lastname="Buchanan",email="jamesb@perzo.com",password="test",mobile='000-0000-0015')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Abraham",lastname="Lincoln",email="abraham@perzo.com",password="test",mobile='000-0000-0016')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Andrew",lastname="Johnson",email="andrewj@perzo.com",password="test",mobile='000-0000-0017')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Ulysses",lastname="Grant",email="ulysses@perzo.com",password="test",mobile='000-0000-0018')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Rutherford Birchard",lastname="Hayes",email="rutherford@perzo.com",password="test",mobile='000-0000-0019')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James Abram",lastname="Garfield",email="jamesg@perzo.com",password="test",mobile='000-0000-0020')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Chester Alan",lastname="Arthur",email="chester@perzo.com",password="test",mobile='000-0000-0021')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Grover",lastname="Cleveland",email="grover@perzo.com",password="test",mobile='000-0000-0022')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Benjamin",lastname="Harrison",email="benjamin@perzo.com",password="test",mobile='000-0000-0023')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Grover",lastname="Cleveland",email="grover2@perzo.com",password="test",mobile='000-0000-0024')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="William",lastname="McKinley",email="williamm@perzo.com",password="test",mobile='000-0000-0025')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Theodore",lastname="Roosevelt",email="theodore@perzo.com",password="test",mobile='000-0000-0026')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="William Howard",lastname="Taft",email="willaimt@perzo.com",password="test",mobile='000-0000-0027')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Woodrow",lastname="Wilson",email="woodrow@perzo.com",password="test",mobile='000-0000-0028')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Warren Gamaliel",lastname="Harding",email="warren@perzo.com",password="test",mobile='000-0000-0029')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Calvin",lastname="Coolidge",email="calvin@perzo.com",password="test",mobile='000-0000-0030')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Herbert Clark",lastname="Hoover",email="herbert@perzo.com",password="test",mobile='000-0000-0031')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Franklin Delano",lastname="Roosevelt",email="franklind@perzo.com",password="test",mobile='000-0000-0032')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Harry S",lastname="Truman",email="calvin@perzo.com",password="test",mobile='000-0000-0033')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Dwight David",lastname="Eisenhower",email="dwight@perzo.com",password="test",mobile='000-0000-0034')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="John Fitzgerald",lastname="Kennedy",email="johnf@perzo.com",password="test",mobile='000-0000-0035')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Lyndon Baines",lastname="Johnson",email="lyndon@perzo.com",password="test",mobile='000-0000-0036')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Richard Milhous",lastname="Nixon",email="calvin@perzo.com",password="test",mobile='000-0000-0037')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Gerald Rudolph",lastname="Ford Jr",email="gerald@perzo.com",password="test",mobile='000-0000-0038')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="James Earl",lastname="Carter",email="jamese@perzo.com",password="test",mobile='000-0000-0039')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Ronald Willson",lastname="Reagan",email="ronald@perzo.com",password="test",mobile='000-0000-0040')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="George Herbert Walker",lastname="Bush",email="georgeh@perzo.com",password="test",mobile='000-0000-0041')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="William Jefferson",lastname="Clinton",email="williamj@perzo.com",password="test",mobile='000-0000-0042')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="George W",lastname="Bush",email="georgew@perzo.com",password="test",mobile='000-0000-0043')
        newuser.put()
        newuser = PerzoUser(parent=perzouserlist_key('default'),firstname="Barak",lastname="Obama",email="barak@perzo.com",password="test",mobile='000-0000-0044')
        newuser.put()
    
    
#
# The basic webapp2 / WSGI routing table:
#
app = webapp2.WSGIApplication([
    ('/userloginhandler', UserLoginHandler),
    ('/useremailexists', UserEmailExists),
    ('/userregistrationhandler', UserRegistrationHandler),
    ('/userdbpopulate', UserdbPopulate),
    ('/userdbdump', UserdbDump),
    ('/userdbdeletelast', UserdbDeleteLastEntry)], debug=True)
