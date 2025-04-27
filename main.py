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
app.config['MYSQL_DB'] = '370_courier' #db_name
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
            cursor.close()
            return redirect(url_for('admin_dashboard')) # go to admin dashboard page 
        
        #check if the email is user email
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['UID']
            session['is_admin'] = False
            session['name'] = user['name']
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid email or password', 'danger')
        

    return render_template('login.html')

#Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
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
        cursor.execute('SELECT COUNT(*) as count FROM admin')
        next_id = cursor.fetchone()['count'] + 1
        
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
        cursor.execute('SELECT COUNT(*) as count FROM wearhouse')
        next_id = cursor.fetchone()['count'] + 1
        
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



if __name__ == "__main__":
    app.run(debug=True)
    
