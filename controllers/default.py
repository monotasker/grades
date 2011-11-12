# -*- coding: utf-8 -*-
if 0:
    from gluon import current, SQLFORM, redirect, A, URL, IS_IN_DB
    from gluon.tools import Auth, Crud
    from gluon.dal import DAL
    db = DAL()
    auth = Auth()
    response = current.response
    service = current.service
    request = current.request
    session = current.session
    crud = Crud()
    
import datetime

### required - do no delete
def user(): 
    courses = db(db.courses.id > 0).select()
    courselist = []
    for c in courses:
        try:
            gradelist = db((db.grades.name == auth.user_id) & (db.grades.course == c.id)).select()
            s=db.grades.grade.sum()
            row = db(db.grades.name == auth.user_id).select(s).first()
            av = row[s]
            avg = round(av/len(gradelist))           
            curve = c.curve
            if curve == None:
                curve = 0
            avg += curve
            
            this_c = {c.course_name:avg}
            courselist.append(this_c)
        except:
            pass
            
    return dict(form=auth(), courselist = courselist)

def download(): return response.download(request,db)

def call(): return service()
### end required

def index():
    courses = db(db.courses.id > 0).select()
    return dict(courses = courses)

def error():
    return dict()

@auth.requires_membership(role='administrators')
def grades_manage():
    form = SQLFORM.smartgrid(db.grades,onupdate=auth.archive)
    return locals()

@auth.requires_membership(role='administrators')
def classes_manage():
    form = SQLFORM.smartgrid(db.courses,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def create_grade():
    """
    TODO: Make sure these fields are all required. 
    TODO: Restrict names in drop-down to students in current course
    TODO: Remove logged-in student from name drop-down
    """
    c = ''
    if request.args:
        c = db.courses[request.args[0]]
    else:
        redirect(URL('index'))
    cname = c.course_name
    cnum = c.id
    m = str(c.max_score)
    if m == 'None':
        m = '4'
    form = SQLFORM(
        db.grades, separator='', 
        fields=['name', 'grade', 'class_date'], 
        labels={'name':"student's name", 'grade':"grade", 'class_date':'class date'}, 
        col3={'name':'The student to receive the grade.', 'grade':'a number out of '+m, 'class_date':"the date when the class took place"},
        submit_button = 'assign this grade'
        )
    form.vars.course = cnum 
    db.grades.name.requires=IS_IN_DB(db(db.grades.course == request.args[0]), 'grades.name', '%(name)s' ) 
    if form.process().accepted:
        response.flash = 'Thanks! The grade was recorded.'
    the_user = db(db.auth_user.id == auth.user_id).select().first()
    fn = the_user.first_name
    cancel_button = A('cancel', _href=URL('index'), _class='cancel')
    return dict(form = form, cancel_button = cancel_button, fn = fn, cname = cname)

@auth.requires_membership(role='administrators')
def grades_report():
    student_list = db(db.auth_user.id > 0).select()
    students = {}
    for s in student_list:
        sindex = s.id
        slast = s.last_name
        sfirst = s.first_name
        students[sindex] = slast + ', ' + sfirst
    
    courses = db(db.courses.id > 0).select()
    d = {}
    for c in courses:
        cn = c.course_name
        l = []
        for k,s in students.items():
            if db((db.grades.course == c) & (db.grades.name == k)).select():
                l.append({k:s})
        d[cn] = l
    
    return dict(students = students, course_d = d)

def grades_detail():
    u = request.args[0]
    n = db.auth_user[u]
    student = n.last_name + ', ' + n.first_name
    
    courses = db(db.courses.id > 0).select()
    courselist = []
    for c in courses:
        try:
            gradelist = db((db.grades.name == u) & (db.grades.course == c.id)).select()
            s=db.grades.grade.sum()
            row = db(db.grades.name == u).select(s).first()
            av = row[s]
            avg = round((av/len(gradelist)), 3)           
            curve = c.curve
            if curve == None:
                curve = 0
            avg += curve
            
            this_c = {c.course_name:avg}
            courselist.append(this_c)
        except:
            print ''
    
    return dict(courselist = courselist, student=student)
