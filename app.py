
from flask import Flask, request, jsonify, redirect, url_for, render_template, session, abort, flash
from flask_cors import CORS
import mysql.connector
from functools import wraps
from mysql.connector import Error
# Remove the duplicate import of Flask and other modules

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Keep only one secret key
CORS(app)

db_config = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Dev1506@**',
    'database': 'check1'
}

def get_db():
    return mysql.connector.connect(**db_config)
# Remove the duplicate get_db() function

# Role-based access control decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'Admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------
# Home, Login, Dashboard, Reports, Logout
# ----------------------------------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"Login attempt: {username}")  # Debug

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return redirect(url_for('login'))

        conn = None
        cur = None
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            
            # Debug: Print database connection info
            print(f"Connected to database: {conn.database}")
            
            cur.execute(
                "SELECT UserID, Username, PasswordHash, Role "
                "FROM USERS WHERE Username = %s",
                (username,)
            )
            user = cur.fetchone()
            
            # Debug: Print user found or not
            print(f"User found: {user is not None}")
            
            if user is None:
                print("No user found with that username")
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('login'))

            # Debug: Print password comparison
            print(f"PasswordHash comparison: '{password}' vs '{user['PasswordHash']}'")
            print(f"Comparison result: {password != user['PasswordHash']}")
            
            if password != user['PasswordHash']:
                print("PasswordHash doesn't match")
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('login'))

            # Success!
            print(f"Login successful for {username}")
            session['user']    = user['Username']
            session['role']    = user['Role']
            session['user_id'] = user['UserID']
            return redirect(url_for('dashboard'))

        except Error as e:
            app.logger.error(f"Database error during login: {e}")
            print(f"Database error: {e}")
            flash('An internal error occurred. Please try again later.', 'danger')
            return redirect(url_for('login'))

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # GET
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard', role=session.get('role'))




@app.route('/reports')
@login_required
def reports():
    # Retrieve reports data
    return render_template('reports.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/SupplierAndCustomerManagement')
@login_required
@admin_required
def supplier_management():
    return render_template('SupplierAndCustomerManagement.html')


# ----------------------------------------
# Serve the Warehouse Management page
# ----------------------------------------
@app.route('/warehouse_management')
@login_required
def warehouse_management():
    return render_template('warehouse_management.html')

@app.route('/inventoryManagement')
@login_required
def inventory_management():
    return render_template('inventoryManagement.html')


@app.route('/shipmentandorderManagement')
@login_required
def shipmentandorder_management():
    return render_template('shipmentandorderManagement.html')

@app.route('/ProductManagement')
@login_required
def Product_management():
    return render_template('ProductManagement.html')




# ----------------------------------------
# Existing Report APIs (unchanged)
# ----------------------------------------
@app.route('/api/inventory-stock')
@login_required
def inventory_stock():

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT WI.WarehouseInventoryID,
             W.Location AS WarehouseLocation,
             P.Name     AS ProductName,
             WI.Quantity
      FROM WAREHOUSE_INVENTORY WI
      JOIN WAREHOUSE W ON WI.WarehouseID = W.WarehouseID
      JOIN PRODUCT   P ON WI.ProductID   = P.ProductID
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/inventory-low-stock')
@login_required
def low_stock():
    threshold = int(request.args.get('threshold', 10))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT W.Location AS WarehouseLocation,
             P.Name     AS ProductName,
             WI.Quantity
      FROM WAREHOUSE_INVENTORY WI
      JOIN WAREHOUSE W ON WI.WarehouseID = W.WarehouseID
      JOIN PRODUCT   P ON WI.ProductID   = P.ProductID
      WHERE WI.Quantity <= %s
    """, (threshold,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/inventory-valuation')
@login_required
def stock_valuation():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT W.Location       AS WarehouseLocation,
             SUM(WI.Quantity) AS TotalUnits
      FROM WAREHOUSE_INVENTORY WI
      JOIN WAREHOUSE W ON WI.WarehouseID = W.WarehouseID
      GROUP BY WI.WarehouseID
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/orders')
@login_required
def orders_by_date():
    start = request.args.get('start_date')
    end   = request.args.get('end_date')
    if not start or not end:
        abort(400, "Please provide start_date and end_date in YYYY-MM-DD")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT O.OrderID,
             O.OrderDate,
             C.Name AS Customer
      FROM ORDERS O
      JOIN CUSTOMER C ON O.CustomerID = C.CustomerID
      WHERE O.OrderDate BETWEEN %s AND %s
    """, (start, end))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/pending-shipments')
@login_required
def pending_shipments():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT S.ShipmentID,
             S.ShipmentDate,
             W.Location AS WarehouseLocation
      FROM SHIPMENT S
      JOIN WAREHOUSE W ON S.WarehouseID = W.WarehouseID
      WHERE S.ShipmentID NOT IN (
        SELECT DISTINCT ShipmentID FROM ORDERS WHERE ShipmentID IS NOT NULL
      )
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/shipment-history')
@login_required
def shipment_history():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT IM.MovementID,
             IM.MovementDate,
             IM.MovementType,
             P.Name       AS Product,
             IM.QuantityMoved,
             S.ShipmentID
      FROM INVENTORY_MOVEMENT IM
      JOIN PRODUCT   P ON IM.ProductID  = P.ProductID
      JOIN SHIPMENT  S ON IM.ShipmentID = S.ShipmentID
      ORDER BY IM.MovementDate DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)
@app.route('/api/inventory-movement')
@login_required
def inventory_movement():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            IM.MovementID,
            IM.MovementDate,
            IM.MovementType,
            P.Name AS Product,
            IM.QuantityMoved,
            WF.Location AS FromLocation,
            WT.Location AS ToLocation
        FROM INVENTORY_MOVEMENT IM
        JOIN PRODUCT P ON IM.ProductID = P.ProductID
        LEFT JOIN WAREHOUSE WF ON IM.WarehouseFromID = WF.WarehouseID
        LEFT JOIN WAREHOUSE WT ON IM.WarehouseToID = WT.WarehouseID
        ORDER BY IM.MovementDate DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/api/product-transfer')
@login_required
def product_transfer():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT IM.MovementID,
             IM.MovementDate,
             P.Name         AS Product,
             IM.QuantityMoved,
             IM.WarehouseFromID,
             IM.WarehouseToID
      FROM INVENTORY_MOVEMENT IM
      JOIN PRODUCT P ON IM.ProductID = P.ProductID
      WHERE IM.MovementType = 'Transfer'
      ORDER BY IM.MovementDate DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/supplier-products')
@login_required
def supplier_products():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT S.SupplierID,
             S.Name       AS Supplier,
             P.ProductID,
             P.Name       AS Product
      FROM PRODUCT P
      JOIN SUPPLIER S ON P.SupplierID = S.SupplierID
      ORDER BY S.SupplierID
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/top-suppliers')
@login_required
def top_suppliers():
    limit = int(request.args.get('limit', 5))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(f"""
      SELECT S.SupplierID,
             S.Name               AS Supplier,
             COUNT(P.ProductID)   AS ProductsSupplied
      FROM SUPPLIER S
      LEFT JOIN PRODUCT P ON P.SupplierID = S.SupplierID
      GROUP BY S.SupplierID
      ORDER BY ProductsSupplied DESC
      LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/top-customers')
@login_required
def top_customers():
    limit = int(request.args.get('limit', 5))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(f"""
      SELECT C.CustomerID,
             C.Name             AS Customer,
             COUNT(O.OrderID)   AS OrderCount
      FROM CUSTOMER C
      LEFT JOIN ORDERS O ON O.CustomerID = C.CustomerID
      GROUP BY C.CustomerID
      ORDER BY OrderCount DESC
      LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/sales-summary')
@login_required
def sales_summary():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT O.OrderID,
             O.OrderDate,
             C.Name       AS Customer,
             P.Name       AS Product,
             OP.QuantityOrdered
      FROM ORDER_PRODUCT OP
      JOIN ORDERS   O ON OP.OrderID   = O.OrderID
      JOIN CUSTOMER C ON O.CustomerID = C.CustomerID
      JOIN PRODUCT  P ON OP.ProductID  = P.ProductID
      ORDER BY O.OrderDate DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# ----------------------------------------
# Warehouse Management APIs
# ----------------------------------------

# 1) List all warehouses
@app.route('/api/warehouses', methods=['GET'])
@login_required
def get_warehouses():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM WAREHOUSE")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# 2) Add a new warehouse
@app.route('/api/warehouses', methods=['POST'])
@login_required
def add_warehouse():
    data = request.json
    loc = data.get('location')
    cap = data.get('capacity')
    if not loc or cap is None:
        return jsonify({'error':'location & capacity required'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO WAREHOUSE (Location, Capacity) VALUES (%s,%s)", (loc, cap))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Warehouse added'}), 201

# 3) Update warehouse
@app.route('/api/warehouses/<int:wid>', methods=['PUT'])
@login_required
def update_warehouse(wid):
    data = request.json
    loc = data.get('location')
    cap = data.get('capacity')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE WAREHOUSE SET Location=%s, Capacity=%s WHERE WarehouseID=%s",
                (loc, cap, wid))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Warehouse updated'})

# 4) Delete warehouse
@app.route('/api/warehouses/<int:wid>', methods=['DELETE'])
@login_required
@admin_required
def delete_warehouse(wid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM WAREHOUSE WHERE WarehouseID=%s", (wid,))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Warehouse deleted'})

# 5) List users (for manager dropdown)
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    role = request.args.get('role')
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    if role:
        cur.execute("SELECT UserID, Username FROM USERS WHERE Role=%s", (role,))
    else:
        cur.execute("SELECT UserID, Username, Role FROM USERS")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/manager-assignments', methods=['GET', 'POST'])
@login_required
@admin_required
def manager_assignments():
    if request.method == 'GET':
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT U.UserID,
                   U.Username,
                   W.WarehouseID,
                   W.Location AS WarehouseLocation
            FROM USER_WAREHOUSE UW
            JOIN USERS U     ON UW.UserID = U.UserID
            JOIN WAREHOUSE W ON UW.WarehouseID = W.WarehouseID
            WHERE U.Role = 'Manager'
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify(rows)

    elif request.method == 'POST':
        data = request.json
        uid = data.get('UserID')
        wid = data.get('WarehouseID')

        if not uid or not wid:
            return jsonify({'error': 'UserID & WarehouseID required'}), 400

        conn = get_db()
        cur = conn.cursor()

        # Remove existing manager for this warehouse
        cur.execute("DELETE FROM USER_WAREHOUSE WHERE WarehouseID = %s", (wid,))
        cur.execute("INSERT INTO USER_WAREHOUSE (UserID, WarehouseID) VALUES (%s, %s)", (uid, wid))
        conn.commit()
        cur.close(); conn.close()

        return jsonify({'message': 'Manager assigned/updated successfully'})


@app.route('/api/warehouses/<int:wid>/capacity-used', methods=['GET'])
@login_required
def capacity_used(wid):
    conn = get_db()
    cur = conn.cursor()
    
    # Get used quantity
    cur.execute("SELECT COALESCE(SUM(Quantity),0) FROM WAREHOUSE_INVENTORY WHERE WarehouseID=%s", (wid,))
    used = cur.fetchone()[0]
    
    # Get total capacity
    cur.execute("SELECT Capacity FROM WAREHOUSE WHERE WarehouseID=%s", (wid,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        abort(404)
    
    capacity = row[0]
    cur.close(); conn.close()
    
    # Return in the format expected by frontend
    return jsonify({
        'Used': used,
        'Capacity': capacity
    })


# 9) Compare two warehouses' inventories
@app.route('/api/warehouse-comparison', methods=['GET'])
@login_required
def warehouse_comparison():
    w1 = request.args.get('w1', type=int)
    w2 = request.args.get('w2', type=int)
    if w1 is None or w2 is None:
        return jsonify({'error':'w1 & w2 required'}), 400
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT p.Name      AS Product,
             COALESCE(wi1.Quantity,0) AS Qty1,
             COALESCE(wi2.Quantity,0) AS Qty2
      FROM PRODUCT p
      LEFT JOIN (
        SELECT ProductID, Quantity FROM WAREHOUSE_INVENTORY WHERE WarehouseID=%s
      ) wi1 ON p.ProductID = wi1.ProductID
      LEFT JOIN (
        SELECT ProductID, Quantity FROM WAREHOUSE_INVENTORY WHERE WarehouseID=%s
      ) wi2 ON p.ProductID = wi2.ProductID
    """, (w1, w2))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)


# ----- CUSTOMER CRUD -----
@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT
        CustomerID AS id,
        Name       AS name,
        ContactInfo AS contact,
        Address    AS address
      FROM CUSTOMER
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/customers', methods=['POST'])
@login_required
@admin_required
def create_customer():
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
      "INSERT INTO CUSTOMER (Name, ContactInfo, Address) VALUES (%s,%s,%s)",
      (data['name'], data['contact'], data['address'])
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Customer created'}), 201

@app.route('/api/customers/<int:cid>', methods=['PUT'])
@login_required
@admin_required
def update_customer(cid):
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
      "UPDATE CUSTOMER SET Name=%s, ContactInfo=%s, Address=%s WHERE CustomerID=%s",
      (data['name'], data['contact'], data['address'], cid)
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Customer updated'})

@app.route('/api/customers/<int:cid>', methods=['DELETE'])
@login_required
@admin_required
def delete_customer(cid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM CUSTOMER WHERE CustomerID=%s", (cid,))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Customer deleted'})



@app.route('/api/customers/<int:cid>/orders', methods=['GET'])
@login_required
def get_customer_orders(cid):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
   SELECT
     O.OrderID,
     DATE_FORMAT(O.OrderDate, '%Y-%m-%d') AS OrderDate,  -- Fixed query here
     P.Name               AS Product,
     OP.QuantityOrdered
   FROM ORDERS O
   JOIN ORDER_PRODUCT OP ON O.OrderID   = OP.OrderID
   JOIN PRODUCT       P  ON OP.ProductID = P.ProductID
   WHERE O.CustomerID = %s
   ORDER BY O.OrderDate DESC
""", (cid,))

    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)


# ----- SUPPLIER CRUD -----
@app.route('/api/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT
        SupplierID AS id,
        Name       AS name,
        ContactInfo AS contact
      FROM SUPPLIER
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/suppliers', methods=['POST'])
@login_required
@admin_required
def create_supplier():
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
      "INSERT INTO SUPPLIER (Name, ContactInfo) VALUES (%s,%s)",
      (data['name'], data['contact'])
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Supplier created'}), 201

@app.route('/api/suppliers/<int:sid>', methods=['PUT'])
@login_required
@admin_required
def update_supplier(sid):
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
      "UPDATE SUPPLIER SET Name=%s, ContactInfo=%s WHERE SupplierID=%s",
      (data['name'], data['contact'], sid)
    )
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Supplier updated'})

@app.route('/api/suppliers/<int:sid>/products', methods=['GET'])
@login_required
def get_products_for_supplier(sid):
    print(f"Fetching products for supplier {sid}")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            ProductID,
            Name,
            Description
        FROM PRODUCT
        WHERE SupplierID = %s
    """, (sid,))
    products = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(products)






# -------------------------------
# Get inventory for one warehouse
# -------------------------------
@app.route('/api/warehouses/<int:wid>/inventory', methods=['GET'])
@login_required
def get_warehouse_inventory(wid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
          WI.ProductID,
          P.Name        AS ProductName,
          P.Description,
          WI.Quantity,
          S.Name        AS Supplier
        FROM WAREHOUSE_INVENTORY WI
        JOIN PRODUCT           P ON WI.ProductID   = P.ProductID
        LEFT JOIN SUPPLIER     S ON P.SupplierID   = S.SupplierID
        WHERE WI.WarehouseID = %s
    """, (wid,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)


# ----- PRODUCT LIST FOR DROPDOWN -----
@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    """
    Returns a list of all products in the system,
    so the UI can show every product in the "Add/Update/Remove" dropdown.
    """
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            ProductID AS ProductID,
            Name      AS Name
        FROM PRODUCT
        ORDER BY Name
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/api/warehouses/<int:wid>/inventory/add', methods=['POST'])
@login_required
def add_inventory(wid):
    data = request.get_json()
    pid = data.get('product_id')
    qty = data.get('quantity')

    if not pid or qty is None or qty < 0:
        return jsonify({'error': 'Valid product_id and quantity required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO WAREHOUSE_INVENTORY (WarehouseID, ProductID, Quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE Quantity = Quantity + VALUES(Quantity)
    """, (wid, pid, qty))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Inventory added/updated successfully'})

@app.route('/api/warehouses/<int:wid>/inventory/<int:pid>', methods=['PUT'])
@login_required
def update_inventory(wid, pid):
    data = request.get_json()
    qty = data.get('quantity')

    if qty is None or qty < 0:
        return jsonify({'error': 'Quantity must be non-negative'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE WAREHOUSE_INVENTORY
        SET Quantity = %s
        WHERE WarehouseID = %s AND ProductID = %s
    """, (qty, wid, pid))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Inventory quantity updated'})


@app.route('/api/warehouses/<int:wid>/inventory/<int:pid>', methods=['DELETE'])
@login_required
def remove_inventory(wid, pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM WAREHOUSE_INVENTORY
        WHERE WarehouseID = %s AND ProductID = %s
    """, (wid, pid))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Inventory removed'})


@app.route('/api/suppliers/<int:sid>', methods=['DELETE'])
@login_required
@admin_required
def delete_supplier(sid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM SUPPLIER WHERE SupplierID=%s", (sid,))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message':'Supplier deleted'})




# Shipment And Orders



# —————————————
# Orders & Shipments Endpoints
# —————————————
# —————————————
# Orders & Shipments Endpoints
# —————————————

# 1) Return every order (so the front‑end can list them)
@app.route('/api/orders/all', methods=['GET'])
@login_required
def get_all_orders():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT
        O.OrderID   AS id,
        C.Name      AS customer_name,
        DATE_FORMAT(O.OrderDate, '%Y-%m-%d')   AS order_date,
        DATE_FORMAT(S.ShipmentDate, '%Y-%m-%d') AS shipment_date
      FROM ORDERS O
      JOIN CUSTOMER C ON O.CustomerID = C.CustomerID
      LEFT JOIN SHIPMENT S ON O.ShipmentID = S.ShipmentID
      ORDER BY O.OrderDate DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# 2) Return the line‑items for a given order ID
@app.route('/api/orders/<int:order_id>/products', methods=['GET'])
@login_required
def get_order_products(order_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT
        P.Name             AS product_name,
        OP.QuantityOrdered AS quantity
      FROM ORDER_PRODUCT OP
      JOIN PRODUCT P ON OP.ProductID = P.ProductID
      WHERE OP.OrderID = %s
    """, (order_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# 3) Return every shipment
@app.route('/api/shipments/all', methods=['GET'])
@login_required
def get_all_shipments():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
      SELECT
        S.ShipmentID       AS id,
        W.Location         AS warehouse_location,
        DATE_FORMAT(S.ShipmentDate, '%Y-%m-%d') AS shipment_date,
        CASE
          WHEN EXISTS (
            SELECT 1 FROM ORDERS O WHERE O.ShipmentID = S.ShipmentID
          ) THEN 'Completed'
          ELSE 'Pending'
        END AS status
      FROM SHIPMENT S
      JOIN WAREHOUSE W ON S.WarehouseID = W.WarehouseID
      ORDER BY S.ShipmentDate DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# 4) Return the products moved in a given shipment
@app.route('/api/shipments/<int:shipment_id>/products', methods=['GET'])
@login_required
def get_shipment_products(shipment_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            P.Name           AS product_name,
            IM.QuantityMoved AS quantity
        FROM INVENTORY_MOVEMENT IM
        JOIN PRODUCT P ON IM.ProductID = P.ProductID
        WHERE IM.ShipmentID = %s
    """, (shipment_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)




# --- Create a new Order --
# --- Create a new Order ---
@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    customer_id = data.get('customer_id')
    products = data.get('products')  # [{product_id:..., quantity:...}, ...]

    if not customer_id or not products:
        return jsonify({'error': 'Missing customer or products'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO ORDERS (CustomerID, OrderDate) VALUES (%s, NOW())", (customer_id,))
    order_id = cur.lastrowid

    for item in products:
        cur.execute("""
            INSERT INTO ORDER_PRODUCT (OrderID, ProductID, QuantityOrdered)
            VALUES (%s, %s, %s)
        """, (order_id, item['product_id'], item['quantity']))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message': 'Order created'})



# --- Create a new Shipment ---
@app.route('/api/shipments', methods=['POST'])
@login_required
def create_shipment():
    data = request.get_json()
    warehouse_id = data.get('warehouse_id')
    shipment_date = data.get('shipment_date')

    if not warehouse_id or not shipment_date:
        return jsonify({'error': 'Missing warehouse or date'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO SHIPMENT (WarehouseID, ShipmentDate) VALUES (%s, %s)",
                (warehouse_id, shipment_date))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({'message': 'Shipment created'})


@app.route('/api/orders/create', methods=['POST'])
@login_required
def create_order_from_frontend():
    data = request.get_json()
    customer_name = data.get('customer_name')
    customer_contact = data.get('customer_contact', 'Unknown')  # Default value if not provided
    customer_address = data.get('customer_address', 'Unknown')  # Default value if not provided
    products = data.get('products')  # [{product_id:..., quantity:...}, ...]
    warehouse_id = data.get('warehouse_id')  # For shipment creation
    
    if not customer_name or not products:
        return jsonify({'error': 'Missing customer name or products'}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Get customer ID or create new customer if needed
        cur.execute("SELECT CustomerID FROM CUSTOMER WHERE Name = %s", (customer_name,))
        customer_row = cur.fetchone()
        
        if customer_row:
            customer_id = customer_row[0]
        else:
            # Create new customer with required fields
            cur.execute(
                "INSERT INTO CUSTOMER (Name, ContactInfo, Address) VALUES (%s, %s, %s)",
                (customer_name, customer_contact, customer_address)
            )
            customer_id = cur.lastrowid
        
        # Create shipment if warehouse_id is provided
        shipment_id = None
        if warehouse_id:
            cur.execute(
                "INSERT INTO SHIPMENT (ShipmentDate, WarehouseID) VALUES (CURDATE(), %s)",
                (warehouse_id,)
            )
            shipment_id = cur.lastrowid
        
        # Create order with shipment_id if available
        if shipment_id:
            cur.execute(
                "INSERT INTO ORDERS (OrderDate, CustomerID, ShipmentID) VALUES (CURDATE(), %s, %s)",
                (customer_id, shipment_id)
            )
        else:
            cur.execute(
                "INSERT INTO ORDERS (OrderDate, CustomerID) VALUES (CURDATE(), %s)",
                (customer_id,)
            )
        
        order_id = cur.lastrowid
        
        # Add products to order
        for item in products:
            cur.execute(
                """INSERT INTO ORDER_PRODUCT (OrderID, ProductID, QuantityOrdered)
                VALUES (%s, %s, %s)""",
                (order_id, item['product_id'], item['quantity'])
            )
            
            # If there's a shipment, we might want to create an inventory movement record (Sale)
            if shipment_id and warehouse_id:
                cur.execute(
                    """INSERT INTO INVENTORY_MOVEMENT 
                    (ProductID, WarehouseFromID, OrderID, ShipmentID, QuantityMoved, MovementDate, MovementType)
                    VALUES (%s, %s, %s, %s, %s, CURDATE(), 'Sale')""",
                    (item['product_id'], warehouse_id, order_id, shipment_id, item['quantity'])
                )
                
                # Update warehouse inventory (subtract the sold quantity)
                cur.execute(
                    """UPDATE WAREHOUSE_INVENTORY 
                    SET Quantity = Quantity - %s
                    WHERE WarehouseID = %s AND ProductID = %s""",
                    (item['quantity'], warehouse_id, item['product_id'])
                )
        
        conn.commit()
        return jsonify({
            'message': 'Order created successfully', 
            'order_id': order_id,
            'shipment_id': shipment_id
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        cur.close()
        conn.close()






# ----- PRODUCT MANAGEMENT APIs -----

# Get all products with supplier information
@app.route('/api/products/all', methods=['GET'])
@login_required
def get_all_products():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            P.ProductID,
            P.Name,
            P.Description,
            P.SupplierID,
            S.Name AS SupplierName
        FROM PRODUCT P
        LEFT JOIN SUPPLIER S ON P.SupplierID = S.SupplierID
        ORDER BY P.Name
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(products)

# Get a specific product by ID
@app.route('/api/products/<int:pid>', methods=['GET'])
@login_required
def get_product(pid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            P.ProductID,
            P.Name,
            P.Description,
            P.SupplierID,
            S.Name AS SupplierName
        FROM PRODUCT P
        LEFT JOIN SUPPLIER S ON P.SupplierID = S.SupplierID
        WHERE P.ProductID = %s
    """, (pid,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(product)

# Create a new product
@app.route('/api/products', methods=['POST'])
@login_required
@admin_required
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    supplier_id = data.get('supplier_id')
    
    if not name or not supplier_id:
        return jsonify({"error": "Name and supplier_id are required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO PRODUCT (Name, Description, SupplierID) VALUES (%s, %s, %s)",
            (name, description, supplier_id)
        )
        conn.commit()
        product_id = cur.lastrowid
        
        cur.close()
        conn.close()
        
        return jsonify({
            "message": "Product created successfully",
            "product_id": product_id
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(err)}), 500

# Update a product
@app.route('/api/products/<int:pid>', methods=['PUT'])
@login_required
@admin_required
def update_product(pid):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    supplier_id = data.get('supplier_id')
    
    if not name or not supplier_id:
        return jsonify({"error": "Name and supplier_id are required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE PRODUCT SET Name = %s, Description = %s, SupplierID = %s WHERE ProductID = %s",
            (name, description, supplier_id, pid)
        )
        conn.commit()
        
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"error": "Product not found or no changes made"}), 404
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Product updated successfully"})
    except mysql.connector.Error as err:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(err)}), 500

# Delete a product
@app.route('/api/products/<int:pid>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(pid):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # First check if product exists
        cur.execute("SELECT 1 FROM PRODUCT WHERE ProductID = %s", (pid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Product not found"}), 404
        
        # Delete the product
        cur.execute("DELETE FROM PRODUCT WHERE ProductID = %s", (pid,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Product deleted successfully"})
    except mysql.connector.Error as err:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(err)}), 500

# Get inventory for a specific product across all warehouses
@app.route('/api/products/<int:pid>/inventory', methods=['GET'])
@login_required
def get_product_inventory(pid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            W.WarehouseID,
            W.Location AS WarehouseLocation,
            COALESCE(WI.Quantity, 0) AS Quantity
        FROM WAREHOUSE W
        LEFT JOIN WAREHOUSE_INVENTORY WI ON W.WarehouseID = WI.WarehouseID AND WI.ProductID = %s
        ORDER BY W.Location
    """, (pid,))
    inventory = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(inventory)



@app.route('/api/inventory/transfer', methods=['POST'])
def transfer_inventory():
    data = request.get_json()
    source_wid = data.get('source_warehouse_id')
    dest_wid = data.get('destination_warehouse_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    # Validate input
    if not all([source_wid, dest_wid, product_id, quantity]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if int(source_wid) == int(dest_wid):
        return jsonify({'error': 'Source and destination warehouses must be different'}), 400
    
    if int(quantity) <= 0:
        return jsonify({'error': 'Quantity must be positive'}), 400
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Begin transaction
        conn.start_transaction()
        
        # 1. Check if source warehouse has enough inventory
        cur.execute("""
            SELECT Quantity FROM WAREHOUSE_INVENTORY 
            WHERE WarehouseID = %s AND ProductID = %s
        """, (source_wid, product_id))
        source_inventory = cur.fetchone()
        
        if not source_inventory or source_inventory['Quantity'] < quantity:
            conn.rollback()
            return jsonify({'error': 'Not enough inventory in source warehouse'}), 400
        
        # 2. Reduce quantity in source warehouse
        cur.execute("""
            UPDATE WAREHOUSE_INVENTORY 
            SET Quantity = Quantity - %s 
            WHERE WarehouseID = %s AND ProductID = %s
        """, (quantity, source_wid, product_id))
        
        # 3. Add or update quantity in destination warehouse
        cur.execute("""
            INSERT INTO WAREHOUSE_INVENTORY (WarehouseID, ProductID, Quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Quantity = Quantity + VALUES(Quantity)
        """, (dest_wid, product_id, quantity))
        
        # 4. Record the movement in INVENTORY_MOVEMENT table
        cur.execute("""
            INSERT INTO INVENTORY_MOVEMENT 
            (ProductID, WarehouseFromID, WarehouseToID, QuantityMoved, MovementDate, MovementType)
            VALUES (%s, %s, %s, %s, CURDATE(), 'Transfer')
        """, (product_id, source_wid, dest_wid, quantity))
        
        # Commit the transaction
        conn.commit()
        
        return jsonify({'message': 'Inventory transferred successfully'}), 200
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        cur.close()
        conn.close()






@app.route('/api/current-user')
@login_required
def current_user():
    return jsonify({
        'UserID': session.get('user_id'),
        'Username': session.get('user'),
        'Role': session.get('role')
    })


@app.route('/api/warehouses/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_warehouses(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT W.WarehouseID, W.Location, W.Capacity
        FROM WAREHOUSE W
        JOIN USER_WAREHOUSE UW ON W.WarehouseID = UW.WarehouseID
        WHERE UW.UserID = %s
    """, (user_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

























# Serve the product management page
@app.route('/product_management')
@login_required
def product_management():
    return render_template('product_management.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    