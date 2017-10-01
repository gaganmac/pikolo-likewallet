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
twilio_sid = os.environ['TWILIO_SID']
twilio_token = os.environ['TWILIO_TOKEN']
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
	elif num > 100000:
		num = int(round(num, -3))
		num = str(num)
		num = num[:-3]
		num = num + 'k'
		return num
	elif num > 1000:
		num = round(num, -2) / 1000
		num = str(num)
		num = num + 'k'
		return num
	else:
		return str('{:,}'.format(num))



def influencerLoop(influencers, likes, comments, posts, media, names, pictures, numPostsArray, likesArray, commentsArray, totalPostsArray, 
	totalLikesArray, totalCommentsArray, current_user):
	length = 0
	mapData = []
	graph = {}

	for influencer in influencers:

		#Get influencer data
		url = urllib.urlopen('https://www.instagram.com/' +  influencer.handle + '/media/')
		data = json.loads(url.read().decode())
		numPosts = 0  #number of posts influencer has available
 		numLikes = 0
 		numComments = 0
 		totalPosts = 0
 		totalLikes = 0
 		totalComments = 0
 		# for item in data['items']:
		
		
		pictures += [data['items'][0]['user']['profile_picture']]
		names += [data['items'][0]['user']['full_name']]

		for post in data['items']:
			totalPosts += 1
			totalLikes += post['likes']['count']
			totalComments += post['comments']['count']
		if not current_user.keyword:
			mediaId = data['items'][0]['id'].split('_')[0]
			media += [data['items'][0]]
			posts += 1
			comments += data['items'][0]['comments']['count']
			likes += data['items'][0]['likes']['count']
			numPosts += 1
			numLikes += data['items'][0]['likes']['count']
			numComments += data['items'][0]['comments']['count']

		else:
			for post in data['items']:
				if current_user.keyword and post['caption'] and post['caption']['text'].lower().find(current_user.keyword.lower()) != -1:
					mediaId = post['id'].split('_')[0]
					media += [post]
					posts += 1
					comments += post['comments']['count']
					likes += post['likes']['count']
					numPosts += 1
					numLikes += post['likes']['count']
					numComments += post['comments']['count']

		# 			try:
		# 				#Get comments data
		# 				commentsUrl = urllib.urlopen('https://api.instagram.com/v1/media/'+ mediaId + '/comments?access_token=' + instagram_access_token)
		# 				commentsData = json.loads(commentsUrl.read().decode())
						
		# 				for comment in commentsData['data']:
		# 					#run sentiment analysis 
		# 					score, magnitude = analyze(comment['text'])
		# 					name = comment['from']['full_name']

		# 					leads = [lead.name for lead in influencer.leads]
		# 					if name not in leads:
		# 						#Get commenter data

		# 						id = comment['from']['id']
		# 						commenterURL = urllib.urlopen('https://www.instagram.com/' +  comment['from']['username'] + '/media/')
		# 						commenterMedia = json.loads(commenterURL.read().decode())
		# 						locations = []
		# 						#Add locations of commenter's media
		# 						for item in commenterMedia['items']:
		# 							if item['location'] is not None:
		# 								locations += [item['location']['name']]

		# 						states = []
						        
		# 						for location in locations:

		# 							#Get location data
		# 							graphURL = urllib.urlopen('https://graph.facebook.com/v2.10/search?type=place&q=' + urllib.quote(location) +'&limit=1&access_token=' + facebook_access_token)
		# 							placeID = json.loads(graphURL.read().decode())['data'][0]['id']
		# 							instagramPlaceURL = urllib.urlopen('https://api.instagram.com/v1/locations/search?facebook_places_id='+ placeID +'&access_token=' + instagram_access_token)
		# 							placeData = json.loads(instagramPlaceURL.read().decode())
		# 							latitude = placeData['data'][0]['latitude']
		# 							longitude = placeData['data'][0]['longitude']
		# 							geocodeURL = urllib.urlopen('https://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(latitude) +','+ str(longitude) +'&sensor=false&result_type=administrative_area_level_1&key=' + geocoding_token)
									
		# 							try:
		# 								place = json.loads(geocodeURL.read().decode())
		# 								if len(place['results']):
		# 									states += [place['results'][0]['address_components'][0]['short_name']]
		# 							except:
		# 								print('Location does not use English characters', sys.stderr)

									

		# 						#Choose most common state of all locations

		# 						state = Counter(states).most_common(1)[0][0]
		# 						#Add new lead to database
		# 						newLead = Lead(id, name, state, score * magnitude, current_user.id)
		# 						influencer.leads.append(newLead)
		# 						db.session.add(newLead)
		# 						db.session.commit()
							
								
		# 					else:

		# 						lead =  Lead.query.filter_by(name=name).filter_by(influencer_id=influencer.id).first()

		# 						#Update score of existing lead

		# 						lead.score = (lead.score + score * magnitude) / 2
		# 						db.session.commit()
							
		# 			except Exception as e:
		# 				print('Cannot access comments ' + str(e), sys.stderr)



	
		# for lead in influencer.leads:
		# 	if lead.location not in graph.keys():
		# 		graph[lead.location] = 1
		# 	else:
		# 		graph[lead.location] += 1
		# 	length += 1

		numPostsArray += [numPosts]
		totalPostsArray += [totalPosts]
		if numPosts == 0:
			likesArray += [0]
			commentsArray += [0]
		else:
			likesArray += [truncate(numLikes/numPosts)]
			commentsArray += [truncate(numComments/numPosts)]
		if totalPosts == 0:
			totalLikesArray += [0]
			totalCommentsArray += [0]
		else:
			totalLikesArray += [truncate(totalLikes/totalPosts)]
			totalCommentsArray += [truncate(totalComments/totalPosts)]

	# for state in graph.keys(): 
	# 	if length != 0:
	# 		graph[state] = (float(graph[state]) / length) * 100
	# 		mapData.append({'value': graph[state], 'code': state})


	#Structure data
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
	'totalCommentsArray' : totalCommentsArray,
	'totalLikesArray' : totalLikesArray,
	'totalPostsArray' : totalPostsArray,
	'json' : mapData

	}


	return templateData


def validateNumber(number):
	try:
		number = client.lookups.phone_numbers(number).fetch(type="carrier")
		if number.country_code == 'US' and number.carrier['type'] == 'mobile':
			return True
		return False
	except:
		return False






