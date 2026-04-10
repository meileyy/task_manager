# Task Manager

A lightweight full-stack Task Manager application demonstrating how to build a RESTful API with Flask and connect it to a plain HTML/JavaScript frontend — no frameworks, no database, no authentication.

## Project Description

Task Manager is a minimal CRUD application for tracking to-do items. It solves the common need for a simple, self-contained task board that can be run locally in seconds, without setting up a database or complex tooling. It's ideal as a learning project, a boilerplate for REST API experimentation, or a starting point for a larger productivity tool.

Tasks are stored in memory on the backend and displayed on a styled table in the frontend. Users can create, update, and delete tasks through an intuitive UI or directly via the REST API.

## Features

- Create tasks with a title, description, and status
- View all tasks in a clean, styled table
- Cycle task status through `pending → in-progress → done` with a single click
- Delete tasks instantly from the UI
- Fully RESTful JSON API
- CORS enabled for seamless frontend-backend communication
- Preloaded example tasks on startup
- Zero external dependencies beyond Flask and Flask-CORS

## Tech Stack

| Layer    | Technology                   |
| -------- | ---------------------------- |
| Backend  | Python 3, Flask, Flask-CORS  |
| Frontend | HTML5, CSS3, Vanilla JavaScript (Fetch API) |
| Storage  | In-memory Python dictionary  |

## Prerequisites

Before running the project, make sure you have:

- **Python 3.8+** installed ([download](https://www.python.org/downloads/))
- **pip** (comes bundled with Python)
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Setup & Installation

1. **Clone or download** the project into a local folder:

   ```bash
   git clone <your-repo-url>
   cd TASK_MANAGER
   ```

2. **(Optional) Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install backend dependencies:**

   ```bash
   pip install flask flask-cors
   ```

## Running the App

### 1. Start the backend

From the project root, run:

```bash
python app.py
```

The Flask server will start at **http://localhost:5000** and preload 3 example tasks.

### 2. Open the frontend

Simply double-click `index.html`, or open it in your browser:

```bash
open index.html       # macOS
xdg-open index.html   # Linux
start index.html      # Windows
```

The UI will automatically fetch and display tasks from the backend.

## API Reference

Base URL: `http://localhost:5000`

| Method   | URL             | Description                                    |
| -------- | --------------- | ---------------------------------------------- |
| `GET`    | `/tasks`        | Retrieve all tasks                             |
| `POST`   | `/tasks`        | Create a new task                              |
| `PUT`    | `/tasks/<id>`   | Update an existing task (title/description/status) |
| `DELETE` | `/tasks/<id>`   | Delete a task by ID                            |

### Task Schema

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending"
}
```

Valid `status` values: `"pending"`, `"in-progress"`, `"done"`.

## Usage Examples

### Get all tasks

```bash
curl http://localhost:5000/tasks
```

### Create a new task

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write README", "description": "Document the project", "status": "in-progress"}'
```

### Update a task's status

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Delete a task

```bash
curl -X DELETE http://localhost:5000/tasks/1
```

### UI Walkthrough

1. Launch the backend and open `index.html` in your browser.
2. Fill in the **Title**, **Description**, and **Status** fields at the top, then click **Add Task**.
3. The new task appears in the table below.
4. Click **Change Status** on any row to cycle through `pending → in-progress → done`.
5. Click **Delete** to remove a task — the table refreshes automatically.

---

**Note:** Because tasks are stored in memory, all data is lost when the Flask server stops. For persistent storage, consider integrating SQLite or another database.
