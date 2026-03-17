# 📚 Library Management System (Flask + SQLite)

> A professional Library Management System built with Python Flask and SQLite, ideal for a final year BCA project.

## 🌟 Description

A feature-rich web app to manage libraries with user authentication, book inventory management, issue/return tracking, due date handling, overdue fine calculation, and dashboards with real-time statistics.

## ✅ Features

- User registration and login (secure authentication)
- Add, view, edit, and delete books
- Issue books to users with due date assignment
- Return books with automatic fine calculation (₹5/day overdue)
- Dashboard metrics (total users, books, issued books, available books)
- Session-based user access control
- Mobile-friendly and responsive UI (after styling)

## 🛠 Technologies Used

- Python 3.x
- Flask
- SQLite
- HTML5 / CSS3 (Bootstrap optional)
- Jinja2 templating
- Werkzeug for password hashing

## 📁 Project Folder Structure

```
library-management-system/
├── app.py                   # Flask application and route logic
├── app_main.py              # Optional entry point if dual-file setup
├── database.db              # SQLite database file (auto-created)
├── static/
│   └── style.css            # Custom styles
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── books.html
│   ├── issued_books.html
│   ├── login.html
│   └── register.html
├── README.md
└── .gitignore
```

## 🚀 Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/harshitha3046/library-management-system.git
cd library-management-system
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate      # windows
# source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:

```bash
pip install flask werkzeug
```

4. Configure environment variables (recommended):

- create `.env`
- set `SECRET_KEY`, `DATABASE_URL`, etc.

5. Initialize database and run app:

```bash
python app.py
```

## ▶️ Run Project Locally

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser at:

`http://127.0.0.1:5000`

3. Register an account, login, and start managing books.

## 🖼 Screenshots (Placeholder)

> Add actual screenshots in `assets/` and update the Markdown links later.

- `![Homepage](assets/screenshot-home.png)`
- `![Dashboard](assets/screenshot-dashboard.png)`
- `![Books](assets/screenshot-books.png)`

## 🚧 Future Improvements

- Implement role-based access (admin, student, librarian)
- Add email notifications for due dates and overdue fines
- Add search, sort, and filter on book lists
- Add comprehensive unit + integration tests
- Add REST API endpoints with JWT token authentication
- Add deployment instructions for Heroku / Azure / AWS

## ✍️ Author

**Harshitha**

- GitHub: [harshitha3046](https://github.com/harshitha3046)
- Project: `library-management-system`

---

## 📌 Notes

- `database.db` is generated the first time the app runs.
- Replace `app.secret_key` with a secure random value for production.
- Fine formula: `max(0, (return_date - due_date).days * 5)`.
- Repository: https://github.com/harshitha3046/library-management-system

