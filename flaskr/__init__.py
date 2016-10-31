############################################################
############################################################
############### Datasets2Tools Test Interface ##############
############################################################
############################################################

#######################################################
########## 1. Setup Web Page ##########################
#######################################################

##############################
##### 1.1 Load Libraries
##############################
# Python Libraries
import sys, json
import pandas as pd

# Flask Libraries
from flask import Flask, request, render_template
from flaskext.mysql import MySQL

# Custom libraries
sys.path.append('static/lib/py')
from lib import *

##############################
##### 1.2 Setup MySQL
##############################
# Initialize Flask App
app = Flask(__name__)

# Initialize MySQL Connection
mysql = MySQL()

# Configure MySQL Connection
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'MyNewPass'
app.config['MYSQL_DATABASE_DB'] = 'datasets2tools'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#######################################################
########## 2. Setup Web Page ##########################
#######################################################

##############################
##### 2.1 Connection Setup
##############################

### 2.1.1 Main
@app.route('/')
def main():
	return 'It works!'

### 2.1.1 Main
@app.route('/data')
def data():
	return render_template('data.html')

### 2.1.2 Dataset Search
@app.route('/datasetSearch', methods=['POST'])
def datasetSearch():
	# Get Form Text
	datasetSearchInput = request.form['dataset_search_input']

	# Perform GEO Search
	geoSearchResults = geoSearch(datasetSearchInput)

	# Run GEO Search
	return json.dumps(geoSearchResults)



#######################################################
########## 3. Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True)