# Library Management System (Flask + SQLite)

A simple library management web app built with Python Flask and SQLite.

## Features

- User registration/login/logout
- Session management
- Add/view/delete books
- Issue books with due date tracking
- Return books with fine calculation (₹5/day overdue)
- Dashboard stats (total users, books, issued, available)

## Folder structure

```
library-management-system/
├── app.py
├── database.db
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── books.html
│   └── issued_books.html
├── static/
│   └── style.css
└── README.md
```

## Quick start

1. Install dependencies

```bash
pip install flask werkzeug
```

2. Run app

```bash
python app.py
```

3. Open browser at `http://127.0.0.1:5000`

## Notes

- `database.db` is created automatically on first run.
- `app.secret_key` should be replaced with a secure random value for production.
- Issue days default is 14 days but is configurable in issue form.
- Fine is computed on return: `max(0, (return_date - due_date).days * 5)`.
