#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_nonmonoroadsandhighways.py
# Created 2016-01-04
# Last Updated 2017-01-27 by dirktall04


from arcpy import (CalculateField_management, CheckExtension,
    CheckInExtension, CheckOutExtension, CreateFileGDB_management,
    Delete_management, env, Exists)
    # DetectNonMonotonicRoutes_locref is imported after checking
    # out the "Highways" extension.

from pathFunctions import returnGDBOrSDEName

env.overwriteOutput = 1

from datareviewerchecks_config import (mainFolder, networkToReview, nonMonotonicOutputGDB,
    nonMonotonicOutputFC, usePrefixSetTestingAndReporting, prefixSetErrorReportingDict, outerTestDict)


def roadsNonMonoCheck():
    try:
        # Check out license
        print('The result of CheckExtension("Highways") is ' + str(CheckExtension("Highways")) + '.')
        if CheckExtension("Highways") == 'Available':
            CheckOutExtension("Highways")
            
            # Do the license check before the deletion, so that you don't
            # remove data and then not put it back in the case that the
            # license is not available.
            from arcpy import DetectNonMonotonicRoutes_locref
            
            if Exists(nonMonotonicOutputGDB):
                try:
                    Delete_management(nonMonotonicOutputGDB)
                except:
                    pass
            else:
                pass
            
            nonMonotonicOutputGDBName = returnGDBOrSDEName(nonMonotonicOutputGDB)
            
            CreateFileGDB_management(mainFolder, nonMonotonicOutputGDBName)
            time.sleep(1)
            
            DetectNonMonotonicRoutes_locref(networkToReview, nonMonotonicOutputFC, "Any", "F_Date", "T_Date", "SourceRouteId")
            
            print("The Roads & Highways Non-Monotonic routes check for " + str(networkToReview) + " has completed.\n")
            
        else:
            print('The Roads & Highways extension is not currently available.')
            print('Skipping R&H Non-Monotonicity check.')
        
    except Exception as Exception1:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print Exception1.message
        try:
            del Exception1
        except:
            pass
    finally:
        try:
            # Check the license back in
            CheckInExtension("Highways")
        except:
            pass


def mainWithPrefixSets():
    for prefixKeyItem in prefixSetErrorReportingDict.keys():
        # Then, set the necessary variables from the dict
        # for the current prefix set in the list.
        prefixKeyItemDict = outerTestDict[prefixKeyItem]
        rAndHCheckdict = prefixKeyItemDict["rAndHCheckdict"]
        
        global nonMonotonicOutputGDB
        nonMonotonicOutputGDB = rAndHCheckdict["nonMonotonicOutputGDB"]
        global nonMonotonicOutputFC
        nonMonotonicOutputFC = rAndHCheckdict["nonMonotonicOutputFC"]
        global networkToReview
        networkToReview = rAndHCheckdict["networkToReview"]
        
        print("nonMonotonicOutputGDB: " + str(nonMonotonicOutputGDB) + ".")
        print("nonMonotonicOutputFC: " + str(nonMonotonicOutputFC) + ".")
        print("networkToReview: " + str(networkToReview) + ".")
        
        # Then, try running the reviewData function
        roadsNonMonoCheck()


def main():
    print('Roads & Highways Non-Monotonic Check started.')
    roadsNonMonoCheck()
    print('Roads & Highways Non-Monotonic Check finished.')


if __name__ == "__main__":
    if usePrefixSetTestingAndReporting == True:
        mainWithPrefixSets()
    else:
        main()

else:
    pass