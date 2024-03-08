from flask import Flask, request
from flask_mysqldb import MySQL

"""
Description: This project will act as a way to connect students (previous, current, or future) to track the classes they have taken.
Students sign up with their school email
Students can register for existing or new classes and say the semester they have taken the class.
Users may also search for other individuals who have taken / will take a given class; allowing them to network and collaborate with their peers.
"""

app = Flask(__name__)

app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_HOST"] = "127.0.01"
app.config["MYSQL_PORT"] = 3307
app.config["MYSQL_DB"] = "cpsc-449"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/initialize-db")
def initialize_db():
    cur = mysql.connection.cursor()
    # create a students table
    cur.execute(
        "CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), full_name VARCHAR(255), gradYear INT)"
    )
    # create a classes table
    cur.execute(
        "CREATE TABLE IF NOT EXISTS classes (id INT AUTO_INCREMENT PRIMARY KEY, subject VARCHAR(255), section INT, semester VARCHAR(255), schoolYear INT, professor VARCHAR(255))"
    )
    # create a enrollments table
    cur.execute(
        "CREATE TABLE IF NOT EXISTS enrollments (id INT AUTO_INCREMENT PRIMARY KEY, student_id INT, class_id INT)"
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Database Initialized!"}


@app.route("/seed-db")
def seed_db():
    cur = mysql.connection.cursor()
    # seed the students table
    cur.execute(
        "INSERT INTO students (email, full_name, gradYear) VALUES (%s, %s, %s)",
        ("john@csu.fullerton.edu", "John Smith", 2023),
    )
    # seed the classes table
    cur.execute(
        "INSERT INTO classes (subject, section, semester, schoolYear, professor) VALUES (%s, %s, %s, %s, %s)",
        ("CPSC", 349, "Fall", 2021, "Dr. Smith"),
    )
    # seed the enrollments table
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)", (1, 1)
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Database Seeded!"}


@app.route(
    "/student/subject/<string:subject>/class/<string:class_number>", methods=["GET"]
)
def get_students_by_enrollments_in_classes(subject: str, class_number: str):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM students s JOIN enrollments e ON s.id = e.student_id JOIN classes c ON e.class_id = c.id WHERE c.subject = %s AND c.class_number = %s",
        (subject, class_number),
    )
    data = cur.fetchall()
    cur.close()
    return {"students": data}


@app.route("/student/register")
def create_student():
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO students (email, full_name, gradYear) VALUES (%s, %s, %s)",
        ("" + request.form["email"], "" + request.form["full_name"], 0),
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Student Created!"}


@app.route("/student/<string:email>/classes")
def get_student_classes(email: str):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM students s JOIN enrollments e ON s.id = e.student_id JOIN classes c ON e.class_id = c.id WHERE s.email = %s",
        (email),
    )
    data = cur.fetchall()
    cur.close()
    return {"classes": data}


@app.route("/student/<string:email>/classes/<string:subject>", methods=["POST"])
def class_sign_up(email: str, subject: str, class_number: str):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM students WHERE email = %s", (email))
    student_id = cur.fetchone()
    cur.execute(
        "SELECT id FROM classes WHERE subject = %s AND class_number = %s",
        (subject, class_number),
    )
    class_id = cur.fetchone()
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
        (student_id, class_id),
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Class Registered!"}


@app.route("/student/<string:email>/classes/<string:subject>", methods=["DELETE"])
def class_drop(email: str, subject: str, class_number: str):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM students WHERE email = %s", (email))
    student_id = cur.fetchone()
    cur.execute(
        "SELECT id FROM classes WHERE subject = %s AND class_number = %s",
        (subject, class_number),
    )
    class_id = cur.fetchone()
    cur.execute(
        "DELETE FROM enrollments WHERE student_id = %s AND class_id = %s",
        (student_id, class_id),
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Class Dropped!"}


@app.route("/student/search", methods=["POST"])
def class_search():
    request_data = request.get_json()
    email = None
    name = None
    gradYear = None
    subject = None
    section = None
    semester = None
    schoolYear = None
    professor = None
    if request_data:
        email = request_data.get("email")
        name = request_data.get("name")
        gradYear = request_data.get("gradYear")
        subject = request_data.get("subject")
        section = request_data.get("section")
        semester = request_data.get("semester")
        schoolYear = request_data.get("schoolYear")
        professor = request_data.get("professor")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM students s JOIN enrollments e ON s.id = e.student_id JOIN classes c ON e.class_id = c.id WHERE s.email = %s AND s.full_name = %s AND s.gradYear = %s AND c.subject = %s AND c.section = %s AND c.semester = %s AND c.schoolYear = %s AND c.professor = %s",
        (email, name, gradYear, subject, section, semester, schoolYear, professor),
    )
    data = cur.fetchall()
    cur.close()
    return {"students": data}


@app.route("/classes", methods=["GET"])
def get_classes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM classes")
    data = cur.fetchall()
    cur.close()
    return {"classes": data}


@app.route("/classes/<string:subject>", methods=["GET"])
def get_classes_by_subject(subject: str):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM classes WHERE subject = %s", (subject))
    data = cur.fetchall()
    cur.close()
    return {"classes": data}


@app.route("/classes", methods=["POST"])
def create_class():
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO classes (subject, section, semester, schoolYear, professor) VALUES (%s, %s, %s, %s, %s)",
        (
            "" + request.form["subject"],
            "" + request.form["section"],
            "" + request.form["semester"],
            "" + request.form["schoolYear"],
            "" + request.form["professor"],
        ),
    )
    mysql.connection.commit()
    cur.close()
    return {"msg": "Class Created!"}


def main():
    if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True)


main()
