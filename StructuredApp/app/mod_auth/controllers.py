# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from app import db

# Import module forms
from app.mod_auth.forms import LoginForm, RegistrationForm, RemoveForm

# Import module models (i.e. User)
from app.mod_auth.models import User

from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_logged_in, current_user

from run import login_manager

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')



# Set the route and accepted methods
@mod_auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard', user=current_user.email))

    if request.method == 'GET':
        return render_template('auth/login.html')
    email = request.form['email']
    password = request.form['password']
    user =  User.query.filter_by(email=email).first()
    if user is None:
        flash("User does not exist")
        return redirect(url_for('auth.login'))
    elif password != user.password:
        flash("Password is incorrect")
        return redirect(url_for('auth.login'))
    else:
        login_user(user, remember=True)
        return redirect(url_for('auth.dashboard', user=email))


@mod_auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard', user=current_user.email))
    if request.method == 'GET':
        return render_template("auth/register.html")
    if User.query.filter_by(email=request.form['email']).first() is not None:
        flash("User already exists")
        return redirect(url_for("auth.register"))
    if not(request.form['password'] == request.form['passwordRepeat']):
        flash("Error: Passwords do not match.")
        return redirect(url_for("auth.register"))
    user = User(request.form['first'], request.form['last'], request.form['company'], 
        request.form['companyWebsite'], request.form['email'], request.form['phone'], request.form['password'])
    db.session.add(user)
    db.session.commit()
    flash("Your account has been registered!  Please log in.")
    return redirect(url_for('auth.login'))





@mod_auth.route("/remove/", methods=['GET','POST'])
@login_required
def remove():
    if request.method == 'GET':
        return render_template('auth/remove.html', username=current_user.email)
    if not(current_user.email == request.form['email']):
        flash("Please enter the email address associated with this account.")
        return render_template('auth/remove.html', username=current_user.email)
    if not(request.form['password'] == request.form['passwordRepeat']):
        flash("Error: Passwords do not match.")
        return render_template('auth/remove.html', username=current_user.email)
    user = User.query.filter_by(email=request.form['email']).first()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('auth.removeSuccess', email=user.email))





@mod_auth.route("/<user>/dashboard", methods=['GET','POST'])
@login_required
def dashboard(user):
    flash("Welcome to " + user + "'s Dashboard.")
    return render_template('auth/dashboard.html', username=user)



@mod_auth.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    name = current_user.email
    logout_user()
    flash(name + " has been logged out.")
    return redirect(url_for('auth.login'))




@mod_auth.route("/remove/<email>", methods=['GET','POST']) 
def removeSuccess(email):
    flash(email + "'s account has been removed.")
    return redirect(url_for("auth.register"))


@mod_auth.errorhandler(401)
def http_error_handler(error):
    flash("You must log in to access this page.")
    return redirect(url_for('auth.login'))
