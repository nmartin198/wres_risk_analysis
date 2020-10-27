# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 11:00:22 2019

@author: nmartin <nick.martin@stanfordalumni.org>

The purpose of this module is to extract the "other", non precipitation time 
series along with the wet state for the day and to produce day of the year 
average values (for each state) as well as day of the year standard deviations
for each state.

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
from math import sqrt
# custom module import
import DBA_DClimComp as DBAD

# module level values for changing
START_DT1 = dt.datetime( 1981, 1, 1, 0, 0, 0 )
END_DT1 = dt.datetime( 2010, 12, 31, 0, 0, 0 )
START_DT2 = dt.datetime( 2011, 1, 1, 0, 0, 0 )
END_DT2 = dt.datetime( 2040, 12, 31, 0, 0, 0 )
START_DT3 = dt.datetime( 2041, 1, 1, 0, 0, 0 )
END_DT3 = dt.datetime( 2070, 12, 31, 0, 0, 0 )
START_DT4 = dt.datetime( 2071, 1, 1, 0, 0, 0 )
END_DT4 = dt.datetime( 2100, 12, 31, 0, 0, 0 )

# grid values and run descriptions. Only for CMIP5
GD_START = 1
GD_END = 168
DS_DESC = "LOCA"
#GD_START = 169
#GD_END = 210
#DS_DESC = "BCCA"
# output directories
OUT_DIR1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochast' \
           r'ic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWeather_1981-2010'
OUT_DIR2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochast' \
           r'ic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWeather_2011-2040'
OUT_DIR3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochast' \
           r'ic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWeather_2041-2070'
OUT_DIR4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochast' \
           r'ic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWeather_2071-2100'
# Input files for smoothed averages. Need to toggle these based on the grid
# type
IN_WET_AVE1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_LOCA_Wet_Smooth_Ave_1981-2010.pickle'
IN_DRY_AVE1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_LOCA_Dry_Smooth_Ave_1981-2010.pickle'
IN_WET_AVE2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_LOCA_Wet_Smooth_Ave_2011-2040.pickle'
IN_DRY_AVE2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_LOCA_Dry_Smooth_Ave_2011-2040.pickle'
IN_WET_AVE3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_LOCA_Wet_Smooth_Ave_2041-2070.pickle'
IN_DRY_AVE3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_LOCA_Dry_Smooth_Ave_2041-2070.pickle'
IN_WET_AVE4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_LOCA_Wet_Smooth_Ave_2071-2100.pickle'
IN_DRY_AVE4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_LOCA_Dry_Smooth_Ave_2071-2100.pickle'
IN_WET_STD1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_LOCA_Wet_Smooth_Std_1981-2010.pickle'
IN_DRY_STD1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_LOCA_Dry_Smooth_Std_1981-2010.pickle'
IN_WET_STD2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_LOCA_Wet_Smooth_Std_2011-2040.pickle'
IN_DRY_STD2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_LOCA_Dry_Smooth_Std_2011-2040.pickle'
IN_WET_STD3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_LOCA_Wet_Smooth_Std_2041-2070.pickle'
IN_DRY_STD3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_LOCA_Dry_Smooth_Std_2041-2070.pickle'
IN_WET_STD4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_LOCA_Wet_Smooth_Std_2071-2100.pickle'
IN_DRY_STD4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_LOCA_Dry_Smooth_Std_2071-2100.pickle'
"""
IN_WET_AVE1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_BCCA_Wet_Smooth_Ave_1981-2010.pickle'
IN_DRY_AVE1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_BCCA_Dry_Smooth_Ave_1981-2010.pickle'
IN_WET_AVE2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_BCCA_Wet_Smooth_Ave_2011-2040.pickle'
IN_DRY_AVE2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_BCCA_Dry_Smooth_Ave_2011-2040.pickle'
IN_WET_AVE3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_BCCA_Wet_Smooth_Ave_2041-2070.pickle'
IN_DRY_AVE3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_BCCA_Dry_Smooth_Ave_2041-2070.pickle'
IN_WET_AVE4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_BCCA_Wet_Smooth_Ave_2071-2100.pickle'
IN_DRY_AVE4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_BCCA_Dry_Smooth_Ave_2071-2100.pickle'
IN_WET_STD1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_BCCA_Wet_Smooth_Std_1981-2010.pickle'
IN_DRY_STD1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_1981-2010\OWeath_BCCA_Dry_Smooth_Std_1981-2010.pickle'
IN_WET_STD2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_BCCA_Wet_Smooth_Std_2011-2040.pickle'
IN_DRY_STD2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2011-2040\OWeath_BCCA_Dry_Smooth_Std_2011-2040.pickle'
IN_WET_STD3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_BCCA_Wet_Smooth_Std_2041-2070.pickle'
IN_DRY_STD3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2041-2070\OWeath_BCCA_Dry_Smooth_Std_2041-2070.pickle'
IN_WET_STD4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_BCCA_Wet_Smooth_Std_2071-2100.pickle'
IN_DRY_STD4 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
                r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWe' \
                r'ather_2071-2100\OWeath_BCCA_Dry_Smooth_Std_2071-2100.pickle'
"""

# threshold for a rainty day
WD_THRESH = 0.2   # in mm
#
LogFile = "CMIP5OWExZs_%s.txt" % DS_DESC

# other parameters
YR = "Year"
DOYR = "DayofYear"
TOTYRDAYS = 366


# standalone execution block
if __name__ == '__main__':
    # make a log file entry
    CurDT = dt.datetime.now()
    with open( LogFile, 'w+' ) as LID:
        LID.write("Start processing CMIP5 data from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
    # end of with block
    # create our query engine
    engine = sqlalchemy.create_engine( DBAD.DSN_STRING )
    # get our starting and ending years
    StartYear1 = START_DT1.year
    StartYear2 = START_DT2.year
    StartYear3 = START_DT3.year
    StartYear4 = START_DT4.year
    EndYear1 = END_DT1.year
    EndYear2 = END_DT2.year
    EndYear3 = END_DT3.year
    EndYear4 = END_DT4.year
    AllYrs1 = [ x for x in range( StartYear1, (EndYear1 + 1), 1 )]
    AllYrs2 = [ x for x in range( StartYear2, (EndYear2 + 1), 1 )]
    AllYrs3 = [ x for x in range( StartYear3, (EndYear3 + 1), 1 )]
    AllYrs4 = [ x for x in range( StartYear4, (EndYear4 + 1), 1 )]
    # acquire the grid definition as a Pandas dataframe
    GridSQL = DBAD.createSQLCMIP5Grid()
    GridDF = pd.read_sql( GridSQL, engine, index_col=DBAD.FIELDN_ID )
    # get the gridd columns
    GridCols = list( GridDF.columns )
    if len( GridCols ) < 1:
        print("Could not acquire grid dataframe!!!!")
        sys.exit([-1])
    # next go through a year at time and then a grid point at a time and
    # build our data averages. Once we have averages then can do the standard
    # deviations
    WStateCnt1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMxRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMxMax1 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMxMin1 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMax1 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMin1 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMaxGrd1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxMinGrd1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMnRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMnMax1 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMnMin1 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMax1 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMin1 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMaxGrd1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMnMinGrd1 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    WStateCnt2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMxRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMxMax2 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMxMin2 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMax2 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMin2 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMaxGrd2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxMinGrd2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMnRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMnMax2 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMnMin2 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMax2 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMin2 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMaxGrd2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMnMinGrd2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    WStateCnt3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMxRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMxMax3 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMxMin3 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMax3 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMin3 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMaxGrd3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxMinGrd3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMnRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMnMax3 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMnMin3 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMax3 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMin3 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMaxGrd3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMnMinGrd3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    WStateCnt4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMxRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMxMax4 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMxMin4 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMax4 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMin4 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMaxGrd4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxMinGrd4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMnRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMnMax4 = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMnMin4 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMax4 = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMin4 = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMaxGrd4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMnMinGrd4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    # read in our wet and dry
    WetAveDF1 = pd.read_pickle( IN_WET_AVE1 )
    DryAveDF1 = pd.read_pickle( IN_DRY_AVE1 )
    WetAveDF2 = pd.read_pickle( IN_WET_AVE2 )
    DryAveDF2 = pd.read_pickle( IN_DRY_AVE2 )
    WetAveDF3 = pd.read_pickle( IN_WET_AVE3 )
    DryAveDF3 = pd.read_pickle( IN_DRY_AVE3 )
    WetAveDF4 = pd.read_pickle( IN_WET_AVE4 )
    DryAveDF4 = pd.read_pickle( IN_DRY_AVE4 )
    WetStdDF1 = pd.read_pickle( IN_WET_STD1 )
    DryStdDF1 = pd.read_pickle( IN_DRY_STD1 )
    WetStdDF2 = pd.read_pickle( IN_WET_STD2 )
    DryStdDF2 = pd.read_pickle( IN_DRY_STD2 )
    WetStdDF3 = pd.read_pickle( IN_WET_STD3 )
    DryStdDF3 = pd.read_pickle( IN_DRY_STD3 )
    WetStdDF4 = pd.read_pickle( IN_WET_STD4 )
    DryStdDF4 = pd.read_pickle( IN_DRY_STD4 )
    # now loop through so that can compile our means
    for gG in range(GD_START, (GD_END + 1)):
        print("Working on grid cell: %d" % gG)
        cGridID = gG
        # get the grid IDs
        gIDArray = gG * np.ones( TOTYRDAYS, dtype=np.float32 )
        # now get the SQL
        ExSQL = DBAD.createSQLCMIPPrecipSP( gG )
        AllPrecipDF = pd.read_sql( ExSQL, engine, 
                                   columns=[ DBAD.FIELDN_DT, 
                                             DBAD.FIELDN_MMPK, 
                                             DBAD.FIELDN_PVAL], 
                                   parse_dates=DBAD.FIELDN_DT )
        if len(AllPrecipDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("Precipitation query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("Precipitation query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        # pivot to get a real time series
        PVPrecipDF = AllPrecipDF.pivot( index=DBAD.FIELDN_DT, 
                                        columns=DBAD.FIELDN_MMPK, 
                                        values=DBAD.FIELDN_PVAL )
        PVPrecipDF[YR] = PVPrecipDF.index.year
        PVPrecipDF[DOYR] = PVPrecipDF.index.dayofyear
        # get the minimimum and maximum temperatures
        # max T
        ExSQL = DBAD.createSQLCMIPTMaxSP( gG )
        AllTMaxDF = pd.read_sql( ExSQL, engine, 
                                 columns=[ DBAD.FIELDN_DT, 
                                           DBAD.FIELDN_MMPK, 
                                           DBAD.FIELDN_TMXVAL], 
                                 parse_dates=DBAD.FIELDN_DT )
        if len(AllTMaxDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("T max query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("T max query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        PVTMaxDF = AllTMaxDF.pivot( index=DBAD.FIELDN_DT, 
                                    columns=DBAD.FIELDN_MMPK, 
                                    values=DBAD.FIELDN_TMXVAL )
        PVTMaxDF[YR] = PVTMaxDF.index.year
        PVTMaxDF[DOYR] = PVTMaxDF.index.dayofyear
        # min T
        ExSQL = DBAD.createSQLCMIPTMinSP( gG )
        AllTMinDF = pd.read_sql( ExSQL, engine, 
                                 columns=[ DBAD.FIELDN_DT, 
                                           DBAD.FIELDN_MMPK, 
                                           DBAD.FIELDN_TMNVAL], 
                                 parse_dates=DBAD.FIELDN_DT )
        if len(AllTMinDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("T min query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("T min query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        PVTMinDF = AllTMinDF.pivot( index=DBAD.FIELDN_DT, 
                                    columns=DBAD.FIELDN_MMPK, 
                                    values=DBAD.FIELDN_TMNVAL )
        PVTMinDF[YR] = PVTMinDF.index.year
        PVTMinDF[DOYR] = PVTMinDF.index.dayofyear
        # now let's check to make sure that have the same columns which 
        # are model runs.
        PreColumns = list( PVPrecipDF.columns )
        TMaxColumns = list( PVTMaxDF.columns )
        TMinColumns = list( PVTMinDF.columns )
        if (PreColumns != TMaxColumns) or (TMaxColumns != TMinColumns):
            # this is an error or issue
            print("Precip, Max T, and Min T, columns are different!!!")
            with open( LogFile, 'a' ) as LID:
                LID.write("Precip, Max T, and Min T, columns are different!\n" \
                          "Length precip columns: %d; length T max columns %d;" \
                          "length T min columns %d \n" % ( len(PreColumns),
                            len( TMaxColumns), len(TMinColumns) ) )
            continue
        # then go through the four year lists and start building our four sets
        # of output arrays
        # Data period - AllYrs1
        for yY in AllYrs1:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt1[:LastDay] = WStateCnt1[:LastDay] + WetState
                DStateCnt1[:LastDay] = DStateCnt1[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                ctWMax1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd1 = np.array( WetStdDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd1 = np.array( DryStdDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax1 ) / ctWStd1 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax1 ) / ctDStd1 ) )
                allZ = wZs + dZs
                ZTMxRSum1[:LastDay] = ZTMxRSum1[:LastDay] + allZ
                ZTMxMax1[:LastDay] = np.where( allZ > ZTMxMax1[:LastDay], allZ, 
                                               ZTMxMax1[:LastDay] )
                ZTMxMin1[:LastDay] = np.where( allZ < ZTMxMin1[:LastDay], allZ, 
                                               ZTMxMin1[:LastDay] )
                TMxMax1[:LastDay] = np.where( TMaxArray > TMxMax1[:LastDay], 
                                              TMaxArray, TMxMax1[:LastDay] )
                TMxMaxGrd1[:LastDay] = np.where( TMaxArray >= TMxMax1[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMaxGrd1[:LastDay] )
                TMxMin1[:LastDay] = np.where( TMaxArray < TMxMin1[:LastDay], 
                                              TMaxArray, 
                                              TMxMin1[:LastDay] )
                TMxMinGrd1[:LastDay] = np.where( TMaxArray <= TMxMin1[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMinGrd1[:LastDay] )
                # minimum temperatures
                ctWMin1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd1 = np.array( WetStdDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd1 = np.array( DryStdDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin1 ) / ctWStd1 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin1 ) / ctDStd1 ) )
                allZ = wZs + dZs
                ZTMnRSum1[:LastDay] = ZTMnRSum1[:LastDay] + allZ
                ZTMnMax1[:LastDay] = np.where( allZ > ZTMnMax1[:LastDay], allZ, 
                                               ZTMnMax1[:LastDay] )
                ZTMnMin1[:LastDay] = np.where( allZ < ZTMnMin1[:LastDay], allZ, 
                                               ZTMnMin1[:LastDay] )
                TMnMax1[:LastDay] = np.where( TMinArray > TMnMax1[:LastDay], 
                                              TMinArray, 
                                              TMnMax1[:LastDay] )
                TMnMaxGrd1[:LastDay] = np.where( TMinArray >= TMnMax1[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMaxGrd1[:LastDay] )
                TMnMin1[:LastDay] = np.where( TMinArray < TMnMin1[:LastDay], 
                                              TMinArray, 
                                              TMnMin1[:LastDay] )
                TMnMinGrd1[:LastDay] = np.where( TMinArray <= TMnMin1[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMinGrd1[:LastDay] )
            # end of column for
        # end of AllYears1 for
        # Projection Period 1 - AllYrs2
        for yY in AllYrs2:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt2[:LastDay] = WStateCnt2[:LastDay] + WetState
                DStateCnt2[:LastDay] = DStateCnt2[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                ctWMax2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd2 = np.array( WetStdDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd2 = np.array( DryStdDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax2 ) / ctWStd2 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax2 ) / ctDStd2 ) )
                allZ = wZs + dZs
                ZTMxRSum2[:LastDay] = ZTMxRSum2[:LastDay] + allZ
                ZTMxMax2[:LastDay] = np.where( allZ > ZTMxMax2[:LastDay], allZ, 
                                               ZTMxMax2[:LastDay] )
                ZTMxMin2[:LastDay] = np.where( allZ < ZTMxMin2[:LastDay], allZ, 
                                               ZTMxMin2[:LastDay] )
                TMxMax2[:LastDay] = np.where( TMaxArray > TMxMax2[:LastDay], 
                                              TMaxArray, TMxMax2[:LastDay] )
                TMxMaxGrd2[:LastDay] = np.where( TMaxArray >= TMxMax2[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMaxGrd2[:LastDay] )
                TMxMin2[:LastDay] = np.where( TMaxArray < TMxMin2[:LastDay], 
                                              TMaxArray, 
                                              TMxMin2[:LastDay] )
                TMxMinGrd2[:LastDay] = np.where( TMaxArray <= TMxMin2[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMinGrd2[:LastDay] )
                # minimum temperatures
                ctWMin2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd2 = np.array( WetStdDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd2 = np.array( DryStdDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin2 ) / ctWStd2 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin2 ) / ctDStd2 ) )
                allZ = wZs + dZs
                ZTMnRSum2[:LastDay] = ZTMnRSum2[:LastDay] + allZ
                ZTMnMax2[:LastDay] = np.where( allZ > ZTMnMax2[:LastDay], allZ, 
                                               ZTMnMax2[:LastDay] )
                ZTMnMin2[:LastDay] = np.where( allZ < ZTMnMin2[:LastDay], allZ, 
                                               ZTMnMin2[:LastDay] )
                TMnMax2[:LastDay] = np.where( TMinArray > TMnMax2[:LastDay], 
                                              TMinArray, 
                                              TMnMax2[:LastDay] )
                TMnMaxGrd2[:LastDay] = np.where( TMinArray >= TMnMax2[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMaxGrd2[:LastDay] )
                TMnMin2[:LastDay] = np.where( TMinArray < TMnMin2[:LastDay], 
                                              TMinArray, 
                                              TMnMin2[:LastDay] )
                TMnMinGrd2[:LastDay] = np.where( TMinArray <= TMnMin2[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMinGrd2[:LastDay] )
            # end of column for
        # end of AllYears2 for
        # Projection Period 2 - AllYrs3
        for yY in AllYrs3:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt3[:LastDay] = WStateCnt3[:LastDay] + WetState
                DStateCnt3[:LastDay] = DStateCnt3[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                ctWMax3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd3 = np.array( WetStdDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd3 = np.array( DryStdDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax3 ) / ctWStd3 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax3 ) / ctDStd3 ) )
                allZ = wZs + dZs
                ZTMxRSum3[:LastDay] = ZTMxRSum3[:LastDay] + allZ
                ZTMxMax3[:LastDay] = np.where( allZ > ZTMxMax3[:LastDay], allZ, 
                                               ZTMxMax3[:LastDay] )
                ZTMxMin3[:LastDay] = np.where( allZ < ZTMxMin3[:LastDay], allZ, 
                                               ZTMxMin3[:LastDay] )
                TMxMax3[:LastDay] = np.where( TMaxArray > TMxMax3[:LastDay], 
                                              TMaxArray, TMxMax3[:LastDay] )
                TMxMaxGrd3[:LastDay] = np.where( TMaxArray >= TMxMax3[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMaxGrd3[:LastDay] )
                TMxMin3[:LastDay] = np.where( TMaxArray < TMxMin3[:LastDay], 
                                              TMaxArray, 
                                              TMxMin3[:LastDay] )
                TMxMinGrd3[:LastDay] = np.where( TMaxArray <= TMxMin3[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMinGrd3[:LastDay] )
                # minimum temperatures
                ctWMin3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd3 = np.array( WetStdDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd3 = np.array( DryStdDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin3 ) / ctWStd3 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin3 ) / ctDStd3 ) )
                allZ = wZs + dZs
                ZTMnRSum3[:LastDay] = ZTMnRSum3[:LastDay] + allZ
                ZTMnMax3[:LastDay] = np.where( allZ > ZTMnMax3[:LastDay], allZ, 
                                               ZTMnMax3[:LastDay] )
                ZTMnMin3[:LastDay] = np.where( allZ < ZTMnMin3[:LastDay], allZ, 
                                               ZTMnMin3[:LastDay] )
                TMnMax3[:LastDay] = np.where( TMinArray > TMnMax3[:LastDay], 
                                              TMinArray, 
                                              TMnMax3[:LastDay] )
                TMnMaxGrd3[:LastDay] = np.where( TMinArray >= TMnMax3[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMaxGrd3[:LastDay] )
                TMnMin3[:LastDay] = np.where( TMinArray < TMnMin3[:LastDay], 
                                              TMinArray, 
                                              TMnMin3[:LastDay] )
                TMnMinGrd3[:LastDay] = np.where( TMinArray <= TMnMin3[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMinGrd3[:LastDay] )
            # end of column for
        # end of AllYears3 for
        # Projection Period 3 - AllYrs4
        for yY in AllYrs4:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            # first check if are on the last year and got nothing
            if (NPrecipDays < 1) or (NTMaxDays < 1) or (NTMinDays < 1):
                print("Returned empty arrays for year %d" % yY)
                with open( LogFile, 'a' ) as LID:
                    LID.write("Returned empty arrays for year %d\n" % yY)
                continue
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt4[:LastDay] = WStateCnt4[:LastDay] + WetState
                DStateCnt4[:LastDay] = DStateCnt4[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                ctWMax4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd4 = np.array( WetStdDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd4 = np.array( DryStdDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax4 ) / ctWStd4 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax4 ) / ctDStd4 ) )
                allZ = wZs + dZs
                ZTMxRSum4[:LastDay] = ZTMxRSum4[:LastDay] + allZ
                ZTMxMax4[:LastDay] = np.where( allZ > ZTMxMax4[:LastDay], allZ, 
                                               ZTMxMax4[:LastDay] )
                ZTMxMin4[:LastDay] = np.where( allZ < ZTMxMin4[:LastDay], allZ, 
                                               ZTMxMin4[:LastDay] )
                TMxMax4[:LastDay] = np.where( TMaxArray > TMxMax4[:LastDay], 
                                              TMaxArray, TMxMax4[:LastDay] )
                TMxMaxGrd4[:LastDay] = np.where( TMaxArray >= TMxMax4[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMaxGrd4[:LastDay] )
                TMxMin4[:LastDay] = np.where( TMaxArray < TMxMin4[:LastDay], 
                                              TMaxArray, 
                                              TMxMin4[:LastDay] )
                TMxMinGrd4[:LastDay] = np.where( TMaxArray <= TMxMin4[:LastDay], 
                                                 gIDArray[:LastDay], 
                                                 TMxMinGrd4[:LastDay] )
                # minimum temperatures
                ctWMin4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd4 = np.array( WetStdDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd4 = np.array( DryStdDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin4 ) / ctWStd4 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin4 ) / ctDStd4 ) )
                allZ = wZs + dZs
                ZTMnRSum4[:LastDay] = ZTMnRSum4[:LastDay] + allZ
                ZTMnMax4[:LastDay] = np.where( allZ > ZTMnMax4[:LastDay], allZ, 
                                               ZTMnMax4[:LastDay] )
                ZTMnMin4[:LastDay] = np.where( allZ < ZTMnMin4[:LastDay], allZ, 
                                               ZTMnMin4[:LastDay] )
                TMnMax4[:LastDay] = np.where( TMinArray > TMnMax4[:LastDay], 
                                              TMinArray, 
                                              TMnMax4[:LastDay] )
                TMnMaxGrd4[:LastDay] = np.where( TMinArray >= TMnMax4[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMaxGrd4[:LastDay] )
                TMnMin4[:LastDay] = np.where( TMinArray < TMnMin4[:LastDay], 
                                              TMinArray, 
                                              TMnMin4[:LastDay] )
                TMnMinGrd4[:LastDay] = np.where( TMinArray <= TMnMin4[:LastDay],
                                                 gIDArray[:LastDay], 
                                                 TMnMinGrd4[:LastDay] )
            # end of column for
        # end of AllYears4 for
    # end of grid ro
    # calculate the day of the year averages and output
    AllStateCnt1 = WStateCnt1 + DStateCnt1
    AllStateCnt2 = WStateCnt2 + DStateCnt2
    AllStateCnt3 = WStateCnt3 + DStateCnt3
    AllStateCnt4 = WStateCnt4 + DStateCnt4
    ZDDict1 = { "AllCounts" : AllStateCnt1 }
    ZDDict2 = { "AllCounts" : AllStateCnt2 }
    ZDDict3 = { "AllCounts" : AllStateCnt3 }
    ZDDict4 = { "AllCounts" : AllStateCnt4 }
    ZMaxDict1 = { "AllCounts" : AllStateCnt1,
                  DBAD.FIELDN_TMXVAL : ZTMxMax1,
                  DBAD.FIELDN_TMNVAL : ZTMnMax1,
                }
    ZMaxDict2 = { "AllCounts" : AllStateCnt2,
                  DBAD.FIELDN_TMXVAL : ZTMxMax2,
                  DBAD.FIELDN_TMNVAL : ZTMnMax2,
                }
    ZMaxDict3 = { "AllCounts" : AllStateCnt3,
                  DBAD.FIELDN_TMXVAL : ZTMxMax3,
                  DBAD.FIELDN_TMNVAL : ZTMnMax3,
                }
    ZMaxDict4 = { "AllCounts" : AllStateCnt4,
                  DBAD.FIELDN_TMXVAL : ZTMxMax4,
                  DBAD.FIELDN_TMNVAL : ZTMnMax4,
                }
    MaxDict1 = { "AllCounts" : AllStateCnt1,
                 DBAD.FIELDN_TMXVAL : TMxMax1,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMaxGrd1,
                 DBAD.FIELDN_TMNVAL : TMnMax1,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMaxGrd1,
                }
    MaxDict2 = { "AllCounts" : AllStateCnt2,
                 DBAD.FIELDN_TMXVAL : TMxMax2,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMaxGrd2,
                 DBAD.FIELDN_TMNVAL : TMnMax2,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMaxGrd2,
                }
    MaxDict3 = { "AllCounts" : AllStateCnt3,
                 DBAD.FIELDN_TMXVAL : TMxMax3,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMaxGrd3,
                 DBAD.FIELDN_TMNVAL : TMnMax3,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMaxGrd3,
                }
    MaxDict4 = { "AllCounts" : AllStateCnt4,
                 DBAD.FIELDN_TMXVAL : TMxMax4,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMaxGrd4,
                 DBAD.FIELDN_TMNVAL : TMnMax4,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMaxGrd4,
                }
    ZMinDict1 = { "AllCounts" : AllStateCnt1,
                  DBAD.FIELDN_TMXVAL : ZTMxMin1,
                  DBAD.FIELDN_TMNVAL : ZTMnMin1,
                }
    ZMinDict2 = { "AllCounts" : AllStateCnt2,
                  DBAD.FIELDN_TMXVAL : ZTMxMin2,
                  DBAD.FIELDN_TMNVAL : ZTMnMin2,
                }
    ZMinDict3 = { "AllCounts" : AllStateCnt3,
                  DBAD.FIELDN_TMXVAL : ZTMxMin3,
                  DBAD.FIELDN_TMNVAL : ZTMnMin3,
                }
    ZMinDict4 = { "AllCounts" : AllStateCnt4,
                  DBAD.FIELDN_TMXVAL : ZTMxMin4,
                  DBAD.FIELDN_TMNVAL : ZTMnMin4,
                }
    MinDict1 = { "AllCounts" : AllStateCnt1,
                 DBAD.FIELDN_TMXVAL : TMxMin1,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMinGrd1,
                 DBAD.FIELDN_TMNVAL : TMnMin1,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMinGrd1,
                }
    MinDict2 = { "AllCounts" : AllStateCnt2,
                 DBAD.FIELDN_TMXVAL : TMxMin2,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMinGrd2,
                 DBAD.FIELDN_TMNVAL : TMnMin2,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMinGrd2,
                }
    MinDict3 = { "AllCounts" : AllStateCnt3,
                 DBAD.FIELDN_TMXVAL : TMxMin3,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMinGrd3,
                 DBAD.FIELDN_TMNVAL : TMnMin3,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMinGrd3,
                }
    MinDict4 = { "AllCounts" : AllStateCnt4,
                 DBAD.FIELDN_TMXVAL : TMxMin4,
                 "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMinGrd4,
                 DBAD.FIELDN_TMNVAL : TMnMin4,
                 "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMinGrd4,
                }
    # get the wet and dry counts in fractional form for multiplication
    zDenom1 = np.where( AllStateCnt1 > 0, 
                        np.array( AllStateCnt1, dtype=np.float32), np.nan )
    zDenom2 = np.where( AllStateCnt2 > 0, 
                        np.array( AllStateCnt2, dtype=np.float32), np.nan )
    zDenom3 = np.where( AllStateCnt3 > 0, 
                        np.array( AllStateCnt3, dtype=np.float32), np.nan )
    zDenom4 = np.where( AllStateCnt4 > 0, 
                        np.array( AllStateCnt4, dtype=np.float32), np.nan )
    zMulti1 = 1.0 / zDenom1
    zMulti2 = 1.0 / zDenom2
    zMulti3 = 1.0 / zDenom3
    zMulti4 = 1.0 / zDenom4
    # max temp
    zAve1 = zMulti1 * ZTMxRSum1
    ZDDict1[DBAD.FIELDN_TMXVAL] = zAve1
    zAve2 = zMulti2 * ZTMxRSum2
    ZDDict2[DBAD.FIELDN_TMXVAL] = zAve2
    zAve3 = zMulti3 * ZTMxRSum3
    ZDDict3[DBAD.FIELDN_TMXVAL] = zAve3
    zAve4 = zMulti4 * ZTMxRSum4
    ZDDict4[DBAD.FIELDN_TMXVAL] = zAve4
    # min temp
    zAve1 = zMulti1 * ZTMnRSum1
    ZDDict1[DBAD.FIELDN_TMNVAL] = zAve1
    zAve2 = zMulti2 * ZTMnRSum2
    ZDDict2[DBAD.FIELDN_TMNVAL] = zAve2
    zAve3 = zMulti3 * ZTMnRSum3
    ZDDict3[DBAD.FIELDN_TMNVAL] = zAve3
    zAve4 = zMulti4 * ZTMnRSum4
    ZDDict4[DBAD.FIELDN_TMNVAL] = zAve4
    # build our data frame
    DaysIndexer = [ x for x in range(1, (TOTYRDAYS + 1), 1)]
    ZAveDF1 = pd.DataFrame( index=DaysIndexer, data=ZDDict1 )
    ZMaxDF1 = pd.DataFrame( index=DaysIndexer, data=ZMaxDict1 )
    ZMinDF1 = pd.DataFrame( index=DaysIndexer, data=ZMinDict1 )
    MaxDF1 = pd.DataFrame( index=DaysIndexer, data=MaxDict1 )
    MinDF1 = pd.DataFrame( index=DaysIndexer, data=MinDict1 )
    ZAveDF2 = pd.DataFrame( index=DaysIndexer, data=ZDDict2 )
    ZMaxDF2 = pd.DataFrame( index=DaysIndexer, data=ZMaxDict2 )
    ZMinDF2 = pd.DataFrame( index=DaysIndexer, data=ZMinDict2 )
    MaxDF2 = pd.DataFrame( index=DaysIndexer, data=MaxDict2 )
    MinDF2 = pd.DataFrame( index=DaysIndexer, data=MinDict2 )
    ZAveDF3 = pd.DataFrame( index=DaysIndexer, data=ZDDict3 )
    ZMaxDF3 = pd.DataFrame( index=DaysIndexer, data=ZMaxDict3 )
    ZMinDF3 = pd.DataFrame( index=DaysIndexer, data=ZMinDict3 )
    MaxDF3 = pd.DataFrame( index=DaysIndexer, data=MaxDict3 )
    MinDF3 = pd.DataFrame( index=DaysIndexer, data=MinDict3 )
    ZAveDF4 = pd.DataFrame( index=DaysIndexer, data=ZDDict4 )
    ZMaxDF4 = pd.DataFrame( index=DaysIndexer, data=ZMaxDict4 )
    ZMinDF4 = pd.DataFrame( index=DaysIndexer, data=ZMinDict4 )
    MaxDF4 = pd.DataFrame( index=DaysIndexer, data=MaxDict4 )
    MinDF4 = pd.DataFrame( index=DaysIndexer, data=MinDict4 )
    # output an interim set of spreadsheets and pickle files
    OFNameRoot1 = "OWeather_%s_PW_Zs_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName1 = "%s.xlsx" % OFNameRoot1
    OutXLSX1 = os.path.normpath( os.path.join( OUT_DIR1, OFName1 ))
    with pd.ExcelWriter(OutXLSX1) as writer:
        ZAveDF1.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF1.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF1.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF1.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF1.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_PW_ZAve_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR1, OFName ) )
    ZAveDF1.to_pickle( OutPickle )
    OFNameRoot2 = "OWeather_%s_PW_Zs_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName2 = "%s.xlsx" % OFNameRoot2
    OutXLSX2 = os.path.normpath( os.path.join( OUT_DIR2, OFName2 ))
    with pd.ExcelWriter(OutXLSX2) as writer:
        ZAveDF2.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF2.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF2.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF2.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF2.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_PW_ZAve_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR2, OFName ) )
    ZAveDF2.to_pickle( OutPickle )
    OFNameRoot3 = "OWeather_%s_PW_Zs_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName3 = "%s.xlsx" % OFNameRoot3
    OutXLSX3 = os.path.normpath( os.path.join( OUT_DIR3, OFName3 ))
    with pd.ExcelWriter(OutXLSX3) as writer:
        ZAveDF3.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF3.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF3.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF3.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF3.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_PW_ZAve_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR3, OFName ) )
    ZAveDF3.to_pickle( OutPickle )
    OFNameRoot4 = "OWeather_%s_PW_Zs_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName4 = "%s.xlsx" % OFNameRoot4
    OutXLSX4 = os.path.normpath( os.path.join( OUT_DIR4, OFName4 ))
    with pd.ExcelWriter(OutXLSX4) as writer:
        ZAveDF4.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF4.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF4.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF4.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF4.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    OFNameRoot = "OWeath_%s_PW_ZAve_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR4, OFName ) )
    ZAveDF4.to_pickle( OutPickle )
    # now we have our average daily Z score for each variable. Need to go
    #  back through and calculate our coefficients
    r0_12_numer1 = 0.0
    r0_12_1denom1 = 0.0
    r0_12_2denom1 = 0.0
    r1_11_numer1 = 0.0
    r1_11_0denom1 = 0.0
    r1_11_1denom1 = 0.0
    r1_12_numer1 = 0.0
    r1_12_1denom1 = 0.0
    r1_12_2denom1 = 0.0
    r1_21_numer1 = 0.0
    r1_21_1denom1 = 0.0
    r1_21_2denom1 = 0.0
    r1_22_numer1 = 0.0
    r1_22_0denom1 = 0.0
    r1_22_1denom1 = 0.0
    r0_12_numer2 = 0.0
    r0_12_1denom2 = 0.0
    r0_12_2denom2 = 0.0
    r1_11_numer2 = 0.0
    r1_11_0denom2 = 0.0
    r1_11_1denom2 = 0.0
    r1_12_numer2 = 0.0
    r1_12_1denom2 = 0.0
    r1_12_2denom2 = 0.0
    r1_21_numer2 = 0.0
    r1_21_1denom2 = 0.0
    r1_21_2denom2 = 0.0
    r1_22_numer2 = 0.0
    r1_22_0denom2 = 0.0
    r1_22_1denom2 = 0.0
    r0_12_numer3 = 0.0
    r0_12_1denom3 = 0.0
    r0_12_2denom3 = 0.0
    r1_11_numer3 = 0.0
    r1_11_0denom3 = 0.0
    r1_11_1denom3 = 0.0
    r1_12_numer3 = 0.0
    r1_12_1denom3 = 0.0
    r1_12_2denom3 = 0.0
    r1_21_numer3 = 0.0
    r1_21_1denom3 = 0.0
    r1_21_2denom3 = 0.0
    r1_22_numer3 = 0.0
    r1_22_0denom3 = 0.0
    r1_22_1denom3 = 0.0
    r0_12_numer4 = 0.0
    r0_12_1denom4 = 0.0
    r0_12_2denom4 = 0.0
    r1_11_numer4 = 0.0
    r1_11_0denom4 = 0.0
    r1_11_1denom4 = 0.0
    r1_12_numer4 = 0.0
    r1_12_1denom4 = 0.0
    r1_12_2denom4 = 0.0
    r1_21_numer4 = 0.0
    r1_21_1denom4 = 0.0
    r1_21_2denom4 = 0.0
    r1_22_numer4 = 0.0
    r1_22_0denom4 = 0.0
    r1_22_1denom4 = 0.0
    # complete loop a second time
    for gG in range(GD_START, (GD_END + 1)):
        print("Working on grid cell: %d" % gG)
        cGridID = gG
        # get the grid IDs
        gIDArray = gG * np.ones( TOTYRDAYS, dtype=np.float32 )
        # now get the SQL
        ExSQL = DBAD.createSQLCMIPPrecipSP( gG )
        AllPrecipDF = pd.read_sql( ExSQL, engine, 
                                   columns=[ DBAD.FIELDN_DT, 
                                             DBAD.FIELDN_MMPK, 
                                             DBAD.FIELDN_PVAL], 
                                   parse_dates=DBAD.FIELDN_DT )
        if len(AllPrecipDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("Precipitation query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("Precipitation query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        # pivot to get a real time series
        PVPrecipDF = AllPrecipDF.pivot( index=DBAD.FIELDN_DT, 
                                        columns=DBAD.FIELDN_MMPK, 
                                        values=DBAD.FIELDN_PVAL )
        PVPrecipDF[YR] = PVPrecipDF.index.year
        PVPrecipDF[DOYR] = PVPrecipDF.index.dayofyear
        # get the minimimum and maximum temperatures
        # max T
        ExSQL = DBAD.createSQLCMIPTMaxSP( gG )
        AllTMaxDF = pd.read_sql( ExSQL, engine, 
                                 columns=[ DBAD.FIELDN_DT, 
                                           DBAD.FIELDN_MMPK, 
                                           DBAD.FIELDN_TMXVAL], 
                                 parse_dates=DBAD.FIELDN_DT )
        if len(AllTMaxDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("T max query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("T max query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        PVTMaxDF = AllTMaxDF.pivot( index=DBAD.FIELDN_DT, 
                                    columns=DBAD.FIELDN_MMPK, 
                                    values=DBAD.FIELDN_TMXVAL )
        PVTMaxDF[YR] = PVTMaxDF.index.year
        PVTMaxDF[DOYR] = PVTMaxDF.index.dayofyear
        # min T
        ExSQL = DBAD.createSQLCMIPTMinSP( gG )
        AllTMinDF = pd.read_sql( ExSQL, engine, 
                                 columns=[ DBAD.FIELDN_DT, 
                                           DBAD.FIELDN_MMPK, 
                                           DBAD.FIELDN_TMNVAL], 
                                 parse_dates=DBAD.FIELDN_DT )
        if len(AllTMinDF) < 1:
            with open( LogFile, 'a' ) as LID:
                LID.write("T min query did not return anything for " \
                          "grid location %d\n\n" % gG)
            print("T min query did not return anything for " \
                          "grid location %d\n\n" % gG)
            continue
        PVTMinDF = AllTMinDF.pivot( index=DBAD.FIELDN_DT, 
                                    columns=DBAD.FIELDN_MMPK, 
                                    values=DBAD.FIELDN_TMNVAL )
        PVTMinDF[YR] = PVTMinDF.index.year
        PVTMinDF[DOYR] = PVTMinDF.index.dayofyear
        # now let's check to make sure that have the same columns which 
        # are model runs.
        PreColumns = list( PVPrecipDF.columns )
        TMaxColumns = list( PVTMaxDF.columns )
        TMinColumns = list( PVTMinDF.columns )
        if (PreColumns != TMaxColumns) or (TMaxColumns != TMinColumns):
            # this is an error or issue
            print("Precip, Max T, and Min T, columns are different!!!")
            with open( LogFile, 'a' ) as LID:
                LID.write("Precip, Max T, and Min T, columns are different!\n" \
                          "Length precip columns: %d; length T max columns %d;" \
                          "length T min columns %d \n" % ( len(PreColumns),
                            len( TMaxColumns), len(TMinColumns) ) )
            continue
        # then go through the four year lists and start building our four sets
        # of output arrays
        # Data period - AllYrs1
        for yY in AllYrs1:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt1[:LastDay] = WStateCnt1[:LastDay] + WetState
                DStateCnt1[:LastDay] = DStateCnt1[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                AveZMx1 = np.array( ZAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMax1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd1 = np.array( WetStdDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd1 = np.array( DryStdDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax1 ) / ctWStd1 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax1 ) / ctDStd1 ) )
                allZ = wZs + dZs
                DiffZ1_0 = allZ - AveZMx1
                DiffSqZ1_0 = (allZ - AveZMx1)**2.0
                DiffZ1_1 = ( np.roll( allZ, 1 ) - AveZMx1 )
                # minimum temperatures
                AveZMn1 = np.array( ZAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWMin1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd1 = np.array( WetStdDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd1 = np.array( DryStdDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin1 ) / ctWStd1 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin1 ) / ctDStd1 ) )
                allZ = wZs + dZs
                
                DiffZ2_0 = allZ - AveZMn1
                DiffSqZ2_0 = (allZ - AveZMn1)**2.0
                DiffZ2_1 = ( np.roll( allZ, 1 ) - AveZMn1 )
                # now do our running sums
                r0_12_numer1 = r0_12_numer1 + np.dot( DiffZ1_0, DiffZ2_0 )
                r0_12_1denom1 = r0_12_1denom1 + DiffSqZ1_0.sum()
                r0_12_2denom1 = r0_12_2denom1 + DiffSqZ2_0.sum()
                r1_11_numer1 = r1_11_numer1 + np.dot( DiffZ1_0, DiffZ1_1 )
                r1_11_0denom1 = r1_11_0denom1 + DiffSqZ1_0.sum()
                r1_11_1denom1 = r1_11_1denom1 + DiffSqZ1_0.sum()
                r1_12_numer1 = r1_12_numer1 + np.dot( DiffZ1_0, DiffZ2_1 )
                r1_12_1denom1 = r1_12_1denom1 + DiffSqZ1_0.sum()
                r1_12_2denom1 = r1_12_2denom1 + DiffSqZ2_0.sum()
                r1_21_numer1 = r1_21_numer1 + np.dot( DiffZ2_0, DiffZ1_1 )
                r1_21_1denom1 = r1_21_1denom1 + DiffSqZ1_0.sum()
                r1_21_2denom1 = r1_21_2denom1 + DiffSqZ2_0.sum()
                r1_22_numer1 = r1_22_numer1 + np.dot( DiffZ2_0, DiffZ2_1 )
                r1_22_0denom1 = r1_22_0denom1 + DiffSqZ2_0.sum()
                r1_22_1denom1 = r1_22_1denom1 + DiffSqZ2_0.sum()
            # end of column for
        # end of AllYears1 for
        # Projection Period 1 - AllYrs2
        for yY in AllYrs2:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt2[:LastDay] = WStateCnt2[:LastDay] + WetState
                DStateCnt2[:LastDay] = DStateCnt2[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                AveZMx2 = np.array( ZAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMax2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd2 = np.array( WetStdDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd2 = np.array( DryStdDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax2 ) / ctWStd2 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax2 ) / ctDStd2 ) )
                allZ = wZs + dZs
                DiffZ1_0 = allZ - AveZMx2
                DiffSqZ1_0 = (allZ - AveZMx2)**2.0
                DiffZ1_1 = ( np.roll( allZ, 1 ) - AveZMx2 )
                # minimum temperatures
                AveZMn2 = np.array( ZAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWMin2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd2 = np.array( WetStdDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd2 = np.array( DryStdDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin2 ) / ctWStd2 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin2 ) / ctDStd2 ) )
                allZ = wZs + dZs
                DiffZ2_0 = allZ - AveZMn2
                DiffSqZ2_0 = (allZ - AveZMn2)**2.0
                DiffZ2_1 = ( np.roll( allZ, 1 ) - AveZMn2 )
                # now do our running sums
                r0_12_numer2 = r0_12_numer2 + np.dot( DiffZ1_0, DiffZ2_0 )
                r0_12_1denom2 = r0_12_1denom2 + DiffSqZ1_0.sum()
                r0_12_2denom2 = r0_12_2denom2 + DiffSqZ2_0.sum()
                r1_11_numer2 = r1_11_numer2 + np.dot( DiffZ1_0, DiffZ1_1 )
                r1_11_0denom2 = r1_11_0denom2 + DiffSqZ1_0.sum()
                r1_11_1denom2 = r1_11_1denom2 + DiffSqZ1_0.sum()
                r1_12_numer2 = r1_12_numer2 + np.dot( DiffZ1_0, DiffZ2_1 )
                r1_12_1denom2 = r1_12_1denom2 + DiffSqZ1_0.sum()
                r1_12_2denom2 = r1_12_2denom2 + DiffSqZ2_0.sum()
                r1_21_numer2 = r1_21_numer2 + np.dot( DiffZ2_0, DiffZ1_1 )
                r1_21_1denom2 = r1_21_1denom2 + DiffSqZ1_0.sum()
                r1_21_2denom2 = r1_21_2denom2 + DiffSqZ2_0.sum()
                r1_22_numer2 = r1_22_numer2 + np.dot( DiffZ2_0, DiffZ2_1 )
                r1_22_0denom2 = r1_22_0denom2 + DiffSqZ2_0.sum()
                r1_22_1denom2 = r1_22_1denom2 + DiffSqZ2_0.sum()
            # end of column for
        # end of AllYears2 for
        # Projection Period 2 - AllYrs3
        for yY in AllYrs3:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt3[:LastDay] = WStateCnt3[:LastDay] + WetState
                DStateCnt3[:LastDay] = DStateCnt3[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                AveZMx3 = np.array( ZAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMax3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd3 = np.array( WetStdDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd3 = np.array( DryStdDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax3 ) / ctWStd3 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax3 ) / ctDStd3 ) )
                allZ = wZs + dZs
                DiffZ1_0 = allZ - AveZMx3
                DiffSqZ1_0 = (allZ - AveZMx3)**2.0
                DiffZ1_1 = ( np.roll( allZ, 1 ) - AveZMx3 )
                # minimum temperatures
                AveZMn3 = np.array( ZAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWMin3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd3 = np.array( WetStdDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd3 = np.array( DryStdDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin3 ) / ctWStd3 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin3 ) / ctDStd3 ) )
                allZ = wZs + dZs
                DiffZ2_0 = allZ - AveZMn3
                DiffSqZ2_0 = (allZ - AveZMn3)**2.0
                DiffZ2_1 = ( np.roll( allZ, 1 ) - AveZMn3 )
                # now do our running sums
                r0_12_numer3 = r0_12_numer3 + np.dot( DiffZ1_0, DiffZ2_0 )
                r0_12_1denom3 = r0_12_1denom3 + DiffSqZ1_0.sum()
                r0_12_2denom3 = r0_12_2denom3 + DiffSqZ2_0.sum()
                r1_11_numer3 = r1_11_numer3 + np.dot( DiffZ1_0, DiffZ1_1 )
                r1_11_0denom3 = r1_11_0denom3 + DiffSqZ1_0.sum()
                r1_11_1denom3 = r1_11_1denom3 + DiffSqZ1_0.sum()
                r1_12_numer3 = r1_12_numer3 + np.dot( DiffZ1_0, DiffZ2_1 )
                r1_12_1denom3 = r1_12_1denom3 + DiffSqZ1_0.sum()
                r1_12_2denom3 = r1_12_2denom3 + DiffSqZ2_0.sum()
                r1_21_numer3 = r1_21_numer3 + np.dot( DiffZ2_0, DiffZ1_1 )
                r1_21_1denom3 = r1_21_1denom3 + DiffSqZ1_0.sum()
                r1_21_2denom3 = r1_21_2denom3 + DiffSqZ2_0.sum()
                r1_22_numer3 = r1_22_numer3 + np.dot( DiffZ2_0, DiffZ2_1 )
                r1_22_0denom3 = r1_22_0denom3 + DiffSqZ2_0.sum()
                r1_22_1denom3 = r1_22_1denom3 + DiffSqZ2_0.sum()
            # end of column for
        # end of AllYears3 for
        # Projection Period 3 - AllYrs4
        for yY in AllYrs4:
            CurPrecipDF = PVPrecipDF[PVPrecipDF[YR] == yY].copy()
            CurTMaxDF = PVTMaxDF[PVTMaxDF[YR] == yY].copy()
            CurTMinDF = PVTMinDF[PVTMinDF[YR] == yY].copy()
            NPrecipDays = len( CurPrecipDF )
            NTMaxDays = len( CurTMaxDF )
            NTMinDays = len( CurTMinDF )
            # first check if are on the last year and got nothing
            if (NPrecipDays < 1) or (NTMaxDays < 1) or (NTMinDays < 1):
                print("Returned empty arrays for year %d" % yY)
                with open( LogFile, 'a' ) as LID:
                    LID.write("Returned empty arrays for year %d\n" % yY)
                continue
            if (NPrecipDays != NTMaxDays) or (NTMaxDays != NTMinDays):
                print("Length of annual precip, tmax, and tmin data sets are " \
                      "different for year %d.\nPrecip = %d, TMax = %d, " \
                      "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                with open( LogFile, 'a' ) as LID:
                    LID.write("Length of annual precip, tmax, and tmin data sets " \
                              "are different for year %d.\nPrecip = %d, TMax = %d, " \
                              "TMin=%d\n" % ( yY, NPrecipDays, NTMaxDays, NTMinDays) )
                continue
            if NPrecipDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # now can start the annual calculations have each column that 
            #  is a model result as realizations
            for tCol in PreColumns:
                if (tCol == YR):
                    continue
                if (tCol == DOYR):
                    continue
                # else do our calcs
                PreArray = np.array( CurPrecipDF[tCol], 
                                     dtype=np.float32 )
                TMaxArray = np.array( CurTMaxDF[tCol], 
                                      dtype=np.float32 )
                TMinArray = np.array( CurTMinDF[tCol], 
                                      dtype=np.float32 )
                WetState = np.where( PreArray > WD_THRESH, 1, 0 )
                DryState = 1 - WetState
                WStateCnt4[:LastDay] = WStateCnt4[:LastDay] + WetState
                DStateCnt4[:LastDay] = DStateCnt4[:LastDay] + DryState
                # now calculate Zs
                # max temperature
                AveZMx4 = np.array( ZAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMax4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWStd4 = np.array( WetStdDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDStd4 = np.array( DryStdDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMaxArray - ctWMax4 ) / ctWStd4 ) )
                dZs = ( DryState * ( ( TMaxArray - ctDMax4 ) / ctDStd4 ) )
                allZ = wZs + dZs
                DiffZ1_0 = allZ - AveZMx4
                DiffSqZ1_0 = (allZ - AveZMx4)**2.0
                DiffZ1_1 = ( np.roll( allZ, 1 ) - AveZMx4 )
                # minimum temperatures
                AveZMn4 = np.array( ZAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWMin4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctWStd4 = np.array( WetStdDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDStd4 = np.array( DryStdDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                wZs = ( WetState * ( ( TMinArray - ctWMin4 ) / ctWStd4 ) )
                dZs = ( DryState * ( ( TMinArray - ctDMin4 ) / ctDStd4 ) )
                allZ = wZs + dZs
                DiffZ2_0 = allZ - AveZMn4
                DiffSqZ2_0 = (allZ - AveZMn4)**2.0
                DiffZ2_1 = ( np.roll( allZ, 1 ) - AveZMn4 )
                # now do our running sums
                r0_12_numer4 = r0_12_numer4 + np.dot( DiffZ1_0, DiffZ2_0 )
                r0_12_1denom4 = r0_12_1denom4 + DiffSqZ1_0.sum()
                r0_12_2denom4 = r0_12_2denom4 + DiffSqZ2_0.sum()
                r1_11_numer4 = r1_11_numer4 + np.dot( DiffZ1_0, DiffZ1_1 )
                r1_11_0denom4 = r1_11_0denom4 + DiffSqZ1_0.sum()
                r1_11_1denom4 = r1_11_1denom4 + DiffSqZ1_0.sum()
                r1_12_numer4 = r1_12_numer4 + np.dot( DiffZ1_0, DiffZ2_1 )
                r1_12_1denom4 = r1_12_1denom4 + DiffSqZ1_0.sum()
                r1_12_2denom4 = r1_12_2denom4 + DiffSqZ2_0.sum()
                r1_21_numer4 = r1_21_numer4 + np.dot( DiffZ2_0, DiffZ1_1 )
                r1_21_1denom4 = r1_21_1denom4 + DiffSqZ1_0.sum()
                r1_21_2denom4 = r1_21_2denom4 + DiffSqZ2_0.sum()
                r1_22_numer4 = r1_22_numer4 + np.dot( DiffZ2_0, DiffZ2_1 )
                r1_22_0denom4 = r1_22_0denom4 + DiffSqZ2_0.sum()
                r1_22_1denom4 = r1_22_1denom4 + DiffSqZ2_0.sum()
            # end of column for
        # end of AllYears4 for
    # end of grid ro
    # calculate our coefficients
    r0_12_1 = r0_12_numer1 / ( sqrt(r0_12_1denom1) * sqrt(r0_12_2denom1) )
    r1_11_1 = r1_11_numer1 / ( sqrt(r1_11_0denom1) * sqrt(r1_11_1denom1) )
    r1_22_1 = r1_22_numer1 / ( sqrt(r1_22_0denom1) * sqrt(r1_22_1denom1) )
    r1_12_1 = r1_12_numer1 / ( sqrt(r1_12_1denom1) * sqrt(r1_12_2denom1) )
    r1_21_1 = r1_21_numer1 / ( sqrt(r1_21_2denom1) * sqrt(r1_21_1denom1) )
    r0_12_2 = r0_12_numer2 / ( sqrt(r0_12_1denom2) * sqrt(r0_12_2denom2) )
    r1_11_2 = r1_11_numer2 / ( sqrt(r1_11_0denom2) * sqrt(r1_11_1denom2) )
    r1_22_2 = r1_22_numer2 / ( sqrt(r1_22_0denom2) * sqrt(r1_22_1denom2) )
    r1_12_2 = r1_12_numer2 / ( sqrt(r1_12_1denom2) * sqrt(r1_12_2denom2) )
    r1_21_2 = r1_21_numer2 / ( sqrt(r1_21_2denom2) * sqrt(r1_21_1denom2) )
    r0_12_3 = r0_12_numer3 / ( sqrt(r0_12_1denom3) * sqrt(r0_12_2denom3) )
    r1_11_3 = r1_11_numer3 / ( sqrt(r1_11_0denom3) * sqrt(r1_11_1denom3) )
    r1_22_3 = r1_22_numer3 / ( sqrt(r1_22_0denom3) * sqrt(r1_22_1denom3) )
    r1_12_3 = r1_12_numer3 / ( sqrt(r1_12_1denom3) * sqrt(r1_12_2denom3) )
    r1_21_3 = r1_21_numer3 / ( sqrt(r1_21_2denom3) * sqrt(r1_21_1denom3) )
    r0_12_4 = r0_12_numer4 / ( sqrt(r0_12_1denom4) * sqrt(r0_12_2denom4) )
    r1_11_4 = r1_11_numer4 / ( sqrt(r1_11_0denom4) * sqrt(r1_11_1denom4) )
    r1_22_4 = r1_22_numer4 / ( sqrt(r1_22_0denom4) * sqrt(r1_22_1denom4) )
    r1_12_4 = r1_12_numer4 / ( sqrt(r1_12_1denom4) * sqrt(r1_12_2denom4) )
    r1_21_4 = r1_21_numer4 / ( sqrt(r1_21_2denom4) * sqrt(r1_21_1denom4) )
    # now make our data frames
    # rho 0 correlation
    r0DDict1 = { "rho_X1" : [ 1.0, r0_12_1 ],
                  "rho_X2" : [ r0_12_1, 1.0 ],
                  }
    r0Ind = [ "rho_1X", "rho_2X" ]
    r0DF1 = pd.DataFrame( index=r0Ind, data=r0DDict1 )
    r0DDict2 = { "rho_X1" : [ 1.0, r0_12_2 ],
                  "rho_X2" : [ r0_12_2, 1.0 ],
                  }
    r0DF2 = pd.DataFrame( index=r0Ind, data=r0DDict2 )
    r0DDict3 = { "rho_X1" : [ 1.0, r0_12_3 ],
                  "rho_X2" : [ r0_12_3, 1.0 ],
                  }
    r0DF3 = pd.DataFrame( index=r0Ind, data=r0DDict3 )
    r0DDict4 = { "rho_X1" : [ 1.0, r0_12_4 ],
                  "rho_X2" : [ r0_12_4, 1.0 ],
                  }
    r0DF4 = pd.DataFrame( index=r0Ind, data=r0DDict4 )
    # rho 1 cross-correlation
    r1DDict1 = { "rho_X1_L1" : [ r1_11_1, r1_12_1 ],
                  "rho_X2_L1" : [ r1_21_1, r1_22_1 ],
                  }
    r1DF1 = pd.DataFrame( index=r0Ind, data=r1DDict1 )
    
    r1DDict2 = { "rho_X1_L1" : [ r1_11_2, r1_12_2 ],
                  "rho_X2_L1" : [ r1_21_2, r1_22_2 ],
                  }
    r1DF2 = pd.DataFrame( index=r0Ind, data=r1DDict2 )
    r1DDict3 = { "rho_X1_L1" : [ r1_11_3, r1_12_3 ],
                  "rho_X2_L1" : [ r1_21_3, r1_22_3 ],
                  }
    r1DF3 = pd.DataFrame( index=r0Ind, data=r1DDict3 )
    r1DDict4 = { "rho_X1_L1" : [ r1_11_4, r1_12_4 ],
                  "rho_X2_L1" : [ r1_21_4, r1_22_4 ],
                  }
    r1DF4 = pd.DataFrame( index=r0Ind, data=r1DDict4 )
    OFNameRoot1 = "OWeather_%s_Zs_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName1 = "%s.xlsx" % OFNameRoot1
    OutXLSX1 = os.path.normpath( os.path.join( OUT_DIR1, OFName1 ))
    with pd.ExcelWriter(OutXLSX1) as writer:
        r0DF1.to_excel( writer, sheet_name="M0", index=True )
        r1DF1.to_excel( writer, sheet_name="M1", index=True )
        ZAveDF1.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF1.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF1.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF1.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF1.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_Z_M0_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR1, OFName ) )
    r0DF1.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_Z_M1_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR1, OFName ) )
    r1DF1.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_ZAve_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR1, OFName ) )
    ZAveDF1.to_pickle( OutPickle )
    OFNameRoot2 = "OWeather_%s_Zs_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName2 = "%s.xlsx" % OFNameRoot2
    OutXLSX2 = os.path.normpath( os.path.join( OUT_DIR2, OFName2 ))
    with pd.ExcelWriter(OutXLSX2) as writer:
        r0DF2.to_excel( writer, sheet_name="M0", index=True )
        r1DF2.to_excel( writer, sheet_name="M1", index=True )
        ZAveDF2.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF2.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF2.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF2.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF2.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_Z_M0_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR2, OFName ) )
    r0DF2.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_Z_M1_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR2, OFName ) )
    r1DF2.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_ZAve_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR2, OFName ) )
    ZAveDF2.to_pickle( OutPickle )
    OFNameRoot3 = "OWeather_%s_Zs_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName3 = "%s.xlsx" % OFNameRoot3
    OutXLSX3 = os.path.normpath( os.path.join( OUT_DIR3, OFName3 ))
    with pd.ExcelWriter(OutXLSX3) as writer:
        r0DF3.to_excel( writer, sheet_name="M0", index=True )
        r1DF3.to_excel( writer, sheet_name="M1", index=True )
        ZAveDF3.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF3.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF3.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF3.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF3.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_Z_M0_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR3, OFName ) )
    r0DF3.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_Z_M1_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR3, OFName ) )
    r1DF3.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_ZAve_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR3, OFName ) )
    ZAveDF3.to_pickle( OutPickle )
    OFNameRoot4 = "OWeather_%s_Zs_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName4 = "%s.xlsx" % OFNameRoot4
    OutXLSX4 = os.path.normpath( os.path.join( OUT_DIR4, OFName4 ))
    with pd.ExcelWriter(OutXLSX4) as writer:
        r0DF4.to_excel( writer, sheet_name="M0", index=True )
        r1DF4.to_excel( writer, sheet_name="M1", index=True )
        ZAveDF4.to_excel( writer, sheet_name="Z_Aves", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMaxDF4.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        ZMinDF4.to_excel( writer, sheet_name="Z_Mins", index=True, 
                          index_label="Days", na_rep=str(np.nan))
        MaxDF4.to_excel( writer, sheet_name="Maxs", index=True, 
                         index_label="Days", na_rep=str(np.nan))
        MinDF4.to_excel( writer, sheet_name="Mins", index=True, 
                         index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_%s_Z_M0_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR4, OFName ) )
    r0DF4.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_Z_M1_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR4, OFName ) )
    r1DF4.to_pickle( OutPickle )
    OFNameRoot = "OWeath_%s_ZAve_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR4, OFName ) )
    ZAveDF4.to_pickle( OutPickle )
    # end of work
    CurDT = dt.datetime.now()
    with open( LogFile, 'a' ) as LID:
        LID.write("Finished processing CMIP5 Zs from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
    # end of with block
    # end of work


#EOF