import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

auth = Blueprint('auth', __name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([name, email, password]):
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))

        hashed = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash("Email already registered.", "danger")
        else:
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)", (name, email, hashed))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('auth.login'))
        cur.close()
        conn.close()

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user'] = email
            flash("Logged in successfully.", "success")
            return redirect(url_for('routes_bp.index'))
        else:
            flash("Invalid credentials.", "danger")

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
