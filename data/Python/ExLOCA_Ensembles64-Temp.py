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

def createSQLCMIP5TMax( StartDT, EndDT, CGridID, CModID ):
    """Create a SQL query string to extract max. temp. time series for the
    specified date range and the specified CMIP5 grid cell and model
    
    Args:
        StartDT (datetime): Starting date time
        EndDT (datetime): Ending date time
        CGridID (int): Primary key, ID for the grid cell to extract
        CModID (int): foreign key, ID for the model run to extract
    
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s]\n" \
               "    WHERE ( %s = %d AND %s = %d AND %s >= '%s' AND %s <= '%s' ) \n" \
               "    ORDER BY %s ASC;" % \
               ( DBAD.FIELDN_DT, DBAD.FIELDN_STRDT, DBAD.FIELDN_TMXVAL, 
                 DBAD.CMIP5_SCHEMA, DBAD.CMIP5_TMAX, DBAD.FIELDN_GNPK, CGridID, 
                 DBAD.FIELDN_MMPK, CModID, DBAD.FIELDN_DT, 
                 StartDT.strftime( DBAD.SQL_DTO_FMT ), DBAD.FIELDN_DT,
                 EndDT.strftime( DBAD.SQL_DTO_FMT ), DBAD.FIELDN_DT )
    # return
    return SQLQuery


def createSQLCMIP5TMin( StartDT, EndDT, CGridID, CModID ):
    """Create a SQL query string to extract min. temp. time series for the
    specified date range and the specified CMIP5 grid cell and model
    
    Args:
        StartDT (datetime): Starting date time
        EndDT (datetime): Ending date time
        CGridID (int): Primary key, ID for the grid cell to extract
        CModID (int): foreign key, ID for the model run to extract
    
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s]\n" \
               "    WHERE ( %s = %d AND %s = %d AND %s >= '%s' AND %s <= '%s' ) \n" \
               "    ORDER BY %s ASC;" % \
               ( DBAD.FIELDN_DT, DBAD.FIELDN_STRDT, DBAD.FIELDN_TMNVAL, 
                 DBAD.CMIP5_SCHEMA, DBAD.CMIP5_TMIN, DBAD.FIELDN_GNPK, CGridID, 
                 DBAD.FIELDN_MMPK, CModID, DBAD.FIELDN_DT, 
                 StartDT.strftime( DBAD.SQL_DTO_FMT ), DBAD.FIELDN_DT,
                 EndDT.strftime( DBAD.SQL_DTO_FMT ), DBAD.FIELDN_DT )
    # return
    return SQLQuery

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
    FirstModel = False
    mCnt = 0
    for jJ in range(1, (NumMods + 1)):
        ModInd = jJ
        if mCnt >= MAX_MODELS:
            break
        # make our joint index
        JntInd = "M%d_%d" % (ModInd, GD_START)
        # now are ready to get our max temp values
        TMxSQL = createSQLCMIP5TMax( START_DT1, END_DT4, GD_START, jJ )
        TMxDF = pd.read_sql( TMxSQL, engine, index_col=DBAD.FIELDN_STRDT, 
                             parse_dates=[DBAD.FIELDN_STRDT] )
        if len( TMxDF ) < 1:
            #print("No values for %s" % JntInd)
            continue
        # end if
        TMxDF.index.name = DBAD.FIELDN_DT
        TMxDF.index = TMxDF.index.tz_convert( None )
        TMxDF.columns = ["Temp_C"]
        # Min temp values
        TMnSQL = createSQLCMIP5TMin( START_DT1, END_DT4, GD_START, jJ )
        TMnDF = pd.read_sql( TMnSQL, engine, index_col=DBAD.FIELDN_STRDT, 
                             parse_dates=[DBAD.FIELDN_STRDT] )
        if len( TMnDF ) < 1:
            #print("No values for %s" % JntInd)
            continue
        # end if
        TMnDF.index.name = DBAD.FIELDN_DT
        TMnDF.index = TMnDF.index.tz_convert( None )
        TMnDF.columns = ["Temp_C"]
        TMxDF["AveTemp_C"] = 0.5 * ( TMxDF["Temp_C"] + TMnDF["Temp_C"] )
        TAveDF = TMxDF[["AveTemp_C"]].copy()
        print("Model %d" % ModInd)
        # now do the resample 
        MonDF = TAveDF.resample( 'MS', axis=0, closed='left', label='left' ).mean()
        AnnDF = TAveDF.resample( 'AS', axis=0, closed='left', label='left' ).mean()
        # now make our appends
        TAveDF.columns = [JntInd]
        GMonDF = MonDF.copy()
        GMonDF.columns = [JntInd]
        GAnnDF = AnnDF.copy()
        GAnnDF.columns = [JntInd]
        # now check where we are
        if (not FirstModel):
            FirstModel = True
            AllDF = TAveDF.copy()
            AllMonDF = GMonDF.copy()
            AllAnnDF = GAnnDF.copy()
        else:
            AllDF = AllDF.merge( TAveDF, how='inner', left_index=True, 
                                 right_index=True )
            AllMonDF = AllMonDF.merge( GMonDF, how='inner', 
                                       left_index=True, right_index=True)
            AllAnnDF = AllAnnDF.merge( GAnnDF, how='inner', 
                                       left_index=True, right_index=True)
        # end if
        mCnt += 1
    # end for
    # output
    CFName = "AveTemp_TS_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    TsPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllDF.to_pickle( TsPCKF )
    CFName = "AveTemp_AllMonth_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    MonPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllMonDF.to_pickle( MonPCKF )
    CFName = "AveTemp_AllYears_%s-%d_%d-%d.pickle" % ( DS_DESC, GD_START, START_DT1.year, END_DT4.year )
    AnnPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllAnnDF.to_pickle( AnnPCKF )
    # done
    
