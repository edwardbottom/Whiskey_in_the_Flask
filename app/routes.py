from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, flash, redirect, url_for, request
from flask_pymongo import PyMongo
from app import app
from flask_login import current_user, login_user
import re
from flask import Flask, session
from flask_session import Session
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
import json
from bson import json_util
from bson.json_util import dumps
from random import *
import datetime

#configure the database
app.config['MONGO_DBNAME'] = 'whiskey_flask'
app.config['MONGO_URI'] = 'mongodb://edward.bottom:Duckunder195!@ds117878.mlab.com:17878/whiskey_flask'
app.secret_key = 'TwoHeartedAle'

#intialize libarary for the database
mongo = PyMongo(app)
client = MongoClient()

#class for the user
class User():
	username = ""
	password_hash = ""

	def __init__(self):
		self.username = ""
		self.password_hash = ""

	def set_password(self, password):
 		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
 		return check_password_hash(self.password_hash, password)

	def set_username(self, username):
 		self.username = username

#login route/ default route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
	session.clear()
	error = request.args.get("error")
	return render_template("login.html", error=error, dont_show_header=True)
#route for the home page
@app.route('/home', methods=['GET', 'POST'])
def home():
	#https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/
	#sets whiskey of the day
	now = datetime.datetime.now()
	month = now.month
	day = now.day
	year = now.year
	date_string = str(month) + "/" + str(day) + "/" + str(year)
	prev_whiskey_of_the_day = mongo.db.whiskey_of_the_day.find()
	#checks current day
	for element in prev_whiskey_of_the_day:
		prev_date = element['Current_date']
	totalWhiskys = mongo.db.whiskeys.find().count()
	day_whiskey_id = None
	#if new whisky of the day
	if prev_date != date_string:
		day_whiskey_id = randint(1, totalWhiskys)
		mongo.db.whiskey_of_the_day.remove({})
		mongo.db.whiskey_of_the_day.insert({'ID' : day_whiskey_id, 'Current_date' : date_string})
	#else the same whiskey
	else:
		day_whiskey_id = mongo.db.whiskey_of_the_day.find_one({'Current_date' : date_string})
		day_whiskey_id = day_whiskey_id['ID']
	whiskey_of_the_day = mongo.db.whiskeys.find_one({'ID' : day_whiskey_id})
	return render_template('home.html', whiskey_of_the_day=whiskey_of_the_day,admin=session['is_admin'])

#processes the login
@app.route('/loadLogin', methods=['POST'])
def process():
	#sets values
	username = request.form['username']
	password = request.form['password']
	#if valid
	if mongo.db.users.find({'username':username}).count() > 0:
		user = mongo.db.users.find_one({'username':username})
		if check_password_hash(user["password_hash"], password):
			#make session
			session['username'] = username 
			session['loggedin'] = True
			if user['admin']:
				session['is_admin'] = True
			else:
				session['is_admin'] = False
			return redirect(url_for('home'))
			#invalud login
		else:
			error = "invalid password"
			return redirect(url_for('login', error=error, dont_show_header=True))
	#invalid login
	else:
		print("username is invalid")
		error = "invalid username"
		return redirect(url_for('login', error=error, dont_show_header=True))

#whiskeys route
@app.route('/whiskeys', methods=['POST', 'GET'])
def whiskeys():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	#get all whiskeys
	collection = mongo.db.whiskeys.find()
	my_whiskeys = mongo.db.my_whiskeys.find({'username': session['username']})
	my_whiskey_IDs = [my_whiskey['ID'] for my_whiskey in my_whiskeys]
	return render_template('whiskeys.html', collection=collection, my_whiskey_IDs=my_whiskey_IDs,admin=session['is_admin'])

#route for my whiskeys
@app.route('/loadMyWhiskeys', methods=['POST','GET'])
def loadMyWhiskeys():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	#get and load my whiskeys from database
	my_whiskeys = mongo.db.my_whiskeys.find({'username': session['username']})
	my_whiskey_IDs = [my_whiskey['ID'] for my_whiskey in my_whiskeys]
	my_whiskey_list = [mongo.db.whiskeys.find_one({'ID':ID}) for ID in my_whiskey_IDs]
	return render_template("mywhiskeys.html", my_whiskey_list=my_whiskey_list,admin=session['is_admin'])

#adds a whiskey to the collection
@app.route('/addToMyCollection', methods=['POST', 'GET'])
def addToMyCollection():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	ID = int(request.form['id'])
	username = session['username']
	#if whiskey is not in collection
	if mongo.db.my_whiskeys.find({'ID':ID,'username':username}).count() == 0:
		mongo.db.my_whiskeys.insert({'ID':ID,'username':username})
		return redirect((url_for('loadHome')))
	#if whiskey is in collection
	else:
		mongo.db.my_whiskeys.remove({'ID':ID,'username':username})
		return redirect((url_for('loadHome')))

@app.route('/removeFromCollection',methods=['POST'])
def removeFromCollection():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	ID = int(request.form['id'])
	mongo.db.my_whiskeys.remove({'ID':ID})
	mongo.db.reviews.remove({'whiskey_id':ID})
	mongo.db.whiskeys.remove({'ID':ID})
	return redirect((url_for('whiskeys')))

#reroutes to the register html
@app.route('/register', methods=['POST'])
def register():
	return render_template('register.html', dont_show_header=True)

#processes register information
@app.route('/processRegister', methods=['GET', 'POST'])
def processRegister():
	error = None
	username = request.form['username']
	password = request.form['password']
	repassword = request.form['repassword']
	#if same password
	if password == repassword:
		#regex check
		if re.search('^[\w_\.\-]+$',username):
			if mongo.db.users.find({'username':username}).count() == 0:
				#cretes account
				mongo.db.users.insert({'username':username,'password_hash':generate_password_hash(password),'admin':False})
				success = "new user " + username + " created"
				return redirect(url_for('login'))
			#invalid
			else:
				error = "the username " + username + " is already taken. "
		#invalid
		else:
			error = "Your username can contain only upper/lowercase letters, numbers, periods, dashes, and underscores. "
	#invalid
	else:
		error = "passwords do not match"
	return render_template('register.html', error=error, dont_show_header=True)

#loads the reviews
@app.route('/goToReviews',methods=['GET'])	
def redirectToReviews():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	session['whiskeyReviewedID'] = int(request.args['id'])		
	return redirect(url_for('loadReviews'))

#gets the reviews from the data base
@app.route('/reviews', methods=['GET', 'POST'])
def loadReviews():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	whiskey_id = session['whiskeyReviewedID']
	whiskey = mongo.db.whiskeys.find_one({'ID' : whiskey_id})
	reviews = mongo.db.reviews.find({'whiskey_id' : whiskey_id})
	review_count = reviews.count()
	user_already_reviewed=False
	user_review = None
	mean = 0
	#iterates through all the reviews
	for review in reviews:
		mean+=review['rating']
		if review['author']==session['username']:
			user_already_reviewed=True
			user_review = review
	if review_count>1:
		mean/=review_count
	return render_template('review.html', whiskey=whiskey, user_review=user_review,reviews=mongo.db.reviews.find({'whiskey_id' : whiskey_id}), review_count=review_count,user_already_reviewed=user_already_reviewed,mean_rating=mean,admin=session['is_admin'],current_user=session['username'])

#submits a values for reviews
@app.route('/submitReview',methods=['POST'])
def processReview():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	whiskey_id = int(request.form['whiskey_id'])
	author = session['username']
	review = request.form['content']
	rating = float(request.form['rating'])
	users_liked = []
	#inserts review
	mongo.db.reviews.insert({'whiskey_id':whiskey_id,'author':author,'review':review,'rating':rating,'users_liked':users_liked,'num_liked':0})
	return redirect(url_for('loadReviews'))

#route to like a review
@app.route('/likeReview',methods=['POST'])
def likeReview():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	author = request.form['author']
	whiskey_id = int(request.form['id'])
	review = mongo.db.reviews.find_one({'author':author,'whiskey_id':whiskey_id})
	users_liked = review['users_liked']
	users_liked.append(session['username'])
	num_liked = review['num_liked']
	num_liked+=1
	#updates likes
	mongo.db.reviews.update_one({'author':author,'whiskey_id':whiskey_id},{'$set':{'users_liked':users_liked,'num_liked':num_liked}})
	return redirect(url_for('loadReviews'))

#route to unlike a review	
@app.route('/unlikeReview',methods=['POST'])
def unlikeReview():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	author = request.form['author']
	whiskey_id = int(request.form['id'])
	review = mongo.db.reviews.find_one({'author':author,'whiskey_id':whiskey_id})
	users_liked = review['users_liked']
	users_liked.remove(session['username'])
	num_liked = review['num_liked']
	num_liked-=1
	#update database
	mongo.db.reviews.update_one({'author':author,'whiskey_id':whiskey_id},{'$set':{'users_liked':users_liked,'num_liked':num_liked}})
	return redirect(url_for('loadReviews'))

#submit a whiskey route
@app.route('/submit')
def submit():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	return render_template("submitwhiskey.html",title="Submit",admin=session['is_admin'])

#logs the user out and destroys the session
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	session.clear()
	return redirect(url_for('.login'))

#redirects to the form for the whiskey
@app.route('/whiskeyForm', methods=['GET', 'POST'])
def whiskeyForm():
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	return render_template("submitwhiskey.html",admin=session['is_admin'])

#route to add a whiskey to the database
@app.route('/addWhiskey', methods=['GET', 'POST'])
def addWhiskey():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	name = request.form['name']
	rating = float(request.form['rating'])
	country = request.form['country']
	category = request.form['category']
	price = request.form['price']
	abv = int(request.form['abv'])
	age = int(request.form['age'])
	brand = request.form['brand'] 
	eyedee = mongo.db.whiskeys.find().count()+1
	#add to data base
	mongo.db.whiskeys.insert({"Name":name,"Rating":rating,"Country":country,"Category":category,"Price":price,"ABV":abv,"Age":age,"Brand":brand,"ID":eyedee})
	return redirect(url_for('whiskeys'))

#edit reviews
@app.route('/editReview', methods=['POST', 'GET'])
def editReview():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	return render_template("editReview.html", author=request.form['author'], rating=request.form['rating'], review=request.form['review'], whiskey_id=request.form['whiskey_id'],admin=session['is_admin'])

#delete a review
@app.route('/deleteReview',methods=['POST'])
def deleteReview():
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	mongo.db.reviews.remove({'whiskey_id':int(request.form['whiskey_id']),'author':request.form['author']})
	return redirect(url_for('loadReviews'))
#update review values
@app.route('/updateReview', methods=['POST', 'GET'])
def updateReview():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	review = request.form['content']
	rating = float(request.form['rating'])
	whiskey_id = int(request.form['whiskey_id'])
	creator = session["username"]
	mongo.db.reviews.update_one({'author':creator,'whiskey_id':whiskey_id},{'$set':{'rating':rating,'review':review}})
	return redirect(url_for('loadReviews'))

#loads the data for the table
@app.route('/data', methods=['POST', 'GET'])
def loadData():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	#renders remplate with data
	whiskeys_data = [whiskey for whiskey in mongo.db.whiskeys.find()]
	reviews = [review for review in mongo.db.reviews.find()]
	return render_template("data.html",admin=session['is_admin'],whiskeys=whiskeys_data,reviews=reviews)

#loads all users for admin status
@app.route('/users',methods=['POST'])
def users():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	users = mongo.db.users.find()
	#render template
	return render_template("users.html",users=users,admin=session['is_admin'])	

#route to give admin status
@app.route('/makeAdmin',methods=['POST'])
def make_admin():
	#session check
	if 'loggedin' not in session or not session['loggedin']:
		return redirect(url_for('login'))
	username = request.form['username']
	#update database
	mongo.db.users.update_one({'username':username},{'$set':{'admin':True}})
	return redirect(url_for('users'))

#runs the main app
if __name__ == '__main__':
	app.secret_key = 'supersecretkey'
	app.run(debug=True)