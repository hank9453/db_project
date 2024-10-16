from flask import Flask, render_template, session, redirect, url_for, request
import sqlite3
import json
from flask import jsonify
app = Flask(__name__)
app.secret_key = '527852785278'  # 設置一個密鑰來加密 session

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/admin/editpro')
def editpro():
    return render_template('admin/edit-product.html')

@app.route('/admin/Load_One_Product', methods=['POST'])
def Load_One_Product():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("select Products.id, Products.name, description,price, stock_num, image, Type.name from Products join Type on Products.category = Type.id where Products.id = ?", (data['id'],))
        result = cursor.fetchone()
        con.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400


@app.route('/admin/edit_products', methods=['POST'])
def edit_one_pro():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("select id from Type where name=?", (data['cate'],))
        type_id = cursor.fetchone()[0]
        cursor.execute("update Products set name=?, price=?, category=?, description=?, image=?, stock_num=? where id=?", (data['acc'], data['price'], type_id, data['des'], data['file'], data['stock'], data['id']))
        con.commit()
        con.close()
        return jsonify({"redirect": url_for('products')})
    except Exception as e:
        print(e)
        return 'error', 400

@app.route('/admin/new_products', methods=['POST'])
def addpro():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("select id from Type where name=?", (data['cate'],))
        type_id = cursor.fetchone()[0]
        cursor.execute("insert into Products(name, price, category, description, image,stock_num) values (?, ?, ?, ?, ?,?)", (data['acc'], data['price'], type_id, data['des'], data['file'], data['stock']))
        con.commit()
        con.close()
        return jsonify({"redirect": url_for('products')})
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Load_Products', methods=['GET'])
def loadpro():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()

    try :
        cursor.execute("select Products.id,Products.name, price, stock_num, Type.name from Products join Type on Products.category = Type.id")
        result = cursor.fetchall()
        con.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Delete_Products', methods=['POST'])
def delpro():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("delete from  Products where id=?", (data['id'],))
        con.commit()
        con.close()
        return 'success', 200
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/products')
def products():
    return render_template('admin/products.html')
@app.route('/admin/add_products')
def add_products():
    return render_template('admin/add-product.html')
@app.route('/admin/Categories', methods=['POST'])
def addcata():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("insert into Type (name) values (?)", (data['name'],))
        con.commit()
        con.close()
        return 'success', 200
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Delete_Categories', methods=['POST'])
def delcata():
    data = json.loads(request.get_data())
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("delete from Type where name=?", (data['name'],))
        con.commit()
        con.close()
        return 'success', 200
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Load_Categories', methods=['GET'])
def loadcata():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    try :
        cursor.execute("select name from Type")
        result = cursor.fetchall()
        con.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400
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