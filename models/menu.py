response.title = "Peergrades"
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Home'), URL('default','index'), URL('default','index'), []),
]
m = response.menu

if auth.has_membership('administrators', auth.user_id) or auth.is_impersonating():
    m += [(T('Admin'), False, None, [(T('Manage classes'),
                                      URL('default','classes_manage'),
                                      URL('default','classes_manage'), []),
                                     (T('Database'),
                                      URL('appadmin'),
                                      URL('appadmin'), [])
                                      ]
           )]

