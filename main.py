from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import json
import os
app = Flask(__name__) #Define the app
app.config["SECRET_KEY"] = "secretkey"

git_username = "rtruong4"
git_token = "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"


@app.route('/data', methods=["GET", "POST"])
def displayData():

	authors = []
	text = request.form['message'] #Get user inputted organization

	gh_session = requests.Session()
	gh_session.auth = (git_username, git_token)
	apiURL = 'https://api.github.com/orgs/' + text
	req = gh_session.get(apiURL).text
	data = json.loads(req)
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

		obj = {"name" : name, "username" : username, "imageURL" : imageURL, "email" : email, "commitCount" : commitCount, "commitTitle" : commitTitle}


		authors.append(obj)
		

	sortedAuthors = sorted(authors, key = lambda k: k["commitCount"], reverse = True)

	retData = json.dumps(sortedAuthors)
	return render_template('printData.html', data = retData)


@app.route('/')
def index():
	# req = requests.get('https://api.github.com/orgs/Netflix')
	# data = json.loads(req.content)

	# return render_template('index.html', data = data)
	return render_template('index.html')



if __name__ == '__main__':
	app.run(debug=True, port = 8080)