#!/usr/bin/env python
# datareviewerchecks_pulldatafromservertorundailytests.py
# -*- coding: utf-8 -*-
# Created 2017-12-27, by dirktall04

from datareviewerchecks_config import (dailyProcessSDESourceCenterlinesLocation, inputCenterlines)
from arcpy import (CopyFeatures_management, Delete_management, Exists)


def main():
    print("Starting the process of copying centerlines from the server to run daily tests.")
    if Exists(inputCenterlines):
        try:
            Delete_management(inputCenterlines)
        except:
            print("Could not delete the feature class at: " + str(inputCenterlines) + ".")
            print("Please clear any locks and try again.")
    else:
        pass
    try:
        CopyFeatures_management(dailyProcessSDESourceCenterlinesLocation, inputCenterlines)
    except:
        print("Could not copy the feature class at: " + str(dailyProcessSDESourceCenterlinesLocation) + "\nTo " + str(inputCenterlines) + ".")
        print("Please make sure that: " + str(dailyProcessSDESourceCenterlinesLocation) + " exists\nand that " + str(inputCenterlines) + " does not yet exist.")


if __name__ == "__main__":
    print("Please do not run this script directly.")
    print("Please set the needed variables in the datareviewerchecks_config")
    print("then call this script's main() function from the datareviewerchecks_dailyprocess.py script.")
    #main()
else:
    pass