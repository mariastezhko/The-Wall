from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re, md5

app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'

mysql = MySQLConnector(app,'forum')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    errors = False
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    conf_password = request.form['conf_password']

    if (len(first_name) < 1) or (len(last_name) < 1) or (len(email) < 1) or (len(password) < 1) or (len(conf_password) < 1):
        flash('All fields are required', 'error')
        errors = True
    if not (first_name.isalpha() and last_name.isalpha()):
            flash('First and Last Name cannot contain any numbers', 'error')
            errors = True
    if not EMAIL_REGEX.match(email):
            flash("Email must be valid")
            errors = True
    if len(password) <= 8:
            flash('Password must be more than 8 characters', 'error')
            errors = True
    if password != conf_password:
            flash("Password doesn't match!", 'error')
            errors = True

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
            return redirect('/wall')
         else:
            flash("User already exists!")
            return redirect('/')
    else:
     return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    select_query = "SELECT id, first_name AS name, email, password FROM users WHERE email = :specific_email LIMIT 1"
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
            session['user_name'] = found[0]['name']
            return redirect('/wall')

@app.route('/post_message', methods=['POST'])
def postMessage():
    message = request.form['message']
    insert_query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
    data = {
     'user_id': session['user_id'],
     'message': message
     }
    mysql.query_db(insert_query, data)
    return redirect('/wall')

@app.route('/post_comment/<int:message_id>', methods=['POST'])
def postComment(message_id):
    print message_id
    comment = request.form['comment']
    insert_query = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id, :message_id, :comment, NOW(), NOW())"
    data = {
     'user_id': session['user_id'],
     'message_id': message_id,
     'comment': comment
     }
    mysql.query_db(insert_query, data)
    return redirect('/wall')

@app.route('/wall')
def wall():
        if 'user_id' in session:
            select_query_messages = "SELECT messages.id AS id, CONCAT(users.first_name, ' ', users.last_name) AS name, messages.created_at AS date_posted, messages.message AS message FROM users JOIN messages ON users.id = messages.user_id"
            messages = mysql.query_db(select_query_messages)
            select_query_comments = "SELECT messages.id AS message_id, CONCAT(users.first_name, ' ', users.last_name) AS name, comments.created_at AS date_posted, comments.comment AS comment FROM users JOIN comments ON users.id = comments.user_id JOIN messages ON messages.id = comments.message_id"
            comments = mysql.query_db(select_query_comments)
            return render_template('wall.html', messages=messages, comments=comments)
        else:
            return redirect('/')
#flash("Success! Your name is {}".format(request.form['name']))

@app.route('/log_off', methods=['POST'])
def logOff():
    session['user_id'] = None
    return redirect('/')


app.run(debug=True)
