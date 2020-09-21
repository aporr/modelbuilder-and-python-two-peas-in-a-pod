# Compute poverty statistics for Ohio counties
# Script name: computeStats.py
# Created by: Center for Urban and Regional Analysis (OSU)

import arcpy
import numpy as np
import pandas as pd

INDEX_FIELD = "OBJECTID"

sourceTable = arcpy.GetParameterAsText(0)
sourceField = arcpy.GetParameterAsText(1)
targetField = arcpy.GetParameterAsText(2)
nQuantiles = arcpy.GetParameter(3)

if(nQuantiles % 2 != 0):
	arcpy.AddError("Number of quantiles must be even")
arr = arcpy.da.TableToNumPyArray(sourceTable, (INDEX_FIELD, sourceField))

bins = np.nanquantile(arr[sourceField], np.linspace(0,1,nQuantiles+1))
labels = np.concatenate((np.arange(-nQuantiles/2, 0, 1), np.arange(1, nQuantiles/2+1, 1)))
assignment = np.searchsorted(bins, arr[sourceField], side="left")
assignment[assignment == 0] = 1
assignment[assignment == 21] = 20
quantiles = [labels[bin-1] for bin in assignment]
outArr = arr.copy()
outArr.dtype.names = (INDEX_FIELD, str(targetField))
outArr[targetField] = quantiles

arcpy.da.ExtendTable(sourceTable, INDEX_FIELD, outArr, INDEX_FIELD ) 
arcpy.SetParameterAsText(4, sourceTable)