#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_dailyprocess.py
# Created 2017-12-26, by dirktall04
# Updated 2017-12-27, by dirktall04

# Part 2 of the separated *_fullprocess.py script.

#### For Part 1, see *_initialonetimeprocess.py, which should be ran on
#### the data when it initially arrives and then not again.

# To change the location of the inputs/outputs
# please visit/modify datareviewerchecks_config.py

# This process produces a null output for the 10B_X_Routes.gdb\Routes feature class,
# so that feature class is not able to be error checked on its own.

import datetime
import time

import datareviewerchecks_config as configsettings
### Can't create from template due to hashed values with unknown algorithm in .rbj files. ###
###import datareviewerchecks_rbjxmlcreation as rbjxmlcreation
# Source Dissolve should happen after simplification and flipping.
# Source Dissolve will become optional and will take place in the daily process, if used.
###import datareviewerchecks_sourcedissolve as sourcedissolve
###import datareviewerchecks_sourcedissolve as sourcedissolve
import datareviewerchecks_keyrecalculation_keyupdatesfromcomponents as keyrecalculation_keyupdatesfromcomponents
import datareviewerchecks_pulldatafromservertorundailytests as pulldatafromservertorundailytests
import datareviewerchecks_loganprocessadditions as loganprocessadditions
import datareviewerchecks_prefixsetgdbcreation as prefixsetgdbcreation
import datareviewerchecks_lrsroutecreation as createtheroutes
import datareviewerchecks_runchecks as runthechecks
import datareviewerchecks_nonmonoroadsandhighways as nonmonorandhcheck
import datareviewerchecks_qcgdbexport as qcgdbexport
import ClassifySelfIntersectingPolylines_for_KDOT as csip_kdot
import datareviewerchecks_exportfeatures as exportthefeatures
import datareviewerchecks_moveerrorsforeditsupport as moveerrorsforeditsupport

startTime = datetime.datetime.now()

def main():
    print('Starting the full process of importing centerlines from ' + str(configsettings.inputCenterlines))
    print('then exporting them as routes to ' + str(configsettings.outputRoutes))
    print('next running the data reviewer checks from ' + str(configsettings.reviewerBatchJob))
    print('and exporting the error features to ' + str(configsettings.errorFeaturesGDB))
    print('at: ' + str(startTime))
    if configSettings.recalculateKeysFromComponents == True:
        keyrecalculation_keyupdatesfromcomponents.main()
    else:
        print("configSettings.recalculateKeysFromComponents is not set to True.")
        print("Not relcalculating LRS Keys from their component fields.")
    if configSettings.pullDataFromServerToRunDailyTests == True:
        pulldatafromservertorundailytests.main()
    else:
        print("configsettings.pullDataFromServerToRunDailyTests is not set to True.")
        print("Not pulling the arnold centerlines from the server to perform testing.")
        print("Will use the last pulled data for testing instead.")
    ##### Process fork #####
    # Everything from here on needs to either be used for just the current dataset,
    # or for each prefix set. Probably the best way to handle this is to rebuild
    # each function as though it expected to run on each prefix set's output and,
    # as a secondary option, could run just on the current one instead.
    if configsettings.usePrefixSetTestingAndReporting == True:
        prefixsetgdbcreation.main()
        # New
        if configsettings.recreateTheRoutes == True:
            time.sleep(25)
            print('Recreating the LRS Routes from the routesSource.')
            #createtheroutes.main()
            createtheroutes.mainWithPrefixSets()
        # New
        elif configsettings.useLoganProcessAdditions == True:
            print("Attempted replication of Logan's process additions in code.")
            print("This section of code has not received extensive testing.")
            print("It may be buggy.")
            print("If that is the case, please disable it until it can be fixed.")
            loganprocessadditions.mainWithPrefixSets()
        else:
            print('Skipping route creation.')
        # New
        if configsettings.runDataReviewerChecks == True:
            ### Can't create .rbj from template due to hashed values with unknown algorithm in .rbj files. ###
            ###rbjxmlcreation.main()
            print('Running the Data reviewer checks. This will take a while.')
            print('Seriously though... check back in an hour or so.')
            runthechecks.mainWithPrefixSets()
        else:
            pass
        # New
        if configsettings.useRAndHCheck == True:
            print('Running the Roads and Highways Non-Monotonicity check.')
            nonmonorandhcheck.mainWithPrefixSets()
        else:
            pass
        # New
        if configsettings.createQCGDB == True:
            qcgdbexport.mainWithPrefixSets()
        else:
            print("Not exporting error features to the QC GDB because the createQCGDB setting value is False.")
        # New
        if configsettings.runClassifySelfIntersectingPolylines == True:
            csip_kdot.mainWithPrefixSets()
        else:
            print("Not classifying self-intersecting polylines because the runClassifySelfIntersectingPolylines setting is False.")
        # New
        if configsettings.exportFeatures == True:
            #exportthefeatures.main()
            exportthefeatures.mainWithPrefixSets()
        else:
            print("Not exporting the error features because the exportFeatures setting for errors is False.")
    else:
        print("The usePrefixSetTestingAndReporting setting is False.")
        print("Will perform single checks rather than using all of the prefix sets.")
        # New
        if configsettings.useLoganProcessAdditions == True:
            print("Approximating Logan's process additions in code.")
            print("This does not yet perform functions that deal with riding routes.")
            loganprocessadditions.main()
        
        if configsettings.recreateTheRoutes == True:
            time.sleep(25)
            print('Recreating the LRS Routes from the routesSource.')
            createtheroutes.main()
        else:
            print('Skipping route creation.')
            pass
        if configsettings.runDataReviewerChecks == True:
            ### Can't create .rbj from template due to hashed values with unknown algorithm in .rbj files. ###
            ###rbjxmlcreation.main()
            print('Running the Data reviewer checks. This will take a while.')
            print('Seriously though... check back in an hour or so.')
            runthechecks.main()
        else:
            pass
        if configsettings.useRAndHCheck == True:
            print('Running the Roads and Highways Non-Monotonicity check.')
            nonmonorandhcheck.main()
        else:
            pass
        if configsettings.createQCGDB == True:
            qcgdbexport.main()
        else:
            print("Not exporting error features to the QC GDB because the createQCGDB setting value is False.")
        if configsettings.runClassifySelfIntersectingPolylines == True:
            csip_kdot.main()
        else:
            print("Not classifying self-intersecting polylines because the runClassifySelfIntersectingPolylines setting is False.")
        # Need to split this so that it does the feature export only and the reporting happens in a different script.
        if configsettings.exportFeatures == True:
            exportthefeatures.main()
        else:
            print("Not exporting the error features because the exportFeatures setting for errors is False.")
    
    #New
    if configSettings.moveErrorsForEditSupport == True:
        moveerrorsforeditsupport.main()
    else:
        print("configsettings.moveErrorsForEditSupport is not set to True.")
        print("Not updating/moving the error features to the server.")
        print("The existing error featuers will remain instead.")
    
    
    settingsToReportList = ['inputCenterlines', 'routeSourceCreationOption', 'rampReplacementToUse', 'fieldLogicToUse', 'usePrefixSetTestingAndReporting', 'recreateTheRoutes',
        'runDataReviewerChecks', 'useRAndHCheck', 'createQCGDB', 'runClassifySelfIntersectingPolylines', 'exportFeatures']
    print('Full process completed')
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
    print('The completed GDBs can be found in ' + str(configsettings.mainFolder) + '.')


if __name__ == "__main__":
    main()
    #Next steps:
    # Include the Ghost Route detection script.
    # Exclude the routes which are detected to have Ghost Route status.
    
    #Then, recreate the lrs routes and run all of the checks to see how much error reduction has taken place.

else:
    pass
