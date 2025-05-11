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
                session["courier_type"] = courier_check["type"]
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
            cursor.execute('INSERT INTO customer (UID, houseNo, road, city) VALUES (%s, %s, %s, %s)', (next_id, houseNo, road, city))
            
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

##Show Warehouse Details
@app.route('/warehouse_details', methods=['POST'])
def warehouse_details():
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        WarehouseID = request.form['WarehouseID']
        cursor.execute('''
                    SELECT *
                    FROM warehouse w, package p
                    WHERE w.WarehouseID = p.WarehouseID and w.WarehouseID = %s\
                       ''', (WarehouseID),)
        
        Details = cursor.fetchall()
        if not Details:
            flash('Warehouse Empty', 'message')
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        
        cursor.close()

        return render_template('warehouse_details.html', Details = Details)

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
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM user u, customer c where u.UID = c.UID and c.UID = %s',(session['user_id'],))
    customer = cursor.fetchone()  

    cursor.execute('''
                    SELECT * FROM package p
                    WHERE p.PackageID and p.customerID = %s
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
        
        ## Available packages
        ## Get the city of the courier
        cursor.execute('''
                        SELECT UPPER(city) as city
                        FROM courier
                        WHERE UID = %s
                       ''', (session['user_id'],))
        c = cursor.fetchone()['city']

        if courier['type'] == 'motorcycle':
            # packages for motorcycle
            cursor.execute('''
                            SELECT *
                            FROM package p, warehouse w 
                            WHERE p.WarehouseID = w.WarehouseID and 
                            (UPPER(p.S_city) = %s or UPPER(w.City) = %s) and 
                            p.status IN ('confirmed', 'stand by')
                           ''', (c,'local',c,))
        else:
            # packages for delivary van
            cursor.execute('''
                            SELECT *
                            FROM package p, warehouse w, transfer t
                            WHERE p.WarehouseID = w.WarehouseID and and w.WarehouseID = t.FROM_WH and p.status = %s and p.type = %s=
                           ''', ('waiting','intercity',))
        packages = cursor.fetchall()
        
        # My packages
        cursor.execute('''
                        SELECT *
                        FROM package p
                        WHERE CourierID = %s
                       ''', (session['user_id'],))
        my_packages = cursor.fetchall()

        return render_template('courier_dashboard.html', 
                            courier=courier, 
                            packages=packages,
                            my_packages=my_packages
                            )
    
    except Exception as e: 
        mysql.connection.rollback()
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(e)
        return redirect(url_for('login'))
    finally:
        cursor.close()


@app.route('/accept_package', methods=['POST'])
def accept_package():
    if 'user_id' not in session:
        flash('Not logged in', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    PackageID = request.form['PackageID']
    status = request.form['status']

    try:
        cursor.execute("""
                        UPDATE package 
                        SET status = %s , CourierID = %s
                        WHERE packageID = %s
                       """, ( status, session['user_id'], PackageID ))
        
        mysql.connection.commit()
        flash('Package accepted successfully! It will remain available until delivery is confirmed.', 'success')
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error accepting package: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('courier_dashboard'))


@app.route('/complete_package', methods=['POST'])
def complete_package():
    if 'user_id' not in session:
        flash('Not logged in', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    PackageID = request.form['PackageID']
    pay = request.form['pay']
    status = request.form['status']
    
    try:
        # Verify package ownership
        cursor.execute("""
                        UPDATE package 
                        SET status = %s
                        WHERE packageID = %s
                       """, ( status, PackageID))
        cursor.execute("""
                        UPDATE user
                        SET wallet = wallet + %s
                        WHERE UID = %s
                       """, (pay,session['user_id'],))
        
        mysql.connection.commit()
        flash('Package marked as delivered!', 'success')
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error completing package: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('courier_dashboard'))

#Transport between warehouses
@app.route('/transport_package', methods=['POST'])
def transport_package():
    if 'user_id' not in session:
        flash('Not logged in', 'danger')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    PackageID = request.form['PackageID']
    status = request.form['status']
    
    try:
        # Verify package ownership
        cursor.execute("""
                        UPDATE package 
                        SET status = %s
                        WHERE packageID = %s
                       """, ( status, PackageID))
        
        mysql.connection.commit()
        flash('Package marked as transported!', 'success')
    
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

            cursor.execute('INSERT INTO payment (acc_number, amount, method, UID,purpose) VALUES (%s, %s, %s, %s,%s)', (acc_number, int(amount), payment_method, session['user_id'], 'recharge'))
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
        if next_id == None:
            next_id = 1
        else:
            next_id = int(next_id)+1
        
        #get warehouse id for the package
        if package_scity == package_dcity:
            package_type = 'local'
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(City) = %s LIMIT 1', (package_scity.upper(),))
            warehouse = cursor.fetchone()
            if not warehouse:
                flash('No warehouse found in the destination city', 'error')
                return redirect(url_for('customer_dashboard'))
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(Area) = %s and  UPPER(City) = %s LIMIT 1', (package_droad.upper(),package_scity.upper(),))
            wh_area = cursor.fetchone()
            
            if not wh_area:
                wh_id = warehouse['WarehouseID']
            elif wh_area['Area'] == package_droad:
                wh_id = wh_area['WarehouseID']

        else:
            package_type = 'intercity'
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(City) = %s LIMIT 1', (package_scity.upper(),))
            warehouse = cursor.fetchone()
            if not warehouse:
                flash('No warehouse found in the destination city', 'error')
                return redirect(url_for('customer_dashboard'))
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(Area) = %s and UPPER(City) = %s LIMIT 1', (package_sroad.upper(),package_scity.upper(),))
            wh_area = cursor.fetchone()
            
            if not wh_area:
                wh_id = warehouse['WarehouseID']
            elif wh_area['Area'] == package_droad:
                wh_id = wh_area['WarehouseID']

        #Make the package
        cursor.execute('''
            INSERT INTO package 
            (PackageID,S_houseNo, S_street, S_city, D_houseNo, D_street, D_city, type, status, WarehouseID, courierID, customerID) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
            (next_id,package_shouse, package_sroad, package_scity, package_dhouse, package_droad, package_dcity,package_type,'unconfirmed', wh_id, -1, session['user_id']))

        mysql.connection.commit()
    
    
    finally:
        cursor.close()   
    return redirect(url_for('customer_dashboard'))


## Dummy Value Generator (Remove later)
@app.route('/create_dummy_data', methods=['POST'])
def create_dummy_data():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Create dummy admin
        cursor.execute('INSERT INTO admin (AdminID, name, email, password) VALUES (999, "Dummy Admin", "dummy@admin.com", "dummy123")')
        
        # Create dummy user/customer
        cursor.execute('INSERT INTO user (UID, email, name, password, phone, AdminID, wallet) VALUES (9999, "dummy@user.com", "Dummy User", "dummy123", 1234567890, 999, 100)')
        cursor.execute('INSERT INTO customer (UID, houseNo, road, city) VALUES (9999, "123", "Main St", "Dummy City")')
        
        # Create dummy courier
        cursor.execute('INSERT INTO user (UID, email, name, password, phone, AdminID, wallet) VALUES (9998, "courier@dummy.com", "Dummy Courier", "dummy123", 987654321, 999, 0)')
        cursor.execute('INSERT INTO courier (UID, name, city, licenseNo, type) VALUES (9998, "Dummy Courier", "Dummy City", "DUMMY123", "motorcycle")')
        
        # Create dummy warehouse
        cursor.execute('INSERT INTO warehouse (WarehouseID, Area, City, AdminID) VALUES ("999", "Dummy Area", "Dummy City", 999)')
        
        mysql.connection.commit()
        flash('Dummy data created successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error creating dummy data: {str(e)}', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('login'))

## Dummy Value Delete (Remove Later)
@app.route('/clear_dummy_data', methods=['POST'])
def clear_dummy_data():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Delete dummy data in reverse order to maintain referential integrity
        cursor.execute('DELETE FROM courier WHERE UID IN (9998)')
        cursor.execute('DELETE FROM customer WHERE UID IN (9999)')
        cursor.execute('DELETE FROM user WHERE UID IN (9998, 9999)')
        cursor.execute('DELETE FROM warehouse WHERE WarehouseID = "999"')
        cursor.execute('DELETE FROM admin WHERE AdminID = 999')
        
        mysql.connection.commit()
        flash('Dummy data cleared successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error clearing dummy data: {str(e)}', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('login'))    


#Confirm Package acter creating
@app.route('/confirm_package', methods=['POST'])
def confirm_package():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    package_id = request.form['package_id']
    account_number = request.form['acc_number']
    payment_method = request.form['payment_method']
    package_price = request.form['price']
    package_type = request.form['type']
    package_status = request.form['status']

    # Check if all data is filled up        
    if not all([account_number, payment_method]):
        flash('Please fill all fields', 'error')
        return redirect(url_for('customer_dashboard'))
    
    try:
        # Check package availability
        cursor.execute("""
            SELECT * 
            FROM package 
            WHERE PackageID = %s
        """, (package_id,))
        package = cursor.fetchone()
        
        if not package:
            flash('Package not found or not assigned to you', 'danger')
            return redirect(url_for('customer_dashboard'))
        
        # Mark package as confirmed (progress = 1)
        cursor.execute("""
            UPDATE package 
            SET status = 'confirmed' 
            WHERE PackageID = %s
        """, (package_id,))

        #Transfer warehouse
        if package_type == 'intercity':
            cursor.execute("""
                SELECT * from package
                WHERE PackageID = %s
            """, (package_id,))
            pkg = cursor.fetchone()
            
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(City) = %s LIMIT 1', (pkg['D_city'].upper(),))
            warehouse = cursor.fetchone()
            if not warehouse:
                flash('No warehouse found in the destination city', 'error')
                return redirect(url_for('customer_dashboard'))
            cursor.execute('SELECT * FROM warehouse WHERE UPPER(Area) = %s and UPPER(City) = %s LIMIT 1', (pkg['D_street'].upper(),pkg['D_city'].upper(),))
            wh_area = cursor.fetchone()
            
            if not wh_area:
                wh_id = warehouse['WarehouseID']
            elif wh_area['Area'] == pkg['D_street']:
                wh_id = wh_area['WarehouseID']

            cursor.execute("""
                           INSERT INTO transfer (FROM_WH, TO_WH) vALUES (%s, %s)
                           """, (pkg['WarehouseID'], wh_id))

            

        #deduct taka
        cursor.execute("""
        UPDATE user
        SET wallet = wallet - %s
        WHERE UID = %s
        """, (package_price, session['user_id']))

        cursor.execute('''
            INSERT INTO payment (acc_number,amount,method,UID,purpose) VALUES (%s, %s, %s, %s, %s)
            ''', (account_number, package_price, payment_method, session['user_id'], 'payment'))
        
        mysql.connection.commit()
        flash('Package confirmed successfully!', 'success')
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error confirming package: {str(e)}', 'danger')
   
    finally:
        cursor.close()
    
    return redirect(url_for('customer_dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
    
