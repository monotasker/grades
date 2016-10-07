# -*- coding: utf-8 -*-

import json
import datetime

if 0:
    from gluon import current, SQLFORM, redirect, URL, IS_IN_DB
    from gluon.tools import Auth, Crud
    from gluon.dal import DAL
    db = DAL()
    auth = Auth()
    response = current.response
    service = current.service
    request = current.request
    session = current.session
    crud = Crud()


### required - do no delete
def user():
    debug = True
    uid = request.vars['user'] if 'user' in request.vars.keys() else auth.user_id
    if debug: print 'profile for user', uid
    courses = db(db.course_membership.name == uid).select()
    if debug: print len(courses), 'courses with membership'
    courselist = []
    for c in courses:
        courserow = db.courses(c.course)
        gradelist = db((db.grades.name == auth.user_id) &
                       (db.grades.course == c.course)).select()
        if len(gradelist) == 0:
            avg = 'no grades assigned yet'
        else:
            s = db.grades.grade.sum()
            row = db(db.grades.name == auth.user_id).select(s).first()
            av = row[s]
            avg = round(av/len(gradelist))
            curve = courserow.curve
            if curve == None:
                curve = 0
            avg += curve

        this_c = {courserow.course_name: avg}
        courselist.append(this_c)

    return dict(form=auth(), courselist=courselist)


def download(): return response.download(request, db)


def call(): return service()
### end required


def index():
    if auth.has_membership('administrators'):
        courses = [{'course_name': c.course_name, 'id': c.id}
                   for c in db(db.courses.id > 0).select()]
    else:
        usr = auth.user_id
        courses_raw = db((db.course_membership.course == db.courses.id) &
                        (db.course_membership.name == usr)).select()
        courses = [{'course_name': c.courses.course_name, 'id': c.courses.id}
                for c in courses_raw]

    return dict(courses=courses)


def error():
    return dict()


@auth.requires_membership(role='administrators')
def grades_manage():
    #get course id passed as first argument of url
    this_course = request.args[0]
    coursename = db(db.courses.id == this_course).select().first().course_name
    #create smartgrid to display all class grades
    form = SQLFORM.smartgrid(db.grades,
                             fields=[db.grades.name,
                                     db.grades.grade,
                                     db.grades.class_date],
                             constraints={'grades': db.grades.course == this_course},
                             onupdate=auth.archive,
                             paginate=300,
                             args=[this_course])
    return locals()


@auth.requires_membership(role='administrators')
def classes_manage():
    form = SQLFORM.smartgrid(db.courses, onupdate=auth.archive)
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
    if m in [None, 'None']:
        m = '10'

    class_members = db(db.course_membership.course == cnum).select()
    member_nums = [member['id'] for member in class_members]
    print 'member_nums', member_nums
    mquery = db(db.auth_user.id.belongs(
                    db(db.course_membership.course == cnum)._select(db.course_membership.name)
                                        ))
    db.grades.name.requires = IS_IN_DB(mquery, 'auth_user.id', '%(last_name)s, %(first_name)s')
    form = SQLFORM(
        db.grades,
        separator='',
        fields=['name', 'grade', 'class_date'],
        labels={'name': "Student's name",
                'grade': "Grade",
                'class_date': 'Class date'},
        col3={'name': 'The student to receive the grade.',
              'grade': 'a number out of {}'.format(m),
              'class_date': "the date when the class took place"},
        submit_button='assign this grade'
        )
    form.vars.course = cnum
    if form.process().accepted:
        response.flash = 'Thanks! The grade was recorded.'

    the_user = db(db.auth_user.id == auth.user_id).select().first()
    fn = the_user.first_name
    return dict(form=form,
                fn=fn,
                cname=cname,
                courseid=cnum)


@auth.requires_membership(role='administrators')
def grades_report():
    classid = request.args[0]
    student_list = db((db.auth_user.id == db.course_membership.name) &
                      (db.course_membership.course == classid)).select()
    students = {s.auth_user.id: '{}, {}'.format(s.auth_user.last_name, s.auth_user.first_name)
                for s in student_list}

    mycourse = db.courses(classid)
    course_name = mycourse.course_name

    return {'students': students,
            'course_name': course_name,
            'course_id': classid}


@auth.requires_login()
def view_grades():
    mycourse = request.args[0]
    coursetitle = db.courses[mycourse]['course_name']
    course_student_list = db((db.auth_user.id == db.course_membership.name) &
                             (db.course_membership.course == mycourse)).select()
    myassigned = db((db.grades.course == mycourse) &
                    (db.grades.submitted_by == auth.user_id)).select()
    assigned_users = list(set([m.name for m in myassigned]))
    assigned_list = []
    for user_id in assigned_users:
        srow = db.auth_user[user_id]
        student_name = srow.last_name + ', ' + srow.first_name
        sgrades = [{'grade': g.grade,
                    'class_date': g.class_date,
                    'submitted_date': g.submitted_date,
                    'record_id': g.id}
                   for g in myassigned.find(lambda r: r.name == user_id)]
        assigned_list.append({'user_id': user_id,
                              'name': student_name,
                              'grades': sgrades})
    return {'assigned_grades': assigned_list,
            'course': mycourse,
            'course_name': coursetitle,
            'uid': auth.user_id}


@auth.requires_login()
def edit_grades():
    newvals = request.vars['newvals']
    newvals = json.loads(newvals)
    newvals = {int(key): float(val) for key, val in newvals.items()}
    changed = {}
    for rowid, val in newvals.items():
        db.grades[rowid] = {'grade': val, 'submitted_date': datetime.datetime.utcnow()}
        changed[rowid] = val
    return str(changed)


def grades_detail():
    mycourse = request.args[0]
    sid = request.args[1]
    srow = db.auth_user[sid]
    student_name = srow.last_name + ', ' + srow.first_name

    sgrades = db((db.grades.course == mycourse) &
                 (db.grades.name == sid)).select()
    grade_dict = {}
    for g in sgrades:
        if g.class_date in grade_dict.keys():
            grade_dict[g.class_date].append((g.grade, g.id))
        else:
            grade_dict[g.class_date] = [(g.grade, g.id)]

    allgrades = [sg.grade for sg in sgrades]
    gradesum = sum(allgrades)
    avg = round((gradesum/len(allgrades)), 3)
    curve = db.courses[mycourse].curve
    if curve == None:
        curve = 0
    avg += curve

    return {'student_name': student_name,
            'grade_dict': grade_dict,
            'avg': avg}
