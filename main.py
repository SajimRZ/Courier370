from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'mintleamonicetea'

app.config['MYSQL_HOST'] = 'localhost' #server 
app.config['MYSQL_USER'] = 'root' #default
app.config['MYSQL_PASSWORD'] = ''  #default
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = '370courier' #db_name
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')

#Login Page
@app.route('/login', methods=['GET', 'POST']) #Log in page
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password))
        admin = cursor.fetchone()

        if admin:
            session['user_id'] = admin['AdminID']
            session['is_admin'] = True
            session['name'] = admin['name']
            cursor.close()
            return redirect(url_for('admin_dashboard')) # go to admin dashboard page 
        
        #check if the email is user email
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['UID']
            session['is_admin'] = False
            session['name'] = user['name']

            cursor.execute('SELECT * FROM user u,courier c WHERE u.UID = c.UID AND u.email = %s AND u.password = %s', (email, password))
            courier_check = cursor.fetchone()
            print(courier_check)
            if courier_check == None:
                return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('courier_dashboard'))
                
            
        cursor.close()
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

#signup page start - for user table data -
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']
        
        session['signup_data'] = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'role': role
            }   
        
        # Redirect based on role
        if role == 'customer':
            return redirect(url_for('customer_signup'))
        elif role == 'courier':
            return redirect(url_for('courier_signup'))
    return render_template('signup.html')

#signup table next page for customer
@app.route('/signup/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        #get cutomer exclusive data
        houseNo = request.form['houseNo']
        road = request.form['road']
        city = request.form['city']
        signup_data = session.get('signup_data', {})

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #check if all data is filled up
        if not all([signup_data['email'], signup_data['name'], signup_data['password'], signup_data['phone'], houseNo, road, city]):
            flash('Please fill all fields', 'error')
            return redirect(url_for('signup'))

        try:
            #check if email already exists or not
            cursor.execute('SELECT email FROM user WHERE email = %s', (signup_data['email'],))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('signup'))
            
            # Insert into user table
            cursor.execute('SELECT max(UID) as count FROM user')
            next_id = int(cursor.fetchone()['count']) + 1

            cursor.execute('SELECT AdminID from admin')
            admin_num = cursor.fetchall()
            cursor.execute('SELECT count(*) as count from admin')
            admin_count = cursor.fetchone()['count']

            id_num = int((next_id-1)%admin_count)+1
            admin_id = admin_num[id_num-1]['AdminID']
            admin_id = int(admin_id)



            cursor.execute('INSERT INTO user (UID, email, name, password, phone, AdminID) VALUES (%s, %s, %s, %s, %s, %s)', (next_id, signup_data['email'], signup_data['name'], signup_data['password'], signup_data['phone'], admin_id))
            #insert into customer table
            cursor.execute('INSERT INTO customer (UID, houseNo, road, city) VALUES (%s, %s, %s, %s)', (next_id, houseNo, city, road))
            
            mysql.connection.commit()
            #if all good go back to login page
            flash('Customer registration successful!', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('signup'))
            
        finally:
            cursor.close()
    
    return render_template('customer_signup.html')

#signup table next page for courier
@app.route('/courier_signup', methods=['GET', 'POST'])
def courier_signup():
    if request.method == 'POST':
        #get courier exclusive data
        licenseNo = request.form['licenseNo']
        type = request.form['type']
        city = request.form['city']
        signup_data = session.get('signup_data', {})

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        #check if all data is filled up
        if not all([signup_data['email'], signup_data['name'], signup_data['password'], signup_data['phone'], licenseNo, type, city]):
            flash('Please fill all fields', 'error')
            return redirect(url_for('signup'))

        try:
            #check if email already exists or not
            cursor.execute('SELECT email FROM user WHERE email = %s', (signup_data['email'],))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('signup'))
            
            # Insert into user table
            cursor.execute('SELECT max(UID) as count FROM user')
            next_id = int(cursor.fetchone()['count']) + 1
            cursor.execute('SELECT AdminID from admin')
            admin_num = cursor.fetchall()
            cursor.execute('SELECT count(*) as count from admin')
            admin_count = cursor.fetchone()['count']

            id_num = int((next_id-1)%admin_count)+1
            admin_id = admin_num[id_num-1]['AdminID']
            admin_id = int(admin_id)


            cursor.execute('INSERT INTO user (UID, email, name, password, phone, AdminID) VALUES (%s, %s, %s, %s, %s, %s)', (next_id, signup_data['email'], signup_data['name'], signup_data['password'], signup_data['phone'], admin_id))
            #insert into courier table
            cursor.execute('INSERT INTO courier (UID, name, city, licenseNo, type) VALUES (%s, %s, %s, %s, %s)', (next_id, signup_data['name'], city, licenseNo, type))
            
            mysql.connection.commit()
            #if all good go back to login page
            flash('Customer registration successful!', 'success')
            return redirect(url_for('login'))
        
        
            
        finally:
            cursor.close()
    
    return render_template('courier_signup.html')

#Admin Dashboard
@app.route('/admin_dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    #delete warehouse
    if request.method == 'POST':
        action = request.args.get('action') 
        
        if action == "delete_wh":
            delete_wh_id = request.form["WarehouseID"]
            cursor.execute("DELETE FROM warehouse WHERE WarehouseID = %s", (delete_wh_id,))
            mysql.connection.commit()
            flash("Warehouse deleted successfully!", "success")

    # Get all users
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    
    # Get all admins
    cursor.execute('SELECT * FROM admin')
    admins = cursor.fetchall()

    cursor.execute('SELECT * FROM warehouse')
    wh = cursor.fetchall()
    
    cursor.close()
    return render_template('admin_dashboard.html', users=users, admins=admins, wh = wh)

## Go to the Admin edit page
@app.route('/admin_dashboard/add_admin')
def add_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM admin')
    admins = cursor.fetchall()
    cursor.close()
    return render_template('add_admin.html', admins=admins)

#Logout system
@app.route('/logout')
def logout():
    session.clear()
    session['is_admin'] = False
    return redirect(url_for('login'))

#make a new admin
@app.route('/admin_dashboard/add_admin/create', methods=['POST'])
def create_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Get next AdminID
        cursor.execute('SELECT max(AdminID) as count FROM admin')
        next_id = int(cursor.fetchone()['count']) + 1
        
        cursor.execute(
            'INSERT INTO admin (AdminID, name, email, password) VALUES (%s, %s, %s, %s)',
            (next_id, name, email, password)
        )
        
        mysql.connection.commit()
        flash('New admin created successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Failed to create admin. Email might already exist.', 'danger')
        print(e)
    finally:
        cursor.close()
    
    return redirect(url_for('add_admin'))

#delete an admin
@app.route('/admin_dashboard/add_admin/delete/<int:AdminID>', methods=['POST'])
def delete_admin(AdminID):
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM admin WHERE AdminID = %s', (AdminID,))
        mysql.connection.commit()
        cursor.close()
        flash("Admin deleted successfully!", "success")
        return redirect(url_for('add_admin'))

##Create Warehouse
@app.route('/admin_dashboard/createwh', methods=['POST'])
def create_warehouse():  
    area = request.form['Area']
    city = request.form['City']
    a_id = request.form['AdminID']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT max(WarehouseID) as count FROM warehouse')
        next_id = int(cursor.fetchone()['count'])+1
        
        cursor.execute(
            'INSERT INTO warehouse (WarehouseID, Area, City, AdminID) VALUES (%s, %s, %s, %s)',
            (next_id, area, city, a_id)
        )
        
        mysql.connection.commit()
        flash('New site created successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Failed to create site.', 'danger')
        print(e)
    finally:
        cursor.close()
    
    return redirect(url_for('admin_dashboard'))

## Customer Dashboard
@app.route('/customer_dashboard', methods = ['GET', 'POST'])
def customer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM user u, customer c where u.UID = c.UID and c.UID = %s',(session['user_id'],))
    customer = cursor.fetchone()  

    cursor.execute('''
        SELECT * FROM package p, creates c, orders o
        WHERE p.PackageID = c.PackageID AND c.OrderID = o.OrderID AND c.customerID = %s
    ''', (session['user_id'],))
    unconfirmed_orders = cursor.fetchall()
    
    cursor.close()
    return render_template('customer_dashboard.html', customer = customer, unconfirmed_orders = unconfirmed_orders)

## Courier Dashboard
@app.route('/courier_dashboard')
def courier_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Get courier info
        cursor.execute('''
            SELECT u.*, c.* 
            FROM user u
            JOIN courier c ON u.UID = c.UID 
            WHERE u.UID = %s
        ''', (session['user_id'],))
        courier = cursor.fetchone()
        
        # Available packages (progress = 0)
        cursor.execute('''
            SELECT p.PackageID, 
                   CONCAT_WS(', ', p.S_houseNo, p.S_street, p.S_city) as pickup, 
                   CONCAT_WS(', ', p.D_HouseNo, p.D_street, p.D_city) as destination
            FROM package p
            JOIN creates c ON p.PackageID = c.PackageID
            JOIN orders o ON c.OrderID = o.OrderID
            WHERE o.progress = 0 
        ''')
        packages = cursor.fetchall()
        
        # My packages (assigned but not delivered)
        cursor.execute('''
            SELECT p.PackageID
            FROM package p
            JOIN delivered_by d ON p.PackageID = d.PackageID
            JOIN orders o ON d.OrderID = o.OrderID
            WHERE o.progress = 0 AND d.CourierID = %s
        ''', (session['user_id'],))
        my_packages = cursor.fetchall()
        
        return render_template('courier_dashboard.html', 
                            courier=courier, 
                            packages=packages,
                            my_packages=my_packages)
    
    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for('login'))
    finally:
        cursor.close()


@app.route('/accept_package/<package_id>', methods=['POST'])
def accept_package(package_id):
    if 'user_id' not in session:
        flash('Not logged in', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Check package availability
        cursor.execute("""
            SELECT o.OrderID 
            FROM creates c
            JOIN orders o ON c.OrderID = o.OrderID
            WHERE c.PackageID = %s AND o.progress = 0
        """, (package_id,))
        order = cursor.fetchone()
        
        if not order:
            flash('Package not available', 'danger')
            return redirect(url_for('courier_dashboard'))
        
        # Only add to delivered_by table without changing progress
        cursor.execute("""
            INSERT INTO delivered_by (PackageID, CourierID, OrderID)
            VALUES (%s, %s, %s)
        """, (package_id, session['user_id'], order['OrderID']))
        
        mysql.connection.commit()
        flash('Package accepted successfully! It will remain available until delivery is confirmed.', 'success')
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error accepting package: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('courier_dashboard'))


@app.route('/complete_package/<package_id>', methods=['POST'])
def complete_package(package_id):
    if 'user_id' not in session:
        flash('Not logged in', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # Verify package ownership
        cursor.execute("""
            SELECT o.OrderID 
            FROM delivered_by d
            JOIN orders o ON d.OrderID = o.OrderID
            WHERE d.PackageID = %s AND d.CourierID = %s AND o.progress = 0
        """, (package_id, session['user_id']))
        order = cursor.fetchone()
        
        if not order:
            flash('Package not found or not assigned to you', 'danger')
            return redirect(url_for('courier_dashboard'))
        
        # Mark package as delivered (progress = 2)
        cursor.execute("""
            UPDATE orders 
            SET progress = 2 
            WHERE OrderID = %s
        """, (order['OrderID'],))
        
        mysql.connection.commit()
        flash('Package marked as delivered!', 'success')
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error completing package: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('courier_dashboard'))


##Update user profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor()
        
        # Update user table
        cursor.execute('''
            UPDATE user SET 
            name = %s, 
            email = %s 
            WHERE UID = %s
        ''', (
            request.form['name'],
            request.form['email'],
            session['user_id']
        ))
        
        # Update customer table
        cursor.execute('''
            UPDATE customer SET
            houseNo = %s,
            road = %s,
            city = %s
            WHERE UID = %s
        ''', (
            request.form['houseNo'],
            request.form['road'],
            request.form['city'],
            session['user_id']
        ))
        
        mysql.connection.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
        
    finally:
        cursor.close()
    
    return redirect(url_for('customer_dashboard'))

##Update courier profile
@app.route('/update_profile_courier', methods=['POST'])
def update_profile_courier():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor()
        
        # Update user table
        cursor.execute('''
            UPDATE user SET 
            name = %s
            WHERE UID = %s
        ''', (
            request.form['name'],
            session['user_id']
        ))
        
        # Update courier table
        cursor.execute('''
            UPDATE courier SET
            city = %s
            WHERE UID = %s
        ''', (
            request.form['city'],
            session['user_id']
        ))
        
        mysql.connection.commit()
        flash('Profile updated successfully!', 'success')
        
    finally:
        cursor.close()
    
    return redirect(url_for('courier_dashboard'))

#add money to wallet
@app.route('/add_money', methods=['POST'])  
def add_money():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    amount = request.form['amount']
    payment_method = request.form['payment_method']
    acc_number = request.form['acc_number']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM user WHERE UID = %s', (session['user_id'],))
        user = cursor.fetchone()
        
        if user:
            new_balance = user['wallet'] + int(amount)
            cursor.execute('UPDATE user SET wallet = %s WHERE UID = %s', (new_balance, session['user_id']))
            mysql.connection.commit()

            #cursor.execute('INSERT INTO payment (acc_number, amount, method, UID) VALUES (%s, %s, %s, %s)', (acc_number, int(amount), payment_method, session['user_id']))
            mysql.connection.commit()
            flash('Money added successfully!', 'success')
        else:
            flash('User not found', 'error')
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error adding money: {str(e)}', 'error')
        
    finally:
        cursor.close()
    
    return redirect(url_for('customer_dashboard'))

#add package to database
@app.route('/create_package', methods=['POST'])
def add_package():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    package_shouse = request.form['houseNo']
    package_sroad = request.form['road']
    package_scity = request.form['city']
    package_dhouse = request.form['receiver_houseNo']
    package_droad = request.form['receiver_road']
    package_dcity = request.form['receiver_city']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #Check if all data is filled up
    if not all([package_shouse, package_sroad, package_scity, package_dhouse, package_droad, package_dcity]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('customer_dashboard'))
    #Check if the sender and receiver address are the same
    elif package_shouse == package_dhouse and package_sroad == package_droad and package_scity == package_dcity:
            flash('Sender and receiver addresses cannot be the same', 'error')
            return redirect(url_for('customer_dashboard'))
    try:   
        #get package id for new package
        cursor.execute('SELECT max(packageID) as count FROM package')
        next_id = cursor.fetchone()['count']
        next_id = 1 if next_id is None else int(next_id) + 1
        
        #get warehouse id for the package
        if package_scity == package_dcity:
            package_type = 'Local'
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(City) = %s LIMIT 1', (package_scity.upper(),))
            warehouse = cursor.fetchone()
            if not warehouse:
                flash('No warehouse found in the destination city', 'error')
                return redirect(url_for('customer_dashboard'))
            wh_id = warehouse['WarehouseID']

        else:
            package_type = 'Intercity'
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(City) = %s LIMIT 1', (package_dcity.upper(),))
            warehouse = cursor.fetchone()
            if not warehouse:
                flash('No warehouse found in the destination city', 'error')
                return redirect(url_for('customer_dashboard'))
            wh_id = warehouse['WarehouseID']

        #Make the package
        
        
        #get the order id for the new order
        cursor.execute('SELECT max(OrderID) as count FROM orders')
        order_id = cursor.fetchone()['count']
        order_id = 1 if order_id is None else int(order_id) + 1
        #get admin id for the new order
        cursor.execute('SELECT AdminID from user WHERE UID = %s', (session['user_id'],))
        admin_id = int(cursor.fetchone()['AdminID'])
        print
        #insert an unconfirmed order into the orders table

        mysql.connection.commit()
    
    
    finally:
        cursor.close()   
    return redirect(url_for('customer_dashboard'))
        
        

if __name__ == "__main__":
    app.run(debug=True)
    
