from flask import Flask, request, render_template
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
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_PORT"] = 3306
app.config["MYSQL_DB"] = "cpsc_449"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/initialize-db")
def initialize_db():
	cur = mysql.connection.cursor()
	cur.execute(
		"DROP TABLE IF EXISTS enrollments"
	)
	cur.execute(
		"DROP TABLE IF EXISTS students"
	)
	cur.execute(
		"DROP TABLE IF EXISTS classes"
	)
	cur.execute(
		"CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), full_name VARCHAR(255), gradYear INT)"
	)
	cur.execute(
		"CREATE TABLE IF NOT EXISTS classes (id INT AUTO_INCREMENT PRIMARY KEY, subject VARCHAR(255), section INT, semester VARCHAR(255), schoolYear INT, professor VARCHAR(255))"
	)
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
    cur.execute(
        "INSERT INTO students (email, full_name, gradYear) VALUES (%s, %s, %s)",
        ("jane@csu.fullerton.edu", "Jane Smith", 2022),
    )
    cur.execute(
        "INSERT INTO students (email, full_name, gradYear) VALUES (%s, %s, %s)",
        ("jack@csu.fullerton.edu", "Jack Smith", 2021),
    )
    # seed the classes table
    cur.execute(
        "INSERT INTO classes (subject, section, semester, schoolYear, professor) VALUES (%s, %s, %s, %s, %s)",
        ("CPSC", 349, "Fall", 2021, "Dr. Smith"),
    )
    cur.execute(
        "INSERT INTO classes (subject, section, semester, schoolYear, professor) VALUES (%s, %s, %s, %s, %s)",
        ("CPSC", 335, "Fall", 2021, "Dr. Smith"),
    )
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
        (1, 1),
    )
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
        (2, 1),
    )
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
        (2, 2),
    )
    cur.execute(
        "INSERT INTO enrollments (student_id, class_id) VALUES (%s, %s)",
        (3, 2),
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
        "SELECT * FROM students s JOIN enrollments e ON s.id = e.student_id JOIN classes c ON c.id = e.class_id WHERE c.subject = %s AND c.section = %s",
        (subject, class_number),
    )
    data = cur.fetchall()
    cur.close()
    return []+list(data)


@app.route("/student/register", methods = ["POST"])
def create_student():
	try:
		request_data = request.get_json()
	except:
		request_data = None
	email = None
	email = request_data.get("email")
	name = None
	name = request_data.get("name")
	gradYear = None
	gradYear = request_data.get("gradYear")
	if request_data and email and name and gradYear:
		cur = mysql.connection.cursor()
		cur.execute(
			"INSERT INTO students (email, full_name, gradYear) VALUES (%s, %s, %s)",
			(email, name, gradYear),
		)
		mysql.connection.commit()
		cur.close()
		return {"msg": "Student Created!"}
	else:
		return{"msg": "Fields Missing!"}


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


@app.route("/student/search", methods=["GET", "POST"])
def class_search():
	try:
		request_data = request.get_json()
	except:
		request_data = None
	email = None
	name = None
	gradYear = None
	subject = None
	section = None
	semester = None
	schoolYear = None
	professor = None
	sqlPrompt = "SELECT * FROM students s JOIN enrollments e ON s.id = e.student_id JOIN classes c ON e.class_id = c.id"
	if request_data:
		sqlPrompt += " WHERE e.id = e.id" #
		email = request_data.get("email")
		if email != None:
			sqlPrompt += f" AND s.email = \"{email}\""
		name = request_data.get("name")
		if name != None:
			sqlPrompt += f" AND s.full_name = \"{name}\""
		gradYear = request_data.get("gradYear")
		if gradYear != None:
			sqlPrompt += f" AND s.gradYear = {gradYear}"
		subject = request_data.get("subject")
		if subject != None:
			sqlPrompt += f" AND c.subject = \"{subject}\""
		section = request_data.get("section")
		if section != None:
			sqlPrompt += f" AND c.section = {section}"
		semester = request_data.get("semester")
		if semester != None:
			sqlPrompt += f" AND c.semester = \"{semester}\""
		schoolYear = request_data.get("schoolYear")
		if schoolYear != None:
			sqlPrompt += f" AND c.schoolYear = {schoolYear}"
		professor = request_data.get("professor")
		if professor != None:
			sqlPrompt += f" AND c.professor = \"{professor}\""
	cur = mysql.connection.cursor()
	print(sqlPrompt)
	cur.execute(sqlPrompt)
	data = cur.fetchall()
	cur.close()
	return [] + list(data)


@app.route("/classes", methods=["GET"])
def get_classes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM classes")
    data = cur.fetchall()
    cur.close()
    return {"classes": data}


@app.route("/classes/add", methods=["POST"])
def create_class():
	try:
		request_data = request.get_json()
	except:
		request_data = None
	subject = None
	subject =request_data.get("subject")
	section = None
	section = request_data.get("section")
	semester = None
	semester = request_data.get("semester")
	schoolYear = None
	schoolYear = request_data.get("schoolYear")
	professor = None
	professor = request_data.get("professor")
	if request_data and subject and section and semester and schoolYear and professor:
		cur = mysql.connection.cursor()
		cur.execute(
			"INSERT INTO classes (subject, section, semester, schoolYear, professor) VALUES (%s, %s, %s, %s, %s)",
			(subject, section, semester, schoolYear, professor)
		)
		mysql.connection.commit()
		cur.close()
		return {"msg": "Class Created!"}
	else: 
		return {"msg": "Fields Missing!"}


def main():
    if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True)


main()
