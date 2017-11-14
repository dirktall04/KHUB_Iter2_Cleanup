#!/usr/bin/env python
# -*- coding:utf-8 -*-
# datareviewerchecks_pushmanualeditsupportinfotoserver.py
# Created by dirktall04 on 2017-11-13

from config import (prefixsetgdbsettings, thingstocopy)

#conflation data path
conflationdatatouse = r'\\Database Connections\Conflation2012_sde.sde\Conflation.SDE.NG911\Conflation.SDE.AllRoadCenterlines_ManualEdit'
# base locations to push the data to
placeToCopyDataTo = r'\\Database Connections\Conflation2012_sde.sde\Conflation.SDE.NG911'
copyFeaturesList = []


# The sde that you're pushing the data to needs to already exist. Don't want to create it here.
# If there is a problem with the sde, then quit with an error message.

