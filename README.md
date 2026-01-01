📌 Student Task Manager — Flask Web Application

A role-based Task Management System built using Flask & SQLite.
Supports authentication (Admin & Student), CRUD operations, task filters, comments, and an activity log — with a modern Bootstrap UI.

🚀 Features
👤 Authentication & Roles

Admin & Student roles

Secure login / logout

Session-based access control

Students can manage only their tasks

Admin can view all tasks

📝 Task Management (CRUD)

Create / Edit / Delete tasks

Priority levels
✔ Low ✔ Medium ✔ High

Status
✔ Pending ✔ In-Progress ✔ Completed

Deadline tracking

Created & Updated timestamps

<img width="1920" height="937" alt="Screenshot 2026-01-01 102409" src="https://github.com/user-attachments/assets/a04aa54f-b0dc-4a5a-a871-0c56f9c40d2e" />

🔎 Search & Filters

Search by title / description

Filter by:

Status

Priority

Deadline

Sort by latest created

💬 Collaboration Features

Add comments on tasks

Track who commented

Timestamp history

🧾 Activity Log (Audit Trail)

Tracks actions such as:

Task Created

Task Updated

Task Deleted

Comment Added

Stores:

user

action

timestamp

🎨 Modern UI

Built with Bootstrap:

Dashboard layout

Status & priority badges

Clean buttons & table styling

Mobile responsive

🛠 Tech Stack

Backend

Python

Flask

Database

SQLite

Frontend

HTML

Bootstrap 5

Other

Jinja Templates

Werkzeug Security (password hashing)

📂 Project Structure
student_task_manager/
 ├─ app.py
 ├─ templates/
 │   ├─ index.html
 │   ├─ add_task.html
 │   ├─ edit_task.html
 │   ├─ view_task.html
 │   ├─ login.html
 │   └─ register.html
 ├─ database.db (auto-generated)
 └─ README.md

▶️ Run Locally
1️⃣ Install dependencies
pip install flask

2️⃣ Run the app
python app.py

3️⃣ Open in browser
http://127.0.0.1:5000/

👤 Default Admin Account
Email : admin@example.com
Password : admin123


You can register Student accounts separately.

🎯 Possible Enhancements (Future Work)

Dashboard analytics & charts

Email notifications

File attachments

REST API + Postman docs

Cloud deployment (Render / PythonAnywhere)

📖 Learning Outcomes

This project demonstrates:

Flask backend development

Database modeling & relationships

Authentication & role-based access

CRUD operations

Form handling & validation

Activity logging

UI design using Bootstrap

Software development workflow

🏆 Author

Vasudha Sekireddy

Aspiring Full-Stack / Backend Developer
