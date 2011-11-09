#for PyDev recognition
if 0:
    from gluon import current
    from gluon.tools import Auth
    from gluon.dal import DAL, Field
    db = DAL()
    auth = Auth()
    request = current.request
    T = current.t
    
########################################
db.define_table('courses',
    Field('course_name', type='string'),
    Field('max_score', type='double', default=4.0),
    Field('curve', type='double', default=0),
    format='%(course_name)s')

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
