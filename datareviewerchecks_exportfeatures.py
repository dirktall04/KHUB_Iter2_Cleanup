#!/usr/bin/env python
# -*- coding:utf-8 -*-
#datareviewerchecks_exportfeatures.py
# Created 2016-12-22
# Updated 2017-01-30 by dirktall04
# Updated 2017-11-13 by dirktall04, to add support for the CSIP features.
# Updated 2017-11-15 by dirktall04

# Use the OBJECTID field from the reviewer table
# to select by ObjectId  in the source feature
# class. Group the output by the Check Title field.

# Get a list of the unique types of Check Titles

# Then, condense the list by removing the spaces
# and dashes.

# Next, create feature classes (based on the Source
# type) with the names of those checks, and transfer
# the matching ObjectIDs into those feature classes.

# Table to read is REVTABLEMAIN in the Reviewer_Sessions GDB
# The "RecordID" for this table is actually its OID.
# The "ObjectID" field for this table is the ObjectID for the
# originating feature class.

# "ORIGINTABLE" is the name of the table that the feature
# comes from.

# "CHECKTITLE" is the name of what the output should be called
# though it needs to be modified a bit, to remove spaces and
# dashes (if any exist).

# Need to create a list of the unique checktitles.

# Then, for each checktitle, get the origintable that it
# applies to, and get a list of the objectIds in that
# table that it applies to. -- Possibility for one
# checktitle to have more than one origintable, so guard
# against that -- even though it probably doesn't occur
# in this dataset.

# Need to create lists of the ObjectIds for each origintable
# then, create a list of the unique checktitles.

# Start with the base gdb location for the features
# then use concatenation to build the Feature class
# name with the origintable field.

# REVTABLEMAIN is the name of the table that holds the error records
# that are of interest.

# Need to move the error reporting parts of this script to a
# separate script.

import os
import time

from arcpy import (AddField_management, AddJoin_management, CopyFeatures_management,
    CreateFileGDB_management, Delete_management, Exists, env,
    GetCount_management, MakeFeatureLayer_management,
    MakeTableView_management, SelectLayerByAttribute_management)

from arcpy.da import SearchCursor as daSearchCursor

from pathFunctions import (returnGDBOrSDEName, returnFeatureClass)

from datareviewerchecks_config import (revTable, originTablesGDB, errorFeaturesGDB,
    mainFolder, errorReportCSVName, errorReportCSV, useRAndHCheck, nonMonotonicOutputFC, 
    errorReportRowsOrder, nullable, single_part_point_errors, single_part_line_errors,
    usePrefixSetTestingAndReporting, prefixSetErrorReportingDict, outerTestDict,
    csip_output_gdb1, csip_ordered_report_rows, csip_unordered_report_rows)


def formatCheckTitle(nameToBeUnderscorified):
    newName = nameToBeUnderscorified
    newName = str(newName).replace(' ', '')
    newName = str(newName).replace('-', '')
    return newName


class tableAndCheckData:
    def __init__(self, tableName, checkTitle):
        self.tableName = tableName
        self.checkTitle = checkTitle
        self.listOfOIDsToUse = list()


def exportErrorsToFeatureClasses(reviewTable, originGDB, errorOutputGDB, errorOutputGDBFolder):
    # Checking to see if the output already exists.
    # If so, remove it.
    if Exists(errorOutputGDB):
        Delete_management(errorOutputGDB)
    else:
        pass
    
    CreateFileGDB_management(errorOutputGDBFolder, returnGDBOrSDEName(errorOutputGDB))
    
    previousWorkspace = env.workspace
    env.workspace = errorOutputGDB
    
    tableFields = ['ORIGINTABLE', 'CHECKTITLE', 'OBJECTID']
    newCursor = daSearchCursor(reviewTable, tableFields)
    
    revRows = list()
    
    for rowItem in newCursor:
        revRows.append(list(rowItem))
    
    try:
        del newCursor
    except:
        pass
    
    originTableList = list()
    checkTitleList = list()
    
    for revRowItem in revRows:
        originTableList.append(revRowItem[0])
        checkTitleList.append(revRowItem[1])
    
    print ('Creating sets from the originTable and checkTitle lists.')
    originTableSet = set(originTableList)
    checkTitleSet = set(checkTitleList)
    print ('Finished set creation.')
    
    originTableList = list(originTableSet)
    checkTitleList = list(checkTitleSet)
    
    tableAndCheckDataObjects = list()
    csvDictOfErrorFeatures = dict()
    
    for originTableItem in originTableList:
        print('Origin table = ' + originTableItem + '.')
        completeOriginTablePath = os.path.join(originGDB, originTableItem)
        print('The full path to the origin table is ' + str(completeOriginTablePath) + '.')
        tableViewName = "ReviewTable_View_" + str(originTableItem)
        originTableWhereClause = """"ORIGINTABLE" = '""" + str(originTableItem) +  """'"""
        try:
            Delete_management(tableViewName)
        except:
            pass
        MakeTableView_management(reviewTable, tableViewName, originTableWhereClause)
        
        for checkTitleItem in checkTitleList:
            print('Check title = ' + checkTitleItem + '.')
            selectionWhereClause = """"CHECKTITLE" = '""" + str(checkTitleItem) + """'"""
            SelectLayerByAttribute_management(tableViewName, "NEW_SELECTION", selectionWhereClause)
            countResult = GetCount_management(tableViewName)
            intCount = int(countResult.getOutput(0))
            
            if intCount >= 1:
                tempTableAndCheckData = tableAndCheckData(originTableItem, checkTitleItem)
                tableViewFields = ["RECORDID", "OBJECTID"]
                
                newCursor = daSearchCursor(tableViewName, tableViewFields, selectionWhereClause)
                
                newOIDList = list()
                
                for cursorItem in newCursor:
                    newOIDList.append(cursorItem[1])
                    
                try:
                    del newCursor
                except:
                    pass
                
                tempTableAndCheckData.listOfOIDsToUse = newOIDList
                
                tableAndCheckDataObjects.append(tempTableAndCheckData)
            else:
                print("There were no features selected for the " + tableViewName + " table.")
    
    print("There are " + str(len(tableAndCheckDataObjects)) + " different items in the tableAndCheckDataObjects list.")
    
    for listObject in tableAndCheckDataObjects:
        
        featureLayerForErrorOutput = 'FeatureClassAsFeatureLayer'
        
        if Exists(featureLayerForErrorOutput):
            Delete_management(featureLayerForErrorOutput)
        else:
            pass
        
        fullPathToFeatureClass = os.path.join(originTablesGDB, listObject.tableName)
        
        MakeFeatureLayer_management(fullPathToFeatureClass, featureLayerForErrorOutput)
        
        # build the selection list & select up to but not more than 999 features at at time
        OIDTotalCounter = 0
        errorOutputWhereClause = """ "OBJECTID" IN ("""
        
        for errorOID in listObject.listOfOIDsToUse:
            if OIDTotalCounter <= 998:
                errorOutputWhereClause = errorOutputWhereClause + str(errorOID) + """, """
                OIDTotalCounter += 1
            else:
                # Remove the trailing ", " and add a closing parenthesis.
                errorOutputWhereClause = errorOutputWhereClause[:-2] + """) """ 
                SelectLayerByAttribute_management(featureLayerForErrorOutput, "ADD_TO_SELECTION", errorOutputWhereClause)
                
                OIDTotalCounter = 0
                errorOutputWhereClause = """ "OBJECTID" IN ("""
                errorOutputWhereClause = errorOutputWhereClause + str(errorOID) + """, """
        
        # Remove the trailing ", " and add a closing parenthesis.
        errorOutputWhereClause = errorOutputWhereClause[:-2] + """) """
        SelectLayerByAttribute_management(featureLayerForErrorOutput, "ADD_TO_SELECTION", errorOutputWhereClause)
        
        ##print "Counting..."
        selectedErrorsResult = GetCount_management(featureLayerForErrorOutput)
        selectedErrorsCount = int(selectedErrorsResult.getOutput(0))
        
        # export the selected data with the correct tableName & checkTitle
        outputFeatureClassName = formatCheckTitle(listObject.checkTitle) + "ErrorsFrom_" + listObject.tableName
        fullPathToOutputFeatureClass = os.path.join(errorOutputGDB, outputFeatureClassName)
        
        csvDictOfErrorFeatures[outputFeatureClassName] = str(selectedErrorsCount)
        
        print(str(selectedErrorsCount) + "\t features will be written to \t" + outputFeatureClassName)
        if selectedErrorsCount >= 1:
            CopyFeatures_management(featureLayerForErrorOutput, fullPathToOutputFeatureClass)
            time.sleep(25)
            AddField_management(outputFeatureClassName, "OptionalInfo", "TEXT", "", "", 250, "ReviewingInfo", nullable)
        else:
            pass
    
    # Need to write a short CSV here that tells the number and type of errors.
    print('Writing error information to an error reports file called ' + str(errorReportCSVName) + '.')
    try:
        with open(errorReportCSV, 'w') as fHandle:
            for errorFeature in errorReportRowsOrder:
                if errorFeature in csvDictOfErrorFeatures:
                    errorFeatureCount = csvDictOfErrorFeatures[errorFeature]
                    fHandle.write(str(errorFeature) + ', ' + str(errorFeatureCount) + '\n')
                else:
                    fHandle.write(str(errorFeature) + ', ' + str(0) + '\n')
            # Add a blank line to match previous formatting.
            fHandle.write('\n')
    except:
        print("There was an error writing to the file.")
    
    # Modify this so that it just checks for the existence of the roads
    # and highways check output, rather than relying on the config
    # file for whether or not this should be ran.
    # The config file can tell the full process whether or not
    # to run the R&H check, but the error report should give
    # details on the R&H check whether or not the config file
    # currently states that the R&H check should be ran again
    # were the full process to run.
    
    env.workspace = previousWorkspace


def reportExtensionForRAndHCheck(featuresToCheck):
    if Exists(featuresToCheck):
        featuresName = returnFeatureClass(featuresToCheck)
        errorsFromRAndH = 'RAndHErrorsAsFeatureLayer'
        try:
            Delete_management(errorsFromRAndH)
        except:
            pass
        MakeFeatureLayer_management(featuresToCheck, errorsFromRAndH)
        errorsFromRAndHResult = GetCount_management(errorsFromRAndH)
        errorsFromRAndHCount = int(errorsFromRAndHResult.getOutput(0))
        
        print("Roads & Highways Non-Monotonic Check output was found.")
        print("Extending the errors report with information from the Roads & Highways Non-Monotonicity Check.")
        
        try:
            with open(errorReportCSV, 'a') as fHandle:
                fHandle.write(featuresName + ', ' + str(errorsFromRAndHCount) + '\n')
        except:
            print("There was an error writing to the file.")
        
        #errorsRHGDB = returnGDBOrSDEName(featuresToCheck)
        #errorsFeatureClass = returnFeatureClass(featuresToCheck)
        #previousWorkspace = env.workspace
        #env.workspace = errorsRHGDB
        
        #time.sleep(25)
        #print("Also adding ReviewUser and ReviewInfo text fields to the")
        #print("Roads & Highways Non-Monotonicity Check error output feature class.")
        #AddField_management(errorsFeatureClass, "OptionalInfo", "TEXT", "", "", 250, "ReviewingInfo", nullable)
        
        #env.workspace = previousWorkspace
        
    else:
        print("No Roads & Highways Non-Monotonic Check output found.")
        print("Will not add additional information to the errors report csv.")


# New function to count the number of SinglePartPointErrors and SinglePartLineErrors.
def reportExtensionForQCGDB(singlePartPointErrors, singlePartLineErrors):
    # Get a count for the singlepart features (if they exist)
    # and append the count data to the end of the errorReportCSV.
    if Exists(singlePartPointErrors) and Exists(singlePartLineErrors):
        singlePartPointFeaturesName = returnFeatureClass(singlePartPointErrors)
        singlePartPointErrorsResult = GetCount_management(singlePartPointErrors)
        singlePartPointErrorsCount = int(singlePartPointErrorsResult.getOutput(0))
        
        singlePartLineFeaturesName = returnFeatureClass(singlePartLineErrors)
        singlePartLineErrorsResult = GetCount_management(singlePartLineErrors)
        singlePartLineErrorsCount = int(singlePartLineErrorsResult.getOutput(0))
        try:
            with open(errorReportCSV, 'a') as fHandle:
                fHandle.write(singlePartPointFeaturesName + ', ' + str(singlePartPointErrorsCount) + '\n')
                fHandle.write(singlePartLineFeaturesName + ', ' + str(singlePartLineErrorsCount) + '\n')
        except:
            print("There was an error writing to the file.")
    else:
        print("The Single Part output was not found.")
        print("Will not add the Single Part information to the errors report csv.")


def reportExtensionForCSIP(csipGDBWithOutput):
    # Create a blank line before the CSIP error counts.
    try:
        with open(errorReportCSV, 'a') as fHandle:
            fHandle.write('\n')
    except:
        print("There was an error writing to the file.")
    
    csipGDBWithOutputFrequencyTable = os.path.join(csipGDBWithOutput, "SelfIntersectingRoutes_CategoryCounts")
    if Exists(csipGDBWithOutputFrequencyTable):
        csipCursorFields = ["SelfIntersectionType", "FREQUENCY"]
        newCursor = daSearchCursor(csipGDBWithOutputFrequencyTable, csipCursorFields)
        errorDescriptionAndCountDict = dict()
        for cursorItem in newCursor:
            if cursorItem[0] is not None and cursorItem[1] is not None:
                errorDescriptionAndCountDict[cursorItem[0]] = cursorItem[1]
            else:
                print("Either the cursorItem[0] or cursorItem[1] were none.")
                print("Will not add this cursorItem to the csip output dictionary.")
        
        # To get the listed error descriptions with associated counts, in order.
        for errorDescToRecordFirst in csip_ordered_report_rows:
            errorDescription = errorDescToRecordFirst
            errorCount = errorDescriptionAndCountDict.get(errorDescToRecordFirst, None)
            if errorCount is not None:
                print("There were " + str(errorCount) + " errors features with the description of: \t" + str(errorDescription) + ".")
                try:
                    with open(errorReportCSV, 'a') as fHandle:
                        fHandle.write(errorDescription + ', ' + str(errorCount) + '\n')
                except:
                    print("There was an error writing to the file.")
            else:
                print("There were 0 errors with the description of: \t" + str(errorDescription) + ".")
                try:
                    with open(errorReportCSV, 'a') as fHandle:
                        fHandle.write(errorDescription + ', ' + '0' + '\n')
                except:
                    print("There was an error writing to the file.")
        
        complexSelfIntersectionsCount = 0
        # To get the unlisted error descriptions with associated counts, in no particular order.
        for errorDescription in errorDescriptionAndCountDict.keys():
            if errorDescription not in csip_ordered_report_rows:
                if errorDescription.find('Complex') >= 0: # Returns -1 if not found.
                    errorCount = errorDescriptionAndCountDict[errorDescription]
                    complexSelfIntersectionsCount += int(errorCount)
                elif errorDescription == 'Not self-intersecting':
                    pass
                else:
                    # This is an issue. Print a warning.
                    print("Warning: The error description of '" + str(errorDescription) + "'")
                    print("is neither in the csip_ordered_report_rows list, nor is it a Complex Self-Intersection.")
            else:
                pass # This should have already been recorded.
            
        try:
            with open(errorReportCSV, 'a') as fHandle:
                fHandle.write('Complex Self-Intersection' + ', ' + str(complexSelfIntersectionsCount) + '\n')
        except:
            print("There was an error writing to the file.")
        
    else:
        print("Could not find the Output Frequency Table in the csip GDB.")


def mainWithPrefixSets():
    # For now, use globals.
    # Make into prettier/prefixSetFirst Python later, that uses
    # dictionary values for everything, including default dictionary values
    # for when the usePrefixSetTestingAndReporting value is false.
    # Start a loop
    for prefixKeyItem in prefixSetErrorReportingDict.keys():
        # Then, set the necessary variables from the dict
        # for the current prefix set in the list.
        prefixKeyItemDict = outerTestDict[prefixKeyItem]
        dataReviewExportDict = prefixKeyItemDict["dataReviewExportDict"]
        csipDict = prefixKeyItemDict["csipDict"]
        
        global errorReportCSVName
        errorReportCSVName = dataReviewExportDict["errorReportCSVName"]
        global errorReportCSV
        errorReportCSV = dataReviewExportDict["errorReportCSV"]
        
        #Non-global, passed directly into the function
        global revTable
        revTable = dataReviewExportDict["revTable"]
        global originTablesGDB
        originTablesGDB = dataReviewExportDict["originTablesGDB"]
        global errorFeaturesGDB
        errorFeaturesGDB = dataReviewExportDict["errorFeaturesGDB"]
        global nonMonotonicOutputFC
        nonMonotonicOutputFC = dataReviewExportDict["nonMonotonicOutputFC"]
        global single_part_point_errors
        single_part_point_errors = dataReviewExportDict["single_part_point_errors"]
        global single_part_line_errors
        single_part_line_errors = dataReviewExportDict["single_part_line_errors"]
        global csip_output_gdb1
        csip_output_gdb1 = csipDict["csip_output_gdb1"]
        
        exportErrorsToFeatureClasses(revTable, originTablesGDB, errorFeaturesGDB, mainFolder)
        reportExtensionForRAndHCheck(nonMonotonicOutputFC)
        reportExtensionForQCGDB(single_part_point_errors, single_part_line_errors)
        reportExtensionForCSIP(csip_output_gdb1)


def main():
    print 'Error exports starting...'
    exportErrorsToFeatureClasses(revTable, originTablesGDB, errorFeaturesGDB, mainFolder)
    reportExtensionForRAndHCheck(nonMonotonicOutputFC)
    reportExtensionForQCGDB(single_part_point_errors, single_part_line_errors)
    reportExtensionForCSIP(csip_output_gdb1)
    print 'Error exports complete.'
# To get the multipart point errors, you can join the REVTABLEPOINT.LINKID to the REVTABLEMAIN.RECORDID.


if __name__ == "__main__":
    if usePrefixSetTestingAndReporting == True:
        mainWithPrefixSets()
    else:
        main()
else:
    pass