import pandas as pd
import sqlite3
import time
import smtplib
import random


from datetime import datetime, date, timedelta
from io import StringIO
from flask import Flask, render_template, request, redirect, session, Response, jsonify

sql = sqlite3.connect("data.db", check_same_thread=False)
cursor = sql.cursor()


cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employee (
    designation TEXT,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    department TEXT NOT NULL,
    password TEXT NOT NULL,
    join_date TEXT NOT NULL,
    PRIMARY KEY (email)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_table (
    designation TEXT,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    department TEXT NOT NULL,
    password TEXT NOT NULL,
    join_date TEXT NOT NULL,
    PRIMARY KEY (email)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_record (
    email TEXT NOT NULL,
    leave_date_start TEXT NOT NULL,
    leave_date_end TEXT NOT NULL,
    leave_type TEXT CHECK(leave_type IN ('Sick_Leave', 'Casual_Leave', 'Conpenstaion_off','Summer_Vacation','Planed_Leave','Duty_Leave','Early_Leave')) NOT NULL,
    applyed_on TEXT DEFAULT (DATE('now')),
    approve TEXT NOT NULL,
    message TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_remaining (
    email TEXT NOT NULL,
    Sick_Leave FLOAT DEFAULT 0,
    Casual_Leave FLOAT DEFAULT 0,
    Conpenstaion_off FLOAT DEFAULT 0,
    Summer_Vacation FLOAT DEFAULT 0,
    Planed_Leave FLOAT DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS approve_table (
    email TEXT NOT NULL,
    leave_type TEXT CHECK(leave_type IN ('Sick_Leave', 'Casual_Leave', 'Conpenstaion_off','Summer_Vacation','Planed_Leave','Duty_Leave','Early_Leave')) NOT NULL,
    leave_date_start TEXT NOT NULL,
    leave_date_end TEXT NOT NULL,
    applyed_on TEXT DEFAULT (datetime('now','localtime')),
    approve TEXT NOT NULL DEFAULT 'Pending',
    message TEXT NOT NULL
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS admin_email (email)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sms_table 
    (email TEXT PRIMARY KEY, sms TEXT, timestamp DATETIME)""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO system_config (key, value)
    VALUES ('last_leave_update', ?)
""",((date.today().isoformat(),)))

sql.commit()


def auto_add_leave(today, last_update):
    today = date.fromisoformat(today)
    last_update = date.fromisoformat(last_update)
    if today.month != last_update.month or today.year != last_update.year:
        cursor.execute("""
            UPDATE leave_remaining
            SET Sick_Leave = Sick_Leave + 0.83,
                Casual_Leave = Casual_Leave + 1
        """)
        today_save = today.isoformat()
        cursor.execute("""
            UPDATE system_config
            SET value = ?
            WHERE key = 'last_leave_update'
        """, (today_save,))

    if today.year != last_update.year:
        cursor.execute("""
            SELECT Summer_Vacation, Planed_Leave FROM leave_remaining
        """)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] > 60:
                cursor.execute("""
                    UPDATE leave_remaining
                    SET Summer_Vacation = 60
                """)
            if row[1] > 60:
                cursor.execute("""
                    UPDATE leave_remaining
                    SET Planed_Leave = 12
                """)
    sql.commit()


def outer_add_emp( designation, email, name, surname, department, password, type, join_date):
    email = email.lower()

    if email != f"{name.lower()}.{surname.lower()}@gnims.com":
        return "Invalid email format OR name/surname does not match!"

    if type == 'admin':
        cursor.execute("SELECT email FROM admin_table WHERE email = ?", (email,))
        if cursor.fetchone():
            return f"Admin {email} already exists!"

        cursor.execute("""
            INSERT INTO admin_table
            (designation, email, name, surname, department, password, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (designation, email, name, surname, department, password, join_date))

        cursor.execute(
            "INSERT INTO leave_remaining (email) VALUES (?)",
            (email,)
        )
                
        cursor.execute("""INSERT OR IGNORE INTO admin_email (email) VALUES (?)
                       """, (email,))
        
        sql.commit()
        return f"Admin {email} added successfully!"
    else:
        cursor.execute("SELECT email FROM employee WHERE email = ?", (email,))
        if cursor.fetchone():
            return f"Employee {email} already exists!"

        cursor.execute("""
            INSERT INTO employee
            ( designation, email, name, surname, department, password, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (designation, email, name, surname, department, password, join_date))

        cursor.execute(
            "INSERT INTO leave_remaining (email) VALUES (?)",
            (email,)
        )

        sql.commit()
        return f"Employee {email} added successfully!"
outer_add_emp("MR", "anurag.yadav@gnims.com", "Anurag", "Yadav", "IT", "123", "admin", "2025-06-25")


def update_last_activity():
    session['last_activity'] = time.time()

def send_email_admin(subject, body):
    to_address = cursor.execute("SELECT email FROM admin_email").fetchone()
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
      WHERE email = ?
    """, (session.get("email"),))

    balance = cursor.fetchone()

    return render_template("employee_dashboard.html", balance=balance)


@app.route("/leavehistory_page")
def leavehistory_page():
    email = session.get("email")
    cursor.execute("""
        SELECT leave_type, leave_date_start, leave_date_end, approve, applyed_on
        FROM leave_record
        WHERE email = ?
        UNION ALL
        SELECT leave_type, leave_date_start, leave_date_end, approve, applyed_on
        FROM approve_table
        WHERE email = ?
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
        FROM employee WHERE EMAIL = ? AND PASSWORD = ?
    """, (email, password))

    data = cursor.fetchone()
    sql.commit()

    if data is None:
        return render_template("login.html", data="Invalid Email or Password Credential")

    session["designation"] = data[0]
    session["type"] = "employee"
    session["email"] = email
    session["user_name"] = data[1]
    session["surname"] = data[2]
    session["department"] = data[3]
    session["join_date"] = data[4]
    update_last_activity()

    return redirect("/dashboard_page")


@app.route("/admin_login", methods=["POST"])
def admin_login():
    email = request.form["email"].lower()
    password = request.form["password"]

    cursor.execute("""
        SELECT designation, name, surname, department, join_date
        FROM admin_table WHERE EMAIL = ? AND PASSWORD = ?
    """, (email, password))

    data = cursor.fetchone()
    sql.commit()

    if data is None:
        return render_template("admin_login.html", data="Invalid Email or Password Credential")

    session["designation"] = data[0]
    session["type"] = "admin"
    session["email"] = email
    session["user_name"] = data[1]
    session["surname"] = data[2]
    session["department"] = data[3]
    session["join_date"] = data[4]
    update_last_activity()

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

    cursor.execute("SELECT sms FROM sms_table WHERE email = ?", (email,))
    sms_record = cursor.fetchone()
    
    if sms_record == None:
        return render_template("/forgot_password.html", data="Email code is required please Send the code", step = '1')
    cursor.execute("""
        SELECT timestamp FROM sms_table WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    expire = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")

    if datetime.now() - expire > timedelta(minutes=5):
        cursor.execute("DELETE FROM sms_table WHERE email = ?", (email,))
        sql.commit()
        return render_template("/forgot_password.html", data="OTP expired Please resend the OTP")

    if sms != sms_record[0]:
        return render_template("/forgot_password.html", data="Invalid SMS code", step="2", email = email, type = type)

    if type == 'admin':
        cursor.execute("UPDATE admin_table SET password = ? WHERE email = ?", (new_password, email,))
    else:
        cursor.execute("UPDATE employee SET password = ? WHERE email = ?", (new_password, email,))
    cursor.execute("DELETE FROM sms_table WHERE email = ?", (email,))
    sql.commit()
    
    return render_template("/forgot_password.html", data="Password Updated Successfully")


@app.route("/send_forgot_sms", methods=["POST"])
def send_forgot_sms():
    email = request.form["email"]
    type = request.form["type"]
    
    if type == "admin":
        cursor.execute("SELECT email FROM admin_table WHERE email = ?", (email,))
    else:
        cursor.execute("SELECT email FROM employee WHERE email = ?", (email,))

    if cursor.fetchone() is None:
        return render_template('/forgot_password.html', data = 'Email Not Register')
    
    sms_code = random.randint(100000, 999999)
    cursor.execute("""INSERT OR REPLACE INTO sms_table (email, sms, timestamp)
                   VALUES (?, ?, ?)""",
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
    return redirect(f"/forgot_password_page?email={email}&type={type}&step=2")


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

    cursor.execute(f"SELECT {leave_type} FROM leave_remaining WHERE email = ?", (email,))
    remain = cursor.fetchone()
    
    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        if remain[0] == 0:
            return render_template("apply_leave.html", data = f"{leave_type} leave stack is empty — cannot apply!")
        count = (datetime.strptime(apply_end_date, "%Y-%m-%d") - datetime.strptime(apply_start_date, "%Y-%m-%d")).days + 1
        if remain[0] < count:
            return render_template("apply_leave.html", data = f"Insufficient {leave_type} Balance, you are trying to apply for {count} days and your leave balance is {int(remain[0])} days.")
    
    cursor.execute("""
            SELECT * FROM approve_table
            WHERE email = ? AND leave_date_start = ?
    """, (email, apply_start_date))
    data = cursor.fetchall()
    if data:
        return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_start_date}.")
    
    cursor.execute("""
            SELECT approve FROM leave_record
            WHERE email = ? AND leave_date_start = ?
    """, (email, apply_start_date))
    data = cursor.fetchall()
    for row in data:
        if row[0] == 'Approved':
            return render_template("apply_leave.html", data = f"You have already applied for leave on this date {apply_start_date}.")
        
    cursor.execute("""
            INSERT INTO approve_table (email, leave_type, leave_date_start, leave_date_end)
            VALUES (?, ?, ?, ?)
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
    cursor.execute("SELECT name, surname FROM employee WHERE email = ?", (email,))
    name, surname = cursor.fetchone()

    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        cursor.execute(f"""
            UPDATE leave_remaining
            SET {leave_type} = {leave_type} - ?
            WHERE email = ?
        """, ((end_date - start_date).days + 1, email,))

    cursor.execute("""
        INSERT INTO leave_record (email, leave_date_start, leave_date_end, leave_type, applyed_on, approve)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email, start, end, leave_type, dateon, "Approved"))
    
    cursor.execute("""
        DELETE FROM approve_table
        WHERE email = ? AND leave_date_start = ? AND leave_date_end = ? AND leave_type = ? AND applyed_on = ?
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
    cursor.execute("SELECT name, surname FROM employee WHERE email = ?", (email,))
    name, surname = cursor.fetchone()
    
    cursor.execute("""
        INSERT INTO leave_record (email, leave_date_start, leave_date_end, leave_type, applyed_on, approve)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email, start, end, leave_type, dateon, "Rejected"))
    
    cursor.execute("""
        DELETE FROM approve_table
        WHERE email = ? AND leave_date_start = ? AND leave_date_end = ? AND leave_type = ? AND applyed_on = ?
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
    cursor.execute("SELECT name, surname FROM employee WHERE email = ?", (email,))
    name, surname = cursor.fetchone()
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = (end_date - start_date).days + 1

    if leave_type != 'Duty_Leave' and leave_type != 'Early_Leave':
        cursor.execute(f"""
            UPDATE leave_remaining
            SET {leave_type} = {leave_type} + ?
            WHERE email = ?
        """, (days, email))

    cursor.execute("""
        UPDATE leave_record
        SET approve = 'Cancelled'
        WHERE email = ? AND leave_date_start = ? AND leave_date_end = ? AND leave_type = ? AND applyed_on = ?
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
    
    cursor.execute("SELECT name, surname FROM employee WHERE email = ?", (to_email,))
    emp_name, emp_surname = cursor.fetchone()
    
    cursor.execute(f"""
        UPDATE leave_remaining
        SET {leave_type} = {leave_type} + ?
        WHERE email = ?
    """, (days, to_email))
    sql.commit()
    
    subject = "No Reply - Added Leave Balance Notification"
    body = f"""Please Don't reply to this email, this is an autogenerated email.

            Leave Added by: {name} {surname} and Gmail: {email}
            Employee Name: {emp_name} {emp_surname}
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
        email, name, surname, department, join_date = emp

        output.write("\n=============================\n")
        output.write(f"EMPLOYEE: {email} - {name} {surname}\n")
        output.write("=============================\n\n")

        cursor.execute("""
            SELECT Sick_Leave, Casual_Leave, Conpenstaion_off, Summer_Vacation
            FROM leave_remaining
            WHERE email = ?
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
            WHERE email = ?
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
    
    today = date.today()
    last_update_str = cursor.execute("SELECT value FROM system_config WHERE key='last_leave_update'").fetchone()[0]
    last_update = date.fromisoformat(last_update_str)
    if today.month != last_update.month or today.year != last_update.year:
        auto_add_leave(today, last_update)


if __name__ == "__main__":
    app.run(debug=True)
