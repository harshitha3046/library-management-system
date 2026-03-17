from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'change_this_secret_key'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                total_copies INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE issued_books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                fine REAL DEFAULT 0,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

_db_initialized = False

@app.before_request
def setup_database():
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or password != confirm_password:
            flash('Please fill all fields and make sure passwords match.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)', (username, hashed_password, datetime.utcnow().isoformat()))
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM books')
    total_books = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM issued_books WHERE return_date IS NULL')
    issued_books = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(total_copies) as total_copies FROM books')
    total_copies = cursor.fetchone()['total_copies'] or 0

    available_books = max(total_copies - issued_books, 0)

    conn.close()

    return render_template('dashboard.html', total_books=total_books, total_users=total_users, issued_books=issued_books, available_books=available_books)

@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        copies = request.form['copies']
        if not title or not author or not copies.isdigit() or int(copies) < 1:
            flash('All fields are required and copies must be a positive integer.', 'danger')
            return redirect(url_for('books'))

        cursor.execute('INSERT INTO books (title, author, total_copies, created_at) VALUES (?, ?, ?, ?)', (title, author, int(copies), datetime.utcnow().isoformat()))
        conn.commit()
        flash('Book added successfully.', 'success')

    books_list = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=books_list)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM issued_books WHERE book_id = ? AND return_date IS NULL', (book_id,))
    active_issue = cursor.fetchone()
    if active_issue:
        flash('Cannot delete a book that is currently issued.', 'warning')
        conn.close()
        return redirect(url_for('books'))

    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    flash('Book deleted successfully.', 'success')
    return redirect(url_for('books'))

@app.route('/issued_books', methods=['GET', 'POST'])
@login_required
def issued_books():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        user_id = request.form.get('user_id')
        days = request.form.get('days', '14')

        if not book_id or not user_id or not days.isdigit() or int(days) < 1:
            flash('Invalid issue request. Fill all fields properly.', 'danger')
            return redirect(url_for('issued_books'))

        issue_date = datetime.utcnow()
        due_date = issue_date + timedelta(days=int(days))

        book = cursor.execute('SELECT total_copies FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            flash('Selected book not found.', 'danger')
            conn.close()
            return redirect(url_for('issued_books'))

        currently_issued = cursor.execute('SELECT COUNT(*) as count FROM issued_books WHERE book_id = ? AND return_date IS NULL', (book_id,)).fetchone()['count']
        if currently_issued >= book['total_copies']:
            flash('No available copies to issue.', 'warning')
            conn.close()
            return redirect(url_for('issued_books'))

        cursor.execute('INSERT INTO issued_books (book_id, user_id, issue_date, due_date, fine) VALUES (?, ?, ?, ?, ?)', (book_id, user_id, issue_date.isoformat(), due_date.isoformat(), 0))
        conn.commit()
        flash('Book issued successfully.', 'success')

    books_list = cursor.execute('SELECT * FROM books').fetchall()
    users_list = cursor.execute('SELECT * FROM users').fetchall()
    issued_records = cursor.execute('''
        SELECT ib.id, b.title, b.author, u.username, ib.issue_date, ib.due_date, ib.return_date, ib.fine
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.id
        JOIN users u ON ib.user_id = u.id
        ORDER BY ib.id DESC
    ''').fetchall()
    conn.close()

    return render_template('issued_books.html', books=books_list, users=users_list, issued_records=issued_records)

@app.route('/return_book/<int:issue_id>', methods=['POST'])
@login_required
def return_book(issue_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    record = cursor.execute('SELECT * FROM issued_books WHERE id = ?', (issue_id,)).fetchone()
    if not record:
        flash('Issue record not found.', 'danger')
        conn.close()
        return redirect(url_for('issued_books'))

    if record['return_date'] is not None:
        flash('Book already returned.', 'info')
        conn.close()
        return redirect(url_for('issued_books'))

    return_date = datetime.utcnow()
    due_date = datetime.fromisoformat(record['due_date'])
    overdue_days = max(0, (return_date - due_date).days)
    fine = overdue_days * 5

    cursor.execute('UPDATE issued_books SET return_date = ?, fine = ? WHERE id = ?', (return_date.isoformat(), fine, issue_id))
    conn.commit()
    conn.close()

    if fine > 0:
        flash(f'Book returned with fine ₹{fine}.', 'warning')
    else:
        flash('Book returned on time. No fine charged.', 'success')

    return redirect(url_for('issued_books'))

if __name__ == '__main__':
    app.run(debug=True)
