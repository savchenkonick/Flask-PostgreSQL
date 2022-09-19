from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, select, Column, Integer, Identity, String
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database


app = Flask(__name__)
engine = create_engine("postgresql://postgres:postgres@localhost/school")
if not database_exists(engine.url):
    create_database(engine.url)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/school"
app.config['SECRET_KEY'] = "mykey"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Group(db.Model):
    __tablename__ = 'groups'

    group_name = Column(String(40), primary_key=True)

    def __init__(self, group_name):
        self.group_name = group_name


class Student(db.Model):
    __tablename__ = 'students'
    student_id = Column(Integer, Identity(),  primary_key=True)
    group_id = Column(String(40))
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)

    def __init__(self, group_id, first_name, last_name):
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name


class Course(db.Model):
    __tablename__ = 'courses'

    course_name = Column(String(40), primary_key=True)
    description = Column(String(40))

    def __init__(self, course_name, description):
        self.course_name = course_name
        self.description = description


@app.route('/', methods=['GET'])
def home():
    context = {}
    return render_template('base.html', context=context)


@app.route('/students/', methods=['POST', 'GET'])
@app.route('/students/<cursor>/', methods=['POST', 'GET'])
@app.route('/students/<cursor>/<int:student_id>', methods=['POST', 'GET'])
def students_view(cursor=None, student_id=None):
    context = {}
    if cursor is not None:
        context['form'] = cursor
    if cursor == 'add':
        context['form'] = 'add'
        return students_add(context)
    elif cursor == 'update':
        context['form'] = 'update'
        return students_update(context, student_id)
    elif cursor == 'delete':
        context['form'] = 'delete'
        confirmed_del = False
        if request.method == 'POST':
            confirmed_del = True
        return students_delete(context, student_id, confirmed_del)
    else:
        context['form'] = 'search'

    if request.method == 'GET':
        args = request.args
        if len(args) == 0:
            return render_template('students.html', context=context)
        filters = {'first_name': args.get('first_name'),
                   'last_name': args.get('last_name'),
                   'group_id': args.get('group_id')
                   }
        for k in list(filters.keys()):
            if filters[k] == '':
                del filters[k]
        query = db.session.query(Student).filter_by(**filters)
        results_list = [(r.student_id, r.first_name, r.last_name, r.group_id)
                        for r in query.all()]
        if len(results_list) == 0:
            context['search_results'] = 0
        else:
            context['search_results'] = results_list
    return render_template('students.html', context=context)


def students_add(context):
    if request.method == 'POST':
        f_name = request.form.get('first_name')
        l_name = request.form.get('last_name')
        group_id = request.form.get('group_id')
        new_student = Student(group_id=group_id,
                              first_name=f_name,
                              last_name=l_name)
        db.session.add(new_student)
        db.session.commit()
        flash(f'Student {f_name} {l_name} added!')
    return render_template('students.html', context=context)


def students_update(context, student_id):
    if request.method == 'POST':
        print(request.form.get('first_name'))
        student_upd = Student.query.get(student_id)
        student_upd.first_name = request.form.get('first_name')
        student_upd.last_name = request.form.get('last_name')
        student_upd.group_id = request.form.get('group_id')
        db.session.commit()
        flash(f'Student info updated!')
        return redirect(url_for('students_view'))
    stmt = select(Student).where(Student.student_id == student_id)
    result = db.session.execute(stmt)
    student = result.scalars().all()[0]
    context['student'] = student
    return render_template('students.html', context=context)


def students_delete(context, student_id, confirmed_del):
    if confirmed_del:
        student_to_del = db.session.query(Student). \
            filter(Student.student_id == student_id).first()
        db.session.delete(student_to_del)
        db.session.commit()
        flash(f'Student deleted!')
        return redirect(url_for('students_view'))
    else:
        stmt = select(Student).where(Student.student_id == student_id)
        result = db.session.execute(stmt)
        student = result.scalars().all()[0]
        context['student'] = student
    return render_template('students.html', context=context)


@app.route('/courses', methods=['GET', 'POST'])
@app.route('/courses/<cursor>', methods=['GET', 'POST'])
@app.route('/courses/<cursor>/<course_name>', methods=['GET', 'POST'])
def courses_view(cursor=None, course_name=None):
    context = {}
    if cursor is not None:
        context['form'] = cursor
    if cursor == 'add':
        context['form'] = 'add'
        return courses_add(context)
    elif cursor == 'update':
        context['form'] = 'update'
        return courses_update(context, course_name)
    elif cursor == 'delete':
        context['form'] = 'delete'
        confirmed_del = False
        if request.method == 'POST':
            confirmed_del = True
        return courses_delete(context, course_name, confirmed_del)
    else:
        context['form'] = 'search'

    if request.method == 'GET':
        args = request.args
        if len(args) == 0:
            return render_template('courses.html', context=context)
        filters = {'course_name': args.get('course_name'),
                   'description': args.get('description')
                   }
        for k in list(filters.keys()):
            if filters[k] == '':
                del filters[k]
        query = db.session.query(Course).filter_by(**filters)
        results_list = [(r.course_name, r.description) for r in query.all()]
        if len(results_list) == 0:
            context['search_results'] = 0
        else:
            context['search_results'] = results_list
    return render_template('courses.html', context=context)


def courses_add(context):
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        description = request.form.get('description')
        new_course = Course(course_name=course_name, description=description)
        db.session.add(new_course)
        db.session.commit()
        flash(f'Course {course_name} added!')
    return render_template('courses.html', context=context)


def courses_update(context, course_name):
    if request.method == 'POST':
        course_upd = Course.query.get(course_name)
        course_upd.course_name = request.form.get('course_name')
        course_upd.description = request.form.get('description')
        db.session.commit()
        flash(f'Course info updated!')
        return redirect(url_for('courses_view'))
    stmt = select(Course).where(Course.course_name == course_name)
    result = db.session.execute(stmt)
    course = result.scalars().all()[0]
    context['course'] = course
    return render_template('courses.html', context=context)


def courses_delete(context, course_name, confirmed_del):
    if confirmed_del:
        course_to_del = db.session.query(Course). \
            filter(Course.course_name == course_name).first()
        db.session.delete(course_to_del)
        db.session.commit()
        flash(f'Course deleted!')
        return redirect(url_for('courses_view'))
    else:
        stmt = select(Course).where(Course.course_name == course_name)
        result = db.session.execute(stmt)
        course = result.scalars().all()[0]
        context['course'] = course
    return render_template('courses.html', context=context)


@app.route('/groups', methods=['GET', 'POST'])
@app.route('/groups/<cursor>', methods=['GET', 'POST'])
@app.route('/groups/<cursor>/<group_name>', methods=['GET', 'POST'])
def groups_view(cursor=None, group_name=None):
    context = {}
    if cursor is not None:
        context['form'] = cursor
    if cursor == 'add':
        context['form'] = 'add'
        return groups_add(context)
    elif cursor == 'update':
        context['form'] = 'update'
        return groups_update(context, group_name)
    elif cursor == 'delete':
        context['form'] = 'delete'
        confirmed_del = False
        if request.method == 'POST':
            confirmed_del = True
        return groups_delete(context, group_name, confirmed_del)
    else:
        context['form'] = 'search'

    if request.method == 'GET':
        args = request.args
        if len(args) == 0:
            return render_template('groups.html', context=context)
        filters = {'group_name': args.get('group_name'),
                   }
        for k in list(filters.keys()):
            if filters[k] == '':
                del filters[k]
        query = db.session.query(Group).filter_by(**filters)
        results_list = [(r.group_name) for r in query.all()]
        if len(results_list) == 0:
            context['search_results'] = 0
        else:
            context['search_results'] = results_list
    return render_template('groups.html', context=context)


def groups_add(context):
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        print(group_name)
        new_group = Group(group_name=group_name)
        db.session.add(new_group)
        db.session.commit()
        flash(f'Course {group_name} added!')
    return render_template('groups.html', context=context)


def groups_update(context, group_name):
    if request.method == 'POST':
        group_upd = Group.query.get(group_name)
        group_upd.group_name = request.form.get('group_name')
        db.session.commit()
        flash(f'Group info updated!')
        return redirect(url_for('groups_view'))
    stmt = select(Group).where(Group.group_name == group_name)
    result = db.session.execute(stmt)
    group = result.scalars().all()[0]
    context['group'] = group
    return render_template('groups.html', context=context)


def groups_delete(context, group_name, confirmed_del):
    if confirmed_del:
        group_to_del = db.session.query(Group). \
            filter(Group.group_name == group_name).first()
        db.session.delete(group_to_del)
        db.session.commit()
        flash(f'Group deleted!')
        return redirect(url_for('groups_view'))
    else:
        stmt = select(Group).where(Group.group_name == group_name)
        result = db.session.execute(stmt)
        group = result.scalars().all()[0]
        context['group'] = group
    return render_template('groups.html', context=context)


if __name__ == '__main__':
    app.run(debug=True)
