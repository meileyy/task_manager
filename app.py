"""
Task Manager RESTful API (Flask + SQLite + JWT Auth)

Run:
    pip install flask flask-cors flask-sqlalchemy bcrypt pyjwt
    python app.py

The API will be available at http://localhost:5000

Auth flow:
    1. POST /register with {username, password}
    2. POST /login    with {username, password}  -> returns a JWT token
    3. Pass the token in subsequent requests:
        Authorization: Bearer <token>
"""

import os
from datetime import datetime, timedelta, timezone, date
from functools import wraps

import bcrypt
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'taskmanager.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production-please")
app.config["JWT_EXP_HOURS"] = 12

db = SQLAlchemy(app)

VALID_STATUSES = {"pending", "in-progress", "done"}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)  # bcrypt hash

    tasks = db.relationship(
        "Task",
        backref="owner",
        cascade="all, delete-orphan",
        lazy=True,
        foreign_keys="Task.user_id",
    )
    assigned_tasks = db.relationship(
        "Task",
        backref="assignee",
        lazy=True,
        foreign_keys="Task.assigned_to",
    )

    def set_password(self, plain_password: str) -> None:
        self.password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.password)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True, default="")
    status = db.Column(db.String(20), nullable=False, default="pending")
    due_date = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def to_dict(self) -> dict:
        assignee_dict = None
        if self.assigned_to is not None:
            assignee = db.session.get(User, self.assigned_to)
            if assignee is not None:
                assignee_dict = {"id": assignee.id, "username": assignee.username}
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "status": self.status,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "user_id": self.user_id,
            "assigned_to": assignee_dict,
        }


def parse_assigned_to(value):
    """Validate an assigned_to user id.

    Returns (parsed, error):
        parsed: int | None  (None means "clear the field")
        error:  str | None
    """
    if value is None or value == "":
        return None, None
    try:
        user_id = int(value)
    except (TypeError, ValueError):
        return None, "'assigned_to' must be an integer user id"
    if db.session.get(User, user_id) is None:
        return None, f"User {user_id} does not exist"
    return user_id, None


def parse_due_date(value):
    """Parse a 'YYYY-MM-DD' string into a date object.

    Returns a tuple (parsed, error):
        parsed: date | None  (None means "clear the field")
        error:  str  | None
    """
    if value is None or value == "":
        return None, None
    if not isinstance(value, str):
        return None, "'due_date' must be a string in YYYY-MM-DD format"
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, "'due_date' must be in YYYY-MM-DD format"


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=app.config["JWT_EXP_HOURS"]),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = db.session.get(User, payload.get("user_id"))
        if user is None:
            return jsonify({"error": "User not found"}), 401

        return f(user, *args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "'username' and 'password' are required"}), 400

    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "user_id": user.id}), 201


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "'username' and 'password' are required"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(user.id)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "username": user.username,
        "user_id": user.id,
    }), 200


# ---------------------------------------------------------------------------
# Task routes (all protected)
# ---------------------------------------------------------------------------

@app.route("/users", methods=["GET"])
@token_required
def list_users(current_user):
    users = User.query.order_by(User.username.asc()).all()
    return jsonify([{"id": u.id, "username": u.username} for u in users]), 200


@app.route("/tasks", methods=["GET"])
@token_required
def get_tasks(current_user):
    tasks = (
        Task.query
        .filter(or_(Task.user_id == current_user.id, Task.assigned_to == current_user.id))
        .order_by(Task.id.asc())
        .all()
    )
    return jsonify([t.to_dict() for t in tasks]), 200


@app.route("/tasks", methods=["POST"])
@token_required
def create_task(current_user):
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "'title' is required and must be a non-empty string"}), 400

    description = data.get("description", "")
    if description is not None and not isinstance(description, str):
        return jsonify({"error": "'description' must be a string"}), 400

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"'status' must be one of {sorted(VALID_STATUSES)}"}), 400

    due_date, err = parse_due_date(data.get("due_date"))
    if err:
        return jsonify({"error": err}), 400

    assigned_to, err = parse_assigned_to(data.get("assigned_to"))
    if err:
        return jsonify({"error": err}), 400

    task = Task(
        title=title.strip(),
        description=(description or "").strip(),
        status=status,
        due_date=due_date,
        assigned_to=assigned_to,
        user_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
@token_required
def update_task(current_user, task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return jsonify({"error": f"Task {task_id} not found"}), 404

    if task.user_id != current_user.id and task.assigned_to != current_user.id:
        return jsonify({"error": "You do not have permission to modify this task"}), 403

    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "'title' must be a non-empty string"}), 400
        task.title = title.strip()

    if "description" in data:
        description = data["description"]
        if description is not None and not isinstance(description, str):
            return jsonify({"error": "'description' must be a string"}), 400
        task.description = (description or "").strip()

    if "status" in data:
        status = data["status"]
        if status not in VALID_STATUSES:
            return jsonify({"error": f"'status' must be one of {sorted(VALID_STATUSES)}"}), 400
        task.status = status

    if "due_date" in data:
        due_date, err = parse_due_date(data["due_date"])
        if err:
            return jsonify({"error": err}), 400
        task.due_date = due_date

    if "assigned_to" in data:
        # Only the owner can reassign a task
        if task.user_id != current_user.id:
            return jsonify({"error": "Only the task owner can change assignment"}), 403
        assigned_to, err = parse_assigned_to(data["assigned_to"])
        if err:
            return jsonify({"error": err}), 400
        task.assigned_to = assigned_to

    db.session.commit()
    return jsonify(task.to_dict()), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(current_user, task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return jsonify({"error": f"Task {task_id} not found"}), 404

    if task.user_id != current_user.id:
        return jsonify({"error": "You do not have permission to delete this task"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted", "id": task_id}), 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_err):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def server_error(_err):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

def _ensure_schema():
    """Lightweight migration: ensure new columns exist on existing SQLite DBs."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if "tasks" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("tasks")}
        with db.engine.begin() as conn:
            if "due_date" not in cols:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date DATE"))
            if "assigned_to" not in cols:
                conn.execute(text(
                    "ALTER TABLE tasks ADD COLUMN assigned_to INTEGER REFERENCES users(id)"
                ))


with app.app_context():
    db.create_all()
    _ensure_schema()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
