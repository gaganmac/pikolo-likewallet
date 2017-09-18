from __future__ import print_function
import sys
import os
import urllib
import ujson as json 

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

import json
import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials
from twilio.rest import Client
credentials = GoogleCredentials.get_application_default()

instagram_access_token = '22061997.f474111.9666e524ddb140608d124b554fb8bda0'
facebook_access_token = '1430922756976623|b9CHdj7HQEPluzKIqZosLTnTaJQ'
google_places_access_token = 'AIzaSyAokrPlw45fd-jNzarVz09OPNVXRB2kdTg'
geocoding_token = 'AIzaSyA3KPOTxkMlp9egIC1Ou_9jL14c1xKyr9g'
twilio_sid = "AC4e3839298177a775fcbba6a542de1003"
twilio_token = "c82ade5b3a42b8881d4cac5623658ff3"
client = Client(twilio_sid, twilio_token)


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
		num = int(round(num, -6))
		num = str(num)
		num = num[:-6]
		num = num + 'm'
		return num
	elif num > 1000:
		num = int(round(num, -3))
		num = str(num)
		num = num[:-3]
		num = num + 'k'
		return num
	else:
		return str('{:,}'.format(num))



def influencerLoop(influencers, likes, comments, posts, media, names, pictures, numPostsArray, likesArray, commentsArray, current_user):
	length = 0
	mapData = []
	graph = {}
	for influencer in influencers:
		url = urllib.urlopen('https://www.instagram.com/' +  influencer.handle + '/media/')
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
			commentsUrl = urllib.urlopen('https://api.instagram.com/v1/media/'+ mediaId + '/comments?access_token=' + instagram_access_token)
			commentsData = json.loads(commentsUrl.read().decode())
			for comment in commentsData['data']:
				score, magnitude = analyze(comment['text'])
				name = comment['from']['full_name']
				lead = Lead.query.filter_by(influencer_id=influencer.id).filter_by(name=name).first()
				if lead is None:
					id = comment['from']['id']
					commenterURL = urllib.urlopen('https://www.instagram.com/' +  comment['from']['username'] + '/media/')
					commenterMedia = json.loads(commenterURL.read().decode())
					locations = []
					for item in commenterMedia['items']:
						if item['location'] is not None:
							locations += [item['location']['name']]

					states = []
			        
					for location in locations:
						graphURL = urllib.urlopen('https://graph.facebook.com/v2.10/search?type=place&q=' + urllib.quote(location) +'&limit=1&access_token=' + facebook_access_token)
						placeID = json.loads(graphURL.read().decode())['data'][0]['id']
						instagramPlaceURL = urllib.urlopen('https://api.instagram.com/v1/locations/search?facebook_places_id='+ placeID +'&access_token=' + instagram_access_token)
						placeData = json.loads(instagramPlaceURL.read().decode())
						latitude = placeData['data'][0]['latitude']
						longitude = placeData['data'][0]['longitude']
						geocodeURL = urllib.urlopen('https://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(latitude) +','+ str(longitude) +'&sensor=false&result_type=administrative_area_level_1&key=' + geocoding_token)
						place = json.loads(geocodeURL.read().decode())
						states += [place['results'][0]['address_components'][0]['short_name']]
					state = Counter(states).most_common(1)[0][0]
					newLead = Lead(id, name, state, score * magnitude, current_user.id)
					influencer.leads.append(newLead)
					db.session.add(newLead)
					db.session.commit()
				
				
					
				else:
					lead.score = (lead.score + score * magnitude) / 2
					db.session.commit()
					

		except:
			print('Cannot access comments', sys.stderr)



	
	
		for lead in influencer.leads:
			if lead.location not in graph.keys():
				graph[lead.location] = 1
			else:
				graph[lead.location] += 1
			length += 1

	for state in graph.keys(): 
		if length != 0:
			graph[state] = (float(graph[state]) / length) * 100
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


def validateNumber(number):
	number = client.lookups.phone_numbers(number).fetch(type="carrier")
	if number.country_code == 'US' and number.carrier['type'] == 'mobile':
		return True
	return False


