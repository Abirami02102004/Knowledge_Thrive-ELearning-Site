from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import re
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, supports_credentials=True)

# 🔹 Secret key for session management
app.secret_key = 'xyzsdfg'
app.permanent_session_lifetime = timedelta(days=1)  # Set session expiration

# 🔹 MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_system'

mysql = MySQL(app)

# ✅ Home Page
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/index')
def index():
    return render_template("index.html")

# ✅ User Registration (with session storage)
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "All fields are required!"}), 400

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify({"message": "Invalid email format!"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `user` WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return jsonify({"message": "Account already exists!"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO `user` (name, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        mysql.connection.commit()

        # Retrieve the newly created user for session storage
        cursor.execute('SELECT * FROM `user` WHERE email = %s', (email,))
        new_user = cursor.fetchone()
        cursor.close()

        # Store session data
        session['loggedin'] = True
        session['userid'] = new_user['userid']
        session['name'] = new_user['name']
        session['email'] = new_user['email']
        session.permanent = True  # Keep session active

        return jsonify({"message": "Registration successful!", "redirect": url_for('student_dashboard')}), 200

    except MySQLdb.Error as db_err:
        return jsonify({"message": "Database error!", "error": str(db_err)}), 500
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred!", "error": str(e)}), 500

# ✅ User Login (Fixing `bcrypt.checkpw` error)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        identifier = data.get('identifier')  # Can be email or username
        password = data.get('password')

        if not identifier or not password:
            return jsonify({"message": "Email/Username and password are required!"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `user` WHERE email = %s OR name = %s', (identifier, identifier))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Store session details
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session.permanent = True
            
            return jsonify({"message": "Login successful!", "redirect": url_for('student_dashboard')}), 200

        return jsonify({"message": "Invalid credentials!"}), 401

    except Exception as e:
        return jsonify({"message": "An error occurred!", "error": str(e)}), 500

# ✅ Student Dashboard (Ensure name is passed)
@app.route('/student_dashboard')
def student_dashboard():
    if 'loggedin' in session:
        return render_template("studDash1.html", name=session['name'])
    return redirect(url_for('index'))

# ✅ Logout User (Allowing GET for redirection)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()  # Clear session data
    if request.method == 'POST':
        return jsonify({"message": "Logout successful!", "redirect": url_for('home')}), 200
    return redirect(url_for('home'))  # Redirect for GET requests

# ✅ Forgot Password (Fixing reset response)
@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not email or not new_password or not confirm_password:
                return jsonify({"message": "All fields are required!"}), 400

            if new_password != confirm_password:
                return jsonify({"message": "Passwords do not match!"}), 400

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM `user` WHERE email = %s', (email,))
            user = cursor.fetchone()

            if not user:
                cursor.close()
                return jsonify({"message": "Email not found!"}), 404

            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('UPDATE `user` SET password = %s WHERE email = %s', (hashed_password, email))
            mysql.connection.commit()
            cursor.close()

            return jsonify({"message": "Password reset successful!", "redirect": url_for('index')}), 200

        except Exception as e:
            return jsonify({"message": "An error occurred!", "error": str(e)}), 500

    return render_template("forget.html")

# ✅ About & Admin Pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ✅ Run Flask Application
if __name__ == "__main__":
    app.run(debug=True)
