# Build a map document showing poverty statistics for Ohio from existing layer files
# Script name: buildMap.py
# Created by: Center for Urban and Regional Analysis (OSU)

import arcpy
import os

# The path to the template ArcMap document
inputMXD = arcpy.GetParameterAsText(0)

OUTPUT_MXD = os.path.abspath("PovertyMap.mxd")

LAYERS = [
    {
        "name": "Counties",
        "lyrFile": "Counties.lyr",
        "visible": True
    },
    {
        "name": "Tracts",
        "lyrFile": "Tracts.lyr",
        "visible": True
    },
    {
        "name": "Zipcodes",
        "lyrFile": "Zipcodes.lyr",
        "visible": False
    }    
]

mxd = arcpy.mapping.MapDocument(inputMXD)

df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    arcpy.mapping.RemoveLayer(df, lyr)

for layer in LAYERS:
    lyr = arcpy.mapping.Layer(layer["lyrFile"])
    arcpy.mapping.AddLayer(df, lyr, "BOTTOM")
    lyr.visible = layer["visible"]

mxd.saveACopy(OUTPUT_MXD)

arcpy.SetParameterAsText(1, OUTPUT_MXD)