# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 11:14:47 2020

@author: nmartin <nick.martin@stanfordalumni.org>

The purpose of this module is to extract the 64 individual ensembles for 
precipitation and temperature.

"""
# Copyright and License
"""
Copyright 2020 Nick Martin

This file is part of a collection of scripts and modules in the GitHub
repository https://github.com/nmartin198/wres_risk_analysis, hereafter
`wres_risk_analysis`.

wres_risk_analysis is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# standard imports
import numpy as np
import pandas as pd
import datetime as dt
import os
import pyodbc
import sqlalchemy
import sys
# custom module import
import DBA_DClimComp as DBAD

# module level values for changing
START_DT1 = dt.datetime( 1981, 1, 1, 0, 0, 0 )
END_DT4 = dt.datetime( 2100, 12, 31, 0, 0, 0 )

# grid values and run descriptions. Only for CMIP5
GD_START = 92
GD_END = 92
DS_DESC = "LOCA"
MAX_MODELS = 64

# module level values that might not need to be changed
OUT_DIR = r'D:\CC_Plots'
WD_THRESH = 0.2   # in mm

# standalone execution block
if __name__ == '__main__':
    # first get our SQL connection
    engine = sqlalchemy.create_engine( DBAD.DSN_STRING )
    # get the model definition
    ModelSQL = DBAD.createSQLCMIP5Model()
    ModelDF = pd.read_sql( ModelSQL, engine, index_col=DBAD.FIELDN_ID )
    ModelCols = list( ModelDF.columns )
    NumMods = len( ModelDF )
    if len( ModelCols ) < 1:
        print("Could not acquire model dataframe!!!!")
        sys.exit([-1])
    # end if
    # output the model table
    CFName = "AllModelsTable.pickle"
    ModPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    ModelDF.to_pickle( ModPCKF )
    FirstModel = False
    mCnt = 0
    for jJ in range(1, (NumMods + 1)):
        if mCnt >= MAX_MODELS:
            break
        ModInd = jJ
        # make our joint index
        JntInd = "M%d_%d" % (ModInd, GD_START)
        # now are ready to get our precipitation values
        PreSQL = DBAD.createSQLCMIP5Pre( START_DT1, END_DT4, GD_START, jJ )
        PreDF = pd.read_sql( PreSQL, engine, index_col=DBAD.FIELDN_STRDT, 
                             parse_dates=[DBAD.FIELDN_STRDT] )
        if len( PreDF ) < 1:
            #print("No values for %s" % JntInd)
            continue
        # end if
        print("Model %d" % ModInd)
        PreDF.index.name = DBAD.FIELDN_DT
        PreDF.index = PreDF.index.tz_convert( None )
        # now do the resample 
        MonDF = PreDF.resample( 'MS', axis=0, closed='left', label='left' ).sum()
        AnnDF = PreDF.resample( 'AS', axis=0, closed='left', label='left' ).sum()
        # change the column names
        MonDF.columns = ["Precip_mm"]
        AnnDF.columns = ["Precip_mm"]
        # now make our appends
        PreDF.columns = [JntInd]
        GMonDF = MonDF.copy()
        GMonDF.columns = [JntInd]
        GAnnDF = AnnDF.copy()
        GAnnDF.columns = [JntInd]
        # now check where we are
        if (not FirstModel):
            FirstModel = True
            AllDF = PreDF.copy()
            AllMonDF = GMonDF.copy()
            AllAnnDF = GAnnDF.copy()
        else:
            AllDF = AllDF.merge( PreDF, how='inner', left_index=True, 
                                 right_index=True )
            AllMonDF = AllMonDF.merge( GMonDF, how='inner', 
                                       left_index=True, right_index=True)
            AllAnnDF = AllAnnDF.merge( GAnnDF, how='inner', 
                                       left_index=True, right_index=True)
        # end if
        mCnt += 1
    # end for
    # output
    CFName = "Precip_TS_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    TsPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllDF.to_pickle( TsPCKF )
    CFName = "Precip_AllMonth_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    MonPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllMonDF.to_pickle( MonPCKF )
    CFName = "Precip_AllYears_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    AnnPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllAnnDF.to_pickle( AnnPCKF )
    # done
    
