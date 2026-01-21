import pandas as pd
import mysql.connector
import time
import smtplib
import random

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta
from io import StringIO
from flask import Flask, render_template, request, redirect, session, Response

sql = mysql.connector.connect(
    host="localhost",
    user="lms_user",
    password="Upscale",
    database="LMS",
    autocommit=True
)

cursor = sql.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employee (
    designation VARCHAR(50),
    email VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50),
    surname VARCHAR(50),
    department VARCHAR(50),
    password VARCHAR(50),
    join_date VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_table (
    designation VARCHAR(50),
    email VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50),
    surname VARCHAR(50),
    department VARCHAR(50),
    password VARCHAR(50),
    join_date VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_email (
    email VARCHAR(50) PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    email VARCHAR(50),
    attendance_date DATE,
    status ENUM('Present','Absent','Late'),
    check_in_time TIME,
    PRIMARY KEY (email, attendance_date)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_remaining (
    email VARCHAR(50),
    Sick_Leave DECIMAL(10,2) DEFAULT 0,
    Casual_Leave DECIMAL(10,2) DEFAULT 0,
    Conpenstaion_off DECIMAL(10,2) DEFAULT 0,
    Summer_Vacation DECIMAL(10,2) DEFAULT 0,
    Planed_Leave DECIMAL(10,2) DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_record (
    email VARCHAR(50),
    leave_date_start VARCHAR(50),
    leave_date_end VARCHAR(50),
    leave_type ENUM(
        'Sick_Leave','Casual_Leave','Conpenstaion_off',
        'Summer_Vacation','Planed_Leave','Duty_Leave','Early_Leave'
    ),
    applyed_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    approve VARCHAR(50),
    message VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS approve_table (
    email VARCHAR(50),
    leave_type ENUM(
        'Sick_Leave','Casual_Leave','Conpenstaion_off',
        'Summer_Vacation','Planed_Leave','Duty_Leave','Early_Leave'
    ),
    leave_date_start VARCHAR(50),
    leave_date_end VARCHAR(50),
    applyed_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    approve VARCHAR(50) DEFAULT 'Pending',
    message VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sms_table (
    email VARCHAR(50) PRIMARY KEY,
    sms VARCHAR(50),
    timestamp DATETIME
)
""")

sql.commit()


def auto_add_leave():
    cursor.execute("""
    UPDATE leave_remaining
        SET Sick_Leave = Sick_Leave + 0.83,
            Casual_Leave = Casual_Leave + 1
    """)
    sql.commit()

def auto_summer_plan():
    cursor.execute("""UPDATE leave_remaining
        SET Summer_Vacation = Summer_Vacation + 30
        WHERE email IN (SELECT email FROM employee)
    """)
    cursor.execute("""UPDATE leave_remaining
        SET Planed_Leave = Planed_Leave + 30
        WHERE email IN (SELECT email FROM admin_table)
    """)
    sql.commit()

def outer_add_emp( designation, email, name, surname, department, password, type, join_date):
    email = email.lower()

    if email != f"{name.lower()}.{surname.lower()}@gnims.com":
        return "Invalid email format OR name/surname does not match!"

    if type == 'admin':
        cursor.execute("SELECT email FROM admin_table WHERE email = %s", (email,))
        if cursor.fetchone():
            return f"Admin {email} already exists!"

        cursor.execute("""
            INSERT INTO admin_table
            (designation, email, name, surname, department, password, join_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (designation, email, name, surname, department, password, join_date))

        cursor.execute(
            "INSERT INTO leave_remaining (email) VALUES (%s)",
            (email,)
        )
         
        cursor.execute("""INSERT INTO admin_email (email) VALUES (%s)
        """, (email,))
        
        sql.commit()
        return f"Admin {email} added successfully!"
    else:
        cursor.execute("SELECT email FROM employee WHERE email = %s", (email,))
        if cursor.fetchone():
            return f"Employee {email} already exists!"

        cursor.execute("""
            INSERT INTO employee
            ( designation, email, name, surname, department, password, join_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (designation, email, name, surname, department, password, join_date))

        cursor.execute(
            "INSERT INTO leave_remaining (email) VALUES (%s)",
            (email,)
        )

        sql.commit()
        return f"Employee {email} added successfully!"
outer_add_emp("MR", "anurag.yadav@gnims.com", "Anurag", "Yadav", "IT", "123", "admin", "2025-06-25")


def send_email_admin(subject, body):
    cursor.execute("SELECT email FROM admin_email")
    to_address = cursor.fetchone()[0]
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.starttls()
    mail.login('anuragyadav8591@gmail.com', 'alaiiqrmnupjzmlt')
    message = f"Subject: {subject}\n\n{body}"
    mail.sendmail('anuragyadav8591@gmail.com', to_address, message)
    mail.quit()

def send_email_emp(subject, body, email):
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.starttls()
    mail.login('anuragyadav8591@gmail.com', 'alaiiqrmnupjzmlt')
    message = f"Subject: {subject}\n\n{body}"
    mail.sendmail('anuragyadav8591@gmail.com', email, message)
    mail.quit()
    
def auto_mark_absent():
    today_str = date.today()
    cursor.execute("""
        INSERT IGNORE INTO attendance (email, attendance_date, status)
        SELECT email, %s, 'Absent'
        FROM employee
        WHERE email NOT IN (
            SELECT email FROM attendance WHERE attendance_date = %s
        )
    """,(today_str, today_str))
    cursor.execute("""
        INSERT IGNORE INTO attendance (email, attendance_date, status)
        SELECT email, %s, 'Absent'
        FROM admin_table
        WHERE email NOT IN (
            SELECT email FROM attendance WHERE attendance_date = %s
        )
    """,(today_str, today_str))
    sql.commit()

app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def home():
    return render_template("login.html")

@app.route("/admin_login_page")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/dashboard_page")
def dashboard_page():
    if "type" not in session:
        return redirect("/")
    if session.get("type") == "admin":
        cursor.execute("""""")
        return render_template("admin_dashboard.html")
    cursor.execute("""
      SELECT Sick_Leave, Casual_Leave, Conpenstaion_off, Summer_Vacation 
      FROM leave_remaining 
      WHERE email = %s
    """, (session.get("email"),))

    balance = cursor.fetchone()

    return render_template("employee_dashboard.html", balance=balance)


@app.route("/leavehistory_page")
def leavehistory_page():
    email = session.get("email")
    cursor.execute("""
        SELECT leave_type, leave_date_start, leave_date_end, approve, applyed_on
        FROM leave_record
        WHERE email = %s
        UNION ALL
        SELECT leave_type, leave_date_start, leave_date_end, approve, applyed_on
        FROM approve_table
        WHERE email = %s
        ORDER BY leave_date_start DESC
    """, (email,email,))
    data = cursor.fetchall()
    return render_template("leave_history.html", data=data)


@app.route("/applyleave_page")
def applyleave_page():
    if "email" not in session:
        return redirect("/")
    return render_template("apply_leave.html")


@app.route("/add_employee_page")
def add_employee_page():
    return render_template("add_employee.html")

@app.route("/approve_leave_page")
def approve_leave_page():
    if "email" not in session:
        return redirect("/")
    cursor.execute("SELECT * FROM approve_table")
    rows = cursor.fetchall()
    return render_template("approve_leave.html", data=rows)

@app.route("/add_leave_balance_page")
def add_leave_balance_page():
    cursor.execute("SELECT email, name, surname FROM employee")
    employees = cursor.fetchall()
    return render_template("add_leave_balance.html", employees=employees)

@app.route("/download_all_reports_page")
def download_all_reports_page():
    return render_template("download_all_reports.html")

@app.route("/forgot_password_page")
def forgot_password_page():
    email = request.args.get("email")
    type = request.args.get("type")
    step = request.args.get("step")
    data = request.args.get("data")

    return render_template(
        "forgot_password.html",
        email=email,
        type=type,
        step=step,
        data=data)


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"].lower()
    password = request.form["password"]

    cursor.execute("""
        SELECT designation, name, surname, department, join_date
        FROM employee WHERE EMAIL = %s AND PASSWORD = %s
    """, (email, password))

    data = cursor.fetchone()

    if data is None:
        return render_template("login.html", data="Invalid Email or Password Credential")

    session["designation"] = data[0]
    session["type"] = "employee"
    session["email"] = email
    session["user_name"] = data[1]
    session["surname"] = data[2]
    session["department"] = data[3]
    session["join_date"] = data[4]

    cursor.execute("""SELECT status FROM attendance
        WHERE email = %s AND attendance_date = %s""", (email, datetime.now().strftime("%Y-%m-%d")))
    attendance_record = cursor.fetchone()
    if attendance_record is None:
        if datetime.now().hour <= 9 and datetime.now().minute <= 0:
            status = "Present"
        else:
            status = "Late"
        cursor.execute("""
            INSERT IGNORE INTO attendance (email, attendance_date, status, check_in_time)
            VALUES (%s, %s, %s, %s)""", (email, date.today(), status, datetime.now().strftime("%H:%M:%S")))
    sql.commit()
    return redirect("/dashboard_page")


@app.route("/admin_login", methods=["POST"])
def admin_login():
    email = request.form["email"].lower()
    password = request.form["password"]

    cursor.execute("""
        SELECT designation, name, surname, department, join_date
        FROM admin_table WHERE EMAIL = %s AND PASSWORD = %s
    """, (email, password))
    data = cursor.fetchone()

    if data is None:
        return render_template("admin_login.html", data="Invalid Email or Password Credential")

    session["designation"] = data[0]
    session["type"] = "admin"
    session["email"] = email
    session["user_name"] = data[1]
    session["surname"] = data[2]
    session["department"] = data[3]
    session["join_date"] = data[4]
    
    if datetime.now().hour <= 9 and datetime.now().minute <= 0:
        status = "Present"
    else:
        status = "Late"
    cursor.execute("""
        INSERT IGNORE INTO attendance (email, attendance_date, status, check_in_time)
        VALUES (%s, %s, %s, %s)""", (email, date.today(), status, datetime.now().strftime("%H:%M:%S")))
    sql.commit()
    return redirect("/dashboard_page")


@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    email = request.form["email"]
    sms = request.form["sms"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]
    type = request.form["type"]

    if new_password != confirm_password:
        return "New Password and Confirm Password do not match"

    cursor.execute("SELECT sms FROM sms_table WHERE email = %s", (email,))
    sms_record = cursor.fetchone()
    
    if sms_record == None:
        return render_template("/forgot_password.html", data="Email code is required please Send the code", step = '1')
    cursor.execute("""
        SELECT timestamp FROM sms_table WHERE email = %s
    """, (email,))
    row = cursor.fetchone()
    expire = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")

    if datetime.now() - expire > timedelta(minutes=5):
        cursor.execute("DELETE FROM sms_table WHERE email = %s", (email,))
        sql.commit()
        return render_template("/forgot_password.html", data="OTP expired Please resend the OTP")

    if sms != sms_record[0]:
        return render_template("/forgot_password.html", data="Invalid SMS code", step="2", email = email, type = type)

    if type == 'admin':
        cursor.execute("UPDATE admin_table SET password = %s WHERE email = %s", (new_password, email,))
    else:
        cursor.execute("UPDATE employee SET password = %s WHERE email = %s", (new_password, email,))
    cursor.execute("DELETE FROM sms_table WHERE email = %s", (email,))
    sql.commit()
    
    return render_template("/forgot_password.html", data="Password Updated Successfully")


@app.route("/send_forgot_sms", methods=["POST"])
def send_forgot_sms():
    email = request.form["email"]
    type = request.form["type"]
    
    if type == "admin":
        cursor.execute("SELECT email FROM admin_table WHERE email = %s", (email,))
    else:
        cursor.execute("SELECT email FROM employee WHERE email = %s", (email,))

    if cursor.fetchone() is None:
        return render_template('/forgot_password.html', data = 'Email Not Register')
    
    sms_code = random.randint(100000, 999999)
    cursor.execute("""INSERT
                   INTO sms_table (email, sms, timestamp)
                   VALUES (%s, %s, %s)""",
                   (email, sms_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    sql.commit()
    send_email_emp(
        f"No Reply - Password Reset SMS Code",
        f"""Please Don't reply to this email, this is an autogenerated email.
            
            Gmail: {email} 
            Your password reset SMS code is: {sms_code}
            If you did not request a password reset, please ignore this email.
                
            Regards,
            Automated Leave Management System""", email)
    return redirect(f"/forgot_password_page%email={email}&type={type}&step=2")


@app.route("/add_employee", methods=["POST"])
def insert_employee_data():
    designation = request.form["designation"]
    email = request.form["email"].lower()
    name = request.form["name"]
    surname = request.form["surname"]
    department = request.form["department"]
    password = request.form["pass"]
    admin = request.form["admin"]
    join_date = request.form["join_date"]
    data = outer_add_emp(designation, email, name, surname, department, password, admin, join_date)
    return render_template("add_employee.html", data = data)


@app.route("/applyleave", methods=["POST"])
def applyleave():
    email = session.get("email")
    name = session.get("user_name")
    surname = session.get("surname")
    apply_start_date = request.form["leave_start"]
    apply_end_date = request.form["leave_end"]
    leave_type = request.form["leave_type"]

    cursor.execute(f"SELECT {leave_type} FROM leave_remaining WHERE email = %s", (email,))
    remain = cursor.fetchone()
    
    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        if remain[0] == 0:
            return render_template("apply_leave.html", data = f"{leave_type} leave stack is empty — cannot apply!")
        count = (datetime.strptime(apply_end_date, "%Y-%m-%d") - datetime.strptime(apply_start_date, "%Y-%m-%d")).days + 1
        if remain[0] < count:
            return render_template("apply_leave.html", data = f"Insufficient {leave_type} Balance, you are trying to apply for {count} days and your leave balance is {int(remain[0])} days.")
        start_date = datetime.strptime(apply_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(apply_end_date, "%Y-%m-%d")
        cursor.execute(f"""
            UPDATE leave_remaining
            SET {leave_type} = {leave_type} - %s
            WHERE email = %s
        """, ((end_date - start_date).days + 1, email,))
    
    cursor.execute("""
            SELECT * FROM approve_table
            WHERE email = %s
    """, (email,))
    data = cursor.fetchall()
    for data in data:
        if data[2] == apply_start_date:
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_start_date}.")
        if data[2] == apply_end_date:
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_end_date}.")
        if data[3] == apply_end_date:
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_end_date}.")
        if data[3] == apply_start_date:
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_start_date}.")

    cursor.execute("""
            SELECT approve FROM leave_record
            WHERE email = %s AND leave_date_start = %s
    """, (email, apply_start_date))
    data = cursor.fetchall()
    for row in data:
        if row[0] == 'Approved':
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_start_date}.")
        
    cursor.execute("""
            INSERT INTO approve_table (email, leave_type, leave_date_start, leave_date_end)
            VALUES (%s, %s, %s, %s)
        """, (email, leave_type, apply_start_date, apply_end_date,))
    send_email_admin(
        f"No Reply - Leave Application Notification from {email}",
        f"""Please Don't reply to this email, this is an autogenerated email.
        
            Employee Name: {name} {surname} 
            Gmail: {email}
            Has applied for {leave_type} from {apply_start_date} to {apply_end_date}.
            Please review and take necessary action.
            Thank you.
            
            Regards,
            Automated Leave Management System""")
    
    send_email_emp(
        f"No Reply - Leave Application Submission Confirmation",
        f"""Please Don't reply to this email, this is an autogenerated email.
        
            Employee Name: {name} {surname}
            Gmail: {email} 
            Your leave application for {leave_type} from {apply_start_date} to {apply_end_date} has been submitted for approval.
            You will be notified once a decision has been made.
            Thank you.
            
            Regards,
            Automated Leave Management System""", email)
    sql.commit()
    return render_template("apply_leave.html", data = "Leave application sent for approval")


@app.route("/approve/<email>/<start>/<end>/<leave_type>/<dateon>")
def approve(email, start, end, leave_type, dateon):
    cursor.execute("SELECT name, surname FROM employee WHERE email = %s", (email,))
    name, surname = cursor.fetchone()

    cursor.execute("""
        INSERT INTO leave_record (email, leave_date_start, leave_date_end, leave_type, applyed_on, approve)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, start, end, leave_type, dateon, "Approved"))
    
    cursor.execute("""
        DELETE FROM approve_table
        WHERE email = %s AND leave_date_start = %s AND leave_date_end = %s AND leave_type = %s AND applyed_on = %s
    """, (email, start, end, leave_type, dateon))
    
    send_email_emp(
        f"No Reply - Leave Application Approved Notification",
        f"""Please Don't reply to this email, this is an autogenerated email.
        
            Employee Name: {name} {surname}
            Gmail: {email} 
            Your leave application for {leave_type} from {start} to {end} has been approved.
            Thank you.
            
            Regards,
            Automated Leave Management System""", email)
    sql.commit()
    return redirect("/approve_leave_page")


@app.route("/reject/<email>/<start>/<end>/<leave_type>/<dateon>")
def reject(email, start, end, leave_type, dateon):
    cursor.execute("SELECT name, surname FROM employee WHERE email = %s", (email,))
    name, surname = cursor.fetchone()
    
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = (end_date - start_date).days + 1

    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        cursor.execute(f"""
            UPDATE leave_remaining
            SET {leave_type} = {leave_type} + %s
            WHERE email = %s
        """, (days, email))
    
    cursor.execute("""
        INSERT INTO leave_record (email, leave_date_start, leave_date_end, leave_type, applyed_on, approve)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, start, end, leave_type, dateon, "Rejected"))
    
    cursor.execute("""
        DELETE FROM approve_table
        WHERE email = %s AND leave_date_start = %s AND leave_date_end = %s AND leave_type = %s AND applyed_on = %s
    """, (email, start, end, leave_type, dateon))

    send_email_emp(
        f"No Reply - Leave Application Rejected Notification",
        f"""Please Don't reply to this email, this is an autogenerated email.
            
            Employee Name: {name} {surname}
            Gmail: {email} 
            Your leave application for {leave_type} from {start} to {end} has been rejected.
            Please contact your administrator for more details.
            Thank you.
            
            Regards,
            Automated Leave Management System""", email)
    sql.commit()
    return redirect("/approve_leave_page")


@app.route("/cancel/<email>/<start>/<end>/<leave_type>/<dateon>")
def cancel_action(email, start, end, leave_type, dateon):
    cursor.execute("SELECT name, surname FROM employee WHERE email = %s", (email,))
    name, surname = cursor.fetchone()
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = (end_date - start_date).days + 1

    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        cursor.execute(f"""
            UPDATE leave_remaining
            SET {leave_type} = {leave_type} + %s
            WHERE email = %s
        """, (days, email))
    cursor.execute("""
        SELECT approve FROM approve_table
        WHERE email = %s AND leave_date_start = %s AND leave_date_end = %s AND leave_type = %s AND applyed_on = %s
    """, (email, start, end, leave_type, dateon))
    data = cursor.fetchone()
    if data != None:
        cursor.execute("""DELETE FROM approve_table
        WHERE email = %s AND leave_date_start = %s AND leave_date_end = %s AND leave_type = %s AND applyed_on = %s
    """, (email, start, end, leave_type, dateon))
        cursor.execute("""INSERT INTO leave_record
        (email, leave_date_start, leave_date_end, leave_type, applyed_on, approve)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, start, end, leave_type, dateon, "Cancelled"))
    else:
        cursor.execute("""
            UPDATE leave_record
            SET approve = 'Cancelled'
            WHERE email = %s AND leave_date_start = %s AND leave_date_end = %s AND leave_type = %s AND applyed_on = %s
        """, (email, start, end, leave_type, dateon))
    
    send_email_emp(
        f"No Reply - Leave Application Cancelled Confirmation",
        f"""Please Don't reply to this email, this is an autogenerated email.
        
            Employee Name: {name} {surname}
            Gmail: {email} 
            Your leave application for {leave_type} from {start} to {end} has been successfully cancelled.
            Thank you.
            
            Regards,
            Automated Leave Management System""", email)
    
    send_email_admin(
        f"No Reply - Leave Application Cancellation Notification from {email}",
        f"""Please Don't reply to this email, this is an autogenerated email.
        
            Employee Name: {name} {surname} 
            Gmail: {email}
            Has cancelled their leave application for {leave_type} from {start} to {end}.
            Thank you.
            
            Regards,
            Automated Leave Management System""")
    sql.commit()
    return redirect("/leavehistory_page")


@app.route("/add_leave_balance", methods=["POST"])
def add_leave_balance():
    name = session.get("user_name")
    surname = session.get("surname")
    email = session.get("email")
    
    to_email = request.form["to_email"]
    leave_type = request.form["leave_type"]
    days = int(request.form["days"])
    
    cursor.execute("SELECT name, surname FROM employee WHERE email = %s", (to_email,))
    data = cursor.fetchone()
    
    cursor.execute(f"""
        UPDATE leave_remaining
        SET {leave_type} = {leave_type} + %s
        WHERE email = %s
    """, (days, to_email))
    sql.commit()
    
    subject = "No Reply - Added Leave Balance Notification"
    body = f"""Please Don't reply to this email, this is an autogenerated email.

            Leave Added by: {name} {surname} and Gmail: {email}
            Employee Name: {data[0]} {data[1]}
            Gmail: {to_email}
            Leave balance has been updated. {days} days have been added to your {leave_type}.
            Thank you.
            
            Regards,
            Automated Leave Management System"""
    send_email_admin(subject, body)
    send_email_emp(subject, body, email)
    session["msg"] = f"Successfully added {days} {leave_type} days to {to_email}"
    return redirect("/add_leave_balance_page")


@app.route("/download_all_reports")
def download_all_reports():
    output = StringIO()
    if session.get("type") == 'admin':
        employees = cursor.execute("SELECT email, name, surname, department, join_date FROM employee").fetchall()

    if not employees:
        return "No employees found"

    for emp in employees:
        email = emp[0]
        name = emp[1]
        surname = emp[2]
        department = emp[3]
        join_date = emp[4]

        output.write("\n=============================\n")
        output.write(f"EMPLOYEE: {email} - {name} {surname}\n")
        output.write("=============================\n\n")

        cursor.execute("""
            SELECT Sick_Leave, Casual_Leave, Conpenstaion_off, Summer_Vacation
            FROM leave_remaining
            WHERE email = %s
        """, (email,))
        remain = cursor.fetchone()

        df_remain = pd.DataFrame([{
            "Email": email,
            "Name": name,
            "Surname": surname,
            "Department": department,
            "Join Date": join_date,
            "Sick_Leave Remaining": remain[0],
            "Casual_Leave Remaining": remain[1],
            "Conpenstaion_off Remaining": remain[2],
            "Summer_Vacation Remaining": remain[3],
        }])

        output.write("=== Leave Remaining ===\n")
        df_remain.to_csv(output, index=False)
        output.write("\n")

        cursor.execute("""
            SELECT leave_type, leave_date_start, leave_date_end, applyed_on, approve
            FROM leave_record
            WHERE email = %s
            ORDER BY leave_date_start DESC
        """, (email,))
        history = cursor.fetchall()
        
        today = datetime.now()
        last_30_days = today - timedelta(days=30)

        recent_records = []

        for row in history:
            applied_on = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
            if applied_on >= last_30_days:
                recent_records.append(row)
        if recent_records:
            df_history = pd.DataFrame(recent_records, columns=[
                "Leave Type", "Leave Start Date", "Leave End Date", "Applied On", "Approval Status"
            ])

            output.write("=== Leave History (Last 30 Days) ===\n")
            df_history.to_csv(output, index=False)
            output.write("\n")
        else:
            output.write("No leave records in the last 30 days.\n\n")

    csv_text = output.getvalue()

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=All_Employee_Monthly_Report.csv"}
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.before_request
def auto_logout():
    allowed_routes = [
        'home',
        'admin_login_page',
        'login',
        'admin_login',
        'forgot_password_page',
        'forgot_password',
        'send_forgot_sms'
    ]

    if request.endpoint in allowed_routes:
        return
    
    if "email" not in session:
        return redirect("/")

    now = time.time()
    last = session.get("last_activity")

    if last and (now - last > 300):
        session.clear()
        return redirect("/")

    session["last_activity"] = now
    

scheduler = BackgroundScheduler()
scheduler.add_job(auto_mark_absent, 'cron', hour=23, minute=59)
scheduler.add_job(auto_add_leave, 'cron', day=1, hour=0, minute=0)
scheduler.add_job(auto_summer_plan, 'cron', month=1, day=1, hour=0, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
