
def KDOTKeyCalculation_NewFieldLogic():
    print("Using the new field logic to calculate the values of the source lrs ID and measure fields.")
    MakeFeatureLayer_management(rampsOutputFullPath, fcAsFeatureLayer)
    # As long as the KDOT_LRS_KEY is not null, calculate from the
    # current fields.
    
    # For the 3rd version:
    '''
    n1FromMeas, n1ToMeas, rampsOutputGDB,
    rampsOutputFC, rampsOutputFullPath, dissolveErrorsFile,
    dissolvedFlippedOutput, dissolveOutFC, useNewFieldLogic, KDOTRouteId,
    KDOTMeasBeg, KDOTMeasEnd
    # Send the data to the source output fields with the correct decimal formatting.
    expressionText1 = 'float("{0:.3f}".format(!' + str(KDOTMeasBeg) + '!))'
    CalculateField_management(fcAsFeatureLayerForMeasuring, n1FromMeas, expressionText1, "PYTHON_9.3")
    expressionText2 = 'float("{0:.3f}".format(!' + str(KDOTMeasEnd) + '!))'
    CalculateField_management(fcAsFeatureLayerForMeasuring, n1ToMeas, expressionText2, "PYTHON_9.3")
    # Reverse the data flow to correct decimals in the original fields.
    expressionText3 = 'float("{0:.3f}".format(!' + str(n1FromMeas) + '!))'
    CalculateField_management(fcAsFeatureLayerForMeasuring, KDOTMeasBeg, expressionText3, "PYTHON_9.3")
    expressionText4 = 'float("{0:.3f}".format(!' + str(n1ToMeas) + '!))'
    CalculateField_management(fcAsFeatureLayerForMeasuring, KDOTMeasEnd, expressionText4, "PYTHON_9.3")
    '''
    selectionQuery = """ "KDOT_LRS_KEY" IS NOT NULL """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = KDOT_LRS_KEY
    CalculateField_management (fcAsFeatureLayer, n1RouteId, "!" + str(KDOTRouteId) + "!", "PYTHON_9.3")
    # SourceFromMeasure = county_log_begin
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!" + str(KDOTMeasBeg) + "!", "PYTHON_9.3")
    # SourceToMeasure = county_log_end
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!" + str(KDOTMeasEnd) + "!", "PYTHON_9.3")
    selectionQuery = """ KDOT_LRS_KEY IS NOT NULL AND county_log_begin IS NULL AND county_log_end IS NULL AND (COUNTY_BEGIN_MP IS NOT NULL OR COUNTY_END_MP IS NOT NULL) """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    countResult = GetCount_management(fcAsFeatureLayer)
    intCount = int(countResult.getOutput(0))
    print("After the new selection query to deal with the fact that State routes did not have their begin and end measure populated correctly, " +
        str(intCount) + " were selected.")
    # SourceFromMeasure = COUNTY_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!COUNTY_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = COUNTY_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!COUNTY_END_MP!", "PYTHON_9.3")


def KDOTKeyCalculation_Update():
    #FieldPopulation with selections and FieldCalculate:
    
    MakeFeatureLayer_management(rampsOutputFullPath, fcAsFeatureLayer)
    
    # This doesn't work well. Don't call it until it's been worked on more.
    ParseLRS_ROUTE_PREFIX(fcAsFeatureLayer)
    
    tempDesc = Describe(fcAsFeatureLayer)
    print("Calculating values for new LRS and measure fields in " + returnFeatureClass(tempDesc.catalogPath) + ".")
    try:
        del tempDesc
    except:
        pass
    
    # A better solution than parsing the LRS ROUTE PREFIX from the LRSKEY
    # and then relying on the LRS ROUTE PREFIX to make decision about where
    # to pull the LRSKEY from would be to just start at the LRSKEY locations...
    
    # -------------------- Start of old calculations. ----------------------- #
    # Select LRS_ROUTE_PREFIX IN ('I', 'U', 'K')
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('I', 'U', 'K') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = StateKey1
    CalculateField_management (fcAsFeatureLayer, n1RouteId, "!StateKey1!", "PYTHON_9.3")
    # SourceFromMeasure = STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!STATE_END_MP!", "PYTHON_9.3")
    
    # Select LRS_ROUTE_PREFIX NOT IN ('I', 'U', 'K') AND LRSKEY IS NOT NULL
    selectionQuery = """ "LRS_ROUTE_PREFIX" NOT IN ('I', 'U', 'K') AND "LRSKEY" IS NOT NULL """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = LRSKEY
    CalculateField_management (fcAsFeatureLayer, n1RouteId,  "!LRSKEY!", "PYTHON_9.3")
    # SourceFromMeasure = NON_STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!NON_STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = NON_STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!NON_STATE_END_MP!", "PYTHON_9.3")
    
    # Select LRS_ROUTE_PREFIX IN ('C') AND LRSKEY NOT LIKE '%W0'
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('C') AND "LRSKEY" NOT LIKE '%W0' """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteID = left([LRSKEY], 11) & "W0"
    # This is the VB version.
    # Python version would be calcExpression1 = "!LRSKEY![0:11] + 'W0'"
    calcExpression1 = 'Left([LRSKEY] ,11 ) & "W0"'
    CalculateField_management(fcAsFeatureLayer, n1RouteId, calcExpression1, "VB")
    
    # --------------------- End of old calculations. ------------------------ #
    # -------------------- Start of new calculations. ----------------------- #
    # Local system LRSKeys should go first, before Ramps, but the local system LRSKeys
    # need to be calculated unique prior to that and the code for that hasn't been tested.
    
    # Select where Ramps_LRSKey is not null or '' or ' '.
    selectionQuery = """ "Ramps_LRSKey" IS NOT NULL AND "Ramps_LRSKey" NOT IN ('', ' ') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = Ramps_LRSKey
    CalculateField_management (fcAsFeatureLayer, n1RouteId,  "!Ramps_LRSKey!", "PYTHON_9.3")
    # SourceFromMeasure = NON_STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!NON_STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = NON_STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!NON_STATE_END_MP!", "PYTHON_9.3")
    
    # Select where Non_State_System_LRSKey is not null or '' or ' '.
    selectionQuery = """ "Non_State_System_LRSKey" IS NOT NULL AND "Non_State_System_LRSKey" NOT IN ('', ' ') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = Non_State_System_LRSKey
    CalculateField_management (fcAsFeatureLayer, n1RouteId,  "!Non_State_System_LRSKey!", "PYTHON_9.3")
    # SourceFromMeasure = NON_STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!NON_STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = NON_STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!NON_STATE_END_MP!", "PYTHON_9.3")
    
    # Would go last as it takes precedence over any other keys, but only needed for State Measure Network System.
    '''
    # Select where State_System_LRSKey is not null or '' or ' '
    selectionQuery = """ "State_System_LRSKey" IS NOT NULL AND "State_System_LRSKey" NOT IN ('', ' ') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = State_System_LRSKey
    CalculateField_management (fcAsFeatureLayer, n1RouteId, "!State_System_LRSKey!", "PYTHON_9.3")
    # SourceFromMeasure = STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!STATE_END_MP!", "PYTHON_9.3")
    '''
    
    # Should have better information than the other fields.
    # Select where CountyKey1 is not null or '' or ' '.
    selectionQuery = """ "CountyKey1" IS NOT NULL AND "CountyKey1" NOT IN ('', ' ') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = Non_State_System_LRSKey
    CalculateField_management (fcAsFeatureLayer, n1RouteId,  "!CountyKey1!", "PYTHON_9.3")
    # SourceFromMeasure = NON_STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!F_CNTY_1!", "PYTHON_9.3")
    # SourceToMeasure = NON_STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!T_CNTY_1!", "PYTHON_9.3")
    
    # Get a count of the features that now have a non-null LRS key in the
    # n1RouteId field along with non-null measures in the n1FromMeas and n1ToMeas fields.
    selectionQuery = ''' "''' + n1RouteId + '''" IS NOT NULL AND "''' + n1RouteId + '''" NOT IN ('', ' ') '''
    selectionQuery += ''' AND "''' + n1FromMeas + '''" IS NOT NULL AND ''' 
    selectionQuery += ''' "''' + n1ToMeas + '''" IS NOT NULL'''
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    
    countResult = GetCount_management(fcAsFeatureLayer)
    intCount = int(countResult.getOutput(0))
    print('Counted ' + str(intCount) + ' features with populated ' + str(n1RouteId) + ', ' +
        str(n1FromMeas) +', and ' +str(n1ToMeas) + '.')
    
    SelectLayerByAttribute_management(fcAsFeatureLayer, "CLEAR_SELECTION")
    

# Used for initially parsing the LRSKeys into component parts a while back.

def ParseLRS_ROUTE_PREFIX(passedFeatureLayer):
    # If LRS_ROUTE_PREFIX doesn't exist, add it.
    # Then, populate it.
    
    lrsPrefixField = 'LRS_ROUTE_PREFIX'
    
    # Domains mess up SQL value testing. Instead of looking for a column to be
    # equal to an 'X' you would be looking for it to be equal to a 7 or an 8.
    # But, whereas the letter is always the same, it might not always be the
    # same number and that's bad. -- Possibly able to get around this by
    # knowing the domain's name and doing a domain lookup for the values that
    # you're interested, but that method is not yet tested.
    try:
        RemoveDomainFromField_management(passedFeatureLayer, lrsPrefixField)
    except:
        print("Could not remove the domain from the '" + str(lrsPrefixField) + "' column.")
        print("The domain or field might not have existed previously.")
    
    # Test for the new fields. If they're not there yet,
    # then add them before the rest of the calculations.
    tempDesc = Describe(passedFeatureLayer)
    print("Parsing the LRS values in  " + returnFeatureClass(tempDesc.catalogPath) + " to figure out what the LRS_ROUTE_PREFIX should be.")
    currentFieldObjects = tempDesc.fields
    try:
        del tempDesc
    except:
        pass
    
    currentFieldNames = [x.name for x in currentFieldObjects]
    
    print("currentFieldNames:")
    for fieldNameItem in currentFieldNames:
        print fieldNameItem
    
    fieldsNeeded = [lrsPrefixField]
    fieldsToAdd = [x for x in fieldsNeeded if x not in currentFieldNames]
    
    if lrsPrefixField in fieldsToAdd:
        AddField_management(passedFeatureLayer, lrsPrefixField, "TEXT", "", "", 1, "LRS_ROUTE_PREFIX", nullable)
    else:
        pass
    
    # Need to reparse the LRSKEY with the current LRS_ROUTE_PREFIX value (if it isn't null or empty)
    # prior to doing all of this or you will overwrite the changes made by Tim's manual edits
    # to the LRS_ROUTE_PREFIX field.
    
    if 'State_System_LRSKEY' in currentFieldNames:
        #Parse from State_System_LRSKEY.
        # LRS_ROUTE_PREFIX = "I"
        selectionQuery1 = '''State_System_LRSKEY LIKE '___I%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'I'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "U"
        selectionQuery1 = '''State_System_LRSKEY LIKE '___U%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'U'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "K"
        selectionQuery1 = '''State_System_LRSKEY LIKE '___K%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'K'", "PYTHON_9.3")
        
    elif 'Non_State_System_LRSKEY' in currentFieldNames:
        #Parse from Non_State_System_LRSKEY.
        # LRS_ROUTE_PREFIX = "C"
        selectionQuery1 = '''Non_State_System_LRSKEY LIKE '___C%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'C'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "R"
        selectionQuery1 = '''Non_State_System_LRSKEY LIKE '___R%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'R'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "M"
        selectionQuery1 = '''Non_State_System_LRSKEY LIKE '___M%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'M'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "L"
        selectionQuery1 = '''Non_State_System_LRSKEY LIKE '___L%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'L'", "PYTHON_9.3")
        
    elif 'Ramps_LRSKEY' in currentFieldNames:
        selectionQuery1 = '''Ramps_LRSKEY LIKE '___X%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        # LRS_ROUTE_PREFIX = "X"
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'X'", "PYTHON_9.3")
    
    elif 'SourceRouteId' in currentFieldNames:
        #Parse from SourceRouteId instead of the other fields.
        # LRS_ROUTE_PREFIX = "I"
        selectionQuery1 = '''SourceRouteId LIKE 'I%' OR SourceRouteId LIKE '___I%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'I'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "U"
        selectionQuery1 = '''SourceRouteId LIKE 'U%' OR SourceRouteId LIKE '___U%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'U'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "K"
        selectionQuery1 = '''SourceRouteId LIKE 'K%' OR SourceRouteId LIKE '___K%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'K'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "C"
        selectionQuery1 = '''SourceRouteId LIKE '___C%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'C'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "R"
        selectionQuery1 = '''SourceRouteId LIKE '___R%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'R'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "M"
        selectionQuery1 = '''SourceRouteId LIKE '___M%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'M'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "X"
        selectionQuery1 = '''SourceRouteId LIKE '___X%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'X'", "PYTHON_9.3")
        
        # LRS_ROUTE_PREFIX = "L"
        selectionQuery1 = '''SourceRouteId LIKE '___L%' '''
        SelectLayerByAttribute_management(passedFeatureLayer, "NEW_SELECTION", selectionQuery1)
        CalculateField_management (passedFeatureLayer, lrsPrefixField, "'L'", "PYTHON_9.3")
        
    try:
        AddDomainToField_management(passedFeatureLayer, "LRS_ROUTE_PREFIX", "LRS_ROUTES")
    except:
        print("Could not add the domain to the 'LRS_ROUTE_PREFIX' column.")
        print("The domain or field might not have existed previously.")


def KDOTKeyCalculation():
    # Using the new method from Kyle.
    #FieldPopulation with selections and FieldCalculate:
    
    # Get the code from Kyle's github - RHUG repository
    # to calibrate the State Highway measures.
    
    MakeFeatureLayer_management(routesSourceIntermediate, fcAsFeatureLayer)
    
    try:
        RemoveDomainFromField_management(fcAsFeatureLayer, "LRS_ROUTE_PREFIX")
    except:
        print("Could not remove the domain from the 'LRS_ROUTE_PREFIX' column.")
        print("It might not have existed previously.")
    
    # Test for the new fields. If they're not there yet,
    # then add them before the rest of the calculations.
    tempDesc = Describe(fcAsFeatureLayer)
    print("Calculating values for new LRS and measure fields in " + returnFeatureClass(tempDesc.catalogPath) + ".")
    currentFields = tempDesc.fields
    try:
        del tempDesc
    except:
        pass
    
    fieldsNeeded = ['FromDate2', 'ToDate2', 'COUNTYKEY2', 'STATEKEY2']
    fieldsToAdd = [x for x in fieldsNeeded if x not in currentFields]
    
    if 'FromDate2' in fieldsToAdd:
        AddField_management(fcAsFeatureLayer, "FromDate2", "DATE", "", "", "", "FromDate2", nullable)
    else:
        pass
    
    if 'ToDate2' in fieldsToAdd:
        AddField_management(fcAsFeatureLayer, "ToDate2", "DATE", "", "", "", "ToDate2", nullable)
    else:
        pass
    
    if 'COUNTYKEY2' in fieldsToAdd:
        AddField_management(fcAsFeatureLayer, "COUNTYKEY2", "TEXT", "", "", 50, "COUNTYKEY2", nullable)
    else:
        pass
    
    if 'STATEKEY2' in fieldsToAdd:
        AddField_management(fcAsFeatureLayer, "STATEKEY2", "TEXT", "", "", 50, "STATEKEY2", nullable)
    else:
        pass
    
    ###-- For the current network keys to LRS Routes for Network 1 (Source). --###
    # Select LRS_ROUTE_PREFIX IN ('I', 'U', 'K')
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('I', 'U', 'K') """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = StateKey1
    CalculateField_management (fcAsFeatureLayer, n1RouteId, "!StateKey1!", "PYTHON_9.3")
    # SourceFromMeasure = STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!STATE_END_MP!", "PYTHON_9.3")
    
    # Select LRS_ROUTE_PREFIX NOT IN ('I', 'U', 'K') AND LRSKEY IS NOT NULL
    selectionQuery = """ "LRS_ROUTE_PREFIX" NOT IN ('I', 'U', 'K') AND "LRSKEY" IS NOT NULL """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteId = LRSKEY
    CalculateField_management (fcAsFeatureLayer, n1RouteId,  "!LRSKEY!", "PYTHON_9.3")
    # SourceFromMeasure = NON_STATE_BEGIN_MP
    CalculateField_management (fcAsFeatureLayer, n1FromMeas, "!NON_STATE_BEGIN_MP!", "PYTHON_9.3")
    # SourceToMeasure = NON_STATE_END_MP
    CalculateField_management (fcAsFeatureLayer, n1ToMeas, "!NON_STATE_END_MP!", "PYTHON_9.3")
    
    # Select LRS_ROUTE_PREFIX IN ('C') AND LRSKEY NOT LIKE '%W0'
    selectionQuery = """ "LRS_ROUTE_PREFIX" IN ('C') AND "LRSKEY" NOT LIKE '%W0' """
    SelectLayerByAttribute_management(fcAsFeatureLayer, "NEW_SELECTION", selectionQuery)
    # SourceRouteID = left([LRSKEY], 11) & "W0"
    # This is the VB version.
    # Python version would be calcExpression1 = "!LRSKEY![0:11] + 'W0'"
    calcExpression1 = 'Left([LRSKEY] ,11 ) & "W0"'
    CalculateField_management(fcAsFeatureLayer, n1RouteId, calcExpression1, "VB")
    
    ###-- For the networks that will be LRM->LRM'd onto. --###    
    # Negatively numbered statements do preprocessing of the Keys needed to
    # set parsing information for the positively numbered statements to follow.
    ##--------------------Start of Parsing/Precalculation--------------------##
    #-1
    selectionQuery = '''"State_System_LRSKey" IS NOT NULL AND "KDOT_LRS_KEY" IS NULL'''
    setExpression = "!State_System_LRSKey!"
    CalculateField_management(fcAsFeatureLayer, "KDOT_LRS_KEY", setExpression, "PYTHON_9.3")
    
    #-2
    selectionQuery = '''"Non_State_System_LRSKey" IS NOT NULL AND "KDOT_LRS_KEY" IS NULL'''
    setExpression = "!Non_State_System_LRSKey!"
    CalculateField_management(fcAsFeatureLayer, "KDOT_LRS_KEY", setExpression, "PYTHON_9.3")
    
    #-3
    selectionQuery = '''"KDOT_LRS_KEY" IS NULL AND "Non_State_System_LRSKey" IS NULL AND "RAMPS_LRSKEY" IS NOT NULL'''
    setExpression = "!RAMPS_LRSKEY!"
    CalculateField_management(fcAsFeatureLayer, "KDOT_LRS_KEY", setExpression, "PYTHON_9.3")
    
    #-4
    selectionQuery = '''"LRS_ROUTE_PREFIX" IS NULL'''
    setExpression = "str(!RAMPS_LRSKEY!)[4:5]"
    CalculateField_management(fcAsFeatureLayer, "KDOT_LRS_KEY", setExpression, "PYTHON_9.3")
    
    #-5 -- Parse the fields for STATE HIGHWAY SYSTEM
    # Use an update cursor to set several fields at once:
    updateFields = ["KDOT_LRS_KEY", "LRS_COUNTY_PRE", "LRS_ROUTE_NUM", "LRS_ROUTE_NUM1", "LRS_ROUTE_SUFFIX", "LRS_DIRECTION", "LRS_SUBCLASS", "LRS_ADMO", "LRS_UNIQUE_IDENT", "LRS_UNIQUE_IDENT1"]
    selectionQuery = '''"LRS_ROUTE_PREFIX" in ('I', 'U', 'K')'''
    newCursor = daUpdateCursor(fcAsFeatureLayer, updateFields, selectionQuery)
    for cursorRow in newCursor:
        editRow = list(cursorRow)
        editRow[1] = editRow[0][0:3]
        editRow[2] = editRow[0][4:9]
        editRow[3] = editRow[0][4:9]
        editRow[4] = editRow[0][10:11]
        editRow[5] = editRow[0][13:15]
        editRow[6] = None
        editRow[7] = None
        editRow[8] = editRow[0][11:12]
        editRow[9] = editRow[0][11:12]
        newCursor.updateRow(editRow)
    try:
        del newCursor
    except:
        pass
    
    #-6 -- Parse the fields for NON_STATE_HIGHWAYS_URBAN_CLASSIFIEDS
    ### - Do something separately to --UPDATE THE COUNTY NUMBER IN LRS_COUNTY_PRE BY SPATIAL LOCATION - ###
    # Use an update cursor to set several fields at once:
    updateFields = ["KDOT_LRS_KEY", "LRS_URBAN_PRE", "LRS_ROUTE_NUM", "LRS_ROUTE_NUM1", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_UNIQUE_IDENT1", "LRS_ADMO", "LRS_SUBCLASS", "FMEAS", "TMEAS", "NON_STATE_BEGIN_MP", "NON_STATE_END_MP"]
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'C' AND FMEAS IS NULL AND TMEAS IS NULL'''
    newCursor = daUpdateCursor(fcAsFeatureLayer, updateFields, selectionQuery)
    for cursorRow in newCursor:
        editRow = list(cursorRow)
        editRow[1] = editRow[0][0:3]
        editRow[2] = editRow[0][4:9]
        editRow[3] = editRow[0][4:9]
        editRow[4] = editRow[0][10:11]
        editRow[5] = editRow[0][11:12]
        editRow[6] = '0' + editRow[0][13:14]
        editRow[7] = editRow[0][14:15]
        editRow[8] = editRow[10]
        editRow[9] = editRow[11]
        newCursor.updateRow(editRow)
    try:
        del newCursor
    except:
        pass
    
    #-7 Parse the fields for NON_STATE_HIGHWAYS Rural Secondary
    # Use an update cursor to set several fields at once:
    updateFields = ["KDOT_LRS_KEY", "LRS_COUNTY_PRE", "LRS_ROUTE_NUM", "LRS_ROUTE_NUM1", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_UNIQUE_IDENT1", "LRS_ADMO", "LRS_SUBCLASS", "FMEAS", "TMEAS", "NON_STATE_BEGIN_MP", "NON_STATE_END_MP"]
    selectionQuery = '''"LRS_ROUTE_PREFIX" in ('R', 'M') AND FMEAS IS NULL AND TMEAS IS NULL'''
    newCursor = daUpdateCursor(fcAsFeatureLayer, updateFields, selectionQuery)
    for cursorRow in newCursor:
        editRow = list(cursorRow)
        editRow[1] = editRow[0][0:3]
        editRow[2] = editRow[0][4:9]
        editRow[3] = editRow[0][4:9]
        editRow[4] = editRow[0][10:11]
        editRow[5] = editRow[0][11:12]
        editRow[6] = '0' + editRow[0][13:14]
        editRow[7] = editRow[0][14:15]
        editRow[8] = editRow[10]
        editRow[9] = editRow[11]
        newCursor.updateRow(editRow)
    try:
        del newCursor
    except:
        pass
    
    #-8 Parse the fields for NON_STATE_HIGHWAYS Local Roads
    # Use an update cursor to set several fields at once:
    updateFields = ["KDOT_LRS_KEY", "LRS_COUNTY_PRE", "LRS_ROUTE_NUM", "LRS_ROUTE_NUM1", "LRS_ROUTE_SUFFIX", "LRS_UNIQUE_IDENT", "LRS_UNIQUE_IDENT1", "LRS_ADMO", "LRS_SUBCLASS", "FMEAS", "TMEAS", "NON_STATE_BEGIN_MP", "NON_STATE_END_MP"]
    selectionQuery = '''"LRS_ROUTE_PREFIX" in ('L') AND FMEAS IS NULL AND TMEAS IS NULL'''
    newCursor = daUpdateCursor(fcAsFeatureLayer, updateFields, selectionQuery)
    for cursorRow in newCursor:
        editRow = list(cursorRow)
        editRow[1] = editRow[0][0:3]
        editRow[2] = editRow[0][4:9]
        editRow[3] = editRow[0][4:9]
        editRow[4] = editRow[0][10:11]
        editRow[5] = editRow[0][11:12]
        editRow[6] = '0' + editRow[0][13:14]
        editRow[7] = editRow[0][14:15]
        editRow[8] = editRow[10]
        editRow[9] = editRow[11]
        newCursor.updateRow(editRow)
    try:
        del newCursor
    except:
        pass
    
    #-9 Parse the fields for RAMPS
    # Use an update cursor to set several fields at once:
    updateFields = ["KDOT_LRS_KEY", "LRS_COUNTY_PRE", "LRS_ROUTE_NUM", "LRS_ROUTE_NUM1", "LRS_UNIQUE_IDENT", "LRS_UNIQUE_IDENT1", "LRS_ADMO", "FMEAS"]
    selectionQuery = '''"LRS_ROUTE_PREFIX" in ('X') AND FMEAS IS NULL AND TMEAS IS NULL'''
    newCursor = daUpdateCursor(fcAsFeatureLayer, updateFields, selectionQuery)
    for cursorRow in newCursor:
        editRow = list(cursorRow)
        editRow[1] = editRow[0][0:3]
        editRow[2] = editRow[0][4:9]
        editRow[3] = editRow[0][4:9]
        editRow[4] = editRow[0][9:11]
        editRow[5] = editRow[0][9:11]
        editRow[6] = editRow[0][11:12]
        editRow[7] = 0
        newCursor.updateRow(editRow)
    try:
        del newCursor
    except:
        pass
    
    #-10
    selectionQuery = '''"LRS_PRIMARY_DIR" IS NULL'''
    setExpression = "0"
    CalculateField_management(fcAsFeatureLayer, "LRS_PRIMARY_DIR", setExpression, "PYTHON_9.3")
    
    #-11
    selectionQuery = '''"FromDate" IS NULL'''
    setExpression = "'1827-01-01'" ## Will have to check this.
    CalculateField_management(fcAsFeatureLayer, "FromDate2", setExpression, "PYTHON_9.3")
    
    #-12
    selectionQuery = '''"STATUS" IN ('Not Built', 'NOT BUILT')'''
    setExpression = "'2020-01-01'" ## Will have to check this.
    CalculateField_management(fcAsFeatureLayer, "FromDate2", setExpression, "PYTHON_9.3")
    
    #-13
    selectionQuery = '''"STATUS" IN ('CLOSED', 'Closed')'''
    setExpression = "'2014-01-01'" ## Will have to check this.
    CalculateField_management(fcAsFeatureLayer, "ToDate2", setExpression, "PYTHON_9.3")
    
    #-14
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'L' AND "RouteID" IS NULL'''
    setExpression = "!LRS_COUNTY_PRE! + !LRS_ROUTE_PREFIX! + !LRS_ROUTE_NUM1! + !LRS_ROUTE_SUFFIX! + !LRS_UNIQUE_IDENT1! + !LRS_PRIMARY_DIR!"
    CalculateField_management(fcAsFeatureLayer, "RouteID", setExpression, "PYTHON_9.3")
    
    #-15
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'X' AND "RouteID" IS NULL'''
    setExpression = "!LRS_COUNTY_PRE! + !LRS_ROUTE_PREFIX! + !LRS_ROUTE_NUM1! + !LRS_UNIQUE_IDENT1! + !LRS_PRIMARY_DIR!"
    CalculateField_management(fcAsFeatureLayer, "RouteID", setExpression, "PYTHON_9.3")
    
    #-16
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'C' AND "LRS_PRIMARY_DIR" IS NULL'''
    setExpression = "0"
    CalculateField_management(fcAsFeatureLayer, "LRS_PRIMARY_DIR", setExpression, "PYTHON_9.3")
    ##---------------------End of Parsing/Precalculation---------------------##
    
    # This (the 2nd email version) should entirely supersede the contents of the first email
    # version, but the attachment content from the first email still runs prior to this,
    # hence the negatively numbered calculations above.
    
    ##--------------------------Start of County Key2-------------------------##
    #1
    #/*  set all unique Identifiers to 00 if they werent calculated from the LRS Key   */
    selectionQuery = '''"LRS_UNIQUE_IDENT1" IS NULL'''
    setExpression = "'00'"
    CalculateField_management(fcAsFeatureLayer, "LRS_UNIQUE_IDENT1", setExpression, "PYTHON_9.3")
    
    #2
    #/*  Calculate the County key field for centerlines identified as Ramps   */
    #/*  Assume all route suffix codes for ramps are 0   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'X' '''
    setExpression = "!LRS_COUNTY_PRE! + '4' + !LRS_ROUTE_NUM! + '0' + !KDOT_DIRECTION_CALC! + !LRS_UNIQUE_IDENT1!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #3
    #/*  Calculate the County key field for rural major, minor, and urban collector   */
    #/*  Assume all route suffix codes for these classified routes are 0   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" in ('R', 'M', 'C')'''
    setExpression = "!LRS_COUNTY_PRE! + '5' + !LRS_ROUTE_NUM! + '0' + !KDOT_DIRECTION_CALC! + !LRS_UNIQUE_IDENT1!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #4
    #/*  Calculate the County key field Kansas State Highwayas without a unique identifier  */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'K' AND "LRS_UNIQUE_IDENT1" = '00' '''
    setExpression = "!LRS_COUNTY_PRE! + '3' + !LRS_ROUTE_NUM! + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #5
    #/*  Calculate the County key field Kansas State Highways with a unique identifier */
    #/*  Assume State Key unique identifier is the same as the county route unique identifier   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'K' AND "LRS_UNIQUE_IDENT1" <> '00'  '''
    setExpression = "!LRS_COUNTY_PRE! + '3' + !LRS_ROUTE_NUM! + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC! + !LRS_UNIQUE_IDENT1!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #6
    #/*  Calculate the County key field for US Numbered Routes with no unique identifier   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'U' AND "LRS_UNIQUE_IDENT1" = '00' '''
    setExpression = "!LRS_COUNTY_PRE! + '2' + !LRS_ROUTE_NUM! + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #7
    #/*  Calculate the County key field for US Numbered Routes with unique identifier   */
    #/*  Assume State Key unique identifier is the same as the county route unique identifier   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'U' AND "LRS_UNIQUE_IDENT1" <> '00' '''
    setExpression = "!LRS_COUNTY_PRE! + '2' + !LRS_ROUTE_NUM! + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC! + !LRS_UNIQUE_IDENT1!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    
    #8
    #/*  Calculate the County key field for Interstate Highways */
    #/*  Assume there are no unique identifiers on these */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'I' '''
    setExpression = "!LRS_COUNTY_PRE! + '1' + !LRS_ROUTE_NUM! + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "COUNTYKEY2", setExpression, "PYTHON_9.3")
    ##---------------------------End of County Key2--------------------------##
    
    ##---------------------------Start of State Key2-------------------------##
    #9
    #/*  Calculate the State Key field for Kansas State Highways with Unique Identifiers */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'K' AND "LRS_UNIQUE_IDENT1" <> '00' '''
    setExpression = "'3' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC! + str(!LRS_UNIQUE_IDENT1!)[1]"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    
    #10
    #/*  Calculate the State Key field for Kansas State Highways without Unique Identifiers */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'K' AND "LRS_UNIQUE_IDENT1" = '00' '''
    setExpression = "'3' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    
    #11
    #/*  Calculate the State Key field for Kansas State Highways with Unique Identifiers */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'U' AND "LRS_UNIQUE_IDENT1" <> '00' '''
    setExpression = "'2' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC! + str(!LRS_UNIQUE_IDENT1!)[1]"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    
    #12
    #/*  Calculate the State key field for US Numbered Routes without unique identifiers   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'U' AND "LRS_UNIQUE_IDENT1" = '00' '''
    setExpression = "'2' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    
    #13
    #/*  Calculate the State key field for US Numbered Routes with unique identifiers   */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'I' AND "LRS_UNIQUE_IDENT1" <> '00' '''
    setExpression = "'1' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC! + str(!LRS_UNIQUE_IDENT1!)[1]"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    
    #14
    #/*  Calculate the County key field for Interstate Highways */
    #/*  Assume there are no unique identifiers on these */
    selectionQuery = '''"LRS_ROUTE_PREFIX" = 'I' '''
    setExpression = "'1' + str(!LRS_ROUTE_NUM!)[2:5] + !LRS_ROUTE_SUFFIX! + !KDOT_DIRECTION_CALC!"
    CalculateField_management(fcAsFeatureLayer, "STATEKEY2", setExpression, "PYTHON_9.3")
    ##----------------------------End of State Key2--------------------------##
    print("KDOT Key Calculation Complete.")

