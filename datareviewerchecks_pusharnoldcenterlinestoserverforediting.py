#!/usr/bin/env python
# datareviewerchecks_pusharnoldcenterlinestoserverforediting.py
# -*- coding: utf-8 -*-
# Created 2017-12-26, by dirktall04
# Updated 2017-12-27, by dirktall04

from datareviewerchecks_onetimeprocess_config import (postInitialProcessRoadCenterlineOutputLocation, oneTimeProcessOutputSQLFeaturesLocation)
from arcpy import (CopyFeatures_management, Delete_management, Exists)


def main():
    continueFlag = True
    if Exists(oneTimeProcessOutputSQLFeaturesLocation):
        print("Are you absolutely SURE that you wish to overwrite the data at: " + str(oneTimeProcessOutputSQLFeaturesLocation))
        print("With the output from the initialonetimeprocess script?")
        print("(y/n)")
        userInput = rawInput('> ')
        if userInput.lower() == 'y':
            pass
        else:
            continueFlag = False
    else:
        print("There was nothing to overwrite at: " + str(oneTimeProcessOutputSQLFeaturesLocation) + "\nProceeding happily.")
    
    if continueFlag == True:
        # Go ahead and replace the data that existed (if any) with the output from the initialonetimeprocess.
        try:
            Delete_management(oneTimeProcessOutputSQLFeaturesLocation)
        except:
            print("Could not delete the feature class at: " + str(oneTimeProcessOutputSQLFeaturesLocation) + ".")
            print("Please clear any locks and try again.")
        try:
            CopyFeatures_management(postInitialProcessRoadCenterlineOutputLocation, oneTimeProcessOutputSQLFeaturesLocation)
        except:
            print("Could not copy the feature class at: " + str(postInitialProcessRoadCenterlineOutputLocation) + "\nTo " + str(oneTimeProcessOutputSQLFeaturesLocation) + ".")
            print("Please make sure that: " + str(postInitialProcessRoadCenterlineOutputLocation) + " exists\nand that " + str(oneTimeProcessOutputSQLFeaturesLocation) + " does not yet exist.")
        
    else:
        print("Will not overwrite the data at: " + str(oneTimeProcessOutputSQLFeaturesLocation) + ".")
        return


if __name__ == "__main__":
    print("Please do not run this script directly.")
    print("Please set the needed variables in the datareviewerchecks_onetimeprocess_config")
    print("then call this script's main() function from the datareviewerchecks_initialonetimeprocess.py script.")
    #Uncomment the next line for Testing
    main()
else:
    pass