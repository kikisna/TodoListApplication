## ToDo List Application

This Task Management System, built with Python (Flask) and MySQL, lets users register, log in, and manage tasks—create, edit, complete, or delete. The application categorizes tasks into three lists: Pending Tasks, Completed Tasks and Uncompleted task. Key features include secure password hashing, session management, flash messages for feedback, and a user-friendly interface powered by Flask's HTML templates.

## Features

### User Authentication
Register a new account.
Login and maintain a session.
Logout functionality.

### Task Management
Add new tasks with a title, description, deadline, and type.
Edit tasks to update details.
Mark tasks as completed.
Delete tasks.

### Overview Page
View all tasks, grouped into completed and uncompleted tasks.
Display tasks completed and uncompleted tasks.

### Session Management
Sessions are securely managed with Flask sessions.
A session lifetime of 7 days ensures user persistence.

### Security Features
Passwords are hashed using werkzeug.security (SHA256).
CSRF protection and input validation.

## Project Setup

### Prequisites
Install Python (v3.8 or higher).
Install MySQL and set up a local server.
Install Python dependencies listed in requirements.txt.

### Database Setup
Create a MySQL database named cs353hw4db
Create the required tables with the following structure:
Visit schema.sql

## Installation Steps
Clone the repository:
git clone https://github.com/kikisna/TodoListApplication.git

Install Python dependencies:
pip install -r requirements.txt

Run the Flask application:
python app.py

## Usage

### Registration and Login
Access the login page at the root URL (/ or /login).
Click on "Register" to create a new account.
Log in with your credentials.

### Task Management
Add Task: Fill out the form on the main page to add tasks.
Edit Task: Click the "Edit" button on a task to modify its details.
Complete Task: Mark a task as done by clicking "Mark as Complete."
Delete Task: Remove a task permanently

### Overview
Navigate to /overview to view detailed task statistics, including:
Tasks grouped as completed or uncompleted.
Where you can perform the edit and deletion of tasks.

### Logout
Click the "Logout" button to securely end the session.

## Future Enhancements
Add analytics features that track user productivity, such as the average time spent on tasks, completion rates, and overdue tasks.

Add task prioritization and categorization features. Users could assign priorities (e.g., low, medium, high) or categories (e.g., work, personal, urgent) to each task.

Develop a mobile app version of the task management system to allow users to manage their tasks on the go.

## References and Resources
GeeksforGeeks. (n.d.). Hashing passwords in Python with bcrypt. GeeksforGeeks. Retrieved December 21, 2024, from https://www.geeksforgeeks.org%2fhashing-passwords-in-python-with-bcrypt

onurcanatac. onurcanatac/TodoListApplication: Advanced ToDo List app. Retrieved December 21, 2024, from https://github.com/onurcanatac/TodoListApplication.git