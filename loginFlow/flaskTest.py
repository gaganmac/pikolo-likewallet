import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, user_logged_in, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dqgpivwiaeynfq:4974dc4f7b498d6a73a172da27ad005ec13d32b4b2dac8a1750b6078af544205@ec2-50-17-217-166.compute-1.amazonaws.com:5432/d8caqcu08s01vk'
app.config['SECRET_KEY'] = 'password'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(30), unique=False)
    
    def __init__(self, email, password):
        self.email = email
        self.password = password
       


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=['GET','POST'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard', user=current_user.email))
	if request.method == 'GET':
  		return render_template("register.html")
	if User.query.filter_by(email=request.form['email']).first() is not None:
		flash("User already exists")
		return redirect(url_for("index"))
	if not(request.form['password'] == request.form['passwordRepeat']):
		flash("Error: Passwords do not match.")
		return redirect(url_for("index"))
	user = User(request.form['email'], request.form['password'])
	db.session.add(user)
	db.session.commit()
	flash("Your account has been registered!  Please log in.")
	return redirect(url_for('login'))




@app.route("/remove", methods=['GET','POST'])
@login_required
def remove():
	if request.method == 'GET':
  		return render_template('remove.html', username=current_user.email)
	if not(request.form['password'] == request.form['passwordRepeat']):
		flash("Error: Passwords do not match.")
		return render_template('remove.html', username=current_user.email)
	username = User(request.form['email'], request.form['password'])
	user = User.query.filter_by(email=username.email).first()
	logout_user()
	db.session.delete(user)
	db.session.commit()
	return redirect(url_for('removeSuccess', email=user.email))

@app.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard', user=current_user.email))

	if request.method == 'GET':
		return render_template('login.html')
	email = request.form['email']
	password = request.form['password']
	user =  User.query.filter_by(email=email).first()
	if user is None:
		flash("User does not exist")
		return redirect(url_for('login'))
	elif password != user.password:
		flash("Password is incorrect")
		return redirect(url_for('login'))
	else:
		login_user(user, remember=True)
		return redirect(url_for('dashboard', user=email))
	

@app.route("/<user>/dashboard", methods=['GET','POST'])
@login_required
def dashboard(user):
	flash("Welcome to " + user + "'s Dashboard.")
	return render_template('dashboard.html', username=user)



@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
	name = current_user.email
	logout_user()
	flash(name + " has been logged out.")
	return redirect(url_for('login'))




@app.route("/remove/<email>", methods=['GET','POST']) 
def removeSuccess(email):
	flash(email + "'s account has been removed.")
	return redirect(url_for("index"))


@app.errorhandler(401)
def http_error_handler(error):
	flash("You must log in to access this page.")
	return redirect(url_for('login'))



  
if __name__ == "__main__":
  db.create_all()
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

