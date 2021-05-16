from flask import Flask, jsonify, request, render_template
import requests
import json
app = Flask(__name__) #Define the app



@app.route('/', methods=['GET'])
def test():
	# req = requests.get('https://api.github.com/orgs/Netflix')
	# data = json.loads(req.content)

	# return render_template('printData.html', data = data)
	return render_template('printData.html')



if __name__ == '__main__':
	app.run(debug=True, port = 8080)