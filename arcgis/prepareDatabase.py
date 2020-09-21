# Create file geodatabase
# Script name: prepareDatabase.py
# Created by: Center for Urban and Regional Analysis (OSU)
#
# usage: C:\Python27\ArcGIS10.7\python prepareDatabase.py <gdbFolder>
#

import os
import sys
import arcpy
import shutil

DEFAULT_FOLDER = "./"
OUTPUT_GDB = "PovertyMap.gdb"

# Get path to folder where geodatabase should be located. Try first to get it from ArcGIS Pro. 
# If it fails, get remaining arguments from the command line.  
gdbFolder = arcpy.GetParameterAsText(0).strip()
if(gdbFolder == ""):
	try: 
		gdbFolder = os.path.normpath(sys.argv[1])
	except IndexError:
		gdbFolder = os.path.normpath(DEFAULT_FOLDER)

arcpy.AddMessage("Using GDB folder: " + gdbFolder)

# Create a new geodatabase to contain new spatial data that we will create.
# If the geodatabase exists already, delete it and recreate it.
ws = os.path.join(gdbFolder, OUTPUT_GDB)
if not arcpy.Exists(ws):
    arcpy.AddMessage("Creating new GDB")
    arcpy.CreateFileGDB_management(gdbFolder, OUTPUT_GDB)
else:
    shutil.rmtree(ws)
    arcpy.AddMessage("Recreating GDB")
    arcpy.CreateFileGDB_management(gdbFolder, OUTPUT_GDB)

arcpy.SetParameterAsText(1, ws)