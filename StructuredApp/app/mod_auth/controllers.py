import os
import urllib.request, json 

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

from app.mod_auth.helpers import truncate, analyze
from collections import Counter

import sys



mod_auth = Blueprint('auth', __name__, url_prefix='/auth')
instagram_access_token = '22061997.f474111.9666e524ddb140608d124b554fb8bda0'
facebook_access_token = '1430922756976623|b9CHdj7HQEPluzKIqZosLTnTaJQ'
google_places_access_token = 'AIzaSyAokrPlw45fd-jNzarVz09OPNVXRB2kdTg'

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
        return redirect(url_for('auth.dashboard'))

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
        return redirect(url_for('auth.dashboard'))


@mod_auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
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
    for influencer in current_user.influencers:
        url = urllib.request.urlopen('https://www.instagram.com/' +  influencer.handle + '/media/')
        data = json.loads(url.read().decode())
        numPosts = 0  #number of posts influencer has available
        numLikes = 0
        numComments = 0
        # for item in data['items']:
        numPosts += 1
        posts += 1
        likes += data['items'][0]['likes']['count']
        comments += data['items'][0]['comments']['count']
        numLikes += data['items'][0]['likes']['count']
        numComments += data['items'][0]['comments']['count']
        numPostsArray += [numPosts]
        likesArray += [truncate(numLikes)]
        commentsArray += [truncate(numComments)]
        pictures += [data['items'][0]['user']['profile_picture']]
        names += [data['items'][0]['user']['full_name']]
        media += [data['items'][0]]
        mediaId = data['items'][0]['id'].split('_')[0]
        try:
            commentsUrl = urllib.request.urlopen('https://api.instagram.com/v1/media/'+ mediaId + '/comments?access_token=' + instagram_access_token)
            commentsData = json.loads(commentsUrl.read().decode())
            for comment in commentsData['data']:
                score, magnitude = analyze(comment['text'])
                name = comment['from']['full_name']
                id = comment['from']['id']
                commenterURL = urllib.request.urlopen('https://www.instagram.com/' +  comment['from']['username'] + '/media/')
                commenterMedia = json.loads(commenterURL.read().decode())
                locations = []
                for item in commenterMedia['items']:
                    if item['location'] is not None:
                        locations += [item['location']['name']]

                states = []
                
                for location in locations:
                    graphURL = urllib.request.urlopen('https://graph.facebook.com/v2.10/search?type=place&q=' + urllib.parse.quote(location) +'&access_token=' + facebook_access_token)
                    placeID = json.loads(graphURL.read().decode())['data'][0]['id']
                    instagramPlaceURL = urllib.request.urlopen('https://api.instagram.com/v1/locations/search?facebook_places_id='+ placeID +'&access_token=' + instagram_access_token)
                    placeData = json.loads(instagramPlaceURL.read().decode())
                    latitude = placeData['data'][0]['latitude']
                    longitude = placeData['data'][0]['longitude']
                    geocodeURL = urllib.request.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(latitude) +','+ str(longitude) +'&sensor=false')
                    place = json.loads(geocodeURL.read().decode())
                    for component in place['results'][0]['address_components']:
                        if 'administrative_area_level_1' in component['types']:
                            states += [component['long_name']]
                state = Counter(states).most_common(1)[0][0]

                lead =  Lead.query.filter_by(id=id).first()

                if lead is not None:
                    lead.score = (lead.score + score * magnitude) / 2
                    db.session.commit()

                else:
                    newLead = Lead(id, name, state, score * magnitude)
                    db.session.add(newLead)
                    db.session.commit()
        except:
            print('Cannot access comments', file=sys.stderr)
       



                







    templateData = {
        'size' : request.args.get('size','thumb'),
        # 'media' : recent_media,
        'media' : media,
        'influencers' : current_user.influencers,
        'likes' : '{:,}'.format(likes),
        'comments' : '{:,}'.format(comments),
        'posts' : '{:,}'.format(posts),
        'pictures' : pictures,
        'names' : names,
        'commentsArray' : commentsArray,
        'likesArray' : likesArray,
        'numPostsArray' : numPostsArray

    }
        
    return render_template('auth/dashboard.html', **templateData)
    # else:
    #     return redirect(url_for('auth.user_photos'))



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

        session['instagram_access_token'] = instagram_access_token
        session['instagram_user'] = user

        influencer = Influencer(user.get('username'), instagram_access_token)
        influencer.users.append(current_user)
        db.session.add(influencer)
        db.session.commit()

        return redirect(url_for('auth.dashboard')) 
        
    else:
        return "No code provided"


@mod_auth.route("/addinfluencer", methods=['GET','POST'])
@login_required
def add():
    influencer = Influencer(request.form['handle'], None)
    influencer.users.append(current_user)
    db.session.add(influencer)
    db.session.commit()
    flash("Influencer has been added")
    return redirect(url_for('auth.manage'))

@mod_auth.route("/removeinfluencer", methods=['GET','POST'])
@login_required
def removeInfluencer():
    influencer = Influencer.query.filter_by(handle=request.form['handle']).first()
    db.session.delete(influencer)
    db.session.commit()
    flash("Influencer has been removed")
    return redirect(url_for('auth.manage'))

@mod_auth.route("/manage", methods=['GET','POST'])
@login_required
def manage():
    pictures = []
    names = []
    for i in current_user.influencers:
        url = urllib.request.urlopen('https://www.instagram.com/' +  i.handle + '/media/')
        data = json.loads(url.read().decode())
        pictures += [data['items'][0]['user']['profile_picture']]
        names += [data['items'][0]['user']['full_name']]
    
    templateData = {
        
        'influencers' : current_user.influencers,
        'userDash' : url_for("auth.dashboard"),
        'pictures' : pictures,
        'names' : names
    }
    return render_template('auth/influencers.html', **templateData)


