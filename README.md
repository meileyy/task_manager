# Task Manager

A full-stack Task Manager application with user authentication, team assignment, and a modern pastel UI. Built with Flask, SQLite, and vanilla JavaScript.

## Project Description

Task Manager is a multi-user CRUD application for organizing tasks. Users register, log in, and manage their own task lists through a clean web interface. Tasks support due dates, status tracking, and team assignment — any task can be assigned to another registered user, who will then see it alongside their own tasks.

The backend exposes a RESTful API secured with JWT tokens. The frontend is a single HTML file with no framework dependencies, featuring a soft pastel glassmorphism design.

## Features

- User registration and login with hashed passwords (bcrypt)
- JWT-based authentication for all protected endpoints
- Create, read, update, and delete tasks
- Task status workflow: `pending → in-progress → done`
- Optional due dates with color-coded indicators (overdue, today, future)
- Team support: assign tasks to other users
- Users see tasks they own or are assigned to
- Auto-migration for database schema changes on startup
- CORS enabled for frontend-backend communication
- Responsive, mobile-friendly UI

## Tech Stack

| Layer          | Technology                                 |
| -------------- | ------------------------------------------ |
| Backend        | Python 3, Flask, Flask-CORS, Flask-SQLAlchemy |
| Database       | SQLite (via SQLAlchemy ORM)                |
| Authentication | bcrypt (password hashing), PyJWT (tokens)  |
| Frontend       | HTML5, CSS3, Vanilla JavaScript (Fetch API) |

## Prerequisites

- **Python 3.8+** ([download](https://www.python.org/downloads/))
- **pip** (bundled with Python)
- A modern web browser

## Setup & Installation

1. **Clone or download** the project:

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

3. **Install dependencies:**

   ```bash
   pip install flask flask-cors flask-sqlalchemy bcrypt pyjwt
   ```

## Running the App

### 1. Start the backend

```bash
python3 app.py
```

The API starts at **http://localhost:5000**. The SQLite database (`taskmanager.db`) is created automatically on first run.

### 2. Open the frontend

Open `index.html` in your browser:

```bash
open index.html       # macOS
xdg-open index.html   # Linux
start index.html      # Windows
```

Or serve it locally:

```bash
python3 -m http.server 8000
```

Then visit **http://localhost:8000**.

## API Reference

Base URL: `http://localhost:5000`

All task and user endpoints require the header: `Authorization: Bearer <token>`

### Authentication

| Method | URL         | Auth | Description              |
| ------ | ----------- | ---- | ------------------------ |
| POST   | `/register` | —    | Create a new user        |
| POST   | `/login`    | —    | Log in and receive a JWT |

### Tasks

| Method | URL             | Auth | Description                                        |
| ------ | --------------- | ---- | -------------------------------------------------- |
| GET    | `/tasks`        | ✓    | List tasks owned by or assigned to the current user |
| POST   | `/tasks`        | ✓    | Create a new task                                   |
| PUT    | `/tasks/<id>`   | ✓    | Update a task (owner or assignee)                   |
| DELETE | `/tasks/<id>`   | ✓    | Delete a task (owner only)                          |

### Users

| Method | URL      | Auth | Description                      |
| ------ | -------- | ---- | -------------------------------- |
| GET    | `/users` | ✓    | List all registered users (id + username) |

### Task Schema

```json
{
  "id": 1,
  "title": "Deploy API",
  "description": "Push to staging and verify health checks",
  "status": "pending",
  "due_date": "2026-04-15",
  "assigned_to": {"id": 2, "username": "alex"},
  "user_id": 1
}
```

## Usage Examples

### Register a user

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "melos", "password": "secret123"}'
```

### Log in

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "melos", "password": "secret123"}'
```

Response:

```json
{"token": "eyJhbGciOi...", "username": "melos", "user_id": 1}
```

### Create a task with due date and assignment

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"title": "Write tests", "description": "Unit tests for auth module", "status": "pending", "due_date": "2026-04-20", "assigned_to": 2}'
```

### Update a task's status

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"status": "done"}'
```

### Delete a task

```bash
curl -X DELETE http://localhost:5000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOi..."
```

### List all users (for assignment dropdown)

```bash
curl http://localhost:5000/users \
  -H "Authorization: Bearer eyJhbGciOi..."
```

---

# Görev Yöneticisi (Task Manager)

Kullanıcı kimlik doğrulaması, takım atama ve modern pastel arayüze sahip full-stack bir görev yönetim uygulaması. Flask, SQLite ve saf JavaScript ile geliştirilmiştir.

## Proje Açıklaması

Görev Yöneticisi, görevleri düzenlemek için çok kullanıcılı bir CRUD uygulamasıdır. Kullanıcılar kayıt olur, giriş yapar ve görev listelerini temiz bir web arayüzü üzerinden yönetir. Görevler bitiş tarihi, durum takibi ve takım atamayı destekler — herhangi bir görev başka bir kayıtlı kullanıcıya atanabilir ve atanan kullanıcı bu görevi kendi görevleriyle birlikte görür.

Backend, JWT token ile korunan RESTful bir API sunar. Frontend, herhangi bir framework bağımlılığı olmadan tek bir HTML dosyasından oluşur ve yumuşak pastel glassmorphism tasarımına sahiptir.

## Özellikler

- Şifrelenmiş parolalarla (bcrypt) kullanıcı kaydı ve girişi
- Tüm korumalı endpoint'ler için JWT tabanlı kimlik doğrulama
- Görev oluşturma, listeleme, güncelleme ve silme (CRUD)
- Görev durumu akışı: `pending → in-progress → done`
- Renk kodlu isteğe bağlı bitiş tarihleri (gecikmiş, bugün, gelecek)
- Takım desteği: görevleri diğer kullanıcılara atama
- Kullanıcılar sahip oldukları veya kendilerine atanan görevleri görür
- Başlangıçta otomatik veritabanı şema geçişi
- Frontend-backend iletişimi için CORS desteği
- Duyarlı (responsive), mobil uyumlu arayüz

## Teknoloji Yığını

| Katman          | Teknoloji                                   |
| --------------- | ------------------------------------------- |
| Backend         | Python 3, Flask, Flask-CORS, Flask-SQLAlchemy |
| Veritabanı      | SQLite (SQLAlchemy ORM ile)                 |
| Kimlik Doğrulama | bcrypt (parola hashleme), PyJWT (token)    |
| Frontend        | HTML5, CSS3, Saf JavaScript (Fetch API)     |

## Ön Gereksinimler

- **Python 3.8+** ([indir](https://www.python.org/downloads/))
- **pip** (Python ile birlikte gelir)
- Modern bir web tarayıcısı

## Kurulum

1. **Projeyi klonlayın veya indirin:**

   ```bash
   git clone <repo-url>
   cd TASK_MANAGER
   ```

2. **(İsteğe bağlı) Sanal ortam oluşturun:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Bağımlılıkları yükleyin:**

   ```bash
   pip install flask flask-cors flask-sqlalchemy bcrypt pyjwt
   ```

## Uygulamayı Çalıştırma

### 1. Backend'i başlatın

```bash
python3 app.py
```

API **http://localhost:5000** adresinde başlar. SQLite veritabanı (`taskmanager.db`) ilk çalıştırmada otomatik olarak oluşturulur.

### 2. Frontend'i açın

`index.html` dosyasını tarayıcınızda açın:

```bash
open index.html       # macOS
xdg-open index.html   # Linux
start index.html      # Windows
```

Veya yerel sunucu ile çalıştırın:

```bash
python3 -m http.server 8000
```

Ardından **http://localhost:8000** adresini ziyaret edin.

## API Referansı

Ana URL: `http://localhost:5000`

Tüm görev ve kullanıcı endpoint'leri şu başlığı gerektirir: `Authorization: Bearer <token>`

### Kimlik Doğrulama

| Metot | URL         | Yetki | Açıklama                    |
| ----- | ----------- | ----- | --------------------------- |
| POST  | `/register` | —     | Yeni kullanıcı oluştur      |
| POST  | `/login`    | —     | Giriş yap ve JWT token al   |

### Görevler

| Metot  | URL             | Yetki | Açıklama                                              |
| ------ | --------------- | ----- | ------------------------------------------------------ |
| GET    | `/tasks`        | ✓     | Kullanıcının sahip olduğu veya atandığı görevleri listele |
| POST   | `/tasks`        | ✓     | Yeni görev oluştur                                     |
| PUT    | `/tasks/<id>`   | ✓     | Görevi güncelle (sahip veya atanan)                    |
| DELETE | `/tasks/<id>`   | ✓     | Görevi sil (yalnızca sahip)                            |

### Kullanıcılar

| Metot | URL      | Yetki | Açıklama                                  |
| ----- | -------- | ----- | ----------------------------------------- |
| GET   | `/users` | ✓     | Tüm kayıtlı kullanıcıları listele (id + kullanıcı adı) |

### Görev Şeması

```json
{
  "id": 1,
  "title": "API'yi yayınla",
  "description": "Staging ortamına gönder ve sağlık kontrollerini doğrula",
  "status": "pending",
  "due_date": "2026-04-15",
  "assigned_to": {"id": 2, "username": "alex"},
  "user_id": 1
}
```

## Kullanım Örnekleri

### Kullanıcı kaydı

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "melos", "password": "sifre123"}'
```

### Giriş yapma

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "melos", "password": "sifre123"}'
```

Yanıt:

```json
{"token": "eyJhbGciOi...", "username": "melos", "user_id": 1}
```

### Bitiş tarihli ve atamalı görev oluşturma

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"title": "Testleri yaz", "description": "Auth modülü için birim testleri", "status": "pending", "due_date": "2026-04-20", "assigned_to": 2}'
```

### Görev durumunu güncelleme

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"status": "done"}'
```

### Görev silme

```bash
curl -X DELETE http://localhost:5000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOi..."
```

### Tüm kullanıcıları listeleme (atama açılır menüsü için)

```bash
curl http://localhost:5000/users \
  -H "Authorization: Bearer eyJhbGciOi..."
```
