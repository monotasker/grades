# -*- coding: utf-8 -*-

if 0:
    from gluon import DAL, URL

import logging
from gluon.tools import Auth, Crud, Service, PluginManager
from gluon.tools import Mail, Recaptcha
from gluon.globals import current

request = current.request
response = current.response

if request.is_local:  # disable in production enviroment
    from gluon.custom_import import track_changes
    track_changes(True)

# -------------------------------------------------------------
# get private data from secure file
# -------------------------------------------------------------

keydata = {}
with open('applications/grades/private/app.keys', 'r') as keyfile:
    for myline in keyfile:
        k, v = myline.split()
        keydata[k] = v

# -------------------------------------------------------------
# define database storage
# -------------------------------------------------------------

db = DAL('sqlite://storage.sqlite')

# -------------------------------------------------------------
# Set up logging
# -------------------------------------------------------------
logger = logging.getLogger('web2py.app.paideia')
logger.setLevel(logging.DEBUG)

# -------------------------------------------------------------
# Generic views
# -------------------------------------------------------------

response.generic_patterns = ['*'] if request.is_local else []

# -------------------------------------------------------------
# set up services
# -------------------------------------------------------------
crud = Crud(db)                 # for CRUD helpers using auth
service = Service()             # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()       # for configuring plugins
current.db = db                 # to access db from modules

# -------------------------------------------------------------
# configure authorization
# -------------------------------------------------------------
auth = Auth(db, hmac_key=Auth.get_or_create_key())

# -------------------------------------------------------------
# place auth in current so it can be imported by modules
# -------------------------------------------------------------

current.auth = auth

# -------------------------------------------------------------
# misc auth settings
# -------------------------------------------------------------
auth.settings.create_user_groups = False
auth.settings.label_separator = ''

# create all tables needed by auth if not custom tables
auth.define_tables()
db.auth_user._format = lambda row: '{}, {}: {}'.format(row.last_name,
                                                       row.first_name,
                                                       row.id)

# -------------------------------------------------------------
# Mail config
# -------------------------------------------------------------

mail = Mail()
mail.settings.server = keydata['email_server']  # 'logging' # SMTP server
mail.settings.sender = keydata['email_address']  # email
mail.settings.login = '{}:{}'.format(keydata['email_user'], keydata['email_pass'])  # credentials or None
mail.settings.tls = True
current.mail = mail

auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://' \
    + request.env.http_host + URL('default', 'user', args=['verify_email']) \
    + '/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://' \
    + request.env.http_host + URL('default', 'user', args=['reset_password'])\
    + '/%(key)s to reset your password'


# -------------------------------------------------------------
# enable recaptcha anti-spam for selected actions
# -------------------------------------------------------------

auth.settings.login_captcha = None
auth.settings.register_captcha = Recaptcha(request,
    keydata['captcha_public_key'], keydata['captcha_private_key'])
auth.settings.retrieve_username_captcha = Recaptcha(request,
    keydata['captcha_public_key'], keydata['captcha_private_key'])
auth.settings.retrieve_password_captcha = Recaptcha(request,
    keydata['captcha_public_key'], keydata['captcha_private_key'])

# -------------------------------------------------------------
# crud settings
# -------------------------------------------------------------

crud.settings.auth = auth  # =auth to enforce authorization on crud
