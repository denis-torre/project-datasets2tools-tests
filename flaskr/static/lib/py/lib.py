############################################################
############################################################
############### Datasets2ToolsTest Python Library ##########
############################################################
############################################################

#######################################################
########## 1. Setup ###################################
#######################################################

##############################
##### 1.1 Load Libraries
##############################
# Python Libraries
import re, requests, xml.etree.ElementTree, urlparse, urllib, numpy
import pandas as pd

#######################################################
########## 2. Add Level 1 #############################
#######################################################

##############################
##### 2.1 geoSearch
##############################
##### Performs a search using the GEO API.  Only supports 'All fields' text input at the moment.

def geoSearch(searchQuery, accessionType='GSE'):

    # Try
    try:
        # Get eSearch URL
        geo_esearch_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term='+ accessionType +'[ETYP]+AND+'+urllib.quote(searchQuery, safe='()')

        # Get eSearch results XML
        esearch_xml = xml.etree.ElementTree.fromstring(requests.get(geo_esearch_url).content)

        # Get GEO IDs
        geo_ids = [x.text for x in esearch_xml.findall('IdList/*')]

        # Get eSummary URL
        geo_esummary_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=' + ','.join(geo_ids)

        # Get eSummary results XML
        esummary_xml = xml.etree.ElementTree.fromstring(requests.get(geo_esummary_url).content)

        # Define result dictionary
        esummary_dict = {}

        # Loop through XML results
        for search_result in esummary_xml:
            esummary_dict[search_result[0].text] = {x.attrib['Name']:x.text for x in search_result[1:]}

        # Return result
        return esummary_dict

    # Except
    except:
        # Resurn result
        return ''

##############################
##### 2.2 fromGeoId
##############################
##### Performs a eSummary search using the GEO API.  Only supports a single ID.

def fromGeoId(geoId, keys={'Accession': 'dataset_accession', 'FTPLink': 'dataset_url', 'summary': 'dataset_description', 'title': 'dataset_title', 'taxon': 'taxon', 'gdsType': 'type'}):

    # Get eSummary URL
    geo_esummary_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=%(geoId)s' % locals()

     # Get eSummary results XML
    esummary_xml = xml.etree.ElementTree.fromstring(requests.get(geo_esummary_url).content)

    # Get data
    esummary_dict = {x.attrib['Name']:x.text for x in esummary_xml[0][1:]}

    # Get subset
    esummary_dict_subset = {keys[x]:esummary_dict[x] for x in keys.keys()}
    
    # Add Database
    esummary_dict_subset['db_fk'] = 1

    # Return result
    return esummary_dict_subset


##############################
##### 2.3 dict2query
##############################
#### Convert dictionary to insert statement

def dict2query(dataDict, table, keys=None):

    # Get Keys
    keys = keys if keys else dataDict.keys()

    # Fix data values
    dataDict = {x:dataDict[x].encode('ascii', 'replace') if type(dataDict[x]) == unicode else dataDict[x] for x in keys}

    # Get Column String
    columnString = ', '.join(["`%(x)s`" %locals() for x in dataDict.keys()])

    # Get Value String, surrounding with '
    insertValues = ["'%(x)s'" % locals() for x in dataDict.values()]

    # Make Value String
    valueString = ', '.join(insertValues)

    # Make Query String
    queryString = ''' INSERT INTO %(table)s (%(columnString)s) VALUES (%(valueString)s); ''' % locals()

    # Check if exists
    requirementString = ' AND '.join(["`" + x + "`='" + str(dataDict[x]) + "'" for x in dataDict.keys()])

    # Make IFexists String
    ifExistsString = '''SELECT id FROM %(table)s WHERE %(requirementString)s;''' % locals()

    return {'query': queryString, 'ifexists': ifExistsString}

##############################
##### 2.4 insertMysqlData
##############################
### Insert data
def insertMysqlData(queryDict, mysql_engine, getId=False):
    
    # Create connection
    connection = mysql_engine.connect()
    
    # Create cursor
    cursor = connection.cursor()

    # Check if exists
    cursor.execute(queryDict['ifexists'])

    # Get results
    existingRecordIds = cursor.fetchall()

    # Look For Matching Records in Table
    if len(existingRecordIds) > 0:

        # Get ID
        recordId = existingRecordIds[0][0]

    else:
        # Try inserting data, if error rollback
        try:
            # Execute query
            cursor.execute(queryDict['query'])
                
            # Commit connection
            connection.commit()     
            
            # Get ID
            if getId:
                # Get ID
                cursor.execute('SELECT LAST_INSERT_ID()')
                
                # Extract ID
                recordId = cursor.fetchall()[0][0]
        # Handle exception
        except:
            # Set NULL
            recordId = 'None!'

            # Rollback connection
            connection.rollback()

    # Close connection
    connection.close()

    # Return ID
    if getId == True:
        # Return
        return recordId



##############################
##### 2.5 executeMysqlQuery
##############################
### Select data

def executeQuery(query, mysql_engine):
    
    # Create cursor
    cursor = mysql_engine.connect().cursor()

    # Call procedure
    cursor.execute(query)

    # Get field names
    field_names = [x[0] for x in cursor.description]

    # Get search results
    query_results = cursor.fetchall()

    # Get query result dataframe
    query_result_dataframe = pd.DataFrame(list(query_results), columns = field_names)

    # Close cursor
    cursor.close()

    # Return result
    return query_result_dataframe

#######################################################
########## 2. Add Level 2 #############################
#######################################################

##############################
##### 2.1 getDatasetId
##############################

def getDatasetId(searchResultDict, mysql):

    # Search if ID has been specified
    if searchResultDict['dataset-selection-method'] == 'search':

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


##############################
##### 2.2 getToolId
##############################

def getToolId(searchResultDict, mysql):

    # Search if Tool has been selected
    if searchResultDict['tool-selection-method'] == 'search':

        # Get ID
        toolRecordId = searchResultDict['tool_id']

    else:
        # Get query
        toolInsertQuery = dict2query(searchResultDict, 'tool', keys=['tool_name', 'tool_icon_url', 'tool_url', 'tool_description'])

        # Get ID
        toolRecordId = insertMysqlData(toolInsertQuery, mysql, getId=True)

    return toolRecordId

##############################
##### 2.3 uploadAnalysis
##############################

def getAnalysisId(searchResultDict, datasetRecordId, toolRecordId, mysql):

    # Get Canned Analysis Insert Dict
    cannedAnalysisDict = {'dataset_fk': datasetRecordId,
                           'tool_fk' : toolRecordId,
                           'canned_analysis_url': searchResultDict['canned_analysis_url']}

    # Get Query String
    analysisInsertQuery = dict2query(cannedAnalysisDict, 'canned_analysis')

    # Get ID
    analysisRecordId = insertMysqlData(analysisInsertQuery, mysql, getId=True)

    # Return result
    return str(analysisRecordId)

#######################################################
########## 3. API Functions ###########################
#######################################################

##############################
##### 3.1 getRecordId
##############################

def getRecordIds(searchParameterDict, table, mysql_engine, field='id'):
    # Try
    try:
        # Make Requirement String
        requirementString = ' AND '.join(["`" + x + "`='" + str(searchParameterDict[x]) + "'" for x in searchParameterDict.keys()])

        # Make Query String
        queryString = '''SELECT %(field)s FROM %(table)s WHERE %(requirementString)s;''' % locals()
        
        # Get cursor
        cursor = mysql_engine.connect().cursor()
        
        # Execute query
        cursor.execute(queryString)
        
        # Get ID
        recordIds = [str(x[0]) for x in cursor.fetchall()]

        # Make string
        recordIdString = ','.join(recordIds) if len(recordIds) > 0 else 'No search results.'
        
        return recordIdString

    # Except
    except:
        return 'Something went wrong - please check URL.'




##############################
##### 2.1 getDatasetId
##############################

##############################
##### 2.1 getDatasetId
##############################

##############################
##### 2.1 getDatasetId
##############################

