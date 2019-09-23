from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Grades'
settings.subtitle = 'a platform for easy submission of peer grades'
settings.author = 'Ian W. Scott'
settings.author_email = 'scottianw@gmail.com'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '16b6e808-9a53-40ad-a113-e30b5b4cf0c3'
settings.email_server = 'localhost'
settings.email_sender = 'scottianw@gmail.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
