from flask import Flask, render_template, request, json, redirect, url_for, session, logging, flash
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import MySQLdb.cursors
from werkzeug import generate_password_hash, check_password_hash
import markdown
from flask import Markup
from functools import wraps

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=30)])
    email = StringField('Email', [validators.Length(min=1, max=50)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.Length(min=1, max=30),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    venue = StringField('Venue', [validators.Length(min=1, max=30)])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO test . user(user_name, user_password, user_email) VALUES( %s,%s,%s )", (name , password, email))
        mysql.connection.commit()
        cur.close()
        flash('Account successfully registered')
        return redirect(url_for('personalize', username=name))
    return render_template('signup.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM test . user WHERE user_email = %s", [email])

        if result > 0:
            return redirect(url_for('home', username=email))
        else:
            error = 'Username not found'
            flash("Username not found")
            return render_template('main.html', error=error)

    return render_template('main.html')


@app.route('/personalize/<username>', methods=['GET','POST'])
def personalize(username):
    if request.method == 'POST':
        return redirect(url_for('home', username=username))

    return render_template("personalize.html", username=username)


@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)


@app.route('/home/<username>')
def home(username):
    return render_template("home.html", username=username)


@app.route('/friends/<username>')
def friends(username):
    return render_template("friends.html", username=username)


@app.route('/rlist/<username>')
def rlist(username):
    return render_template("rlist.html", username=username)


@app.route('/venue/<venuename>')
def venue(venuename):
    return render_template("venue.html", venuename=venuename)


if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)

