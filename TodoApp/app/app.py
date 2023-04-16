
import datetime
import re  
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s AND password = %s', (username, password,))
        user = cursor.fetchone()
        if user:
            # Create session data
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password!'
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
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, %s, %s, %s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'
    elif request.method == 'POST':
        message = 'Please fill all the fields!'
    return render_template('register.html', message=message)


@app.route('/tasks', methods =['GET', 'POST'])
def tasks():
    message = ""
    userid = session['userid']
    renewPage = False

    #edit task
    if request.method == 'POST' and 'title_edit' in request.form and 'description_edit' in request.form and 'deadline_edit' in request.form and 'task_type_edit' in request.form and 'taskid' in request.form:

        taskid = request.form['taskid']
        
        newtitle = request.form['title_edit']
        newdescription = request.form['description_edit']
        newdeadline = request.form['deadline_edit']
        newtype = request.form['task_type_edit']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET title = %s, description = %s, deadline = %s, task_type = %s WHERE id = %s', (newtitle, newdescription, newdeadline, newtype, taskid,))
        mysql.connection.commit()
        cursor.close()
        renewPage = True

    #mark task as completed
    if request.method == 'POST' and 'done_taskid' in request.form:
        
        donetaskid = request.form['done_taskid']
        donetimedone = datetime.datetime.utcnow()+datetime.timedelta(hours=3)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Task SET status = %s, done_time = %s WHERE id = %s', ('Done', donetimedone,donetaskid,))
        mysql.connection.commit()
        cursor.close()
        renewPage = True

    #delete task
    if request.method == 'POST' and 'del_taskid' in request.form:
        
        deltaskid = request.form['del_taskid']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM Task WHERE id = %s', ( deltaskid,))
        mysql.connection.commit()
        cursor.close()
        renewPage = True

    #create new task
    if request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'deadline' in request.form and 'type' in request.form:
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        type = request.form['type']
        creationTime = datetime.datetime.utcnow()+datetime.timedelta(hours=3)
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Task (user_id, title, description, deadline, task_type, creation_time, status) VALUES (% s, % s, % s, % s, %s, %s, %s)', (userid, title, description, deadline, type, creationTime, 'Todo',))
        mysql.connection.commit()
        cursor.close()
        renewPage = True
    
    #load/reload page
    if(request.method == 'GET' or renewPage):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT T.id,title, description, creation_time, deadline, task_type, status FROM User U, Task T WHERE U.id = T.user_id and T.status = % s  and U.id = % s ORDER BY deadline ASC', ('Todo', userid,))
        userTasks = cursor.fetchall()

        cursor.execute('SELECT T.id,title, description, creation_time, deadline, done_time, task_type, T.status FROM User U, Task T WHERE U.id = T.user_id and T.status = % s and U.id = % s ORDER BY done_time ASC', ('Done', userid,))
        completedTasks = cursor.fetchall()

        cursor.execute('SELECT type FROM TaskType')
        alltasktypes = cursor.fetchall()

        cursor.close()

        if not userTasks:
            message = "There are no incomplete tasks at the moment"
        if not completedTasks:
            message = "There are no complete tasks at the moment"
            
    return render_template('main.html', message = message, tasks = userTasks, incomTasks = completedTasks, tasktypes = alltasktypes) 

@app.route('/analysis', methods=['GET'])
def analysis():
    
    userid = session['userid']

    # 1. List the title and latency of the tasks that were completed after their deadlines (for the user)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT title, TIMESTAMPDIFF(MINUTE, deadline, done_time) AS latency FROM Task WHERE user_id = %s AND status = %s AND done_time > deadline ORDER BY done_time ASC', (userid, 'Done',))
    tasksAfterDeadline = cursor.fetchall()

    # 2. Give the average task completion time of the user.
    cursor.execute('SELECT AVG(TIMESTAMPDIFF(MINUTE, creation_time, done_time)) AS avg_completion_time FROM Task WHERE user_id = %s AND status = %s', (userid, 'Done',))
    avgCompletionTime = cursor.fetchone()['avg_completion_time']

    # 3. List the number of the completed tasks per task type, in descending order (for the user).
    cursor.execute('SELECT task_type, COUNT(*) AS count FROM Task WHERE user_id = %s AND status = %s GROUP BY task_type ORDER BY count DESC', (userid, 'Done',))
    completedTasksByType = cursor.fetchall()

    # 4. List the title and deadline of uncompleted tasks in increasing order of deadlines (for the user).
    cursor.execute('SELECT title, deadline FROM Task WHERE user_id = %s AND status = %s AND deadline > NOW() ORDER BY deadline ASC', (userid, 'Todo',))
    uncompletedTasksByDeadline = cursor.fetchall()

    # 5. List the title and task completion time of the top 2 completed tasks that took the most time, in
    #descending order (for the user). (You can use the LIMIT clause).
    cursor.execute('SELECT title, TIMESTAMPDIFF(MINUTE, creation_time, done_time) AS completion_time FROM Task WHERE user_id = %s AND status = %s ORDER BY completion_time DESC LIMIT 2', (userid, 'Done',))
    topCompletedTasks = cursor.fetchall()

    cursor.close()

    return render_template('analysis.html', tasks_after_deadline=tasksAfterDeadline, avg_completion_time=avgCompletionTime, completed_tasks_by_type=completedTasksByType, uncompleted_tasks_by_deadline=uncompletedTasksByDeadline, top_completed_tasks=topCompletedTasks)


@app.route('/logout')
def logout():

    #delete info of prev. session
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('email', None)

    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
