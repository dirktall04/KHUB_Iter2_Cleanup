#!/usr/bin/env python
# datareviewerchecks_keyrecalculation_keyupdatesfromcomponents.py
# -*- coding: utf-8 -*-
# Created 2017-12-27, by dirktall04

# Operates on the DEFAULT version of a versioned feature class
# or the unversioned version of a feature class.
import os
from arcpy import (AddField_management, CalculateField_management,
    GetCount_management, ListFields,
    MakeFeatureLayer_management, SelectLayerByAttribute_management)

from arcpy.da import (UpdateCursor as daUpdateCursor, Editor)
from datareviewerchecks_config import (useSQLLocationToRecalculateFields, sqlFCWithFieldsToRecalculate,
    fcWithFieldsToRecalculate, fcAsFeatureLayer, KDOTRouteId, KDOTMeasBeg, KDOTMeasEnd, 
    n1RouteId, n1FromMeas, n1ToMeas, nullable)

fieldsToCheckForAndAdd = [n1RouteId, n1FromMeas, n1ToMeas]

# Check for the cause of NB & EB instead of NB & SB on odd numbered routes.
# Attempted fix on 2017-12-27. Needs Testing.
def main():
    print("Using the new field logic to calculate the values of the source lrs ID and measure fields.")
    
    if useSQLLocationToRecalculateFields == True:
        addMissingFields(sqlFCWithFieldsToRecalculate)
        MakeFeatureLayer_management(sqlFCWithFieldsToRecalculate, fcAsFeatureLayer)
        workspace = os.path.dirname(sqlFCWithFieldsToRecalculate)
        editSession = Editor(workspace)
        editSession.startEditing(False, True)
        editSession.startOperation()
        
        recalculateKeyValues()
        edit.stopOperation()

        # Stop the edit session and save the changes
        edit.stopEditing(True)
    else:
        MakeFeatureLayer_management(fcWithFieldsToRecalculate, fcAsFeatureLayer)
        recalculateKeyValues()


def recalculateKeyValues():
    # As long as the KDOT_LRS_KEY is not null, calculate from the
    # current fields.
    
    # Prior to doing any of this, I added a field to cache the
    # current KDOT_LRS_KEY to check for mistakes and recover from
    # them if any were found.
    
    # Use the prefix field to decide on what action to take to update the KDOTRouteId.
    # If the prefix is null, do nothing.
    # If the prefix is I, U, K, create the KDOTRouteId value from the SHS component parts.
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('I', 'U', 'K') """
    necessaryFields = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "KDOT_DIRECTION_CALC"]
    dynNonNullSelectionQuery = GenerateNonNullSelectionQuery(necessaryFields)
    fullSelectionQuery = selectionQuery + """ AND """ + dynNonNullSelectionQuery
    
    fieldsToUseForUpdating = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "KDOT_DIRECTION_CALC", "KDOT_LRS_KEY"]
    
    newCursor = daUpdateCursor(fcAsFeatureLayer, fieldsToUseForUpdating, fullSelectionQuery)
    
    for cursorRowItem in newCursor:
        cursorListItem = list(cursorRowItem)
        countyPre = cursorListItem[0]
        routePre = cursorListItem[1]
        routeNum = cursorListItem[2]
        routeSuf = cursorListItem[3]
        lrsUniqueIdent = cursorListItem[4]
        if len(lrsUniqueIdent) > 1:
            lrsUniqueIdent = lrsUniqueIdent[-1]
        else:
            pass
        directionCalc = cursorListItem[5]
        directionText = ''
        
        # Modified 2017-17-27 to fix the issue of non-primary sides, esp. on odd-numbered routes, receiving '-EB'.
        try:
            if int(routeNum) % 2 == 0:
                if directionCalc is not None and int(directionCalc) == 1:
                    directionText = '-WB'
                else:
                    # Default, if the non-primary side is receiving this, make sure that it has a 1 in the directionCalc.
                    directionText = '-EB'
            
            if int(routeNum) % 2 == 1:
                if directionCalc is not None and int(directionCalc) == 1:
                    directionText = '-SB'
                else:
                    # Default, if the non-primary side is receiving this, make sure that it has a 1 in the directionCalc.
                    directionText = '-NB'
            newKey = str(countyPre) + str(routePre) + str(routeNum) + str(routeSuf) + str(lrsUniqueIdent) + directionText
            cursorListItem[6] = newKey
            # For Debugging
            ##print("Updating the lrs key to: " + str(newKey) + ".")
            newCursor.updateRow(cursorListItem)
        except:
            try:
                print(traceback.format_exc())
                print("Could not calculate a new LRS_KEY for the given row.")
                print("The row looks like this: " + str(cursorListItem) + ".")
            except:
                pass
            newCursor.next()
    
    try:
        del newCursor
    except:
        pass
    
    ###------------------------------------------------------------------------------------------------------------###
    ### If the prefix is not I, U, K and not X, create the KDOTRouteID from the Non-SHS, Non-Ramp component parts. ###
    ###------------------------------------------------------------------------------------------------------------###
    
    # For prefix R & M
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('R', 'M') """
    necessaryFields = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO"]
    dynNonNullSelectionQuery = GenerateNonNullSelectionQuery(necessaryFields)
    fullSelectionQuery = selectionQuery + """ AND """ + dynNonNullSelectionQuery
    
    fieldsToUseForUpdating = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO",
        "KDOT_DIRECTION_CALC", "KDOT_LRS_KEY"]
    
    newCursor = daUpdateCursor(fcAsFeatureLayer, fieldsToUseForUpdating, fullSelectionQuery)
    
    for cursorRowItem in newCursor:
        cursorListItem = list(cursorRowItem)
        countyPre = cursorListItem[0]
        routePre = cursorListItem[1]
        routeNum = cursorListItem[2]
        routeSuf = cursorListItem[3]
        lrsUniqueIdent = cursorListItem[4]
        if len(lrsUniqueIdent) > 1:
            lrsUniqueIdent = lrsUniqueIdent[-1] # Get the right-most value. e.g. 47 => 7, 52 => 2
        else:
            pass
        lrsAdmo = cursorListItem[5]
        directionCalc = cursorListItem[6]
        if directionCalc is None:
            directionCalc = '0'
        else:
            pass
        try:
            newKey = str(countyPre) + str(routePre) + str(routeNum) + str(routeSuf) + str(lrsUniqueIdent) + str(lrsAdmo) + str(directionCalc)
            cursorListItem[7] = newKey
            newCursor.updateRow(cursorListItem)
        except:
            try:
                print(traceback.format_exc())
                print("Could not calculate a new LRS_KEY for the given row.")
                print("The row looks like this: " + str(cursorListItem) + ".")
            except:
                pass
            newCursor.next()
    
    try:
        del newCursor
    except:
        pass
    
    # For prefix C, Urban Classified, which uses LRS_URBAN_PRE.
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('C') """
    necessaryFields = ["LRS_URBAN_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO"]
    dynNonNullSelectionQuery = GenerateNonNullSelectionQuery(necessaryFields)
    # Uses LRS_ADMO
    ####LRS_ROUTE_NUM, LRS_ROUTE_SUFFIX, LRS_UNIQUE_IDENT, then LRS_ADMO, then 0 for inventory direction.
    fullSelectionQuery = selectionQuery + """ AND """ + dynNonNullSelectionQuery
    
    fieldsToUseForUpdating = ["LRS_URBAN_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO",
        "KDOT_DIRECTION_CALC", "KDOT_LRS_KEY"]
    
    newCursor = daUpdateCursor(fcAsFeatureLayer, fieldsToUseForUpdating, fullSelectionQuery)
    
    for cursorRowItem in newCursor:
        cursorListItem = list(cursorRowItem)
        urbanPre = cursorListItem[0]
        routePre = cursorListItem[1]
        routeNum = cursorListItem[2]
        routeSuf = cursorListItem[3]
        lrsUniqueIdent = cursorListItem[4]
        if len(lrsUniqueIdent) > 1:
            lrsUniqueIdent = lrsUniqueIdent[-1] # Get the right-most value. e.g. 47 => 7, 52 => 2
        else:
            pass
        lrsAdmo = cursorListItem[5]
        directionCalc = cursorListItem[6]
        if directionCalc is None:
            directionCalc = '0'
        else:
            pass
        try:
            newKey = str(urbanPre) + str(routePre) + str(routeNum) + str(routeSuf) + str(lrsUniqueIdent) + str(lrsAdmo) + str(directionCalc)
            cursorListItem[7] = newKey
            newCursor.updateRow(cursorListItem)
        except:
            try:
                print(traceback.format_exc())
                print("Could not calculate a new LRS_KEY for the given row.")
                print("The row looks like this: " + str(cursorListItem) + ".")
            except:
                pass
            newCursor.next()
    
    try:
        del newCursor
    except:
        pass
    
    
    # If the prefix is X, create the KDOTRouteID from the Ramp route component parts.
    selectionQuery = """ "LRS_ROUTE_PREFIX" = 'X' """
    # Doesn't make sense to require *_SUFFIX on ramps. - Just use '0' if it is null.
    # Only 12 Ramps have non-null LRS_ROUTE_SUFFIX values. For those, it is all '0' or 'No Suffix'.
    # If people set LRS_ROUTE_SUFFIX to 'G' or 'Z' for ramps though, that needs to be handled correctly.
    necessaryFields = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_UNIQUE_IDENT", "LRS_ADMO"]
    dynNonNullSelectionQuery = GenerateNonNullSelectionQuery(necessaryFields)
    fullSelectionQuery = selectionQuery + """ AND """ + dynNonNullSelectionQuery
    
    fieldsToUseForUpdating = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO",
        "KDOT_DIRECTION_CALC", "KDOT_LRS_KEY"]
    
    newCursor = daUpdateCursor(fcAsFeatureLayer, fieldsToUseForUpdating, fullSelectionQuery)
    
    for cursorRowItem in newCursor:
        cursorListItem = list(cursorRowItem)
        countyPre = cursorListItem[0]
        routePre = cursorListItem[1]
        routeNum = cursorListItem[2]
        routeSuf = cursorListItem[3]
        if routeSuf is None:
            routeSuf = '0'
        else: # Use whatever character is in the Route Suffix if it's not None/Null.
            pass
        lrsUniqueIdent = cursorListItem[4]
        if len(lrsUniqueIdent) > 1:
            lrsUniqueIdent = lrsUniqueIdent[-1]
        else:
            pass
        lrsAdmo = cursorListItem[5]
        directionCalc = cursorListItem[6]
        if directionCalc is None:
            directionCalc = '0'
        else:
            pass
        try:
            newKey = str(countyPre) + str(routePre) + str(routeNum) + str(routeSuf) + str(lrsUniqueIdent) + str(lrsAdmo) + str(directionCalc)
            cursorListItem[7] = newKey
            newCursor.updateRow(cursorListItem)
        except:
            try:
                print(traceback.format_exc())
                print("Could not calculate a new LRS_KEY for the given row.")
                print("The row looks like this: " + str(cursorListItem) + ".")
            except:
                pass
            newCursor.next()
    
    try:
        del newCursor
    except:
        pass
    
    # For all other prefixes.
    selectionQuery = """ "LRS_ROUTE_PREFIX" NOT IN ('I', 'U', 'K', 'X', 'R', 'M', 'C') """
    necessaryFields = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO"]
    dynNonNullSelectionQuery = GenerateNonNullSelectionQuery(necessaryFields)
    fullSelectionQuery = selectionQuery + """ AND """ + dynNonNullSelectionQuery
    
    fieldsToUseForUpdating = ["LRS_COUNTY_PRE", "LRS_ROUTE_PREFIX", "LRS_ROUTE_NUM", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_ADMO",
        "KDOT_DIRECTION_CALC", "KDOT_LRS_KEY"]
    
    newCursor = daUpdateCursor(fcAsFeatureLayer, fieldsToUseForUpdating, fullSelectionQuery)
    
    for cursorRowItem in newCursor:
        cursorListItem = list(cursorRowItem)
        countyPre = cursorListItem[0]
        routePre = cursorListItem[1]
        routeNum = cursorListItem[2]
        routeSuf = cursorListItem[3]
        lrsUniqueIdent = cursorListItem[4]
        if len(lrsUniqueIdent) > 1:
            lrsUniqueIdent = lrsUniqueIdent[-1]
        else:
            pass
        lrsAdmo = cursorListItem[5]
        directionCalc = cursorListItem[6]
        if directionCalc is None:
            directionCalc = '0'
        else:
            pass
        try:
            newKey = str(countyPre) + str(routePre) + str(routeNum) + str(routeSuf) + str(lrsUniqueIdent) + str(lrsAdmo) + str(directionCalc)
            cursorListItem[7] = newKey
            newCursor.updateRow(cursorListItem)
        except:
            try:
                print(traceback.format_exc())
                print("Could not calculate a new LRS_KEY for the given row.")
                print("The row looks like this: " + str(cursorListItem) + ".")
            except:
                pass
            newCursor.next()
    
    try:
        del newCursor
    except:
        pass
    
    # Something's not right. The calculates should fail every time because the n1 fields don't exist in this layer yet. :(
    selectionQuery = """ "KDOT_LRS_KEY" IS NOT NULL """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = KDOT_LRS_KEY
    CalculateField_management (fcAsFeatureLayer, n1RouteId, "!" + str(KDOTRouteId) + "!", "PYTHON_9.3")
    # SourceFromMeasure = county_log_begin
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!" + str(KDOTMeasBeg) + "!", "PYTHON_9.3")
    # SourceToMeasure = county_log_end
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!" + str(KDOTMeasEnd) + "!", "PYTHON_9.3")
    selectionQuery = """ KDOT_LRS_KEY IS NOT NULL AND county_log_begin IS NULL AND county_log_end IS NULL AND (COUNTY_BEGIN_MP IS NOT NULL OR COUNTY_END_MP IS NOT NULL) """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    countResult = GetCount_management(fcAsFeatureLayer)
    intCount = int(countResult.getOutput(0))
    print("After the new selection query to deal with the fact that some State routes did not have their begin and end measure populated correctly, " +
        str(intCount) + " segments were selected.")
    # SourceFromMeasure = COUNTY_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!COUNTY_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = COUNTY_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!COUNTY_END_MP!", "PYTHON_9.3")


# Helper function
def GenerateNonNullSelectionQuery(passedInFields):
    selectionQuery = """ """
    fieldCounter = 0
    for fieldToUse in passedInFields:
        if fieldCounter != 0:
            selectionQuery += """ AND \"""" + str(fieldToUse) + """\" IS NOT NULL """
        else:
            selectionQuery += """ \"""" + str(fieldToUse) + """\" IS NOT NULL """
        
        fieldCounter += 1
    
    return selectionQuery


def addMissingFields(fcToAddFieldsTo):
    currentFieldObjectsList = ListFields(fcToAddFieldsTo)
    currentFieldNames = [x.name for x in currentFieldObjectsList]
    for fieldToCheckForAndAddItem in fieldsToCheckForAndAdd:
        if fieldToCheckForAndAddItem not in currentFieldNames:
            if fieldToCheckForAndAddItem == n1RouteId:
                routeIDFieldName = fieldToCheckForAndAddItem
                routeIDFieldType = "TEXT"
                routeIDFieldLength = 50
                routeIDFieldAlias = routeIDFieldName
                AddField_management(fcToAddFieldsTo, routeIDFieldName, routeIDFieldType, "", "", routeIDFieldLength, routeIDFieldAlias, nullable)
            else:
                routeMeasureFieldName = fieldToCheckForAndAddItem
                routeMeasureFieldType = "DOUBLE"
                routeMeasureFieldPrecision = 38
                routeMeasureFieldScale = 8
                routeMeasureFieldAlias = routeIDFieldName
                AddField_management(fcToAddFieldsTo, routeMeasureFieldName, routeMeasureFieldType, routeMeasureFieldPrecision, routeMeasureFieldScale, "", routeMeasureFieldAlias, nullable)
        else:
            pass


if __name__ == "__main__":
    print("Please do not run this script directly.")
    print("Please set the needed variables in the datareviewerchecks_config then")
    print("call this script's main() function from the datareviewerchecks_dailyprocess.py script.")
    #Uncomment the next line for Testing
    main()
else:
    pass