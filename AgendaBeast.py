from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "hello"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#This table haas every single user that is using the system, along with their password
class users(db.Model):
	username = db.Column(db.String(100), primary_key=True)
	password = db.Column(db.String(100))
	
	def __init__(self,username,password):
		self.username = username
		self.password = password

#This table has The columns userName, taskName, descriptiion, due date, whether or not task is finished
class userTable(db.Model):
	username = db.Column(db.String(100), primary_key=True)
	task = db.Column(db.String(100), primary_key=True)
	description = db.Column(db.String(100))
	dueDate = db.Column(db.String(100))
	finished = db.Column(db.Boolean)

	def __init__(self,username,task,description,dueDate,finished=False):
		self.username = username 
		self.task = task 
		self.description = description 
		self.dueDate = dueDate
		self.finished = finished

@app.route("/", methods=["POST", "GET"])
def home():
	if request.method == "POST":
		user = users.query.filter_by(username=request.form["username"]).first() #seeing if the username is in the users table
		if(not(user) or request.form["pw"] != user.password): #checking if the username and password are valid
			flash("the username or password does not match our records please try again","info")
		else:
			return redirect(url_for("getUserTable", name=request.form["username"]))
	return render_template("login.html")

@app.route("/createAccount", methods=["POST", "GET"])
def createAccount(): 
	if request.method == "POST":
		try: #all usernames must be unique otherwise we get an exception
			username = request.form["username"]
			pw = request.form["pw"]
			newEntry = users(username,pw)
			db.session.add(newEntry)
			db.session.commit() 
			return redirect(url_for("getUserTable", name=username))
		except:
			flash("this user name is taken, please try another one","info")
	return render_template("createAccount.html")

@app.route("/updateTable<name>", methods=["POST", "GET"])
def getUserTable(name): 
	if request.method == "POST":
		for t in userTable.query.filter_by(username=name).filter(userTable.task.in_(request.form.getlist("finishedTasks"))).all(): #we have a check mark next each of our tasks when the user checkmark's the task it will be added to the list finishedTasks
			t.finished=True 
		db.session.commit()
	return render_template("userTable.html",values=userTable.query.filter_by(username=name).filter_by(finished=False).all(),userName=name,finalCol="finished")

@app.route("/add<name>", methods=["POST", "GET"])
def add(name): #The method used to add tasks
	if request.method == "POST":
		try: #every task has to be unique other wise an exception will be raised, this is because userName,taskName is a primary key in the userTable
			newEntry = userTable(name,request.form['taskName'],request.form['description'],request.form['dueDate'])
			db.session.add(newEntry)
			db.session.commit() 
		except:
			flash("you already have this task, please use a new name","info")
	return render_template("addTask.html",userName=name)

@app.route("/getPastTasks<name>", methods=["POST", "GET"])
def getPastTasks(name):
	if(request.method == "POST"):
		for t in userTable.query.filter_by(username=name).filter(userTable.task.in_(request.form.getlist("finishedTasks"))).all(): #we have a check mark next each of our tasks when the user checkmark's the task it will be added to the list finishedTasks
			db.session.delete(t)
		db.session.commit()
	return render_template("userTable.html",values=userTable.query.filter_by(username=name).filter_by(finished=True).all(),userName=name,finalCol="Remove Task")

if __name__ == "__main__":
	with app.app_context():
		db.create_all()
	app.run(debug=False,host='0.0.0.0') #when running locally change this line to app.run(debug=True)

