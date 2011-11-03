# -*- coding: utf-8 -*-
from gluon import * 
import datetime

### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
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
    form = crud.create(db.grades)
    return dict(form = form)

@auth.requires_membership(role='administrators')
def grades_report():
    student_list = db(db.auth_user.id > 0).select()
    students = {}
    for s in student_list:
        sindex = s.id
        slast = s.last_name
        sfirst = s.first_name
        students[sindex] = slast + ', ' + sfirst
    u = request.args[0]
    n = db.auth_user[u]
    student = n.last_name + ', ' + n.first_name
    gradelist = db(db.grades.name == u).select()
    session.debug = request.args[0]
    g = {}
    for r in gradelist:
        the_date = r.class_date
        c = db(db.courses.id == r.course).select().first()
        the_course = c.course_name
        if the_course in g:
            dates = g[the_course]
            if the_date in dates:
                dates[the_date].append(r.grade)
            else:
                dates[the_date] = [r.grade]                
        else:
            l = [r.grade]
            the_date = r.class_date
            g[r.course] = dict(the_date = l)
    return dict(grades = g, students = students, student = student)                