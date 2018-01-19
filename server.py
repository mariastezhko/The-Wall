from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re, md5

app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'

mysql = MySQLConnector(app,'mydb')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/', methods=['POST', 'GET'])
def index():
    errors = False
    if request.method == 'POST':

        form = request.form['purpose']

        if form == 'register':

                first_name = request.form['first_name']
                last_name = request.form['last_name']
                email = request.form['email']
                password = request.form['password']
                conf_password = request.form['conf_password']

                if (len(first_name) < 1) or (len(last_name) < 1) or (len(email) < 1) or (len(password) < 1) or (len(conf_password) < 1):
                    flash('All fields are required', 'error')
                    errors = True
                    #flash("Success! Your name is {}".format(request.form['name']))
                #elif not (first_name.isalpha() and last_name.isalpha()):
                if not (first_name.isalpha() and last_name.isalpha()):
                        flash('First and Last Name cannot contain any numbers', 'error')
                        errors = True
                #elif not EMAIL_REGEX.match(email):
                if not EMAIL_REGEX.match(email):
                        flash("Email must be valid")
                        errors = True
                #elif len(password) <= 8:
                if len(password) <= 8:
                        flash('Password must be more than 8 characters', 'error')
                        errors = True
                #elif password != conf_password:
                if password != conf_password:
                        flash("Password doesn't match!", 'error')
                        errors = True
                #else:

                if errors == False:
                     # check if user exists
                     select_query = "SELECT email FROM users WHERE email = :specific_email LIMIT 1"
                     data = {'specific_email': email}
                     found = mysql.query_db(select_query, data)
                     if not found:
                        flash("Thanks for submitting your information!")
                        insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
                        data = {
                         'first_name': first_name,
                         'last_name': last_name,
                         'email': email,
                         'password': md5.new(password).hexdigest()
                         }
                        mysql.query_db(insert_query, data)
                        flash("Registration completed!")
                        return redirect('/success')
                     else:
                        flash("User already exists!")
                        return redirect('/')
                else:
                 return redirect('/')
        else:
                email = request.form['email']
                password = md5.new(request.form['password']).hexdigest()
                select_query = "SELECT id, email, password FROM users WHERE email = :specific_email LIMIT 1"
                data = {'specific_email': email}
                found = mysql.query_db(select_query, data)
                print ("***found", found)
                if not found:
                    flash("Email was not found")
                    return redirect('/')
                else:
                    if (found[0]['password']) != password:
                        flash("Wrong password!")
                        return redirect('/')
                    else:
                        flash("You have successfully logged in!")
                        session['user_id'] = found[0]['id']
                        return redirect('/success')
    else:
        return render_template('index.html')

@app.route('/success')
def success():    
    return render_template('success.html')



app.run(debug=True)
