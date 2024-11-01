from flask import Flask, render_template, session, redirect, url_for, request
import json
import psycopg2
from flask import jsonify
app = Flask(__name__)
app.secret_key = '527852785278'  # 設置一個密鑰來加密 session
@app.route('/')

def home():
    return render_template('index.html')

@app.route('/Top_Customers', methods=['GET'])
def Top_Customers():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT 
                a.account AS 用戶帳號,
                SUM(oi."Quantity" * oi."Price") AS 總消費金額,
                COUNT(DISTINCT o."OrderID") AS 訂單數量
            FROM 
                "Order" o
            JOIN 
                accounts a ON o."UserID" = a.id
            JOIN 
                "OrderItem" oi ON o."OrderID" = oi."OrderID"
            GROUP BY 
                a.account
            ORDER BY 
                總消費金額 DESC

        ''')
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/Sales_By_Date', methods=['GET'])
def Sales_By_Date():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            WITH RECURSIVE dates AS (
                SELECT CURRENT_DATE - INTERVAL '1 month' AS date
                UNION ALL
                SELECT date + INTERVAL '1 day'
                FROM dates
                WHERE date < CURRENT_DATE
            ),
            categories AS (
                SELECT id, name
                FROM "Type"
            ),
            category_dates AS (
                SELECT 
                    c.id AS category_id, 
                    c.name AS category_name, 
                    d.date AS sales_date
                FROM 
                    categories c
                CROSS JOIN 
                    dates d
            ),
            sales AS (
                SELECT 
                    p.category AS category_id,
                    DATE(o."OrderDate") AS sales_date,
                    SUM(oi."Quantity" * p."price") AS total_sales
                FROM 
                    "OrderItem" oi
                JOIN 
                    "Products" p ON oi."ProductID" = p.id
                JOIN 
                    "Order" o ON oi."OrderID" = o."OrderID"
                WHERE 
                    DATE(o."OrderDate") BETWEEN CURRENT_DATE - INTERVAL '1 month' 
                                            AND CURRENT_DATE
                GROUP BY 
                    p.category, 
                    DATE(o."OrderDate")
            )
            SELECT 
                cd.category_name AS "類別名稱",
                TO_CHAR(cd.sales_date, 'MM-DD') AS "銷售日期",
                COALESCE(s.total_sales, 0) AS "銷售金額"
            FROM 
                category_dates cd
            LEFT JOIN 
                sales s 
                ON s.category_id = cd.category_id 
                AND s.sales_date = cd.sales_date
            ORDER BY 
                cd.category_name, 
                cd.sales_date;
        """)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400

@app.route('/New_Order', methods=['POST'])
def New_Order():
    user_id = session['user_id']
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    cursor.execute('SELECT "cart_id" FROM "Cart" WHERE "user_id" = %s', (user_id,))
    result = cursor.fetchone()
    cart_id = result[0]
    cursor.execute('SELECT "product_id", "quantity" FROM "CartItem" WHERE "cart_id" = %s', (cart_id,))
    items = cursor.fetchall()
    cursor.execute('INSERT INTO "Order" ("UserID", "OrderDate", "Payment", "Location", "Status") VALUES (%s, CURRENT_DATE, %s, %s, %s)', (user_id, data['paymentMethod'], data['address'], '處理中'))
    cursor.execute('SELECT LASTVAL()')
    
    order_id = cursor.fetchone()[0]
    for item in items:
        cursor.execute('SELECT "price" FROM "Products" WHERE "id" = %s', (item[0],))
        price = cursor.fetchone()[0]
        print(price)
        cursor.execute('INSERT INTO "OrderItem" ("OrderID", "ProductID", "Quantity", "Price") VALUES (%s, %s, %s, %s)', (order_id, item[0], item[1], price))
        cursor.execute('UPDATE "Products" SET "stock_num" = "stock_num" - %s WHERE "id" = %s', (item[1], item[0]))
    cursor.execute('DELETE FROM "CartItem" WHERE "cart_id" = %s', (cart_id,))
    cursor.execute('DELETE FROM "Cart" WHERE "cart_id" = %s', (cart_id,))
    cursor.execute('INSERT INTO "Cart" ("user_id") VALUES (%s)', (user_id,))
    connection.commit()
    connection.close()
    return jsonify({"message": "Order created successfully"})

@app.route('/Top_Selling_Products', methods=['GET'])
def Top_Selling_Products():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    cursor.execute('''
        SELECT p.name AS 商品名稱, SUM(oi."Quantity") AS 總銷售數量
        FROM "OrderItem" oi
        JOIN "Products" p ON oi."ProductID" = p.id
        GROUP BY p.name
        ORDER BY 總銷售數量 DESC
        LIMIT 10
    ''')
    result = cursor.fetchall()
    connection.close()
    return jsonify(result)


@app.route('/Sales_By_Category', methods=['GET'])
def Sales_By_Category():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT 
                t.name AS 類別名稱, 
                SUM(oi."Quantity" * p.price) AS 銷售金額
            FROM 
                "OrderItem" oi
            JOIN 
                "Products" p ON oi."ProductID" = p.id
            JOIN 
                "Type" t ON p.category = t.id
            GROUP BY 
                t.name
            ORDER BY 
                銷售金額 DESC
        ''')
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400






@app.route('/Delete_Cart', methods=['POST'])   # Load_Cart
def Delete_Cart():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('DELETE FROM "CartItem" WHERE "item_id" = %s', (data['item_id'],))
        connection.commit()
        connection.close()
        return jsonify({"message": "Item deleted successfully"})
    except Exception as e:
        print(e)
        return 'error', 400


@app.route('/Update_Cart', methods=['POST'])   # Load_Cart
def Update_Cart():
    user_id = session['user_id']
    data = json.loads(request.get_data())

    if 'user_id' not in session:
        return 'User not logged in', 401
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('UPDATE "CartItem" SET "quantity" = %s WHERE "item_id" = %s', (data['quantity'], data['item_id']))
        connection.commit()
        connection.close()
        return jsonify({"message": "Item updated successfully"})
    except Exception as e:
        print(e)
        return 'error', 400



@app.route('/Add_Cart', methods=['Post'])   # Load_Cart
def Add_Cart():
    user_id = session['user_id']
    data = json.loads(request.get_data())

    if 'user_id' not in session:
        return 'User not logged in', 401
    
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "cart_id" FROM "Cart" WHERE "user_id" = %s', (user_id,))
        result = cursor.fetchone()
        cart_id = result[0]
        cursor.execute('SELECT "quantity" FROM "CartItem" WHERE "cart_id" = %s AND "product_id" = %s', (cart_id, data['product_id']))
        item = cursor.fetchone()
        if item:
            cursor.execute('UPDATE "CartItem" SET "quantity" = "quantity" + 1 WHERE "cart_id" = %s AND "product_id" = %s', (cart_id, data['product_id']))
        else:
            cursor.execute('INSERT INTO "CartItem" ("cart_id", "product_id", "quantity") VALUES (%s, %s, 1)', (cart_id, data['product_id']))
        connection.commit()
        connection.close()
        return jsonify({"message": "Item added to cart successfully"})
    except Exception as e:
        print(e)
        return 'error', 400



@app.route('/Load_Cart', methods=['GET'])   # Load_Cart
def Load_Cart():
    user_id = session['user_id']
    if 'user_id' not in session:
        return 'User not logged in', 401
    
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "cart_id" FROM "Cart" WHERE "user_id" = %s', (user_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO "Cart" ("user_id") VALUES (%s)', (user_id,))
            connection.commit()
            cursor.execute('SELECT "cart_id" FROM "Cart" WHERE "user_id" = %s', (user_id,))
            result = cursor.fetchone()
        cursor.execute('SELECT "cart_id" FROM "Cart" WHERE "user_id" = %s', (user_id,))
        result = cursor.fetchone()
        cart_id = result[0]
        cursor.execute('SELECT "CartItem"."item_id", "Products"."name", "Products"."price", "Products"."image", "CartItem"."quantity" FROM "CartItem" JOIN "Products" ON "CartItem"."product_id" = "Products"."id" WHERE "cart_id" = %s', (cart_id,))
        result = cursor.fetchall()
        if result:
            result = [list(row) for row in result]
            for row in result:
                if row[3] is not None:
                    row[3] = row[3].tobytes().decode('utf-8')
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400



@app.route('/Search_InStock_Product', methods=['POST'])
def Search_InStock_Product():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "Products".id, "Products".name, "price", "image", "Type".name FROM "Products" JOIN "Type" ON "Products".category = "Type".id WHERE "stock_num" > 0 AND "Products".name ILIKE %s ORDER BY "Type".name', ('%' + data['keyword'] + '%',))
        result = cursor.fetchall()
        if result:
            result = [list(row) for row in result]
            for row in result:
                if row[3] is not None:
                    row[3] = row[3].tobytes().decode('utf-8')  # Convert memoryview to string
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400





@app.route('/Load_InStock_Product', methods=['GET'])
def Load_InStock_Product():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "Products".id, "Products".name, "price", "image", "Type".name FROM "Products" JOIN "Type" ON "Products".category = "Type".id WHERE "stock_num" > 0 ORDER BY "Type".name')
        result = cursor.fetchall()

        if result:
            result = [list(row) for row in result]
            for row in result:
                if row[3] is not None:
                    row[3] = row[3].tobytes().decode('utf-8')  # Convert memoryview to string
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/Load_Orders', methods=['GET'])
def Load_Orders():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :

        cursor.execute("""
            SELECT "Order"."OrderID", "Order"."OrderDate", "Order"."Payment", "Order"."Location", "Order"."Status", "Order"."UserID", 
               SUM("OrderItem"."Quantity" * "OrderItem"."Price") as TotalAmount
            FROM "Order"
            JOIN "OrderItem" ON "Order"."OrderID" = "OrderItem"."OrderID"
            GROUP BY "Order"."OrderID", "Order"."OrderDate", "Order"."Payment", "Order"."Location", "Order"."UserID"
        """)
        result = cursor.fetchall()
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400







@app.route('/admin/editpro')
def editpro():
    return render_template('admin/edit-product.html')

@app.route('/admin/Load_One_Product', methods=['POST'])
def Load_One_Product():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "Products".id, "Products".name, "Products".description, "Products".price, "Products".stock_num, "Products".image, "Type".name FROM "Products" JOIN "Type" ON "Products".category = "Type".id WHERE "Products".id = %s', (data['id'],))
        result = cursor.fetchone()
        if result:
            result = list(result)
            if result[5] is not None:
                result[5] = result[5].tobytes().decode('utf-8')  # Convert memoryview to string
        connection.close()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400

@app.route('/admin/edit_products', methods=['POST'])
def edit_one_pro():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT id FROM "Type" WHERE name=%s', (data['cate'],))
        type_id = cursor.fetchone()[0]
        cursor.execute('UPDATE "Products" SET name=%s, price=%s, category=%s, description=%s, image=%s, stock_num=%s WHERE id=%s', 
                   (data['acc'], data['price'], type_id, data['des'], data['file'], data['stock'], data['id']))
        connection.commit()
        connection.close()
        return jsonify({"redirect": url_for('products')})
    except Exception as e:
        print(e)
        return 'error', 400

@app.route('/admin/new_products', methods=['POST'])
def addpro():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT id FROM "Type" WHERE name=%s', (data['cate'],))
        type_id = cursor.fetchone()[0]
        cursor.execute('INSERT INTO "Products" (name, price, category, description, image, stock_num) VALUES (%s, %s, %s, %s, %s, %s)', 
                   (data['acc'], data['price'], type_id, data['des'], data['file'], data['stock']))
        connection.commit()
        connection.close()
        return jsonify({"redirect": url_for('products')})
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Load_Products', methods=['GET'])
def loadpro():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('SELECT "Products".id, "Products".name, price, stock_num, "Type".name FROM "Products" JOIN "Type" ON "Products".category = "Type".id ORDER BY "Type".name')
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Delete_Products', methods=['POST'])
def delpro():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    cursor = connection.cursor()
    try :
        cursor.execute('DELETE FROM "Products" WHERE id=%s', (data['id'],))
        connection.commit()
        connection.close()
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
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    data = json.loads(request.get_data())
    cursor = connection.cursor()
    try:
        cursor.execute('INSERT INTO "Type" (name) VALUES (%s)', (data['name'],))
        connection.commit()
        cursor.close()
        connection.close()
        return 'success', 200
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Delete_Categories', methods=['POST'])
def delcata():
    data = json.loads(request.get_data())
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")

    cursor = connection.cursor()
    try :
        cursor.execute('DELETE FROM "Type" WHERE name=%s', (data['name'],))
        connection.commit()
        connection.close()
        return 'success', 200
    except Exception as e:
        print(e)
        return 'error', 400
@app.route('/admin/Load_Categories', methods=['GET'])
def loadcata():
    connection = psycopg2.connect(
                    user="project_16",
                    password="nz8ku3",
                    host="140.117.68.66",
                    port="5432",
                    database="project_16")
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT name FROM "Type"')
        result = cursor.fetchall()
        cursor.close()
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
    connection = psycopg2.connect(
                    user="project_16",
                    password="nz8ku3",
                    host="140.117.68.66",
                    port="5432",
                    database="project_16")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "administrator" WHERE "acc"=%s', (data['acc'],))
    if cursor.fetchone() is not None:
        return 'Account already exists in  table', 400

    cursor.execute('SELECT * FROM "accounts" WHERE "account"=%s', (data['acc'],))
    if cursor.fetchone() is not None:
        return 'Account already exists in accounts table', 400
    
    cursor.execute('INSERT INTO "accounts" (account, password) VALUES (%s, %s)', (data['acc'], data['pss']))
    connection.commit()
    return 'success', 200
@app.route('/login', methods=['POST'])
def login():
    connection = psycopg2.connect(
                user="project_16",
                password="nz8ku3",
                host="140.117.68.66",
                port="5432",
                database="project_16")
    data = json.loads(request.get_data())
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM administrator WHERE acc=%s AND pss=%s", (data['acc'], data['pss']))
    user = cursor.fetchone()
    if user:
        session['user_id'] = user[0]
        session['logged_in'] = True
        cursor.close()
        return jsonify({"redirect": url_for('admin')})
    cursor.execute("SELECT * FROM accounts WHERE account=%s AND password=%s", (data['acc'], data['pss']))
    user = cursor.fetchone()
    cursor.close()
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