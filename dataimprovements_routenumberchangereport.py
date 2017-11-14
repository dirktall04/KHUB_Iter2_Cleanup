#!usr/bin/env python
# -*- coding:utf-8 -*-
# dataimprovements_routenumberchangereport.py
# Created by dirktall04 on 2017-06-28
# Updated by dirktall04 on 2017-06-29

# Need to give Pavement Management System a listing of the C routes which
# changed.
# It may also be useful to know the M routes which changed for other
# systems, so make a similar report for that as well.
# Should include the source LRS Key, begin MP,  end MP and the
# target LRS Key for that segment.

# Read the output County_ARNOLD feature class's data.
# Get the C Routes
# and the M Routes

# Create a new temp table and fill it will the info from the C Routes
# but only include the Source LRS Key, begin MP, end MP and target LRS Key.

# For the R routes, create a new temp table and fill it will the info
# extracted above. Then, export the table as a pdf
# but only include the Source LRS Key, begin MP, end MP and target LRS Key.