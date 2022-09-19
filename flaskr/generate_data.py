import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import string
import itertools
import pprint


def gen_groups():
    """Generate and return list with 10 groups with random name"""

    group_names_list_tuples = []
    group_list = []
    for _ in range(10):
        name = ''
        for i in range(4):
            if i == 2:
                name += '_'
            name += random.choice(string.ascii_lowercase)
        t = (name,)
        group_list.append(name)
        group_names_list_tuples.append(t)
    return group_list, group_names_list_tuples


def gen_groups_size() -> list:
    """Return a list of groups size. 10 groups will have between 30 and 10
     students"""
    deviation = []
    for _ in range(5):
        deviation.append(random.randint(0, 10))
    deviation = deviation + [-n for n in deviation]
    groups = [20]*10
    students_in_groups = [n + g for n, g in zip(deviation, groups)]
    return students_in_groups


def generate_students(group_names) -> list:
    """Return 200 students with random names"""

    first_names = ['Liam', 'Olivia', 'Noah', 'Emma', 'Oliver', 'Charlotte',
                   'Elijah', 'Amelia', 'James', 'Ava', 'William', 'Sophia' ,
                   'Benjamin', 'Isabella', 'Lucas', 'Mia', 'Henry', 'Evelyn',
                   'Theodore', 'Harper'
                   ]
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis',
                  'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas',
                  'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia',
                  'Martinez', 'Robinson'
                  ]
    samples = random.sample(tuple(itertools.product(
        first_names, last_names)), 200)
    students = []
    groups_sizes = gen_groups_size()
    index = 0
    for group_name in group_names:
        for i in range(groups_sizes[index]):
            student = samples.pop()
            students.append((student[0], student[1], group_name))
        index += 1
    return students


def gen_courses() -> list:
    """Generate and return list with 10 courses"""

    course_names = [
        ('IT', 'Computer science'),
        ('Math', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Astronomy', 'Astrophysics'),
        ('Med', 'Medicine'),
        ('Geo', 'Geography'),
        ('Bio', 'Biology'),
        ('Econ', 'Economics'),
        ('Eco', 'Ecology'),
        ('Python', 'Not recommended')
    ]
    return course_names


def course_insert(courses):
    query = "INSERT INTO courses(course_name, description) VALUES(%s,%s)"
    psql_request(query, many=True, params=courses)


def groups_insert(group_names):
    query = "INSERT INTO groups(group_name) VALUES(%s)"
    psql_request(query, many=True, params=group_names)


def students_insert(students):
    query = "INSERT INTO students(first_name, last_name, group_id)" \
            " VALUES(%s,%s,%s)"
    psql_request(query, many=True, params=students)


def gen_students_courses():
    query_students = """SELECT student_id, first_name, last_name FROM students;"""
    students = psql_request(query_students, response_req=True)
    query_courses = """SELECT course_name FROM courses;"""
    courses = psql_request(query_courses, response_req=True)
    result = []
    for student in students:
        temp_courses = courses[:]
        for _ in range(random.randint(1, 3)):
            course_index = random.randint(0, len(temp_courses)-1)
            course = temp_courses.pop(course_index)
            result.append((*student, course[0]))
    return result


def create_many_to_many():
    sql_create_table = """CREATE TABLE students_courses (
    student_id integer REFERENCES students (student_id) ON UPDATE CASCADE 
    ON DELETE CASCADE,
    first_name VARCHAR(40),
    last_name VARCHAR(40),
    course_name VARCHAR(40) REFERENCES courses (course_name) ON UPDATE CASCADE
    ON DELETE CASCADE
    );"""
    sql_insert_data = """INSERT INTO students_courses (student_id, first_name, 
    last_name, course_name) VALUES (%s,%s,%s,%s);"""
    psql_request(sql_create_table)
    students_courses = gen_students_courses()
    psql_request(sql_insert_data, params=students_courses, many=True)


def insert_test_data():
    groups_list, groups_for_sql = gen_groups()
    students = generate_students(groups_list)
    groups_insert(groups_for_sql)
    students_insert(students)
    courses_list = gen_courses()
    course_insert(courses_list)
    create_many_to_many()


def test_queries():
    # Find all groups with less or equals student count:
    max_group_size = random.randint(15, 30)
    q1 = f"""
    SELECT group_id, count(student_id)
    FROM students
    GROUP BY group_id
    HAVING count(student_id) <= {max_group_size};"""
    q1_res = psql_request(q1, response_req=True)

    # Find all students related to the course with a given name.
    course = 'Math'
    q2 = f"""
    SELECT first_name, last_name 
    FROM students
    WHERE student_id IN 
    (SELECT student_id from students_courses where course_name='{course}')"""
    q2_res = psql_request(q2, response_req=True)

    # Add new student
    table_name = 'students'
    query_str = """INSERT INTO {table} ({fields}) VALUES (%s,%s,%s)"""
    q3 = sql.SQL(query_str).format(table=sql.Identifier(table_name),
                                      fields=sql.SQL(',').join([
                                          sql.Identifier('group_id'),
                                          sql.Identifier('first_name'),
                                          sql.Identifier('last_name'),
                                      ]),)
    # q3_res = psql_request(q3, ('jc_gm', 'test_name', 'test_last_name'))

    # Delete student by STUDENT_ID
    table_name = 'students'
    id_to_del = 806
    q4 = f"""DELETE FROM {table_name} WHERE student_id={id_to_del}"""
    # q4_res = psql_request(q4)

    # Add a student to the course
    table_name = 'students_courses'
    student_id = 301
    course_name = 'Math'
    q5 = f"""
            INSERT INTO {table_name} (student_id, first_name,
                                    last_name, course_name)
            SELECT {student_id}, first_name, last_name, '{course_name}'
            FROM students
            WHERE student_id={student_id}
            """
    # q5_res = psql_request(q5)


    # Remove the student from one of his or her courses
    table_name = 'students_courses'
    student_id = 300
    course_name = 'Math'
    q6 = f"""
        DELETE FROM {table_name}
        WHERE student_id={student_id} AND course_name='{course_name}'
        """
    # q6res = psql_request(q6)

    results = [q1_res, q2_res]
    pprint.pprint(results)


def psql_request(query, params=None, many=False, response_req=False):
    conn = None
    try:
        conn = psycopg2.connect(dbname='school', user='postgres',
                                password='admin', host='localhost', port='5432')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        conn.autocommit = True
        cursor = conn.cursor()
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)
        if response_req:
            result = cursor.fetchall()
        else:
            result = None
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        result = error
    finally:
        if conn is not None:
            conn.close()
    return result


if __name__ == '__main__':
    # insert_test_data()
    # test_queries()
    pass
