from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
import sqlite3, os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')


def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (request.form['username'], request.form['password']))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = dict(user)
            return redirect('/home')
    return render_template('login.html')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('home.html', current_user=session['user'])


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        return redirect('/')
    current = session['user']
    if current['role'] == 'user':
        return "Access denied", 403

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        form = request.form
        target_id = form.get('id') or form.get('edit') or form.get('delete')
        target_role = form.get('role') or form.get('new_role')
        password = form.get('password') or form.get('new_password')

        if current['role'] == 'admin':
            if 'add' in form:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                               (form['username'], password, target_role))

            elif 'edit' in form:
                if password.strip():
                    cursor.execute("UPDATE users SET password=?, role=? WHERE id=?",
                                   (password, target_role, target_id))
                else:
                    cursor.execute("UPDATE users SET role=? WHERE id=?", (target_role, target_id))

            elif 'delete' in form:
                cursor.execute("DELETE FROM users WHERE id=?", (target_id,))

        elif current['role'] == 'moderator':
            cursor.execute("SELECT role FROM users WHERE id=?", (target_id,))
            target = cursor.fetchone()
            if not target:
                conn.close()
                return "Пользователь не найден", 404

            if 'add' in form and target_role == 'user':
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                               (form['username'], password, 'user'))

            elif target['role'] == 'user':
                if 'edit' in form:
                    if password.strip():
                        cursor.execute("UPDATE users SET password=? WHERE id=?", (password, target_id))
                elif 'delete' in form:
                    cursor.execute("DELETE FROM users WHERE id=?", (target_id,))
        conn.commit()

    if current['role'] == 'admin':
        cursor.execute("SELECT * FROM users")
    elif current['role'] == 'moderator':
        cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=users, current_user=current)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/passwords')
def show_passwords():
    if 'user' not in session or session['user']['role'] != 'admin':
        return "Access denied", 403
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, password FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('passwords.html', users=users)


if __name__ == '__main__':
    app.run('0.0.0.0', port=50001, debug=True)