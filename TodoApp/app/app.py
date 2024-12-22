import re
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'abcdefgh'  # Secret key for session management
app.permanent_session_lifetime = datetime.timedelta(days=7)  # Optional: set session expiration time

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Change if you have a password
app.config['MYSQL_DB'] = 'cs353hw4db'  # Change this to your database name

mysql = MySQL(app)  # Initialize MySQL

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            # Create session data
            session.permanent = True  # Ensure session persists
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Incorrect username or password!'
    return render_template('login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
        elif not username or not password or not email:
            message = 'Please fill out the form!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, %s, %s, %s)', 
                           (username, email, hashed_password,))
            mysql.connection.commit()
            message = 'User successfully created!'
    return render_template('register.html', message=message)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    message = ""
    userid = session['userid']
    renewPage = False
    userTasks = []
    completedTasks = []

    # Create new task
    if request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'deadline' in request.form and 'task_type' in request.form:
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        task_type = request.form['task_type']
        creationTime = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

        # Check if the deadline format is correct (dd/mm/yyyy)
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', deadline):
            flash('Invalid date format. Please use dd/mm/yyyy.', 'error')
            return redirect(url_for('tasks'))

        try:
            # Convert the deadline to a datetime object
            deadline_date = datetime.datetime.strptime(deadline, '%d/%m/%Y')
        except ValueError:
            flash('Invalid date. Please select a valid date.', 'error')
            return redirect(url_for('tasks'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Task (user_id, title, description, deadline, task_type, creation_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (userid, title, description, deadline_date, task_type, creationTime, 'Todo',))
        mysql.connection.commit()
        cursor.close()
        flash('Task added successfully!', 'success')
        renewPage = True

    # Edit task
    if request.method == 'POST' and 'title_edit' in request.form and 'description_edit' in request.form and 'deadline_edit' in request.form and 'task_type_edit' in request.form and 'taskid' in request.form:
        taskid = request.form['taskid']
        newtitle = request.form['title_edit']
        newdescription = request.form['description_edit']
        newdeadline = request.form['deadline_edit']
        newtype = request.form['task_type_edit']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET title = %s, description = %s, deadline = %s, task_type = %s WHERE id = %s',
                       (newtitle, newdescription, newdeadline, newtype, taskid,))
        mysql.connection.commit()
        cursor.close()
        flash('Task updated successfully!', 'success')
        renewPage = True

    # Mark task as completed
    if request.method == 'POST' and 'done_taskid' in request.form:
        donetaskid = request.form['done_taskid']
        donetimedone = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET status = %s, done_time = %s WHERE id = %s',
                       ('Done', donetimedone, donetaskid,))
        mysql.connection.commit()
        cursor.close()
        renewPage = True

    # Delete task
    if request.method == 'POST' and 'del_taskid' in request.form:
        deltaskid = request.form['del_taskid']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM Task WHERE id = %s', (deltaskid,))
        mysql.connection.commit()
        cursor.close()
        renewPage = True

    # Load tasks
    if request.method == 'GET' or renewPage:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT T.id, title, description, creation_time, deadline, task_type, status FROM User U, Task T WHERE U.id = T.user_id AND T.status = %s AND U.id = %s ORDER BY deadline ASC',
                       ('Todo', userid,))
        userTasks = cursor.fetchall()

        cursor.execute('SELECT T.id, title, description, creation_time, deadline, done_time, task_type, T.status FROM User U, Task T WHERE U.id = T.user_id AND T.status = %s AND U.id = %s ORDER BY done_time ASC',
                       ('Done', userid,))
        completedTasks = cursor.fetchall()

        cursor.close()

        if not userTasks:
            message = "There are no incomplete tasks at the moment"
        if not completedTasks:
            message = "There are no completed tasks at the moment"

    return render_template('main.html', message=message, tasks=userTasks, incomTasks=completedTasks)

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if 'userid' in session:  # Changed 'user_id' to 'userid' to match your session key
        # Update task status in the database
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Task SET status = 'Done', done_time = %s WHERE id = %s", 
                       (datetime.datetime.utcnow() + datetime.timedelta(hours=3), task_id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'userid' in session:  # Ensure user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch the current task details to pre-fill the form
        cursor.execute("SELECT * FROM Task WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        
        if not task:
            flash("Task not found!", "error")
            return redirect(url_for('tasks'))
        
        if request.method == 'POST':  # Handle form submission
            title = request.form.get('title')
            description = request.form.get('description')
            deadline = request.form.get('deadline')
            task_type = request.form.get('task_type')

            if not all([title, description, deadline, task_type]):
                flash("All fields are required!", "error")
                return render_template('edit_task.html', task=task)

            # Update the task in the database
            cursor.execute("""
                UPDATE Task 
                SET title = %s, description = %s, deadline = %s, task_type = %s 
                WHERE id = %s
            """, (title, description, deadline, task_type, task_id))
            mysql.connection.commit()
            cursor.close()

            flash("Task updated successfully!", "success")
            return redirect(url_for('tasks'))
        
        cursor.close()
        return render_template('edit_task.html', task=task)  # Render the edit form with task details

    flash("Please log in to edit tasks!", "error")
    return redirect(url_for('login'))

@app.route('/overview', methods=['GET'])
def overview():
    userid = session['userid']

    # Get all tasks
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Task WHERE user_id = %s ORDER BY deadline', (userid,))
    allTasks = cursor.fetchall()

    # Tasks after deadline
    cursor.execute('SELECT title, TIMESTAMPDIFF(MINUTE, deadline, done_time) AS latency FROM Task WHERE user_id = %s AND status = %s AND done_time > deadline ORDER BY done_time ASC', (userid, 'Done',))
    tasksAfterDeadline = cursor.fetchall()

    # Completed tasks
    cursor.execute('SELECT title, done_time FROM Task WHERE user_id = %s AND status = %s ORDER BY done_time DESC', (userid, 'Done',))
    completedTasks = cursor.fetchall()

    # Uncompleted tasks
    cursor.execute('SELECT title, deadline FROM Task WHERE user_id = %s AND status = %s ORDER BY deadline ASC', (userid, 'Todo',))
    uncompletedTasks = cursor.fetchall()

    cursor.close()

    return render_template('overview.html', allTasks=allTasks, tasksAfterDeadline=tasksAfterDeadline, completedTasks=completedTasks, uncompletedTasks=uncompletedTasks)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
