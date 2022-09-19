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


@app.route('/students/', methods=['GET'])
@app.route('/students/search', methods=['GET'])
def students_view():
    context = {'form': 'search'}
    args = request.args
    filters = {'first_name': '',
               'last_name': '',
               'group_id': ''
               }
    if args:
        filters['first_name'] = args.get('first_name')
        filters['last_name'] = args.get('last_name')
        filters['group_id'] = args.get('group_id')
    for k in list(filters.keys()):
        if filters[k] == '':
            del filters[k]
    query = db.session.query(Student)\
        .filter_by(**filters)\
        .order_by(Student.student_id)
    results_list = [(r.student_id, r.first_name, r.last_name, r.group_id)
                    for r in query.all()]
    if results_list:
        context['search_results'] = results_list
    else:
        context['search_results'] = 0
    return render_template('students.html', context=context)


@app.route('/students/add/', methods=['GET', 'POST'])
def students_add():
    context = {'form': 'add'}
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


@app.route('/students/update/<int:student_id>', methods=['GET', 'POST'])
def students_update(student_id):
    context = {'form': 'update'}
    if request.method == 'POST':
        print(request.form.get('first_name'))
        student_upd = Student.query.get(student_id)
        student_upd.first_name = request.form.get('first_name')
        student_upd.last_name = request.form.get('last_name')
        student_upd.group_id = request.form.get('group_id')
        db.session.commit()
        flash(f'Student info updated!')
        return redirect(url_for('students_view'))
    elif request.method == 'POST':
        stmt = select(Student).where(Student.student_id == student_id)
        result = db.session.execute(stmt)
        student = result.scalars().all()[0]
        context['student'] = student
        return render_template('students.html', context=context)


@app.route('/students/delete/<int:student_id>', methods=['GET', 'POST'])
def students_delete(student_id):
    context = {'form': 'delete'}
    if request.method == 'POST':
        student_to_del = db.session.query(Student). \
            filter(Student.student_id == student_id).first()
        db.session.delete(student_to_del)
        db.session.commit()
        flash(f'Student deleted!')
        return redirect(url_for('students_view'))
    elif request.method == 'GET':
        stmt = select(Student).where(Student.student_id == student_id)
        result = db.session.execute(stmt)
        student = result.scalars().all()[0]
        context['student'] = student
        return render_template('students.html', context=context)


@app.route('/courses', methods=['GET'])
@app.route('/courses/search', methods=['GET'])
def courses_view():
    context = {'form': 'search'}
    filters = {'course_name': '',
               'description': ''
               }
    args = request.args
    if args:
        filters['course_name'] = args.get('course_name')
        filters['description'] = args.get('description')
    for k in list(filters.keys()):
        if filters[k] == '':
            del filters[k]
    query = db.session.query(Course)\
        .filter_by(**filters)\
        .order_by(Course.course_name)
    results_list = [(r.course_name, r.description) for r in query.all()]
    if results_list:
        context['search_results'] = results_list
    else:
        context['search_results'] = 0
    return render_template('courses.html', context=context)


@app.route('/courses/add', methods=['GET', 'POST'])
def courses_add():
    context = {'form': 'add'}
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        description = request.form.get('description')
        new_course = Course(course_name=course_name, description=description)
        db.session.add(new_course)
        db.session.commit()
        flash(f'Course {course_name} added!')
    return render_template('courses.html', context=context)


@app.route('/courses/update/<course_name>', methods=['GET', 'POST'])
def courses_update(course_name):
    context = {'form': 'update'}
    if request.method == 'POST':
        course_upd = Course.query.get(course_name)
        course_upd.course_name = request.form.get('course_name')
        course_upd.description = request.form.get('description')
        db.session.commit()
        flash(f'Course info updated!')
        return redirect(url_for('courses_view'))
    elif request.method == 'GET':
        stmt = select(Course).where(Course.course_name == course_name)
        result = db.session.execute(stmt)
        course = result.scalars().all()[0]
        context['course'] = course
        return render_template('courses.html', context=context)


@app.route('/courses/delete/<course_name>', methods=['GET', 'POST'])
def courses_delete(course_name):
    context = {'form': 'delete'}
    if request.method == 'POST':
        course_to_del = db.session.query(Course). \
            filter(Course.course_name == course_name).first()
        db.session.delete(course_to_del)
        db.session.commit()
        flash(f'Course deleted!')
        return redirect(url_for('courses_view'))
    elif request.method == 'GET':
        stmt = select(Course).where(Course.course_name == course_name)
        result = db.session.execute(stmt)
        course = result.scalars().all()[0]
        context['course'] = course
        return render_template('courses.html', context=context)


@app.route('/groups', methods=['GET'])
@app.route('/groups/search', methods=['GET'])
def groups_view():
    context = {'form': 'search'}
    filters = {'group_name': ''}
    args = request.args
    if args:
        filters['group_name'] = args.get('group_name')
    for k in list(filters.keys()):
        if filters[k] == '':
            del filters[k]
    query = db.session.query(Group)\
        .filter_by(**filters)\
        .order_by(Group.group_name)
    results_list = [r.group_name for r in query.all()]
    if results_list:
        context['search_results'] = results_list
    else:
        context['search_results'] = 0
    return render_template('groups.html', context=context)


@app.route('/groups/add/', methods=['GET', 'POST'])
def groups_add():
    context = {'form': 'add'}
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        print(group_name)
        new_group = Group(group_name=group_name)
        db.session.add(new_group)
        db.session.commit()
        flash(f'Course {group_name} added!')
    return render_template('groups.html', context=context)


@app.route('/groups/update/<group_name>', methods=['GET', 'POST'])
def groups_update(group_name):
    context = {'form': 'update'}
    if request.method == 'POST':
        group_upd = Group.query.get(group_name)
        group_upd.group_name = request.form.get('group_name')
        db.session.commit()
        flash(f'Group info updated!')
        return redirect(url_for('groups_view'))
    elif request.method == 'GET':
        stmt = select(Group).where(Group.group_name == group_name)
        result = db.session.execute(stmt)
        group = result.scalars().all()[0]
        context['group'] = group
        return render_template('groups.html', context=context)


@app.route('/groups/delete/<group_name>', methods=['GET', 'POST'])
def groups_delete(group_name):
    context = {'form': 'delete'}
    if request.method == 'POST':
        group_to_del = db.session.query(Group). \
            filter(Group.group_name == group_name).first()
        db.session.delete(group_to_del)
        db.session.commit()
        flash(f'Group deleted!')
        return redirect(url_for('groups_view'))
    elif request.method == 'GET':
        stmt = select(Group).where(Group.group_name == group_name)
        result = db.session.execute(stmt)
        group = result.scalars().all()[0]
        context['group'] = group
        return render_template('groups.html', context=context)


if __name__ == '__main__':
    app.run(debug=True)
