# Publish layer of poverty statistics for Ohio counties
# Script name: overwriteService.py
# Created by: Center for Urban and Regional Analysis (OSU)

# This script converts the MXD file to a service definition and publishes it as a hosted feature layer on ArcGIS Online. 
# Assumptions:
#     1. Service exists already (i.e. it will be overwritten)
#     2. Service name is "OhioPovertyMap"
#     3. Service is published in the root folder (i.e. it is not in a folder)
#     4. User is already logged in to ArcGIS Oline

import arcpy
import os
import xml.dom.minidom as DOM 

arcpy.env.overwriteOutput = True

# Service definition draft file.  This is deleted after service is staged and for some reason I can't create one 
# programmatically (see below).  Instead keep a backup copy and duplicate it each time
SDDRAFT_BACKUP = os.path.normpath("./PovertyMap.sddraft.backup")
SDDRAFT_PATH = os.path.normpath("./PovertyMap.sddraft")

# Service definition file
SD_PATH = os.path.normpath("./PovertyMap.sd")

# Name and location of the service on ArcGIS Online
SERVICE_NAME = "OhioPovertyMap"
FOLDER_NAME = None

# Specify input MXD file at run time
mapDocument = arcpy.GetParameterAsText(0)

# Create service definition draft from MXD
arcpy.AddMessage("Converting MXD to service definition draft: " + SDDRAFT_PATH)
arcpy.mapping.CreateMapSDDraft (mapDocument, SDDRAFT_PATH, SERVICE_NAME, 
    server_type = "MY_HOSTED_SERVICES", 
    copy_data_to_server = True, 
    folder_name = FOLDER_NAME
)

## The following section reconfigures the service definition draft
# Read sddraft xml
doc = DOM.parse(SDDRAFT_PATH)

# Iterate through configuration properties and change a few, specifically:
#   - Disable caching
#   - Increase the maximum number of records returned (there are 1300+ census tracts in Ohio)
configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
propArray = configProps.firstChild
propSets = propArray.childNodes
for propSet in propSets:
    keyValues = propSet.childNodes
    for keyValue in keyValues:
        if keyValue.tagName == 'Key':
            if keyValue.firstChild.data == "isCached":
                newValue = "false"
                arcpy.AddMessage("Setting service property " + keyValue.firstChild.data + " to " + newValue)
                keyValue.nextSibling.firstChild.data = newValue
            elif keyValue.firstChild.data == "maxRecordCount":
                newValue = "10000"
                arcpy.AddMessage("Setting service property " + keyValue.firstChild.data + " to " + newValue)
                keyValue.nextSibling.firstChild.data = newValue
            else:
                arcpy.AddMessage("Service property " + keyValue.firstChild.data + " is " + keyValue.nextSibling.firstChild.data + "(no change)" )

# Specify that this is a replacement service.  We will overwrite the existing service.
tagsType = doc.getElementsByTagName('Type')
for tagType in tagsType:
    if tagType.parentNode.tagName == 'SVCManifest':
        if tagType.hasChildNodes():
            tagType.firstChild.data = "esriServiceDefinitionType_Replacement"

tagsState = doc.getElementsByTagName('State')
for tagState in tagsState:
    if tagState.parentNode.tagName == 'SVCManifest':
        if tagState.hasChildNodes():
            tagState.firstChild.data = "esriSDState_Published"

# Change service type from map service to feature service
typeNames = doc.getElementsByTagName('TypeName')
for typeName in typeNames:
    if typeName.firstChild.data == "MapServer":
        typeName.firstChild.data = "FeatureServer"

# Turn on feature access capabilities
configProps = doc.getElementsByTagName('Info')[0]
propArray = configProps.firstChild
propSets = propArray.childNodes
for propSet in propSets:
    keyValues = propSet.childNodes
    for keyValue in keyValues:
        if keyValue.tagName == 'Key':
            if keyValue.firstChild.data == "WebCapabilities":
                keyValue.nextSibling.firstChild.data = "Query"
                
# Rewrite the service definition draft
outXml = os.path.join(SDDRAFT_PATH)   
if os.path.exists(outXml): os.remove(outXml)
f = open(outXml, 'w')     
doc.writexml( f )     
f.close() 

# Create service definition from draft
arcpy.AddMessage("Staging service definition: " + SD_PATH)
temp = arcpy.StageService_server(os.path.abspath(SDDRAFT_PATH), os.path.abspath(SD_PATH))
warnings = arcpy.GetMessages(1)
print(warnings)

# Publish service on ArcGIS Online (assumes user is logged in via the ArcMap file menu)
message = "Uploading service to ArcGIS Online as " + SERVICE_NAME
if(FOLDER_NAME == None):
    message += " (root folder)"
else:
    message += " in folder " + FOLDER_NAME
arcpy.AddMessage(message)
arcpy.UploadServiceDefinition_server(in_sd_file=SD_PATH, in_server="My Hosted Services",
    in_override = "OVERRIDE_DEFINITION",
    in_my_contents = "SHARE_ONLINE",
    in_public = "PUBLIC",
    in_organization = "SHARE_ORGANIZATION"
)
	
sys.exit(0)
