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
import re, requests, xml.etree.ElementTree, urlparse, urllib, numpy, pandas

#######################################################
########## 2. Add Functions ###########################
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

        # Define fields
        fields = ['Accession', 'GDS', 'GPL', 'n_samples', 'FTPLink','taxon','title']

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