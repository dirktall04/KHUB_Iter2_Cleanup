#!/usr/bin/env python
#-*- coding:utf-8 -*-
# datareviewerchecks_singlepart_export.py
# Created 2017-09-05 by Dirk Talley

# This script exports the output from the data reviewer
# process to singlepart feature classes that are easier
# to work since they don't require the data reviewer
# extension's clunky tools to use effectivelys.

# from datareviewerchecks_config import (mainFolder, reviewerExportGDB, dataReviewerChecksGDB)

# Create a join between the REVLINETABLE and REVMAINTABLE
# Where the REVLINETABLE's LINKID matches the REVMAINTABLE's RECORDID.
# Then, export the result to a new feature class.
# Next, create a singlepart version of that feature class.

# Create a join between the REVPOINTTABLE and REVMAINTABLE
# Where the REVPOINTTABLE's LINKID matches the REVMAINTABLE's RECORDID.
# Then, export the result to a new feature class.
# Next, create a singlepart version of that feature class.

import os
from arcpy import (Copy_management, CreateFileGDB_management, Delete_management, Exists,
                    JoinField_management, MultipartToSinglepart_management)
from arcpy.da import (SearchCursor as daSearchCursor)

from datareviewerchecks_config import(mainFolder, reviewerSessionGDB, nonMonotonicOutputGDB, errorFeaturesQCGDB, errorFeaturesQCGDBName)

rev_table_main = os.path.join(reviewerSessionGDB, "REVTABLEMAIN")
rev_table_point = os.path.join(reviewerSessionGDB, "REVTABLEPOINT")
rev_table_line = os.path.join(reviewerSessionGDB, "REVTABLELINE")

multipart_point_errors = os.path.join(errorFeaturesQCGDB, "All_Point_Errors_Multipart")
multipart_line_errors = os.path.join(errorFeaturesQCGDB, "All_Line_Errors_Multipart")

single_part_point_errors = os.path.join(errorFeaturesQCGDB, "All_Point_Errors_Single_Part")
single_part_line_errors = os.path.join(errorFeaturesQCGDB, "All_Line_Errors_Single_Part")

rev_join_field1 = 'LINKID'
rev_join_field2 = 'RECORDID'


# Copy the data from the rev_table_point and rev_table_line feature classes into the
# output location, then add the fields from the rev_table_main that match up.

# Next, take the features from the output locations and split them into single
# parts to get the final data product for the points and the lines.

def setupQCGDB():
    print("Setting up the QC GDB.")
    if (Exists(errorFeaturesQCGDB)):
        Delete_management(errorFeaturesQCGDB)
    else:
        pass
    CreateFileGDB_management(mainFolder, errorFeaturesQCGDBName)


def pointErrorsExportToQCGDB():
    print("Exporting the data reviewer points.")
    if (Exists(multipart_point_errors)):
        try:
            Delete_management(multipart_point_errors)
        except:
            print("The feature class at: " + str(multipart_point_errors) + " already exists and could not be deleted.")
    else:
        pass
    if (Exists(single_part_point_errors)):
        try:
            Delete_management(single_part_point_errors)
        except:
            print("The feature class at: " + str(single_part_point_errors) + " already exists and could not be deleted.")
    else:
        pass
    Copy_management(rev_table_point, multipart_point_errors)
    JoinField_management(multipart_point_errors, rev_join_field1, rev_table_main, rev_join_field2)
    MultipartToSinglepart_management(multipart_point_errors, single_part_point_errors)


def lineErrorsExportToQCGDB():
    print("Exporting the data reviewer lines.")
    if (Exists(multipart_line_errors)):
        try:
            Delete_management(multipart_line_errors)
        except:
            print("The feature class at: " + str(multipart_line_errors) + " already exists and could not be deleted.")
    else:
        pass
    if (Exists(single_part_line_errors)):
        try:
            Delete_management(single_part_line_errors)
        except:
            print("The feature class at: " + str(single_part_line_errors) + " already exists and could not be deleted.")
    else:
        pass
    Copy_management(rev_table_line, multipart_line_errors)
    JoinField_management(multipart_line_errors, rev_join_field1, rev_table_main, rev_join_field2)
    MultipartToSinglepart_management(multipart_line_errors, single_part_line_errors)


def main():
    setupQCGDB()
    pointErrorsExportToQCGDB()
    lineErrorsExportToQCGDB()


if __name__ == '__main__':
    main()
else:
    pass