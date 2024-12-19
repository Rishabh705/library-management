from flask import Flask, jsonify, request, render_template
import sqlite3
import uuid
import hashlib
from sqlite3 import IntegrityError, OperationalError
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
DATABASE = 'library.db'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'test.db'
# db = SQLAlchemy(app)

# Utility functions
def generate_id():
    return str(uuid.uuid4())


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def is_authenticated(token: str) -> bool:
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM tokens WHERE token = ?', (token,)).fetchone()
    conn.close()
    return user is not None


def init_db():
    conn = get_db_connection()
    with open('queries.sql', 'r') as f:
            conn.executescript(f.read())
    print("Database initialized successfully.")

    conn.close()
    
def validate(required_keys: list, data: dict) -> tuple:
    missing_keys = [key for key in required_keys if key not in data]
    empty_keys = [key for key in required_keys if not data.get(key)]

    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"

    if empty_keys:
        return False, f"Keys with empty values: {', '.join(empty_keys)}"

    return True, None


# Routes

@app.route('/')
def index():
    return render_template('index.html')

# login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid request format"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()

        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hashed_password)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({"error": "Invalid username or password"}), 401

        token = generate_id()

        existing_token = conn.execute(
            'SELECT token FROM tokens WHERE id = ?', (user['id'],)
        ).fetchone()

        if existing_token:
            conn.execute(
                'UPDATE tokens SET token = ? WHERE id = ?', (token, user['id'])
            )
        else:
            conn.execute(
                'INSERT INTO tokens (id, token) VALUES (?, ?)', (user['id'], token)
            )

        conn.commit()
        conn.close()

        return jsonify({"message": "Login successful", "token": token}), 200

    except Exception as e:
        print(f"Error during login: {str(e)}")

        return jsonify({"error": "An internal server error occurred"}), 500


# register
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = get_db_connection()

        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            conn.close()  
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (username, hashed_password))
        conn.commit()

        user_id = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()[0]

        conn.close()

        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# add book
@app.route('/books', methods=['POST'])
def add_book():
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    required_keys = ["title", "author", "year"]
    result, message = validate(required_keys, data)

    if not result:
        return jsonify({"error": message}), 400

    if not isinstance(data.get('year'), int) or data.get('year') < 0:
        return jsonify({"error": "Invalid 'year': Must be a non-negative integer"}), 400

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
                     (data['title'], data['author'], data['year']))
        conn.commit()
        return jsonify({"message": "Book added successfully"}), 201
    except IntegrityError:
        return jsonify({"error": "Database constraint violation"}), 400
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# get all books
@app.route('/books', methods=['GET'])
def get_books():
    token = request.headers.get('Authorization')
    print(token)
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    title = request.args.get('title')
    author = request.args.get('author')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    query = 'SELECT * FROM books'
    params = []

    if title:
        query += ' WHERE title LIKE ?'
        params.append(f'%{title}%')
    if author:
        query += ' AND author LIKE ?' if title else ' WHERE author LIKE ?'
        params.append(f'%{author}%')

    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])

    try:
        conn = get_db_connection()
        books = conn.execute(query, params).fetchall()
        return jsonify([dict(book) for book in books]), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# get a book
@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(dict(book)), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()


# update a book
@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    token = request.headers.get('Authorization')
    print(token)
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    required_keys = ["title", "author", "year"]
    result, message = validate(required_keys, data)

    if not result:
        return jsonify({"error": message}), 400

    if not isinstance(data.get('year'), int) or data.get('year') < 0:
        return jsonify({"error": "Invalid 'year': Must be a non-negative integer"}), 400

    try:
        conn = get_db_connection()
        conn.execute('UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?',
                    (data.get('title'), data.get('author'), data.get('year'), book_id))
        conn.commit()
        return jsonify({"message": "Book updated successfully"}), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# delete a book
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        return jsonify({"message": "Book deleted successfully"}), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# add member
@app.route('/members', methods=['POST'])
def add_member():
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    required_keys = ["name", "email"]
    result, message = validate(required_keys, data)

    if not result:
        return jsonify({"error": message}), 400

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO members (name, email) VALUES (?, ?)',
                     (data['name'], data['email']))
        conn.commit()
        return jsonify({"message": "Member added successfully"}), 201
    except IntegrityError:
        return jsonify({"error": "Database constraint violation"}), 400
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# get all members
@app.route('/members', methods=['GET'])
def get_members():
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    name = request.args.get('name')
    email = request.args.get('email')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    query = 'SELECT * FROM members'
    params = []

    if name:
        query += ' WHERE name LIKE ?'
        params.append(f'%{name}%')
    if email:
        query += ' AND email LIKE ?' if name else ' WHERE email LIKE ?'
        params.append(f'%{email}%')

    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])

    try:
        conn = get_db_connection()
        members = conn.execute(query, params).fetchall()
        return jsonify([dict(member) for member in members]), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# get a member
@app.route('/members/<member_id>', methods=['GET'])
def get_member(member_id):
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
        if not member:
            return jsonify({"error": f"No member found with id {member_id}"}), 404
        return jsonify(dict(member)), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()


# update a member
@app.route('/members/<member_id>', methods=['PUT'])
def update_member(member_id):
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    required_keys = ["name", "email"]
    result, message = validate(required_keys, data)

    if not result:
        return jsonify({"error": message}), 400

    try:
        conn = get_db_connection()
        conn.execute('UPDATE members SET name = ?, email = ? WHERE id = ?',
                     (data.get('name'), data.get('email'), member_id))
        conn.commit()
        return jsonify({"message": "Member updated successfully"}), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

# delete a member
@app.route('/members/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM members WHERE id = ?', (member_id,))
        conn.commit()
        return jsonify({"message": "Member deleted successfully"}), 200
    except OperationalError as e:
        return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
