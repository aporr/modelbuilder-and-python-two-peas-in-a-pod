# Retrieve U.S. Census poverty data for Ohio tracts and zipcodes
# Script name: getCensusData.py
# Created by: Center for Urban and Regional Analysis (OSU)
#
# usage: C:\Python27\ArcGIS10.7\python getCensusData.py <YEAR>
#

import os
import sys
import urllib
import pandas as pd
import zipfile
import shutil
import json

# Default path for all files created by script (can be overridden by input parameter)
DEFAULT_OUTPUT_FOLDER = os.path.normpath("./data")

# List of census variables to download:
#	NAME (Description of geography)
#	GEO_ID (Unique identifier for the geography)
#   S1701_C01_001E (Total population) for whom poverty status is determined
#   S1701_C02_001E (Below poverty level)
#   S1701_C03_001E (Percent below poverty level)
ACS_VARIABLES = ["NAME","GEO_ID","S0101_C01_001E","S1701_C02_001E","S1701_C03_001E"]

COLUMNS = ["NAME","GEO_ID","TOTAL","POVERTY","POVERTY_PCT"]

# Counter for ArcGIS parameters
i = 0;

# Get year of data to be retrieved. This is the only required parameter.  Try first to get it from ArcGIS. 
# If it succeeds, get all remaining arguments from ArcGIS. If it fails, try to get arguments from the 
# command line.  
year = os.path.normpath(sys.argv[1])
i += 1

try:
	outputFolder = os.path.normpath(sys.argv[2])
except IndexError:
	outputFolder = ""
i += 1

print("Fetching data for year: " + year)

# If any of the optional parameters are still undefined, set them to their
# default values
if(outputFolder == ""):
	outputFolder = DEFAULT_OUTPUT_FOLDER
	print("Output folder is not specified. Using default folder.")

# If the output folder doesn't exist, create it.	
if (not os.path.exists(os.path.join(outputFolder, year))):
	print("Specified output folder (or year-specific subfolder) does not exist. Attempting to create it recursively.")
	try:
		os.makedirs(os.path.join(outputFolder, year))
	except:
		print("Failed to create output folder.")
		sys.exit(-1)
		
print("Using year-specific output folder: " + os.path.join(outputFolder, year))

# Source URLs for zip files containing cartographic boundaries shapefiles
boundariesSeq = ["zipcodes", "tracts", "states", "counties"]
boundariesUrl = {
	"zipcodes":"https://www2.census.gov/geo/tiger/GENZ{0}/shp/cb_{0}_us_zcta510_500k.zip".format(year),
	"tracts": "https://www2.census.gov/geo/tiger/GENZ{0}/shp/cb_{0}_39_tract_500k.zip".format(year),
	"states": "https://www2.census.gov/geo/tiger/GENZ{0}/shp/cb_{0}_us_state_500k.zip".format(year),
	"counties": "https://www2.census.gov/geo/tiger/GENZ{0}/shp/cb_{0}_us_county_500k.zip".format(year)
}

# API calls to retrieve ACS data from Census 
# See https://www.census.gov/data/developers/data-sets.html 
# and https://www.census.gov/content/dam/Census/data/developers/api-user-guide/api-guide.pdf
dataSeq = ["zipcodes", "tracts"]
dataUrl = {
	"zipcodes": "https://api.census.gov/data/{0}/acs/acs5/subject?get={1}&for=zip%20code%20tabulation%20area:*".format(year, ",".join(ACS_VARIABLES)),
	"tracts": "https://api.census.gov/data/{0}/acs/acs5/subject?get={1}&for=tract:*&in=state:39".format(year, ",".join(ACS_VARIABLES))
}

# Retrieve cartographic boundary shapefiles unless they already exist, then unzip the files
for dataset in boundariesSeq:
	saveFile = os.path.join(outputFolder, year, dataset + "_shp.zip")
	if (os.path.exists(saveFile)):
		print(dataset.capitalize() + " shapefile already exists for this year.  Skipping download.")
	else:
		print("Downloading shapefile for " + dataset + ". (This might take a while)")
		try:
			urllib.urlretrieve(boundariesUrl[dataset], saveFile)
		except:
			print("Failed to download shapefile for " + dataset)
			sys.exit(-1)
			
	zipOutputFolder = os.path.join(outputFolder, year, dataset + "_shp")
	if (os.path.exists(zipOutputFolder)):
		print("Deleting previously extracted data for " + dataset)	
		try:
			shutil.rmtree(zipOutputFolder)
		except:
			print("Failed to remove zip folder for " + dataset)
			sys.exit(-1)		

	print("Unzipping data for " + dataset)
	try:
		zipFile = zipfile.ZipFile(saveFile, 'r')
		zipFile.extractall(zipOutputFolder)
		zipFile.close()
	except:
		print("Failed to unzip shapefile for " + dataset)
		sys.exit(-1)
	files = os.listdir(zipOutputFolder)
	for file in files:
		ext = file.split(".", 1)[1]
		os.rename(os.path.join(zipOutputFolder, file), os.path.join(zipOutputFolder, dataset + "." + ext))

	i += 1
		
# Retrieve census data for each geography.  If data already exists, delete it and download
# fresh data. Convert the data from JSON to CSV.
for dataset in dataSeq:
	saveFile = os.path.join(outputFolder, year, dataset + "_data.json")
	if (os.path.exists(saveFile)):
		print(dataset.capitalize() + " data already exists for this year.  Deleting it.")
		try:
			os.unlink(saveFile)
		except:
			print("Failed to delete existing data for " + dataset)
			sys.exit(-1)		

	print("Downloading data for " + dataset + ". (This might take a while)")
	try:
		urllib.urlretrieve(dataUrl[dataset], saveFile)
	except:
		print("Failed to download data for " + dataset)
		sys.exit(-1)

	print("Converting data for " + dataset + " to CSV")
	try:
		with open(saveFile, "r") as f:
			dataStr = f.read()
		dataObj = json.loads(dataStr)
		df = pd.DataFrame(data=dataObj[1:], columns=dataObj[0])
		df.set_index("GEO_ID", inplace=True)
		df.to_csv(saveFile.replace(".json", ".csv"))

		i += 1
	except:
		print("Failed to convert data for " + dataset)
		sys.exit(-1)
