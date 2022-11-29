"""REST API for Web App that provides access to school PostgreSQL DB.
This API intended to give access via GET, POST, PUT, DELETE JSON requests using
sqlalchemy and flask rest framework.
Call this api passing a version of api and "students" or "courses" table.
    Example:
        /api/v1/students/
        /api/v1/students/420/
        where 420 is student_id
        or
        /api/v1/courses/
        /api/v1/courses/med/
        where "med" is course_name

    To extract OpenAPI-Specification go to:
    apidocs/

    Classes:
        Students:
            Handles GET, POST, PUT, DELETE request for students table
        Courses:
            Handles GET, POST, PUT, DELETE request for courses table
"""

from flask import jsonify, make_response
from flask_restful import Resource, Api, abort
from flasgger import Swagger
from app import Student, Course, app, db, request

api = Api(app)
swagger = Swagger(app)


class Students(Resource):

    def get(self, api_version, student_id=None):
        """REST API for Web App that provides access to school PostgreSQL DB.
        This API intended to give access via GET, POST, PUT, DELETE JSON
        requests using sqlalchemy and flask rest framework.
        Call this api passing a version of api and "students"
        Example:
            /api/v1/students/
            /api/v1/students/420/
            where 420 is student_id
        ---

        tags:
          - API for accessing data about students
        parameters:
          - name: api_version
            in: path
            type: string
            required: true
            description: Version of API. Current v1
          - name: table name
            in: path
            type: string
            required: true
          - name: student id
            in: query
            type: int
            required: false
            description: student_id in students table
        produces:
          - application/json
        responses:
          404:
            description: wrong api or id
          200:
            description: requested data in JSON format"""

        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        if student_id:
            student = Student.query.get(student_id)
            # student = Student.query.all()
            if not student:
                abort(404, message=f"Student with id={student_id} not found")
            results = {"student_id": student.student_id,
                       "first_name": student.first_name,
                       "last_name": student.last_name,
                       "group_id": student.group_id}
        else:  # No student_id provided
            students = Student.query.all()
            if not students:
                abort(404, message=f"Student with id={student_id} not found")
            results = []
            for student in students:
                results.append({"student_id": student.student_id,
                                "first_name": student.first_name,
                                "last_name": student.last_name,
                                "group_id": student.group_id})
        # elif request.get_json():
        #     results = []
        #     json_data = request.get_json()
        #     print(type(json_data))
        #     if type(json_data) is dict:
        #         query = db.session.query(Student). \
        #             filter_by(**json_data). \
        #             order_by(Student.student_id)
        #         for r in query.all():
        #             results.append({"student_id": r.student_id,
        #                             "first_name": r.first_name,
        #                             "last_name": r.last_name,
        #                             "group_id": r.group_id})
        #     elif type(json_data) is list:
        #         for filters in json_data:
        #             query = db.session.query(Student). \
        #                 filter_by(**filters). \
        #                 order_by(Student.student_id)
        #             for r in query.all():
        #                 results.append({"student_id": r.student_id,
        #                                 "first_name": r.first_name,
        #                                 "last_name": r.last_name,
        #                                 "group_id": r.group_id})
        #     else:
        #         # Json is empty. Querying all students
        #         query = db.session.query(Student).order_by(Student.student_id)
        #         results = [{"student_id": student.student_id,
        #                     "first_name": student.first_name,
        #                     "last_name": student.last_name,
        #                     "group_id": student.group_id}
        #                    for student in query.all()]
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def post(self, api_version, student_id=None):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        json_data = request.get_json()
        results = {}
        if student_id:  # if json has info about only one student
            if Student.query.get(student_id):
                abort(404, message=f'student_id is already exists')
            new_student = Student(student_id=student_id,
                                  group_id=json_data['group_id'],
                                  first_name=json_data['first_name'],
                                  last_name=json_data['last_name'])
            db.session.add(new_student)
            db.session.commit()
            results['message'] = 'Student added successfully'
        elif type(json_data) is dict:
            new_student = Student(group_id=json_data['group_id'],
                                  first_name=json_data['first_name'],
                                  last_name=json_data['last_name'])
            db.session.add(new_student)
            db.session.commit()
            results['message'] = 'Students added successfully'
        elif type(json_data) is list:  # if json is a list of new students
            for student in json_data:
                new_student = Student(group_id=student['group_id'],
                                      first_name=student['first_name'],
                                      last_name=student['last_name'])
                db.session.add(new_student)
            db.session.commit()
            results['message'] = 'Students added successfully'
        json_report = jsonify(results)
        resp = make_response(json_report, 201)
        resp.mimetype = r'application\json'
        return resp

    def put(self, api_version, student_id):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        json_data = request.get_json()
        results = {}
        if student_id:
            student_upd = Student.query.get(student_id)
            if not student_upd:
                abort(404, message=f'student_id {student_id} not found')
            if type(json_data) is not dict:
                abort(404, message=f'wrong query type')
            try:
                student_upd.first_name = json_data['first_name']
                student_upd.last_name = json_data['last_name']
                student_upd.group_id = json_data['group_id']
                db.session.commit()
                results['message'] = f"Student's info with id = {student_id} " \
                                     f"updated successfully"
            except KeyError as e:
                abort(404, message=f'Info for student with id = {student_id} is'
                                   f' not complete. Field {str(e)} is required')
        else:  # for list of students
            for student in json_data:
                student_upd = Student.query.get(student['student_id'])
                if not student_upd:
                    if 'errors' not in results:
                        results['errors'] = []
                    results['errors'].append(f'Student with'
                                             f' id = {student_id} not found')
                try:
                    student_upd.first_name = student['first_name']
                    student_upd.last_name = student['last_name']
                    student_upd.group_id = student['group_id']
                    db.session.commit()
                    results['message'] = f"Student's info with" \
                                         f" id = {student['student_id']} " \
                                         f"updated successfully"
                except KeyError as e:
                    if "errors" not in results:
                        results['errors'] = []
                    results['errors'].append(f'Info for student with '
                                             f'id = {student["student_id"]} is'
                                             f' not complete.'
                                             f' Field {str(e)} is required')

        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def delete(self, api_version, student_id=None):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        results = {}
        if student_id:
            Student.query.filter_by(student_id=student_id).delete()
            db.session.commit()
            results['message'] = f'Deleted student with id={student_id}'
        else:
            # if no id it's needed to query DB with json fields and delete all
            json_data = request.get_json()
            query = db.session.query(Student).filter_by(**json_data)
            for student_to_del in query.all():
                db.session.delete(student_to_del)
                db.session.commit()
            results['message'] = f'Deleted {len(query.all())} student'
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp


class Courses(Resource):

    def get(self, api_version, course_name=None):
        if "v1" != api_version:
            abort(404, message=f"not supported api version: {api_version}")
        if course_name:
            course = Course.query.get(course_name.title())
            if not course:
                abort(404, message=f"Course {course_name} not found")
            results = {"course_name": course.course_name,
                       "description": course.description}
        else:
            # No course_name provided. Querying all courses
            query = db.session.query(Course).order_by(Course.course_name)
            results = [{"course_name": course.course_name,
                        "description": course.description}
                       for course in query.all()]
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def post(self, api_version, course_name=None):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        json_data = request.get_json()
        results = {'message': []}
        if course_name:
            # if json has info about only one course
            # course_check = Course.query.get(course_name)
            if Course.query.get(course_name):
                abort(404, message=f'Course is already exists')
            new_course = Course(course_name=course_name,
                                description=json_data['description'])
            db.session.add(new_course)
            db.session.commit()
            results['message'] = 'Course added successfully'
        elif type(json_data) is dict:  # if json is a list of new courses
            if Course.query.get(json_data["course_name"]):
                abort(404, message=f'Course is already exists')
            new_course = Course(course_name=json_data["course_name"],
                                description=json_data['description'])
            db.session.add(new_course)
            results['message'].append(f'Course {json_data["course_name"]}'
                                      f' added')
            db.session.commit()
        elif type(json_data) is list:  # json is a list of new courses
            for course in json_data:
                if Course.query.get(course["course_name"]):
                    if 'errors' not in results:
                        results['errors'] = []
                    results['errors'].append(f'Course {course["course_name"]} '
                                             f'is already exists')
                    continue
                new_course = Course(course_name=course["course_name"],
                                    description=course['description'])
                db.session.add(new_course)
                results['message'].append(f'Course {course["course_name"]}'
                                          f' added')
            db.session.commit()
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def put(self, api_version, course_name=None):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        json_data = request.get_json()
        results = {}
        if not course_name:
            abort(404, message=f"Provide course_name in URL")
        course_upd = Course.query.get(course_name)
        if not course_upd:
            abort(404, message=f"Course {course_name} not found")
        try:
            if json_data.get('course_name'):
                course_upd.course_name = json_data.get('course_name')
            course_upd.description = json_data.get('description')
            db.session.commit()
            results['message'] = f"{course_name} info updated"
        except (IndexError, AttributeError):
            if 'errors' not in results:
                results['errors'] = []
            results['errors'].append(f'Course "{course_name}" not found')
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def delete(self, api_version, course_name=None):
        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        results = {}
        if course_name:
            if not Course.query.filter_by(course_name=course_name).delete():
                abort(404, description=f"Course {course_name} not found")
            db.session.commit()
            results['message'] = f'Deleted course {course_name}'
        else:
            # if no id it's needed to query DB with json fields and delete all
            json_data = request.get_json()
            query = db.session.query(Course).filter_by(**json_data)
            courses_found = len(query.all())
            for course_to_del in query.all():
                db.session.delete(course_to_del)
                db.session.commit()
            results['message'] = f'Deleted {courses_found} courses'
        json_report = jsonify(results)
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp


api.add_resource(Students, '/api/<string:api_version>/students/',
                 '/api/<string:api_version>/students/<int:student_id>/',
                 endpoint='students')
api.add_resource(Courses, '/api/<string:api_version>/courses/',
                 '/api/<string:api_version>/courses/<course_name>/',
                 endpoint='courses')

if __name__ == '__main__':
    app.run(debug=True)
