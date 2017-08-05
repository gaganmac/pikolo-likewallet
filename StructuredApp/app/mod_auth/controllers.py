import os

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from app import db
from app import app

# Import module forms
from app.mod_auth.forms import LoginForm, RegistrationForm, RemoveForm

# Import module models (i.e. User)
from app.mod_auth.models import User

from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_logged_in, current_user

from run import login_manager

from instagram.client import InstagramAPI



mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

instaConfig = {

    'client_id': 'f47411163bd6493bae1667a70e793fb5',
    'client_secret': '76b892dd1f054d9fba7afcdc2c5d7f18',
    'redirect_uri' : 'https://damp-cliffs-30092.herokuapp.com/auth/instagram_callback'
}
api = InstagramAPI(**instaConfig)



@mod_auth.route('/connect')
@login_required
def user_photos():
    url = api.get_authorize_url(scope=["likes","comments"])
    return redirect(url)




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
        flash("Error: Please enter the email address associated with this account.")
        return render_template('auth/remove.html', username=current_user.email)
    if not(request.form['password'] == current_user.password):
        flash("Error: Incorrect password.")
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
    if 'instagram_access_token' in session and 'instagram_user' in session:
        userAPI = InstagramAPI(access_token=session['instagram_access_token'])
        recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=25)

        templateData = {
            'size' : request.args.get('size','thumb'),
            'media' : recent_media
        }

        return render_template('auth/instagram.html', **templateData)
        

    else:

        return redirect(url_for('auth.user_photos'))



@mod_auth.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    session.clear()
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





@mod_auth.route('/instagram_callback')
@login_required
def instagram_callback():

    code = request.args.get('code')

    if code:

        access_token, user = api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'

        app.logger.debug('got an access token')
        app.logger.debug(access_token)

        # Sessions are used to keep this data 
        session['instagram_access_token'] = access_token
        session['instagram_user'] = user

        return redirect(url_for('auth.dashboard', user=current_user.email)) 
        
    else:
        return "No code provided"
