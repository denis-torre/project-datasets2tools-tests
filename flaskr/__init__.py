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

### 2.1.2 Data
@app.route('/data')
def data():
	db_dataframe = executeQuery("SELECT * FROM db", mysql)
	return render_template('data.html', db_dataframe=db_dataframe)

### 2.1.2 Dataset Search
@app.route('/datasetSearch', methods=['POST'])
def datasetSearch():
	# Get Form Text
	datasetSearchInput = request.form['dataset_search_input']

	# Perform GEO Search
	geoSearchResults = geoSearch(datasetSearchInput)

	# Run GEO Search
	return json.dumps(geoSearchResults)

### 2.1.3 Dataset Upload
@app.route('/datasetUpload', methods=['POST'])
def datasetUpload():

	# Create dictionary
	searchResultDict = {x:request.form[x] for x in request.form.keys()}

	# Search if ID has been specified
	if 'selected_dataset_id' in searchResultDict.keys():

		# Re-get data from GEO
		datasetGeoData = fromGeoId(searchResultDict['selected_dataset_id'])

		# Get Insert Query
		datasetInsertQuery = dict2query(datasetGeoData, 'dataset')

	else:

		# If New Database
		if searchResultDict['db_fk'] == 'newdb':

			# Remove DB Key
			del searchResultDict['db_fk']

			# Get Query String
			databaseInsertQuery = dict2query(searchResultDict, 'db', keys=['db_name', 'db_url', 'db_icon_url'])

			# Add and get last inserted id
			newDbId = insertMysqlData(databaseInsertQuery, mysql, getId=True)

			# Add Database ID To Dictionary
			searchResultDict['db_fk'] = newDbId
		
		# Get Query
		datasetInsertQuery = dict2query(searchResultDict, 'dataset', keys=['dataset_title', 'dataset_accession', 'dataset_url', 'db_fk'])

	# Add data
	datasetRecordId = insertMysqlData(datasetInsertQuery, mysql, getId=True)

	return str(datasetRecordId)

### 2.1.3 Tools
@app.route('/tools')
def tools():
	tool_dataframe = executeQuery("SELECT * FROM tool", mysql)
	return render_template('tools.html', tool_dataframe=tool_dataframe)

### 2.1.3 Tool Upload
@app.route('/toolUpload', methods=['POST'])
def toolUpload():

	# Create dictionary
	searchResultDict = {x:request.form[x] for x in request.form.keys()}

	# Search if Tool has been selected
	if 'id' in searchResultDict.keys():

		# Get ID
		toolRecordId = searchResultDict['id']

	else:

		# Get query
		datasetInsertQuery = dict2query(searchResultDict, 'tool')

		# Get ID
		toolRecordId = insertMysqlData(datasetInsertQuery, mysql, getId=True)

	return str(toolRecordId)

#######################################################
########## 3. Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True)