from flask import Flask, render_template, session, redirect, url_for, request
import sqlite3
import json
from flask import jsonify
app = Flask(__name__)
app.secret_key = '527852785278'  # 設置一個密鑰來加密 session

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin/index.html')
@app.route('/store')
def store():
    return render_template('jewellery.html')
@app.route('/register', methods=['POST'])
def resgister():
    data = json.loads(request.get_data())
    print(data)
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administrator WHERE acc=?", (data['acc'],))
    if cursor.fetchone() is not None:
        return 'Account already exists in  table', 400

    cursor.execute("SELECT * FROM accounts WHERE account=?", (data['acc'],))
    if cursor.fetchone() is not None:
        return 'Account already exists in accounts table', 400
    
    cursor.execute("INSERT INTO accounts (account, password) VALUES (?, ?)", (data['acc'], data['pss']))
    conn.commit()
    return 'success', 200

@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.get_data())
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administrator WHERE acc=? AND pss=?", (data['acc'], data['pss']))
    user = cursor.fetchone()
    print(user)
    if user :
        print('admin')
        session['user_id'] = user[0]
        session['logged_in'] = True
        return jsonify({"redirect": url_for('admin')})
    cursor.execute("SELECT * FROM accounts WHERE account=? AND password=?", (data['acc'], data['pss']))
    user = cursor.fetchone()
    if user is None:
        return 'Invalid credentials', 401
    session['user_id'] = user[0]
    session['logged_in'] = True
    return jsonify({"redirect": url_for('store')})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)