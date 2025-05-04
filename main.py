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

        #check if the email is an Admin email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password))

        admin = cursor.fetchone()
        if admin:
            session['user_id'] = admin['AdminID']
            session['is_admin'] = True
            session['name'] = admin['name']

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
            
            if courier_check == None:
                return redirect(url_for('customer_dashboard'))
            
        cursor.close()
        flash('Invalid email or password', 'danger')
        

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        house = request.form['house']
        road = request.form['road']
        city = request.form['city']
        license = request.form['license']
        vtype = request.form['type'] 
        role = request.form['role']  # 'customer' or 'courier'
        
        # Validate inputs
        if not all([name, email, password, role]):
            flash('Please fill all fields', 'error')
            return redirect(url_for('signup'))
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Check if email already exists
            cursor.execute('SELECT email FROM user WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('signup'))
            
            # Insert into user table (common fields)
            cursor.execute('SELECT max(UID) as count FROM user')
            next_id = int(cursor.fetchone()['count']) + 1
            cursor.execute('''
                INSERT INTO user (UID, email, name, password, phone)
                VALUES (%s, %s, %s, %s)
            ''', (next_id, email, name, password, phone))
            
            # Insert into role-specific table
            if role == 'customer':
                cursor.execute('''
                    INSERT INTO customer (UID, houseNo, road, city)
                    VALUES (%s, %s, %s, %s)
                ''', (next_id, house, road, city))
            elif role == 'courier':
                cursor.execute('''
                    INSERT INTO courier (UID, name, city, licenseNo, type)
                    VALUES (%s, %s, %s)
                ''', (next_id, name, city, license, vtype))
            
            mysql.connection.commit()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('signup'))
            
        finally:
            cursor.close()
    
    return render_template('signup.html')

#Admin Dashboard
@app.route('/admin_dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    #delete wearhouse
    if request.method == 'POST':
        action = request.args.get('action') 
        
        if action == "delete_wh":
            delete_wh_id = request.form["WearhouseID"]
            cursor.execute("DELETE FROM wearhouse WHERE WearhouseID = %s", (delete_wh_id,))
            mysql.connection.commit()
            flash("Wearhouse deleted successfully!", "success")

    # Get all users
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    
    # Get all admins
    cursor.execute('SELECT * FROM admin')
    admins = cursor.fetchall()

    cursor.execute('SELECT * FROM wearhouse')
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

##Create Wearhouse
@app.route('/admin_dashboard/createwh', methods=['POST'])
def create_wearhouse():  
    area = request.form['Area']
    city = request.form['City']
    a_id = request.form['AdminID']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT max(WearhouseID) as count FROM wearhouse')
        next_id = int(cursor.fetchone()['count'])+1
        
        cursor.execute(
            'INSERT INTO wearhouse (WearhouseID, Area, City, AdminID) VALUES (%s, %s, %s, %s)',
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
    
    #properties of the icons
    # name, what it looks like, color, what it does
    icons = [
        {'name': 'Profile', 'icon_class': 'fa-user', 'color': 'primary', 'action': 'profile'},
        {'name': 'Quick Delivery', 'icon_class': 'fa-motorcycle', 'color': 'success', 'action': 'quick'},
        {'name': 'Shipment', 'icon_class': 'fa-truck', 'color': 'info', 'action': 'long'},
        {'name': 'Orders', 'icon_class': 'fa-chart-bar', 'color': 'warning', 'action': 'orders'},
        {'name': 'Payment Options', 'icon_class': 'fa-dollar', 'color': 'success', 'action': 'payment options'},
        {'name': 'Edit', 'icon_class': 'fa-cog', 'color': 'secondary', 'action': 'edit'},
    ]

    return render_template('customer_dashboard.html', icons = icons)


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
        
        

if __name__ == "__main__":
    app.run(debug=True)
    
