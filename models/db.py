# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

db = DAL('sqlite://storage.sqlite')

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
from gluon.tools import Mail, Recaptcha
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()

keydata = {}
with open('applications/grades/private/app.keys', 'r') as keyfile:
    for line in keyfile:
        k, v = line.split()
	keydata[k] = v

## configure email
mail=Mail()
mail.settings.server = keydata['email_sender'] or 'smtp.gmail.com:587'
mail.settings.sender = keydata['email_address']
mail.settings.login = keydata['email_pass']

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

auth.settings.login_captcha = None
auth.settings.register_captcha = Recaptcha(request, keydata['captcha_public_key'], keydata['captcha_private_key'])
auth.settings.retrieve_username_captcha = Recaptcha(request, keydata['captcha_public_key'], keydata['captcha_private_key'])
auth.settings.retrieve_password_captcha = Recaptcha(request, keydata['captcha_public_key'], keydata['captcha_private_key'])
