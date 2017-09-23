from flask import Flask
from flask_login import UserMixin
from app import db
import hashlib
from sqlalchemy.orm import relationship
from random import randint

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.String(64), db.ForeignKey('auth_user.id')),
    db.Column('influencer_id', db.String(64), db.ForeignKey('auth_influencer.id'))
)

class User(UserMixin, db.Model):
	__tablename__ = 'auth_user'

	id = db.Column(db.String(64), primary_key=True)
	first = db.Column(db.String(128))
	last = db.Column(db.String(128))
	company = db.Column(db.String(128))
	website = db.Column(db.String(128))
	email = db.Column(db.String(128), unique=True)
	phone = db.Column(db.String(12))
	password = db.Column(db.String(128))
	keyword = db.Column(db.String(128))
	influencers = db.relationship("Influencer", secondary=association_table, backref=db.backref('users', lazy='dynamic'))
	


	
    
	def __init__(self, first, last, company, website, email, phone, password):
		self.first = first
		self.last = last
		self.company = company
		self.website = website
		self.email = email
		self.phone = phone
		self.password = password
		hashed = hashlib.sha1()
		hashed.update(email.encode('utf-8'))
		self.id = str(hashed)

		


class Influencer(db.Model):
	__tablename__ = 'auth_influencer'

	id = db.Column(db.String(64), primary_key=True)
	handle = db.Column(db.String(128))
	token = db.Column(db.String(128))
	stars = db.Column(db.Integer)
	leads = db.relationship("Lead", backref="influencer", lazy='dynamic')


	
	def __init__(self, handle, token):
		self.handle = handle
		self.token = token
		hashed = hashlib.sha1()
		hashed.update(handle.encode('utf-8'))
		self.id = str(hashed)




class Lead(db.Model):
	__tablename__ = 'auth_lead'

	id = db.Column(db.String(64), primary_key=True)
	name = db.Column(db.String(128))
	location = db.Column(db.String(128))
	score = db.Column(db.Float)
	createdBy = db.Column(db.String(128))
	influencer_id = db.Column(db.String(64), db.ForeignKey('auth_influencer.id'))


	
	def __init__(self, id, name, location, score, createdBy):
		self.name = name
		self.location = location
		self.score = score
		hashed = hashlib.sha1()
		unique = str(createdBy) + str(id)
		hashed.update(unique.encode('utf-8'))
		self.id = str(hashed)
		self.createdBy = createdBy




	
       
