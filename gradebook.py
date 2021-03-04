import json
import os
from datetime import date
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# TODO Assignment comments and feedback
# TODO Email reports to students
# TODO Add email to student records
# TODO Generate markdown file for record
# TODO Use table functionality with markdown

today = date.today()

selected_class = None

my_book = None

# Creates a student and puts them in the currently selected class
def createStudent():
    name = input("Student name: ")
    username = input("Student username: ")
    standards = []
    return {
        'name' : name,
        'username' : username,
        'standards' : standards
        }

# Creates a new class and saves the class in the JSON file
def createClass():
    some_class = []
    class_name = str(input("Class name: "))
    number_of_s = int(input("Class size: "))
    for i in range(number_of_s):
        some_class.append(createStudent())
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    my_class = {
            "students" : some_class,
            "assignment_id" : 1
    }
    my_book[class_name] = my_class
    with open("gradebook.json", 'w') as gradebook:
        gradebook.write(json.dumps(my_book))
    
# Create a new standard and add it to every student's record in the
# currently selected class
def addStandard():
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    name = input("Standard Number: ")
    description = input("Standard Description: ")
    assignments = []
    standard = {
        "name" : name,
        "description" : description,
        "assignments" : assignments
    }
    curr_class = my_book[selected_class]
    for student in curr_class["students"]:
        student['standards'].append(standard)
    with open("gradebook.json", 'w') as gradebook:
        gradebook.write(json.dumps(my_book))

# Create a new assignment, given the standards, and add it to every 
# student's record in the currently selected class
def addAssignment():
    # Structure of an assignment object
    # * assignment
    #   * id
    #   * name
    #   * grade
    #   * date
    #   * comment
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    assignment_name = str(input("What is the assignment name? \n\t"))
    num_standards = int(input("How many standards are being assesed? \n\t"))
    # List the standards for the user to select from...
    curr_class = my_book[selected_class]
    sample_student = curr_class["students"][0]
    possible_standards = []
    for standard in sample_student["standards"]:
        possible_standards.append((standard["name"], standard["description"]))
    for standard in possible_standards:
        print(f'\t{standard[0]}: {standard[1]}\n')
    # .................................................
    standards_to_grade = []
    for i in range(num_standards):
        standard_name = str(input("Please enter one of the standards (01/02/03...) from the assignment: "))
        standards_to_grade.append(standard_name)
    curr_class = my_book[selected_class]
    for student in curr_class["students"]:
        name = student["name"]
        ass_comment = str(input(f'Comment for {student["name"]}:\n\t'))
        for standard_name in standards_to_grade:
            for standard in student["standards"]:
                if standard["name"] == standard_name:
                    grade = float(input(f'Please enter the grade {name} earned for standard {standard_name}: \n\t'))
                    ass_num = int(curr_class["assignment_id"])
                    # Figure out best way to add assignment comments
                    assignment = {
                        "id" : ass_num,
                        "name" : assignment_name,
                        "grade" : grade,
                        "date" : str(today),
                        "comment" : ass_comment
                    }
                    standard["assignments"].append(assignment)
    curr_class["assignment_id"] += 1
    with open("gradebook.json", 'w') as gradebook:
        gradebook.write(json.dumps(my_book))

# Formats a comment to fit on an appropriate number of lines
def formatComment(comment, width=60):
    comment_length = len(comment)
    num_lines = comment_length // width
    if num_lines > 0:
        output = "\t"
        for i in range(num_lines+1):
            output += comment[(i)*width:(i)*width + width]
            if (output[len(output) - 1] != " " and i < num_lines):
                output += "-"
            output += "\n\t"
        return output
    return comment

# Generates a text report for each individual student in the appropriate
# folder. Note the parent folder needs to exist before this can happen
# TODO add os operations to make this process smoother.
def generateReport():    
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    curr_class = my_book[selected_class]
    for student in curr_class["students"]:
        output = "-" * 120
        output += "\n"
        with open(f'C:\\Users\\matth\\Documents\\Gradebook-Reports\\{selected_class}\\{student["username"]}.txt', "w") as report:
            # Information for individual student
            ##########################################################################################################
            class_average = 0
            num_standards = 0
            output += f'{student["name"]}\n'
            output += "-" * 120
            output += "\n"
            for standard in student["standards"]:
                num_standards += 1
                output += f'{standard["name"]} {standard["description"]}\n\n'
                sum_grades = 0
                num_assignments = len(standard["assignments"])
                # TODO Account for decaying average
                assignments = standard["assignments"]
                if len(assignments) >= 3:
                    most_recent = assignments[len(assignments) - 1]
                    middle = assignments[len(assignments) - 2]
                    last = assignments[len(assignments) - 3]
                    a = most_recent["grade"]
                    b = middle["grade"]
                    c = last["grade"]
                    sum_grades = 0.60 * a + 0.25 * b + 0.15 * c
                elif len(assignments) == 2:
                    most_recent = assignments[len(assignments) - 1]
                    middle = assignments[len(assignments) - 2]
                    a = most_recent["grade"]
                    b = middle["grade"]
                    sum_grades = 0.60 * a + 0.40 * b
                elif len(assignments) == 1:
                    most_recent = assignments[len(assignments) - 1]
                    a = most_recent["grade"]
                    sum_grades = 1.0 * a
                elif len(assignments) == 0:
                    sum_grades = 0
                class_average += sum_grades
                for assignment in standard["assignments"]:
                    # TODO Account for missing assignments
                    # sum_grades += assignment["grade"]
                    output += f'{assignment["id"]}: {assignment["name"]}\n\t | {assignment["date"]} | \t\t\t {assignment["grade"]}\n\n'
                    if curr_class["assignment_id"] - 1 == assignment["id"]:
                        output += formatComment(assignment["comment"])
                        output += "\n\n"
                if num_assignments > 0:
                    output += f'Average \t\t\t\t\t {sum_grades}\n'
                else:
                    output += f'Average \t\t\t\t\t {"0"}\n'
                output += "-" * 120
                output += "\n"
            if num_standards > 0:
                output += f'Class Average \t\t\t\t\t {class_average / num_standards}\n'
            ##########################################################################################################
            output += "-" * 120
            output += "\n"
            report.write(output)
        
# TODO Need generic email account to make this happen?
def emailReports():
    generateReport()
    # Get the directory given the class
    url = f'C:\\Users\matth\Documents\Gradebook-Reports\{selected_class}'
    files = os.listdir(url)
    sender_email = str(input("Sender Email: "))
    password = str(input("Password: "))
    for filename in files:
        test = open(f'{url}\{filename}')
        receiver_email = f'{filename[0 : len(filename) - 4]}@hotchkiss.org'
        subject = f'Grade Update for {selected_class}'
        body = ""
        for line in test:
            body += line

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        # message["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

# TODO Give assignment new description, id stays the same
def renameAssignment():
    # TODO Rename an assignment for all students
    pass

# TODO Delete a given assignment (by id) from all students
def deleteAssignment():
    # TODO Delete an assignment for all students
    pass

# Changes the grade(s) for a specific student assignment NOTE: this changeGrade()
# function is different from a reassessment opportunity. Changes in-place.
def changeGrade():
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    curr_class = my_book[selected_class]
    possible_students = ""
    for student in curr_class["students"]:
        possible_students += student["username"]
        possible_students += "\n"
    student_choice = input(f'What student would you like to choose?\n\n{possible_students}\n\nStudent: ')
    sel_student = None
    for student in curr_class["students"]:
        if student["username"] == student_choice:
            sel_student = student
    # Remember, a single assignment has multiple standards
    assignments = set()
    for standard in sel_student["standards"]:
        for assignment in standard["assignments"]:
            assignments.add(f'{assignment["id"]}: {assignment["name"]}')
    possible_assignments = ""
    for ass in assignments:
        possible_assignments += ass
        possible_assignments += "\n"
    assignment_choice = input(f'Type the assignment ID to modify...\n\n{possible_assignments}\n\nAssignment: ')
    ass_comment = str(input("Comment (optional): \n\t"))
    for standard in sel_student["standards"]:
        for assignment in standard["assignments"]:
            if assignment["id"] == int(assignment_choice):
                assignment["grade"] = int(input(f'Standard {standard["name"]}:\n\tPrev. Grade: {assignment["grade"]}\n\tNew Grade: '))
                assignment["comment"] = ass_comment
                print("---------------------")
    with open("gradebook.json", 'w') as gradebook:
        gradebook.write(json.dumps(my_book))
    # print(assignments)

# Create a reassessment assignment for a single student. This
# only applies to the given student, not the entire class.
def createReassessment():
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    curr_class = my_book[selected_class]
    possible_students = []
    student_name = ""
    for student in curr_class["students"]:
        possible_students.append(student["username"])
    for student in possible_students:
        print(f'\t{student}\n')
    student_name = str(input(f'Please select a student username from the following list:\n\t'))
    sel_student = None
    for student in curr_class["students"]:
        if student_name == student["username"]:
            sel_student = student
    reassessment_name = str(input("Please enter the name of the reassessment: \n\t"))
    possible_standards = ""
    standard_name = ""       
    for standard in sel_student["standards"]:
        possible_standards += f'\t{standard["name"]}: {standard["description"]}\n'
    print(possible_standards)
    standard_name = str(input(f'Please select a standard from the following list: \n\t'))
    sel_standard = None
    for standard in sel_student["standards"]:
        if standard_name == standard["name"]:
            sel_standard = standard
    grade = float(input(f'Please enter the grade {sel_student["name"]} earned for standard {sel_standard["name"]}: {sel_standard["description"]}: \n\t'))
    ass_num = int(curr_class["assignment_id"])
    comment = str(input("Comment: \n\t"))
    # Figure out best way to add assignment comments
    assignment = {
        "id" : ass_num,
        "name" : reassessment_name,
        "grade" : grade,
        "date" : str(today),
        "comment" : comment
    }
    sel_standard["assignments"].append(assignment)
    curr_class["assignment_id"] += 1
    with open("gradebook.json", 'w') as gradebook:
        gradebook.write(json.dumps(my_book))

# Changes the selected class for operations and grade changes
def changeClass():
    global selected_class
    my_book = None
    with open("gradebook.json") as gradebook:
        my_book = json.load(gradebook)
    options = list(my_book.keys())
    selected_class = str(input(f'Please select a class to work with: {options}: '))
    while selected_class not in options:
        print("Error: please type the class as it appears in the following list: ")
        selected_class = str(input(f'{options}: '))

user_input = input("Press any key to continue...")

introduction = """
Matthijs van Mierlo's SBG (Standards Based Grading) Tool
o       o   o   o   o   o       o
o   o   o       o       o       o
o       o       o       o       o
o       o       o           o
Command Line Interface for an SBG Gradebook
Supports Multiple Classes/Sections
Supports Missing/Exempt Assignments
"""

print(introduction)

while(user_input != "EXIT" and user_input != "exit"):
    while selected_class == None:
        my_book = None
        with open("gradebook.json") as gradebook:
            my_book = json.load(gradebook)
        if list(my_book.keys()) == []:
            print("No classes created, please create one before continuing...")
            createClass()
            with open("gradebook.json") as gradebook:
                my_book = json.load(gradebook)
        # selected_class = str(input(f'Please select a class to work with: {list(my_book.keys())}: '))
        changeClass()
    os.system("cls")
    print(introduction)
    print("-" * 100)
    print(f'Current Class: {selected_class}')
    selections = """
\t0 - Change class selection
\t1 - Create a new class 
\t2 - Add a standard (for all students)
\t3 - Add an assignment (for all students)
\t4 - Create a reassessment (for one student)
\t5 - Change grade in-place (for one student)
\t6 - Generate a report (for all students)
\t7 - Email reports (for all students)
\tType "EXIT" or "exit to quit
"""
    user_input = input(f'{selections}{"-" * 100}\n')
    print("-" * 100)
    if user_input == "0":
        changeClass()
    elif user_input == "1":
        createClass()
    elif user_input == "2":
        addStandard()
    elif user_input == "3":
        addAssignment()
    elif user_input == "4":
        createReassessment()
    elif user_input == "5":
        changeGrade()
    elif user_input == "6":
        generateReport()
    elif user_input == "7":
        emailReports()
    else:
        pass