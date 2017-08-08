from flask import Flask
from flask_login import UserMixin
from app import db
import hashlib


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
		
       
