from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key_replace_later"


# ---------- DB CONNECTION ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------- CREATE TABLES ----------
def create_tables():
    conn = get_db()

    # USERS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # TASKS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            status TEXT,
            priority TEXT,
            deadline TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # COMMENTS
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            user_id INTEGER,
            comment TEXT,
            created_at TEXT
        )
    """)

    # ACTIVITY LOG
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            user_id INTEGER,
            action TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# ---------- DEFAULT ADMIN ----------
def create_admin():
    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM users WHERE email=?",
        ("admin@example.com",)
    ).fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            ("Admin User",
             "admin@example.com",
             generate_password_hash("admin123"),
             "admin")
        )
        conn.commit()

    conn.close()


create_admin()


# ---------- ACTION LOG ----------
def log_action(task_id, user_id, action):
    conn = get_db()
    conn.execute(
        "INSERT INTO activity_log (task_id, user_id, action, timestamp) VALUES (?, ?, ?, ?)",
        (task_id, user_id, action,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


# ---------- LOGIN CHECK ----------
def login_required():
    return "user_id" in session


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            return redirect("/")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- REGISTER STUDENT ----------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password, "student")
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------- HOME / LIST TASKS ----------
@app.route("/", methods=["GET"])
def index():

    if not login_required():
        return redirect("/login")

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    deadline = request.args.get("deadline", "")

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    # student sees only their tasks
    if session["role"] == "student":
        query += " AND user_id=?"
        params.append(session["user_id"])

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if status and status != "All":
        query += " AND status=?"
        params.append(status)

    if priority and priority != "All":
        query += " AND priority=?"
        params.append(priority)

    if deadline:
        query += " AND deadline <= ?"
        params.append(deadline)

    query += " ORDER BY created_at DESC"

    conn = get_db()
    tasks = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


# ---------- ADD TASK ----------
@app.route("/add", methods=["GET", "POST"])
def add_task():

    if not login_required():
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        priority = request.form["priority"]
        deadline = request.form["deadline"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, status, priority, deadline, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["user_id"], title, description, status,
              priority, deadline, now, now))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        log_action(task_id, session["user_id"], "Task Created")

        return redirect("/")

    return render_template("add_task.html")


# ---------- VIEW TASK ----------
@app.route("/view/<int:id>")
def view_task(id):

    if not login_required():
        return redirect("/login")

    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id=?",
        (id,)
    ).fetchone()

    comments = conn.execute("""
        SELECT c.comment, c.created_at, u.name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE task_id=?
        ORDER BY c.created_at DESC
    """, (id,)).fetchall()

    activity = conn.execute("""
        SELECT a.action, a.timestamp, u.name
        FROM activity_log a
        JOIN users u ON a.user_id = u.id
        WHERE task_id=?
        ORDER BY a.timestamp DESC
    """, (id,)).fetchall()

    conn.close()

    return render_template(
        "view_task.html",
        task=task,
        comments=comments,
        activity=activity
    )


# ---------- ADD COMMENT ----------
@app.route("/comment/<int:task_id>", methods=["POST"])
def add_comment(task_id):

    if not login_required():
        return redirect("/login")

    comment = request.form["comment"]

    conn = get_db()
    conn.execute("""
        INSERT INTO comments (task_id, user_id, comment, created_at)
        VALUES (?, ?, ?, ?)
    """, (task_id, session["user_id"], comment,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    log_action(task_id, session["user_id"], "Comment Added")

    return redirect(f"/view/{task_id}")


# ---------- EDIT TASK ----------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    if not login_required():
        return redirect("/login")

    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()

    if session["role"] == "student" and task["user_id"] != session["user_id"]:
        conn.close()
        return "Unauthorized"

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        status = request.form["status"]
        priority = request.form["priority"]
        deadline = request.form["deadline"]

        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            UPDATE tasks SET title=?, description=?, status=?, priority=?, deadline=?, updated_at=?
            WHERE id=?
        """, (title, description, status, priority, deadline, updated, id))

        conn.commit()
        conn.close()

        log_action(id, session["user_id"], "Task Updated")

        return redirect("/")

    conn.close()
    return render_template("edit_task.html", task=task)


# ---------- DELETE TASK ----------
@app.route("/delete/<int:id>")
def delete_task(id):

    if not login_required():
        return redirect("/login")

    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()

    if session["role"] == "student" and task["user_id"] != session["user_id"]:
        conn.close()
        return "Unauthorized"

    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    log_action(id, session["user_id"], "Task Deleted")

    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
