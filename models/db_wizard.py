#for PyDev recognition
from gluon import *
request,session,response,T,cache=current.request,current.session,current.response,current.T,current.cache

########################################
db.define_table('courses',
    Field('course_name', type='string',
          label=T('Course Name')),
    auth.signature,
    format='%(course_name)s',
    migrate=settings.migrate)

########################################
db.define_table('grades',
    Field('name', db.auth_user, default=auth.user_id),
    Field('grade', type='double'),
    Field('course', db.courses),          
    Field('class_date', type='date'),
    Field('submitted_date', type='date', default=request.now),
    format='%(f_name)s')

db.define_table('grades_archive',db.grades,Field('current_record','reference grades',readable=False,writable=False))

db.define_table('courses_archive',db.courses,Field('current_record','reference courses',readable=False,writable=False))
