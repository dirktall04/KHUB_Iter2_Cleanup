#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_fullprocess.py
# Created 2016-12-30
# Updated 2017-01-027 by dirktall04
# Updated 2017-02-06 by dirktall04
# Updated 2017-10-16 by dirktall04

# Run ALL the things!
# To change the location of the inputs/outputs
# please visit/modify datareviewerchecks_config.py

# With the KDOTProcess, ramps are not currently showing up in the output.
# Fix next.

# This process produces a null output for the 10B_X_Routes.gdb\Routes feature class, so
# it is not able to be error checked on its own.

import datetime
import time

import datareviewerchecks_config as configsettings
import datareviewerchecks_routessourcecreation as createtheroutessource
####import datareviewerchecks_kdotprocessimprovements_iter2 as kdotprocesstocreatetheroutesource
import datareviewerchecks_kdotprocessimprovements_iter3 as kdotprocesstocreatetheroutesource
### Can't create from template due to hashed values with unknown algorithm in .rbj files. ###
###import datareviewerchecks_rbjxmlcreation as rbjxmlcreation
# Source dissolve should happen after simplification and flipping, but before ... ghost route detection?
# Means it needs to be inside the kdotprocessimprovements_iter2 script.
###import datareviewerchecks_sourcedissolve as sourcedissolve
import datareviewerchecks_prefixsetgdbcreation as prefixsetgdbcreation
import datareviewerchecks_lrsroutecreation as createtheroutes
import datareviewerchecks_runchecks as runthechecks
import datareviewerchecks_nonmonoroadsandhighways as nonmonorandhcheck
import datareviewerchecks_exportfeatures as exportthefeatures
import datareviewerchecks_qcgdbexport as qcgdbexport
###import datareviewerchecks_grabconflationdata as grabconflationdata
import ClassifySelfIntersectingPolylines_for_KDOT as csip_kdot

startTime = datetime.datetime.now()

def main():
    print('Starting the full process of importing centerlines from ' + str(configsettings.inputCenterlines))
    print('then exporting them as routes to ' + str(configsettings.outputRoutes))
    print('next running the data reviewer checks from ' + str(configsettings.reviewerBatchJob))
    print('and exporting the error features to ' + str(configsettings.errorFeaturesGDB))
    print('at: ' + str(startTime))
    #if configsettings.importNewConflationData == True:
    #    grabconflationdata.main()
    #else:
    #    pass
    if configsettings.routeSourceCreationOption.lower() == 'base':
        print('Creating the routesSource from centerlines & ramps.')
        createtheroutessource.main()
    elif configsettings.routeSourceCreationOption.lower() == 'kdot':
        print("Using KDOT's improvements to create the routesSource from centerlines & ramps.")
        kdotprocesstocreatetheroutesource.main()
    else:
        print("The routeSourceCreationOption is neither 'base' nor 'kdot'. Will not recreate the routeSource.")
        pass
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
        
        
    print('Full process completed')
    completeTime = datetime.datetime.now()
    print('at approximately: ' + str(completeTime))
    durationTime = completeTime - startTime
    print('and taking ' + str(durationTime))
    print('The completed GDBs can be found in ' + str(configsettings.mainFolder) + '.')


if __name__ == "__main__":
    main()
    #Next steps:
    # Include the Ghost Route detection script.
    # Exclude the routes which are detected to have Ghost Route status.
    
    #Then, recreate the lrs routes and run all of the checks to see how much error reduction has taken place.

else:
    pass
