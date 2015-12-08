# -*- coding: utf-8 -*-
if 0:
    from gluon import current, SQLFORM, redirect, A, URL
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
    courses = db(db.courses.id > 0).select()
    courselist = []
    for c in courses:
        try:
            gradelist = db((db.grades.name == auth.user_id) & (db.grades.course == c.id)).select()
            s = db.grades.grade.sum()
            row = db(db.grades.name == auth.user_id).select(s).first()
            av = row[s]
            avg = round(av/len(gradelist))
            curve = c.curve
            if curve == None:
                curve = 0
            avg += curve

            this_c = {c.course_name: avg}
            courselist.append(this_c)
        except:
            pass

    return dict(form=auth(), courselist=courselist)


def download(): return response.download(request, db)


def call(): return service()
### end required


def index():
    courses = db(db.courses.id > 0).select()
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
    cancel_button = A('cancel', _href=URL('index'), _class='cancel')
    return dict(form=form, cancel_button=cancel_button, fn=fn, cname=cname)


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
