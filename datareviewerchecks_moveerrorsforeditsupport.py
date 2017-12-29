#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_moveerrorsforeditsupport.py
# Created 2016-12-27, by dirktall04

import os
from arcpy import(CopyFeatures_management, Delete_management, Exists)
from datareviewerchecks_config import (mainFolder, dailyProcessSDESourceCenterlinesLocation, reviewerSessionGDB,
    gdbBasePart3, nonMonotonicOutputGDB, errorFeaturesQCGDB, errorFeaturesQCGDBName,
    multipart_point_errors, multipart_line_errors, single_part_point_errors, single_part_line_errors, nonMonotonicOutputFC,
    csip_routes, csip_output_gdb1, usePrefixSetTestingAndReporting, prefixSetErrorReportingDict, outerTestDict)

from pathFunctions import (returnGDBOrSDEPath, returnFeatureClass)

csip_check_output = os.path.join(csip_output_gdb1, 'Routes_SelfIntClassification_' + gdbBasePart3)
prefixesToMoveErrorsFor = [single_part_point_errors, single_part_line_errors, nonMonotonicOutputFC, csip_check_output]


def moveLocalErrorsToSQL(prefixKeyName):
    print("Moving errors from the Local gdb to SQL for the prefix key name of: " + str(prefixKeyName) + ".")
    for errorItemFC in prefixesToMoveErrorsFor:
        errorItemFCBaseName = returnFeatureClass(errorItemFC)
        sqlPath = returnGDBOrSDEPath(dailyProcessSDESourceCenterlinesLocation)
        errorItemCopyName = prefixKeyName + '_' + errorItemFCBaseName
        errorItemSQLLocation = os.path.join(sqlPath, errorItemCopyName)
        lowerstrErrorItemFCBaseName = str(errorItemFCBaseName).lower()
        if lowerstrErrorItemFCBaseName.find('selfintclassification') >= 0:
            # Already includes the prefix name in the basename, so just use the full BaseName for the class.
            errorItemSQLLocation = os.path.join(sqlPath, errorItemFCBaseName)
        else:
            pass
        if Exists(errorItemSQLLocation):
            try:
                Delete_management(errorItemSQLLocation)
            except:
                print("Could not delete the FC at: " + str(errorItemSQLLocation) + ".")
                print("Please make sure that the FC does not have any locks on it and try again.")
        try:
            CopyFeatures_management(errorItemFC, errorItemSQLLocation)
        except:
            print("Could not copy from the FC at: " + str(errorItemFC))
            print("to the FC at: " + str(errorItemSQLLocation) + ".")
            print("Please make sure that the FC to copy from exists")
            print("and that the FC to copy to is not locked.")


def main():
    # Use the gdbBasePart3 variable since that should be the same as the prefix key would be
    # iff you're not using the Prefix Set Testing And Reporting for this run.
    moveLocalErrorsToSQL(gdbBasePart3)


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
        global errorFeaturesQCGDB
        errorFeaturesQCGDB = dataReviewExportDict["errorFeaturesQCGDB"]
        global single_part_point_errors
        single_part_point_errors = dataReviewExportDict["single_part_point_errors"]
        global single_part_line_errors
        single_part_line_errors = dataReviewExportDict["single_part_line_errors"]
        
        rAndHCheckdict = prefixKeyItemDict["rAndHCheckdict"]
        global nonMonotonicOutputGDB
        nonMonotonicOutputGDB = rAndHCheckdict["nonMonotonicOutputGDB"]
        global nonMonotonicOutputFC
        nonMonotonicOutputFC = rAndHCheckdict["nonMonotonicOutputFC"]
        
        csipDict = prefixKeyItemDict["csipDict"]
        csip_output_gdb1 = csipDict["csip_output_gdb1"]
        global csip_check_output
        csip_check_output = os.path.join(csip_output_gdb1, 'Routes_SelfIntClassification_' + prefixKeyItem)
        global prefixesToMoveErrorsFor
        prefixesToMoveErrorsFor = [single_part_point_errors, single_part_line_errors, nonMonotonicOutputFC, csip_check_output]
        
        # Use the prefix key item for the current prefix name.
        moveLocalErrorsToSQL(prefixKeyItem)


if __name__ == "__main__":
    if usePrefixSetTestingAndReporting == True:
        mainWithPrefixSets()
    else:
        main()