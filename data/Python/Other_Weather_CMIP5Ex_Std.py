# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 11:00:22 2019

@author: nmartin <nick.martin@stnafordalumni.org>

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
"""
# threshold for a rainty day
WD_THRESH = 0.2   # in mm
#
LogFile = "CMIP5OWExStd_%s.txt" % DS_DESC

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
    TMxWRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnWRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMxDRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnDRSum1 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    WStateCnt2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt2 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxWRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnWRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMxDRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnDRSum2 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    WStateCnt3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt3 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxWRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnWRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMxDRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnDRSum3 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    WStateCnt4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt4 = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxWRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnWRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMxDRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnDRSum4 = np.zeros( TOTYRDAYS, dtype=np.float32 )
    # read in our wet and dry
    WetAveDF1 = pd.read_pickle( IN_WET_AVE1 )
    DryAveDF1 = pd.read_pickle( IN_DRY_AVE1 )
    WetAveDF2 = pd.read_pickle( IN_WET_AVE2 )
    DryAveDF2 = pd.read_pickle( IN_DRY_AVE2 )
    WetAveDF3 = pd.read_pickle( IN_WET_AVE3 )
    DryAveDF3 = pd.read_pickle( IN_DRY_AVE3 )
    WetAveDF4 = pd.read_pickle( IN_WET_AVE4 )
    DryAveDF4 = pd.read_pickle( IN_DRY_AVE4 )
    # now loop through so that can compile our means
    for gG in range(GD_START, (GD_END + 1)):
        print("Working on grid cell: %d" % gG)
        cGridID = gG
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
                # get the average/smoothed daily values
                ctWMax1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMin1 = np.array( WetAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin1 = np.array( DryAveDF1.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                # now can add values to our running sum
                TMxWRSum1[:LastDay] = ( TMxWRSum1[:LastDay] + ( WetState *
                                        ( TMaxArray - ctWMax1 )**2.0 ) )
                TMnWRSum1[:LastDay] = ( TMnWRSum1[:LastDay] + ( WetState *
                                        ( TMinArray - ctWMin1 )**2.0 ) )
                TMxDRSum1[:LastDay] = ( TMxDRSum1[:LastDay] + ( DryState *
                                        ( TMaxArray - ctDMax1 )**2.0 ) )
                TMnDRSum1[:LastDay] = ( TMnDRSum1[:LastDay] + ( DryState *
                                        ( TMinArray - ctDMin1 )**2.0 ) )
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
                # get the average/smoothed daily values
                ctWMax2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMin2 = np.array( WetAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin2 = np.array( DryAveDF2.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                # now can add values to our running sum
                TMxWRSum2[:LastDay] = ( TMxWRSum2[:LastDay] + ( WetState *
                                        ( TMaxArray - ctWMax2 )**2.0 ) )
                TMnWRSum2[:LastDay] = ( TMnWRSum2[:LastDay] + ( WetState *
                                        ( TMinArray - ctWMin2 )**2.0 ) )
                TMxDRSum2[:LastDay] = ( TMxDRSum2[:LastDay] + ( DryState *
                                        ( TMaxArray - ctDMax2 )**2.0 ) )
                TMnDRSum2[:LastDay] = ( TMnDRSum2[:LastDay] + ( DryState *
                                        ( TMinArray - ctDMin2 )**2.0 ) )
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
                # get the average/smoothed daily values
                ctWMax3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMin3 = np.array( WetAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin3 = np.array( DryAveDF3.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                # now can add values to our running sum
                TMxWRSum3[:LastDay] = ( TMxWRSum3[:LastDay] + ( WetState *
                                        ( TMaxArray - ctWMax3 )**2.0 ) )
                TMnWRSum3[:LastDay] = ( TMnWRSum3[:LastDay] + ( WetState *
                                        ( TMinArray - ctWMin3 )**2.0 ) )
                TMxDRSum3[:LastDay] = ( TMxDRSum3[:LastDay] + ( DryState *
                                        ( TMaxArray - ctDMax3 )**2.0 ) )
                TMnDRSum3[:LastDay] = ( TMnDRSum3[:LastDay] + ( DryState *
                                        ( TMinArray - ctDMin3 )**2.0 ) )
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
                # get the average/smoothed daily values
                ctWMax4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctDMax4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                                    dtype=np.float32 )
                ctWMin4 = np.array( WetAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                ctDMin4 = np.array( DryAveDF4.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                                    dtype=np.float32 )
                # now can add values to our running sum
                TMxWRSum4[:LastDay] = ( TMxWRSum4[:LastDay] + ( WetState *
                                        ( TMaxArray - ctWMax4 )**2.0 ) )
                TMnWRSum4[:LastDay] = ( TMnWRSum4[:LastDay] + ( WetState *
                                        ( TMinArray - ctWMin4 )**2.0 ) )
                TMxDRSum4[:LastDay] = ( TMxDRSum4[:LastDay] + ( DryState *
                                        ( TMaxArray - ctDMax4 )**2.0 ) )
                TMnDRSum4[:LastDay] = ( TMnDRSum4[:LastDay] + ( DryState *
                                        ( TMinArray - ctDMin4 )**2.0 ) )
            # end of column for
        # end of AllYears4 for
    # end of grid ro
    # calculate the day of the year averages and output
    WDDict1 = { "Wet Counts" : WStateCnt1 }
    DDDict1 = { "Dry Counts" : DStateCnt1 }
    WDDict2 = { "Wet Counts" : WStateCnt2 }
    DDDict2 = { "Dry Counts" : DStateCnt2 }
    WDDict3 = { "Wet Counts" : WStateCnt3 }
    DDDict3 = { "Dry Counts" : DStateCnt3 }
    WDDict4 = { "Wet Counts" : WStateCnt4 }
    DDDict4 = { "Dry Counts" : DStateCnt4 }
    # get the wet and dry counts in fractional form for multiplication
    # wet
    wDenom1 = np.where( WStateCnt1 > 0, np.array( WStateCnt1, dtype=np.float32),
                        np.nan )
    wMulti1 = 1.0 / wDenom1
    wDenom2 = np.where( WStateCnt2 > 0, np.array( WStateCnt2, dtype=np.float32),
                        np.nan )
    wMulti2 = 1.0 / wDenom2
    wDenom3 = np.where( WStateCnt3 > 0, np.array( WStateCnt3, dtype=np.float32),
                        np.nan )
    wMulti3 = 1.0 / wDenom3
    wDenom4 = np.where( WStateCnt4 > 0, np.array( WStateCnt4, dtype=np.float32),
                        np.nan )
    wMulti4 = 1.0 / wDenom4
    # dry
    dDenom1 = np.where( DStateCnt1 > 0, np.array( DStateCnt1, dtype=np.float32),
                        np.nan )
    dMulti1 = 1.0 / dDenom1
    dDenom2 = np.where( DStateCnt2 > 0, np.array( DStateCnt2, dtype=np.float32),
                        np.nan )
    dMulti2 = 1.0 / dDenom2
    dDenom3 = np.where( DStateCnt3 > 0, np.array( DStateCnt3, dtype=np.float32),
                        np.nan )
    dMulti3 = 1.0 / dDenom3
    dDenom4 = np.where( DStateCnt4 > 0, np.array( DStateCnt4, dtype=np.float32),
                        np.nan )
    dMulti4 = 1.0 / dDenom4
    # max temp
    tWAve1 = wMulti1 * TMxWRSum1
    tWAve2 = wMulti2 * TMxWRSum2
    tWAve3 = wMulti3 * TMxWRSum3
    tWAve4 = wMulti4 * TMxWRSum4
    tDAve1 = dMulti1 * TMxDRSum1
    tDAve2 = dMulti2 * TMxDRSum2
    tDAve3 = dMulti3 * TMxDRSum3
    tDAve4 = dMulti4 * TMxDRSum4
    WDDict1[DBAD.FIELDN_TMXVAL] = np.sqrt( tWAve1 )
    WDDict2[DBAD.FIELDN_TMXVAL] = np.sqrt( tWAve2 )
    WDDict3[DBAD.FIELDN_TMXVAL] = np.sqrt( tWAve3 )
    WDDict4[DBAD.FIELDN_TMXVAL] = np.sqrt( tWAve4 )
    DDDict1[DBAD.FIELDN_TMXVAL] = np.sqrt( tDAve1 )
    DDDict2[DBAD.FIELDN_TMXVAL] = np.sqrt( tDAve2 )
    DDDict3[DBAD.FIELDN_TMXVAL] = np.sqrt( tDAve3 )
    DDDict4[DBAD.FIELDN_TMXVAL] = np.sqrt( tDAve4 )
    # min temp
    tWAve1 = wMulti1 * TMnWRSum1
    tWAve2 = wMulti2 * TMnWRSum2
    tWAve3 = wMulti3 * TMnWRSum3
    tWAve4 = wMulti4 * TMnWRSum4
    tDAve1 = dMulti1 * TMnDRSum1
    tDAve2 = dMulti2 * TMnDRSum2
    tDAve3 = dMulti3 * TMnDRSum3
    tDAve4 = dMulti4 * TMnDRSum4
    WDDict1[DBAD.FIELDN_TMNVAL] = np.sqrt( tWAve1 )
    WDDict2[DBAD.FIELDN_TMNVAL] = np.sqrt( tWAve2 )
    WDDict3[DBAD.FIELDN_TMNVAL] = np.sqrt( tWAve3 )
    WDDict4[DBAD.FIELDN_TMNVAL] = np.sqrt( tWAve4 )
    DDDict1[DBAD.FIELDN_TMNVAL] = np.sqrt( tDAve1 )
    DDDict2[DBAD.FIELDN_TMNVAL] = np.sqrt( tDAve2 )
    DDDict3[DBAD.FIELDN_TMNVAL] = np.sqrt( tDAve3 )
    DDDict4[DBAD.FIELDN_TMNVAL] = np.sqrt( tDAve4 )
    # build our data frames
    DaysIndexer = [ x for x in range(1, (TOTYRDAYS + 1), 1)]
    WetDF1 = pd.DataFrame( index=DaysIndexer, data=WDDict1 )
    WetDF2 = pd.DataFrame( index=DaysIndexer, data=WDDict2 )
    WetDF3 = pd.DataFrame( index=DaysIndexer, data=WDDict3 )
    WetDF4 = pd.DataFrame( index=DaysIndexer, data=WDDict4 )
    DryDF1 = pd.DataFrame( index=DaysIndexer, data=DDDict1 )
    DryDF2 = pd.DataFrame( index=DaysIndexer, data=DDDict2 )
    DryDF3 = pd.DataFrame( index=DaysIndexer, data=DDDict3 )
    DryDF4 = pd.DataFrame( index=DaysIndexer, data=DDDict4 )
    # output to Excel
    OFNameRoot1 = "OWeather_%s_Std_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFNameRoot2 = "OWeather_%s_Std_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFNameRoot3 = "OWeather_%s_Std_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFNameRoot4 = "OWeather_%s_Std_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName1 = "%s.xlsx" % OFNameRoot1
    OFName2 = "%s.xlsx" % OFNameRoot2
    OFName3 = "%s.xlsx" % OFNameRoot3
    OFName4 = "%s.xlsx" % OFNameRoot4
    OutXLSX1 = os.path.normpath( os.path.join( OUT_DIR1, OFName1 ))
    OutXLSX2 = os.path.normpath( os.path.join( OUT_DIR2, OFName2 ))
    OutXLSX3 = os.path.normpath( os.path.join( OUT_DIR3, OFName3 ))
    OutXLSX4 = os.path.normpath( os.path.join( OUT_DIR4, OFName4 ))
    with pd.ExcelWriter(OutXLSX1) as writer:
        WetDF1.to_excel( writer, sheet_name="Wet Days", index=True, 
                        index_label="Days" )
        DryDF1.to_excel( writer, sheet_name="Dry Days", index=True, 
                        index_label="Days" )
    with pd.ExcelWriter(OutXLSX2) as writer:
        WetDF2.to_excel( writer, sheet_name="Wet Days", index=True, 
                        index_label="Days" )
        DryDF2.to_excel( writer, sheet_name="Dry Days", index=True, 
                        index_label="Days" )
    with pd.ExcelWriter(OutXLSX3) as writer:
        WetDF3.to_excel( writer, sheet_name="Wet Days", index=True, 
                        index_label="Days" )
        DryDF3.to_excel( writer, sheet_name="Dry Days", index=True, 
                        index_label="Days" )
    with pd.ExcelWriter(OutXLSX4) as writer:
        WetDF4.to_excel( writer, sheet_name="Wet Days", index=True, 
                        index_label="Days" )
        DryDF4.to_excel( writer, sheet_name="Dry Days", index=True, 
                        index_label="Days" )
    # now write some pickle files
    OFNameRoot1 = "OWeathWetDF_%s_Std_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFNameRoot2 = "OWeathWetDF_%s_Std_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFNameRoot3 = "OWeathWetDF_%s_Std_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFNameRoot4 = "OWeathWetDF_%s_Std_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName1 = "%s.pickle" % OFNameRoot1
    OFName2 = "%s.pickle" % OFNameRoot2
    OFName3 = "%s.pickle" % OFNameRoot3
    OFName4 = "%s.pickle" % OFNameRoot4
    OutPickle1 = os.path.normpath( os.path.join( OUT_DIR1, OFName1 ) )
    OutPickle2 = os.path.normpath( os.path.join( OUT_DIR2, OFName2 ) )
    OutPickle3 = os.path.normpath( os.path.join( OUT_DIR3, OFName3 ) )
    OutPickle4 = os.path.normpath( os.path.join( OUT_DIR4, OFName4 ) )
    WetDF1.to_pickle( OutPickle1 )
    WetDF2.to_pickle( OutPickle2 )
    WetDF3.to_pickle( OutPickle3 )
    WetDF4.to_pickle( OutPickle4 )
    OFNameRoot1 = "OWeathDryDF_%s_Std_%s-%s" % (DS_DESC, StartYear1, EndYear1)
    OFNameRoot2 = "OWeathDryDF_%s_Std_%s-%s" % (DS_DESC, StartYear2, EndYear2)
    OFNameRoot3 = "OWeathDryDF_%s_Std_%s-%s" % (DS_DESC, StartYear3, EndYear3)
    OFNameRoot4 = "OWeathDryDF_%s_Std_%s-%s" % (DS_DESC, StartYear4, EndYear4)
    OFName1 = "%s.pickle" % OFNameRoot1
    OFName2 = "%s.pickle" % OFNameRoot2
    OFName3 = "%s.pickle" % OFNameRoot3
    OFName4 = "%s.pickle" % OFNameRoot4
    OutPickle1 = os.path.normpath( os.path.join( OUT_DIR1, OFName1 ) )
    OutPickle2 = os.path.normpath( os.path.join( OUT_DIR2, OFName2 ) )
    OutPickle3 = os.path.normpath( os.path.join( OUT_DIR3, OFName3 ) )
    OutPickle4 = os.path.normpath( os.path.join( OUT_DIR4, OFName4 ) )
    DryDF1.to_pickle( OutPickle1 )
    DryDF2.to_pickle( OutPickle2 )
    DryDF3.to_pickle( OutPickle3 )
    DryDF4.to_pickle( OutPickle4 )
    # write out the wrap up to the log file
    CurDT = dt.datetime.now()
    with open( LogFile, 'a' ) as LID:
        LID.write("\nFinish processing CMIP5 data at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
    # end of with block
    # end of work


#EOF