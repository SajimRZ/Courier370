from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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
    cursor.close()
    return render_template('customer_dashboard.html', customer = customer)

@app.route('/courier_dashboard', methods = ['GET', 'POST'])
def courier_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM user u, courier c where u.UID = c.UID and c.UID = %s',(session['user_id'],))
    courier = cursor.fetchone()
    cursor.execute('SELECT * FROM package') #type filtering todo
    packages = cursor.fetchall()  
    cursor.close()
    return render_template('courier_dashboard.html', courier = courier)

## Courier Dashboard
@app.route('/courier_dashboard', methods=['GET', 'POST'])
def courier_dashboard_action():
    if 'user_id' not in session:    
        return redirect(url_for('login'))   
    
    return render_template('courier_dashboard.html')

## Click action in customer dashboard
@app.route('/handle_click/<action>')
def handle_click(action):
    #Profile
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if action == 'profile':
        cursor.execute('SELECT * FROM user u, customer c where c.UID = u.UID and c.UID = %s', (session['user_id'],))
        user_info = cursor.fetchone()
    cursor.close
    return render_template('profile.html', user=user_info)      


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

#accept package (incomplete)
@app.route('/accept_package/<package_id>', methods=['POST'])
def accept_package(package_id):
    if 'courier_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()

    # try:
    #     cursor.execute("SELECT * FROM package WHERE packageID = %s", (package_id)) #forgot how to sql
    #     package = cursor.fetchone()

    #     if not package:
    #         return jsonify({'success': False, 'message': 'Package not found'})
        
    #     if package.status != 'Available':
    #         return jsonify({'success': False, 'message': 'Package already taken'})
        
    # package.status = 'In Transit'
    # package.courier_id = session['courier_id']
    # db.session.commit()
    
    #return jsonify({'success': True})

#recieve package for transfer
@app.route('/my_package', methods=['GET', 'POST'])
def my_package():
    print("kisu akta/it works")
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

            cursor.execute('INSERT INTO payment (acc_number, amount, method, UID) VALUES (%s, %s, %s, %s)', (acc_number, int(amount), payment_method, session['user_id']))
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
        
        

if __name__ == "__main__":
    app.run(debug=True)
    
