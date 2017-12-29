#!/usr/bin/env python
# datareviewerchecks_loganprocessadditions.py
# -*- coding: utf-8 -*-
# Created 2017-12-26, by dirktall04

from pathFunctions import returnGDBOrSDEPath, returnFeatureClass, returnGDBOrSDEName

from arcpy import (AddField_management, CalculateField_management,
    CreateFileGDB_management, CreateRoutes_lr, CopyFeatures_management,
    Delete_management, DeleteField_management, Describe, Dissolve_management, env,
    Exists, FeatureVerticesToPoints_management, FieldInfo,
    FieldMap, FieldMappings, MakeFeatureLayer_management,
    Merge_management)

from datareviewerchecks_config import (
    outputRoutes,
    featureLayerCL_For_Start_CP, featureLayerCL_For_End_CP,
    routesSourceCenterlines, startCalibrationPoints, endCalibrationPoints,
    mergedCalibrationPoints, dissolvedCalibrationPoints,
    mainFolder, nullable, mResolution, mTolerance, usePrefixSetTestingAndReporting,
    prefixSetErrorReportingDict, outerTestDict,
    loganProcessAdditionsGDBName, loganProcessAdditionsGDB, stateRoutesAndNullRouteIDs,
    preRouteSourceNoMeasures, stateNonPrimarySourceRoutesName, 
    stateNonPrimarySourceRoutes, stateNonPrimarySourceRoutesRouteID, statePrimarySourceRoutesName, 
    statePrimarySourceRoutes, statePrimarySourceRoutesRouteID, routesSourceCountyLRSArnoldName, 
    routesSourceCountyLRSArnold, routesSourceCountyLRSArnoldRouteID, 
    routesSourceCountyLRSArnoldFromMeasure, routesSourceCountyLRSArnoldToMeasure, 
    unprunedAttributesRoadCenterlinesName, unprunedAttributesRoadCenterlines, 
    unprunedAttributesRoadCenterlinesRouteID, preRouteSourceCRMLFields, preRouteSourceCRMLName, 
    preRouteSourceCRML, stateRoutesAndNullRouteIDsSelectionQuery, stateRoutesAndNullRouteIDsName, 
    fcAsFeatureLayerLG, fcAsFeatureLayerLG2, scratchFC, scratchFC2, scratchFC3, NEW_SELECTION_CONST)


def main():
    print("Sorry, ran out of time on writing this script.")
    print("Please do these modifications by hand from the")
    print("K-Hub Iteration 2 Source Route Creation Process 217-10-31.docx file")
    print("or have Kyle write a script for them.")
    print("I apologize for the inconvenience. -- Dirk")
    #recreateLoganProcessAdditionsGDB()
    #preparingSourceCountyData()
    #addingDividedAttributeAndCreatingRoutes()
    #addingConcurrentRoutes()
    #addingExceptions()
    #addingCalibrationPoints()


def recreateLoganProcessAdditionsGDB():
    print("Starting the recreateLoganProcessAdditionsGDB function!")
    if Exists(loganProcessAdditionsGDB):
        try:
            Delete_management(loganProcessAdditionsGDB)
        except:
            print("Could not delete the loganProcessAdditionsGDB.")
            print("Please remove any locks and try again.")
    else:
        pass
    
    CreateFileGDB_management(mainFolder, loganProcessAdditionsGDBName)


def preparingSourceCountyData():
    print("Starting the preparingSourceCountyData function!")
    
    if Exists(preRouteSourceCRML):
        try:
            Delete_management(preRouteSourceCRML)
        except:
            print("Could not delete the features located at: " + str(preRouteSourceCRML) + ".")
    else:
        pass
    
    # Make a copy
    CopyFeatures_management(routesSourceCountyLRSArnold, preRouteSourceCRML)
    
    # Remove unnecessary fields
    preRouteSourceCRMLDescription = Describe(preRouteSourceCRML)
    preRouteSourceCRMLOIDFieldName = preRouteSourceCRMLDescription.OIDFieldName
    preRouteSourceCRMLShapeFieldName = preRouteSourceCRMLDescription.shapeFieldName
    preRouteSourceCRMLShapeAndOIDFieldNames = [preRouteSourceCRMLOIDFieldName, preRouteSourceCRMLShapeFieldName]
    preRouteSourceCRMLFieldObjectsList = ListFields(preRouteSourceCRML)
    preRouteSourceFieldNames = [x.name for x in preRouteSourceCRMLFieldObjectsList]
    fieldNamesToKeep = [y for y in preRouteSourceFieldNames if y in preRouteSourceCRMLFields or y in preRouteSourceCRMLShapeAndOIDFieldNames]
    
    fieldNamesToRemove = [z for z in preRouteSourceFieldNames if z not in fieldNamesToKeep]
    
    for fieldNameItem in fieldNamesToRemove:
        DeleteField_management(preRouteSourceCRML, fieldNameItem)
    
    print("Done deleting unnecessary fields.")
    
    MakeFeatureLayer_management(preRouteSourceCRML, fcAsFeatureLayerLG)
    selectionQueryL1 = """ SourceRouteId IS NULL OR LRS_ROUTE_PREFIX IN ('I', 'U', 'K') """
    SelectLayerByAttribute(fcAsFeatureLayerLG, NEW_SELECTION_CONST, selectionQueryL1)
    CopyFeatures_management(fcAsFeatureLayerLG, stateRoutesAndNullRouteIDs)
    DeleteRows_management(fcAsFeatureLayerLG)
    selectionQueryL2 = """ SourceFromMeasure IS NULL OR SourceToMeasure IS NULL """
    SelectLayerByAttribute(fcAsFeatureLayerLG, NEW_SELECTION_CONST, selectionQueryL2)
    CopyFeatures_management(fcAsFeatureLayerLG, preRouteSourceNoMeasures)
    selectionQueryL3 = """ SourceFromMeasure IS NULL """
    SelectLayerByAttribute(fcAsFeatureLayerLG, NEW_SELECTION_CONST, selectionQueryL3)
    CalculateField_management(fcAsFeatureLayerLG, "SourceFromMeasure", "0", PYTHON_9_3_CONST)
    selectionQueryL4 = """ SourceToMeasure IS NULL """
    SelectLayerByAttribute(fcAsFeatureLayerLG, NEW_SELECTION_CONST, selectionQueryL4)
    CalculateField_management(fcAsFeatureLayerLG, "SourceToMeasure", "!SHAPE.LENGTH@MILES!", PYTHON_9_3_CONST)


def addingDividedAttributeAndCreatingRoutes():
    print("Starting the addingDividedAttributeAndCreatingRoutes function!")
    
    #try:
    #    Delete_management(fcAsFeatureLayerLG)
    #except:
    #    pass
    #MakeFeatureLayer_management(unprunedAttributesRoadCenterlines, fcAsFeatureLayerLG)
    selectionQueryL5 = """ LRS_ROUTE_PREFIX NOT IN ('I', 'U', 'K') AND KDOT_DIRECTION_CALC = '1' """
    #SelectLayerByAttribute_management(fcAsFeatureLayerLG, NEW_SELECTION_CONST, selectionQueryL5)
    #CopyFeatures_management(fcAsFeatureLayerLG, scratchFC)
    try:
        Delete_management(fcAsFeatureLayerLG)
    except:
        pass
    #MakeFeatureLayer_management(scratchFC, fcAsFeatureLayerLG)
    preRouteSourceCRMLFieldObjectsList = ListFields(preRouteSourceCRML)
    preRouteSourceCRMLFieldNamesList = [x.name for x in preRouteSourceCRMLFieldObjectsList]
    dividedFilterFieldName = "DividedFilter"
    dividedFilterFieldType = "TEXT"
    dividedFilterFieldLength = 3
    dividedFilterFieldAlias = dividedFilterFieldName
    if fieldName not in preRouteSourceCRMLFieldNamesList:
        AddField_management(preRouteSourceCRML, dividedFilterFieldName, dividedFilterFieldType, "", "", dividedFilterFieldLength, dividedFilterFieldAlias, nullable)
    else:
        pass
    #MakeFeatureLayer_management(preRouteSourceCRML, fcAsFeatureLayerLG2)
    #AddRelate_management(fcAsFeatureLayerLG, 'Non_State_System_LRSKey', fcAsFeatureLayerLG2, 'SourceRouteId', 'TempRelate', "MANY_TO_MANY")
    # Bypass definition query and relate nonsense with a searchcursor / updatecursor pair.
    nonStateDividedKeysList = list()
    searchCursorFields = ['Non_State_System_LRSKey']
    newCursor = daSearchCursor(unprunedAttributesRoadCenterlines, searchCursorFields, selectionQueryL5)
    
    for cursorRowItem in newCursor:
        nonStateDividedKeysList.append(cursorRowItem)
    
    try:
        del newCursor
    except:
        pass
    
    updateCursorFields = ['SourceRouteId', dividedFilterFieldName]
    newCursor = daUpdateCursor(preRouteSourceCRML, updateCursorFields)
    for cursorRowItem in newCursor:
        if cursorRowItem[0] is not None and str(cursorRowItem[0]) in nonStateDividedKeysList:
            cursorListItem = list(cursorRowItem)
            cursorListItem[1] = "yes"
            newCursor.update(cursorListItem)
        else:
            pass
    
    try:
        del newCursor
    except:
        pass
    
    selectionQueryL6 = ''' DividedFiler = "yes" '''
    MakeFeatureLayerManagement(preRouteSourceCRML, fcAsFeatureLayerLG2)
    SelectLayerByAttribute_management(fcAsFeatureLayerLG2, selectionQueryL6)
    CopyFeatures_management(fcAsFeatureLayerLG2, scratchFC2)
    FeatureVerticesToPoints(scratchFC2, scratchFC3, 'MID')
    raise KeyboardError("Stop. scratchFC3 created.")
    #SpatialJoin()


def addingConcurrentRoutes():
    print("Starting the addingConcurrentRoutes function!")
    
    


def addingExceptions():
    print("Starting the addingExceptions function!")
    
    


def addingCalibrationPoints():
    print("Starting the addingCalibrationPoints function!")
    
    


if __name__ == "__main__":
    print("Please do not run this script directly.")
    print("Please set the needed variables in the datareviewerchecks_config")
    print("then call this script's main() function from the datareviewerchecks_dailyprocess.py script.")
    #main()
else:
    pass