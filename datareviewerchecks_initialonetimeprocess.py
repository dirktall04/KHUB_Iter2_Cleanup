#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_initialonetimeprocess.py
# Created 2017-12-26, by dirktall04
# Updated 2017-12-27, by dirktall04

# Part 1 of the separated *_fullprocess.py script.

#### For Part 2, see *_dailyprocess.py, which should be ran on
#### the data every evening.

# This script should be ran just once, after receiving the data from GeoComm,
# but then not again after.

# To change the location of the inputs/outputs
# please visit/modify datareviewerchecks_config.py

# Check on ramp importing to make sure that it is behaving correctly.

import datetime
import time

import datareviewerchecks_onetimeprocess_config as configsettings
### Can't create from template due to hashed values with unknown algorithm in .rbj files. ###
###import datareviewerchecks_rbjxmlcreation as rbjxmlcreation
import datareviewerchecks_pulldatafromservertoprocessarnoldcenterlines as pulldatafromservertoprocessarnoldcenterlines
import datareviewerchecks_kdotprocessimprovements_iter3 as kdotprogrammaticfixesforarnoldcenterlines
import datareviewerchecks_pusharnoldcenterlinestoserverforediting as pusharnoldcenterlinestoserverforediting
### datareviewerchecks_routessourcecreation is obsolete. Don't use it.

startTime = datetime.datetime.now()

def main():
    print('Starting the initial, one-time, process of importing centerlines from ' + str(configsettings.initialGeoCommConflationDataLocation))
    print('then exporting them as modified centerlines to ' + str(configsettings.postInitialProcessRoadCenterlineOutputLocation))
    print('at: ' + str(startTime))
    
    if configsettings.routeSourceCreationOption.lower() == 'kdot':
        print("Pulling the data from the server to use as a base for the programmatic fixes.")
        pulldatafromservertoprocessarnoldcenterlines.main()
        print("Using KDOT's programmatic improvements to create the initial version of the arnold centerlines from the conflated PSAP centerlines & HPMS ramps.")
        kdotprogrammaticfixesforarnoldcenterlines.main()
        print("Writing the arnold centerines back to the server for manual editing.")
        pusharnoldcenterlinestoserverforediting.main()
    else:
        print("The routeSourceCreationOption is not 'kdot'. Will not recreate the routeSource.")
        pass
    
    settingsToReportList = ['initialGeoCommConflationDataLocation', 'inputCenterlines', 'outputCenterlines',
        'postInitialProcessRoadCenterlineOutputLocation', 'routeSourceCreationOption', 'rampReplacementToUse']
    print('Initial, one-time, process completed.')
    completeTime = datetime.datetime.now()
    print('at approximately: ' + str(completeTime))
    durationTime = completeTime - startTime
    print('and taking ' + str(durationTime))
    print('Using the following settings: ')
    for settingToReportOn in settingsToReportList:
        if (settingToReportOn in dir(configsettings)):
            print(str(settingToReportOn) + ": " + str(getattr(configsettings, str(settingToReportOn))))
        else:
            pass
    settingsToDisplayInConsole = [configsettings.usePrefixSetTestingAndReporting]
    print('The Post-Initial Process Road Centerlines can be found at ' + str(configsettings.postInitialProcessRoadCenterlineOutputLocation) + '.')


if __name__ == "__main__":
    main()

else:
    pass
