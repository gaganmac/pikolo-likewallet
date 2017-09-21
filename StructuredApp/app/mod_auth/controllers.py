from __future__ import print_function
import sys
import os
import urllib

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
from app.mod_auth.models import User, Influencer, Lead

from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_logged_in, current_user

from run import login_manager

from instagram.client import InstagramAPI
from BeautifulSoup import BeautifulSoup


from collections import Counter
from helpers import truncate, analyze, influencerLoop, validateNumber

import ujson as json
import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials
from twilio.twiml.voice_response import Reject, VoiceResponse, Say, Dial, Number
credentials = GoogleCredentials.get_application_default()

instagram_access_token = '22061997.f474111.9666e524ddb140608d124b554fb8bda0'
facebook_access_token = '1430922756976623|b9CHdj7HQEPluzKIqZosLTnTaJQ'
google_places_access_token = 'AIzaSyAokrPlw45fd-jNzarVz09OPNVXRB2kdTg'



mod_auth = Blueprint('auth', __name__, url_prefix='')


instaConfig = {

    'client_id': 'f47411163bd6493bae1667a70e793fb5',
    'client_secret': '76b892dd1f054d9fba7afcdc2c5d7f18',
    'redirect_uri' : 'https://damp-cliffs-30092.herokuapp.com/auth/instagram_callback'

}
api = InstagramAPI(**instaConfig)



@mod_auth.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('auth.register'))

@mod_auth.route('/connect')
@login_required
def user_photos():
    url = api.get_authorize_url(scope=["likes","comments"])
    return redirect(url)



#Login controller
@mod_auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'GET':
        return render_template('auth/login.html')
    email = request.form['email']
    password = request.form['password']
    user =  User.query.filter_by(email=email).first()
    #Check if username or password are incorrect
    if user is None or password != user.password:
        flash("Error: Email or password is incorrect")
        return redirect(url_for('auth.login'))
    else:
        login_user(user, remember=True)
        return redirect(url_for('auth.dashboard'))


#Registration controller
@mod_auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'GET':
        return render_template("auth/register.html")
    #Check that email is not taken
    if User.query.filter_by(email=request.form['email']).first() is not None:
        flash("Error: Email is already taken")
        return redirect(url_for("auth.register"))
    #Check that passwords match
    if not(request.form['password'] == request.form['passwordRepeat']):
        flash("Error: Passwords do not match.")
        return redirect(url_for("auth.register"))
    #Add new user to database
    user = User(request.form['first'], request.form['last'], request.form['company'], 
        request.form['companyWebsite'], request.form['email'], request.form['phone'], request.form['password'])
    if not validateNumber(user.phone):
        user.phone = None
    db.session.add(user)
    db.session.commit()
    flash("Your account has been registered!  Please log in.")
    return redirect(url_for('auth.login'))




#Delete account controller
@mod_auth.route("/remove/", methods=['GET','POST'])
@login_required
def remove():
    if request.method == 'GET':
        return render_template('auth/remove.html', username=current_user.email)
    #Check that email is correct
    if not(current_user.email == request.form['email']):
        flash("Error: Email or password is incorrect.")
        return render_template('auth/remove.html', username=current_user.email)
    #Check that password is correct
    if not(request.form['password'] == current_user.password):
        flash("Error: Email or password is incorrect.")
        return render_template('auth/remove.html', username=current_user.email)
    #Check that passwords match
    if not(request.form['password'] == request.form['passwordRepeat']):
        flash("Error: Passwords do not match.")
        return render_template('auth/remove.html', username=current_user.email)
    user = User.query.filter_by(email=request.form['email']).first()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('auth.removeSuccess', email=user.email))

#Dashboard controller
@mod_auth.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard():
    likes = 0   #total likes
    comments = 0 #total comments
    posts = 0 #total posts
    media = []
    names = []
    pictures = []  
    numPostsArray = []  #posts per influencer
    likesArray = []     #likes per influencer
    commentsArray = [] #comments per influencer

    # if session.get('instagram_access_token') and session.get('instagram_user'):
    # userAPI = InstagramAPI(access_token=session['instagram_access_token'])
    # recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=25)
    
    templateData = influencerLoop(current_user.influencers, likes, comments, posts, media, names, pictures, numPostsArray, likesArray, commentsArray, current_user)

    return render_template('auth/dashboard.html', **templateData)
    # else:
    #     return redirect(url_for('auth.user_photos'))


#Logout controller
@mod_auth.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    session['instagram_user'] = None
    session['instagram_access_token'] = None
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


# @mod_auth.route('/instagram_callback')
# @login_required
# def instagram_callback():

#     code = request.args.get('code')

#     if code:

#         access_token, user = api.exchange_code_for_access_token(code)
#         if not access_token:
#             return 'Could not get access token'

#         app.logger.debug('got an access token')
#         app.logger.debug(access_token)

#         session['instagram_access_token'] = instagram_access_token
#         session['instagram_user'] = user

#         influencer = Influencer(user.get('username'), instagram_access_token)
#         influencer.users.append(current_user)
#         db.session.add(influencer)
#         db.session.commit()

#         return redirect(url_for('auth.dashboard')) 
        
#     else:
#         return "No code provided"


#Adding new Influencer
@mod_auth.route("/addinfluencer", methods=['GET','POST'])
@login_required
def add():
    influencer = Influencer(request.form['handle'], None)
    influencer.users.append(current_user)
    db.session.add(influencer)
    db.session.commit()
    flash("Influencer has been added")
    return redirect(url_for('auth.manage'))

#Removing Influencer
@mod_auth.route("/removeinfluencer", methods=['GET','POST'])
@login_required
def removeInfluencer():
    influencer = Influencer.query.filter_by(handle=request.form['handle']).first()
    db.session.delete(influencer)
    db.session.commit()
    flash("Influencer has been removed")
    return redirect(url_for('auth.manage'))

#Influencer manager controller
@mod_auth.route("/manage", methods=['GET','POST'])
@login_required
def manage():
    pictures = []
    names = []
    followers = []
    posts = []
    for i in current_user.influencers:
        url = urllib.urlopen('https://www.instagram.com/' +  i.handle + '/media/')
        page = urllib.urlopen('https://www.instagram.com/' +  i.handle).read()
        soup = BeautifulSoup(page)
        description = soup.find("meta",  property="og:description")['content'].split(' ')
        followers += [description[description.index('Followers,') - 1]]
        posts += [description[description.index('Posts') - 1]]
        data = json.loads(url.read().decode())
        pictures += [data['items'][0]['user']['profile_picture']]
        names += [data['items'][0]['user']['full_name']]
    
    templateData = {
        
        'influencers' : current_user.influencers,
        'userDash' : url_for("auth.dashboard"),
        'pictures' : pictures,
        'names' : names,
        'followers' : followers,
        'posts' : posts
    }
    return render_template('auth/influencers.html', **templateData)


@mod_auth.route("/call", methods=['GET','POST'])
def call():
    numbers = ['720-938-7168', '774-232-6921', '513-675-5664', '310-502-9285']
    response = VoiceResponse()
    caller = request.values['From']
    if not validateNumber(caller):
        response.reject()
    else:
        response.say('Thank you for calling LikeWallet!  Please remain on the line and the next available representative will assist you.', voice='woman', language='en')
        dial = Dial()
        for number in numbers:
            dial.number(number)
            response.append(dial)

    return str(response)

