#!/usr/bin/env python
# datareviewerchecks_pulldatafromservertoprocessarnoldcenterlines.py
# -*- coding: utf-8 -*-
# Created 2017-12-26, by dirktall04
# Updated 2017-12-27, by dirktall04

from datareviewerchecks_onetimeprocess_config import (initialGeoCommConflationDataLocation, oneTimeProcessInputFeaturesLocation)
from arcpy import (CopyFeatures_management, Delete_management, Exists)


def main():   
    if Exists(oneTimeProcessInputFeaturesLocation):
        try:
            Delete_management(oneTimeProcessInputFeaturesLocation)
        except:
            print("Could not delete the feature class at: " + str(oneTimeProcessInputFeaturesLocation) + ".")
            print("Please clear any locks and try again.")
    else:
        pass
    try:
        CopyFeatures_management(initialGeoCommConflationDataLocation, oneTimeProcessInputFeaturesLocation)
    except:
        print("Could not copy the feature class at: " + str(initialGeoCommConflationDataLocation) + "\nTo " + str(oneTimeProcessInputFeaturesLocation) + ".")
        print("Please make sure that: " + str(initialGeoCommConflationDataLocation) + " exists\nand that " + str(oneTimeProcessInputFeaturesLocation) + " does not yet exist.")


if __name__ == "__main__":
    print("Please do not run this script directly.")
    print("Please set the needed variables in the datareviewerchecks_onetimeprocess_config")
    print("then call this script's main() function from the datareviewerchecks_initialonetimeprocess.py script.")
    #Uncomment the next line for testing.
    main()
else:
    pass