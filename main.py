from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_paginate import Pagination, get_page_parameter, get_page_args
import requests
import json
import os
app = Flask(__name__) #Define the app
app.config["SECRET_KEY"] = "secretkey"

git_username = os.environ["username"]
git_token = os.environ["token"]
# git_username = ""
# git_token = ""

def getUsers(offset=0, per_page=10):
	return session["data"][offset: offset + per_page]


@app.route('/reset', methods=["GET", "POST"])
def resetSession():
	session.pop("data", None)
	return render_template('index.html'), 200

@app.route('/data', methods=["GET", "POST"])
def displayData():
	if "data" in session:
		retData = session["data"]
	else:

		authors = []
		text = request.form['message'] #Get user inputted organization

		gh_session = requests.Session()
		gh_session.auth = (git_username, git_token)
		apiURL = 'https://api.github.com/orgs/' + text
		req = gh_session.get(apiURL).text
		data = json.loads(req)

		try:

			membersURL = data["public_members_url"][:-9]
			reqMembers = gh_session.get(membersURL).text
			membersData = json.loads(reqMembers)
			
			for member in membersData:
				memberURL = member["url"]
				reqMember = gh_session.get(memberURL).text
				memberData = json.loads(reqMember)
				name = memberData["name"]
				username = memberData["login"]
				imageURL = memberData["avatar_url"]
				email = memberData["email"]
				
				eventsURL = memberData["events_url"][:-10]
				reqEvents = gh_session.get(eventsURL).text
				eventsData = json.loads(reqEvents)
				commitCount = 0
				commitTitle = None
				for event in eventsData:
					if event["type"] == "PushEvent":
						commits = event["payload"]["commits"]
						for commit in commits:
							if commit["author"]["name"] == name:
								if commitCount == 0:
									commitTitle = commit["message"]
								commitCount += 1

				obj = {"name" : name, "username" : username, "imageURL" : imageURL, "email" : email, "commitCount" : commitCount, "latestCommitTitle" : commitTitle}


				authors.append(obj)
				

			sortedAuthors = sorted(authors, key = lambda k: k["commitCount"], reverse = True)

			retData = sortedAuthors

			session["data"] = retData
		except:
			retData = data
	page, per_page, offset = get_page_args(page_parameter="page",per_page_parameter="per_page")

	pagination = Pagination(page=page, per_page = per_page, total=len(retData), css_framework="bootstrap4")

	return render_template('printData.html', retData = json.dumps(getUsers(offset, per_page), indent = 2, sort_keys = True), page = page, per_page = per_page, pagination=pagination), 200


@app.route('/')
def index():
	return render_template('index.html'), 200



if __name__ == '__main__':
	app.run(debug=True, port = 8080)