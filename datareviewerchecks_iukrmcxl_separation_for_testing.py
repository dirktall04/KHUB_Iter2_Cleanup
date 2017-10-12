#!/usr/bin/env/ python
#-*- coding: utf-8 -*-
#datareviewerchecks_iukrmcxl_separation_for_testing.py
# Created 2017-10-10 by dirktall04

# This script takes in the non-separated dataset and separates
# it out to prepare it for testing. Then, the user has to
# create the necessary .rbj files to match the separated
# dataset names, since that part isn't scriptable.

# Get the two portions of the base name from the config
# file along with the route prefixes to separate out
# for testing.
import os

from arcpy import (CopyFeatures_management, CreateFileGDB_management, MakeFeatureLayer_management, SelectLayerByAttribute_management)
from config import (advancedErrorReportingDict, gdbBasePart1, gdbBasePart2, gdbBasePart3, gdbForSourceCreation,
                    gdbForSourceNamePart,
                    mainFolder, otherFCsToCopyList, routesSource2, routesSourceFeatureLayer, routesSourceName)
routesSource2FeatureLayer = routesSourceFeatureLayer + '_2'


for dictKey in advancedErrorReportingDict:
    # Need to create a _Source and a base gdb where
    # the _Source includes at least Calpts and Routes from
    # the full gdb for the current data mirroring version.
    
    # For each dictKey in the advancedErrorReportingDict
    # Create a new GDB in mainFolder (1st dictKey gdb) called gdbBasePart1 + '_' + gdbBasePart2 + '_' +  dictKey + '_' + gdbForSourceNamePart + '.gdb'
    dictKey_SourceGDB = gdbBasePart1 + '_' + gdbBasePart2 + '_' +  dictKey + '_' + gdbForSourceNamePart + '.gdb'
    CreateFileGDB_management(mainFolder, dictKey_SourceGDB)
    # and create a new gdb in the same folder (2nd dictKey gdb) called gdbBasePart1 + '_' + gdbBasePart2 + '_' +  dictKey + '.gdb'
    dictKey_GDB = gdbBasePart1 + '_' + gdbBasePart2 + '_' +  dictKey + '.gdb'
    CreateFileGDB_management(mainFolder, dictKey_GDB)
    # Then, load a feature layer of the RoutesSource from the gdbForSourceCreation so that you can do a selection on it
    MakeFeatureLayer_management(routesSource2, routesSource2FeatureLayer)
    # Use the value associated with the dict key as the selection where clause for the routesSourceFeatureLayer
    dictWhereClause = advancedErrorReportingDict[dictKey]
    SelectLayerByAttribute_management(routesSource2FeatureLayer, "CLEAR_SELECTION")
    SelectLayerByAttribute_management(routesSource2FeatureLayer, "NEW_SELECTION", dictWhereClause)
    # Copy the selected features from the feature layer to the dictKey_SourceGDB.
    dictKeyRoutesSource = os.path.join(dictKey_SourceGDB, routesSourceName)
    CopyFeatures_management(routesSource2FeatureLayer, dictKeyRoutesSource)
    
    try:
        del routesSource2FeatureLayer
    except:
        pass
    
    # Also copy the other feature classes from the fullRoadSet_SourceGDB besides All_Road_Centerlines to the first dictKey gdb.
    # Copy the CalPts and Routes FCs from the fullRoadSet_GDB to the second dictKey gdb.
    # # Consider renaming the Non_Source gdb to something like gdbBaseName + _RtsCalPts.gdb
    for additionalFCNameToCopy in otherFCsToCopyList: # Loop inside a loop, not great, but the correct process at this time.
        # Copy the additional needed FCs for the routes testing... are there any FCs needed for that?
        # Have to copy the RoutesSourceCountyLRS_ARNOLD as RoutesSource iirc due to the way that the script runs when it recreates
        # the Routes and CalPts.
        fullFCPathToCopyFrom = os.path.join(gdbForSourceCreation, additionalFCNameToCopy)
        fullFCPathToCopyTo = os.path.join(dictKey_SourceGDB, additionalFCNameToCopy)
        CopyFeatures_management(fullFCPathToCopyFrom, fullFCPathToCopyTo)

