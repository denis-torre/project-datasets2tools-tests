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
##### 2.1 Templates
##############################

### 2.1.1 Merged
@app.route('/')
def main():
	return 'It works!'

### 2.1.1 Merged
@app.route('/merged')
def merged():
	db_dataframe = executeQuery("SELECT * FROM db", mysql)
	tool_dataframe = executeQuery("SELECT * FROM tool", mysql)
	return render_template('merged.html', db_dataframe=db_dataframe, tool_dataframe=tool_dataframe)

##############################
##### 2.2 POST Requests
##############################

### 2.2.1 Dataset Search
@app.route('/datasetSearch', methods=['POST'])
def datasetSearch():
	# Get Form Text
	datasetSearchInput = request.form['dataset_search_input']

	# Perform GEO Search
	geoSearchResults = geoSearch(datasetSearchInput)

	# Run GEO Search
	return json.dumps(geoSearchResults)


### 2.2.2 grandSubmission
@app.route('/grandSubmission', methods=['POST'])
def grandSubmission():

	# Create dictionary
	searchResultDict = {x:request.form[x] for x in request.form.keys()}

	# Get Dataset ID
	datasetRecordId = getDatasetId(searchResultDict, mysql)

	# Get Tool ID
	toolRecordId = getToolId(searchResultDict, mysql)

	# Get Analysis ID
	analysisRecordId = getAnalysisId(searchResultDict, datasetRecordId, toolRecordId, mysql)

	return(str(analysisRecordId))

##############################
##### 2.3 APIs
##############################

### 2.3.1 Datasets API
@app.route('/datasets', methods=['GET', 'POST'])
def datasets():
	# Get Search Parameters in Dictionary
	searchParameterDict = dict(urlparse.parse_qsl(request.query_string))

	# Get Dataset IDs
	datasetIds = getRecordIds(searchParameterDict, 'dataset', mysql)

	return datasetIds

### 2.3.2 Canned Analysis API
@app.route('/canned_analyses')
def canned_analyses():
	# Get Search Parameters in Dictionary
	searchParameterDict = dict(urlparse.parse_qsl(request.query_string))

	# Get Canned Analysis IDs
	cannedAnalysisUrls = getRecordIds(searchParameterDict, 'canned_analysis', mysql, field='canned_analysis_url')

	return cannedAnalysisUrls

#######################################################
########## 3. Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True)