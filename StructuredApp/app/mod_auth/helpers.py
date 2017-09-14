from __future__ import print_function
import os
import urllib2, json 
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


from collections import Counter

import sys
import json

import argparse


from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()

instagram_access_token = '22061997.f474111.9666e524ddb140608d124b554fb8bda0'
facebook_access_token = '1430922756976623|b9CHdj7HQEPluzKIqZosLTnTaJQ'
google_places_access_token = 'AIzaSyAokrPlw45fd-jNzarVz09OPNVXRB2kdTg'


def analyze(content):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()

    document = types.Document(
        content=content,
        type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    # Print the results
    return score, magnitude


def truncate(num):
	if num > 1000000:
		num = round(num, -6)
		num = str(num)
		num = num[:-6]
		num = num + 'm'
		return num
	elif num > 1000:
		num = round(num, -3)
		num = str(num)
		num = num[:-3]
		num = num + 'k'
		return num
	else:
		return str('{:,}'.format(num))



def influencerLoop(influencers, likes, comments, posts, media, names, pictures, numPostsArray, likesArray, commentsArray):
	for influencer in influencers:
		url = urllib2.urlopen('https://www.instagram.com/' +  influencer.handle + '/media/')
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
		commentsUrl = urllib2.urlopen('https://api.instagram.com/v1/media/'+ mediaId + '/comments?access_token=' + instagram_access_token)
		commentsData = json.loads(commentsUrl.read().decode())
		for comment in commentsData['data']:
			score, magnitude = analyze(comment['text'])
			name = comment['from']['full_name']
			id = comment['from']['id']
			commenterURL = urllib2.urlopen('https://www.instagram.com/' +  comment['from']['username'] + '/media/')
			commenterMedia = json.loads(commenterURL.read().decode())
			locations = []
			for item in commenterMedia['items']:
				if item['location'] is not None:
					locations += [item['location']['name']]

			states = []
	        
			for location in locations:
				graphURL = urllib2.urlopen('https://graph.facebook.com/v2.10/search?type=place&q=' + urllib2.pathname2url(location) +'&access_token=' + facebook_access_token)
				placeID = json.loads(graphURL.read().decode())['data'][0]['id']
				instagramPlaceURL = urllib2.urlopen('https://api.instagram.com/v1/locations/search?facebook_places_id='+ placeID +'&access_token=' + instagram_access_token)
				placeData = json.loads(instagramPlaceURL.read().decode())
				latitude = placeData['data'][0]['latitude']
				longitude = placeData['data'][0]['longitude']
				geocodeURL = urllib2.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(latitude) +','+ str(longitude) +'&sensor=false')
				place = json.loads(geocodeURL.read().decode())
				for component in place['results'][0]['address_components']:
					if 'administrative_area_level_1' in component['types']:
						states += [component['short_name']]
			state = Counter(states).most_common(1)[0][0]

			lead =  Lead.query.filter_by(id=id).first()

			if lead is not None:
				lead.score = (lead.score + score * magnitude) / 2
				db.session.commit()

			else:
				newLead = Lead(id, name, state, score * magnitude)
				db.session.add(newLead)
				db.session.commit()
	except Exception as e:
		print('Cannot access comments' + str(e), file=sys.stderr)



	mapData = []
	graph = {}
	audience = Lead.query.count()
	for lead in Lead.query.all():
		if lead.location not in graph.keys():
			graph[lead.location] = 1
		else:
			graph[lead.location] += 1

	for state in graph.keys(): 
		graph[state] = (float(graph[state]) / audience) * 100
		mapData.append({'value': graph[state], 'code': state})



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
	'numPostsArray' : numPostsArray,
	'json' : mapData

	}


	return templateData



