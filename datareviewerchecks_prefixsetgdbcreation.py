#!/usr/bin/env python
# -*- coding:utf-8 -*-
#datareviewerchecks_prefixsetgdbcreation.py
#Created 2017-10-24 by dirktall04

import os
import time
from arcpy import (CopyFeatures_management, CreateFileGDB_management, Delete_management, 
    Exists, MakeFeatureLayer_management, SelectLayerByAttribute_management)
from datareviewerchecks_config import (mainFolder, usePrefixSetTestingAndReporting, prefixSetErrorReportingDict,
    routesSource2, otherFCsToCopyList, outerTestDict)
from pathFunctions import (returnGDBOrSDEPath, returnFeatureClass, returnGDBOrSDEName)

## Switch to routesSource1 after modifying the original script to only output 2 routesSources,
## the first of which is what used to be the RoutesSource_CountyLRS_ARNOLD version,
## merged with any extra data that may have been presented in the base version (not sure yet, will check).
routesSourceFC = routesSource2 
routesSourceFCAsALayer = 'routesSourceFCAsALayer'


def main():
    if usePrefixSetTestingAndReporting == True:
        for prefixKey in prefixSetErrorReportingDict.keys():
            prefixAttributeQuery = prefixSetErrorReportingDict[prefixKey]
            prefixKeyItemDict = outerTestDict[prefixKey]
            prefixSetGdbBaseName = prefixKeyItemDict["prefixSetGdbBaseName"]
            prefixSetSourceGDBName = prefixSetGdbBaseName + '_Source.gdb'
            prefixSetSourceGDBLocation = os.path.join(mainFolder, prefixSetSourceGDBName)
            routesSourceOutputLocation = os.path.join(prefixSetSourceGDBLocation, 'RoutesSource')
            
            try:
                Delete_management(routesSourceFCAsALayer) #pre-emptive layer delete prior to rebuilding it
                time.sleep(3)
            except:
                pass
            
            MakeFeatureLayer_management(routesSourceFC, routesSourceFCAsALayer)
            routesSourceSelectionClause = """ """ + str(prefixAttributeQuery) + """ """
            SelectLayerByAttribute_management(routesSourceFCAsALayer, "NEW_SELECTION", routesSourceSelectionClause)
            
            if Exists(returnGDBOrSDEPath(routesSourceOutputLocation)):
                pass
            else:
                CreateFileGDB_management(mainFolder, returnGDBOrSDEName(returnGDBOrSDEPath(routesSourceOutputLocation)))
            # Checking to see if the output already exists.
            # If so, remove it.
            if Exists(routesSourceOutputLocation):
                print("Deleting the previous routesSourceOutputLocation at: \n" + str(routesSourceOutputLocation) + ".")
                Delete_management(routesSourceOutputLocation)
                time.sleep(7)
            else:
                pass
            # Create a new file for the output.
            print("Making a copy of the selection in the routesSourceFCAsALayer at: \n" + routesSourceOutputLocation + ".")
            CopyFeatures_management(routesSourceFCAsALayer, routesSourceOutputLocation)
            
            #Repeat for each of the other layers to be copied into the new *_Source.gdb.
            for itemToCopy in otherFCsToCopyList:
                itemToCopyInputLocation = os.path.join(returnGDBOrSDEPath(routesSourceFC), itemToCopy)
                itemToCopyOutputLocation = os.path.join(prefixSetSourceGDBLocation, itemToCopy)
                if Exists(itemToCopyOutputLocation):
                    print("Deleting the previous itemToCopyOutputLocation at: \n" + str(itemToCopyOutputLocation) + ".")
                    Delete_management(itemToCopyOutputLocation)
                    time.sleep(7)
                else:
                    pass
                print("Making a copy of the itemToCopy at: \n" + str(itemToCopyOutputLocation) + ".")
                CopyFeatures_management(itemToCopyInputLocation, itemToCopyOutputLocation)
            
    else:
        print("The usePrefixSetTestingAndReporting value is not True. Will not create separate prefix set gdbs.")


if __name__ == "__main__":
    main()
else:
    pass