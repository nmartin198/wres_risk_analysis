# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 11:00:22 2019

@author: nmartin <nick.martin@stanfordalumni.org>

The purpose of this module is to extract the "other", non precipitation time 
series, load the daily means and standard deviations, and calculate Z-scores
for each non-precipitation. Determine the mean daily Z-score.

Then go back through and calculate the require coefficients for the A and
B matrices.

For the PRISM data, we can calculate daily relative humidity from the dew
point temperature.

use ...
https://www.vcalc.com/wiki/rklarsen/Calculating+Dew+Point+Temperature+from+Relative+Humidity

**does not work well **
T_d = T - ((100 -Rh)/5)

((100 - Rh)/5) = T - T_d

100 - Rh = ( T - T_d )/5
Rh = 100 - (( T - T_d)/5)

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
import pickle
from math import exp
from math import sqrt
# custom module import
import DBA_DClimComp as DBAD

# module level values for changing
START_DT = dt.datetime( 1981, 1, 1, 0, 0, 0 )
END_DT = dt.datetime( 2010, 12, 31, 0, 0, 0 )
WD_THRESH = 0.2   # in mm

# grid values and run descriptions. Only for CMIP5
#GD_START = 1
#GD_END = 168
#DS_DESC = "LOCA"
#GD_START = 169
#GD_END = 210
#DS_DESC = "BCCA"

OUT_DIR = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoch' \
          r'astic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weather'
WD_THRESH = 0.2   # in mm
#LogFile = "PRISMOWEx_Start_%s_%s.txt" % (DS_DESC, START_DT.strftime("%Y%m%d"))
LogFile = "PRISMOWZs_Start_%s.txt" % START_DT.strftime("%Y%m%d")
IN_WET_AVE = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Wet_Smooth_Ave_1981-2010.pickle'
IN_WET_STD = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Wet_Smooth_Std_1981-2010.pickle'
IN_DRY_AVE = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Dry_Smooth_Ave_1981-2010.pickle'
IN_DRY_STD = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Dry_Smooth_Std_1981-2010.pickle'

# other parameters
DOYR = "DayofYear"
TOTYRDAYS = 366
RELHUM = "RelHum"
A1 = 17.625
B1 = 243.04
CRelHum2 = lambda Td, Ta: ( 100.0 * exp( ( (A1*(Td/B1))-((Td/B1)*((A1*Ta)/(B1+Ta)))-
                                           ((A1*Ta)/(B1+Ta)) ) /
                                           ( 1.0 + (Td/B1) ) ) )
#CRelHum = lambda Td, Ta: 100.0 - (( Ta - Td)/5.0)

def AdjustRelHm( MaxRH, cRH ):
    """Adjust relative humidity that is calculated to be between 0 and 100
    percent. It is possible for relative humidity to be 105 or so but we
    want to keep all of our values in the standard range.
    
    Args:
        MaxRH (float): maximum relative humidity calculated for the current year
        cRH (float): current relative humidity value.
        
    Returns:
        adjRH (float): adjusted relative humidity
    """
    if cRH < 0.0:
        return 0.0
    # now look at max
    if MaxRH > 100.0:
        Scaler = 100.0 / MaxRH
    else:
        Scaler = 1.0
    return Scaler * cRH


# standalone execution block
if __name__ == '__main__':
    # make a log file entry
    CurDT = dt.datetime.now()
    with open( LogFile, 'w+' ) as LID:
        LID.write("Start processing PRISM data from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
        #LID.write("Downscaling method: %s\n" % DS_DESC)
        LID.write("Start date: %s\n" % START_DT.strftime("%m/%d/%Y") )
        LID.write("End date: %s\n\n" % END_DT.strftime("%m/%d/%Y") )
    # end of with block
    # get our smoothed, average data frames
    WetAveDF = pd.read_pickle( IN_WET_AVE )
    WetStdDF = pd.read_pickle( IN_WET_STD )
    DryAveDF = pd.read_pickle( IN_DRY_AVE )
    DryStdDF = pd.read_pickle( IN_DRY_STD )
    # create our query engine
    engine = sqlalchemy.create_engine( DBAD.DSN_STRING )
    # get our starting and ending years
    StartYear = START_DT.year
    EndYear = END_DT.year
    AllYrs = [ x for x in range( StartYear, (EndYear + 1), 1 )]
    # now get our PRISM grid
    GridSQL = DBAD.createSQLPRISMGrid()
    GridDF = pd.read_sql( GridSQL, engine, index_col=DBAD.FIELDN_ID )
    # Now have the Grid that need to go through
    NumGrid = len( GridDF )
    # next go through a year at time and then a grid point at a time and
    # build our data averages. Once we have averages then can do the standard
    # deviations
    WStateCnt = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DStateCnt = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMxRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMxMax = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMxMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMax = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMxMaxGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMxMinGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTAvRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTAvMax = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTAvMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TAvMax = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TAvMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TAvMaxGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TAvMinGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZTMnRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZTMnMax = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZTMnMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMax = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    TMnMaxGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    TMnMinGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZDpRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZDpMax = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZDpMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    DpMax = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    DpMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    DpMaxGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    DpMinGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    ZRHRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ZRHMax = np.ones( TOTYRDAYS, dtype=np.float32 )
    ZRHMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    RHMax = -10.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    RHMin = 999.0 * np.ones( TOTYRDAYS, dtype=np.float32 )
    RHMaxGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    RHMinGrd = np.zeros( TOTYRDAYS, dtype=np.int32 )
    # Set up our extraction columns
    ExCols = [ DBAD.FIELDN_DT, DBAD.FIELDN_PVAL, DBAD.FIELDN_TMXVAL,
               DBAD.FIELDN_TAVEVAL, DBAD.FIELDN_TMNVAL, DBAD.FIELDN_TDPT ]
    # now loop through so that can compile our means
    for yY in AllYrs:
        print("Working on ZAve year: %d" % yY)
        for gG in range( 1, (NumGrid + 1), 1):
            cGridID = GridDF.at[ gG, DBAD.FIELDN_GRIDIND ]
            # make our grid ids
            gIDArray = gG * np.ones( TOTYRDAYS, dtype=np.float32 )
            # get our query string
            ExSQL = DBAD.createSQLPRISMAllYear( gG, yY )
            # get the dataframe
            YrNodeDF = pd.read_sql( ExSQL, engine, columns=ExCols, 
                                    parse_dates=DBAD.FIELDN_DT, 
                                    index_col=DBAD.FIELDN_DT )
            # add in the day of year
            YrNodeDF[DOYR] = YrNodeDF.index.dayofyear
            NumDays = len( YrNodeDF )
            if NumDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # determine the state for the year
            WetState = np.where( np.array( YrNodeDF[ExCols[1]], 
                                           dtype=np.float32 ) > WD_THRESH, 1, 0 )
            DryState = 1 - WetState
            WStateCnt[:LastDay] = WStateCnt[:LastDay] + WetState
            DStateCnt[:LastDay] = DStateCnt[:LastDay] + DryState
            # calculate relative humidty
            YrNodeDF[RELHUM] = YrNodeDF.apply( lambda row: 
                                    CRelHum2( row[DBAD.FIELDN_TDPT], 
                                              row[DBAD.FIELDN_TAVEVAL]), 
                                              axis=1 )
            MaxRelHum = YrNodeDF[RELHUM].max()
            YrNodeDF[RELHUM] = YrNodeDF.apply( lambda row: 
                                                 AdjustRelHm( MaxRelHum, 
                                                              row[RELHUM] ), 
                                                              axis=1 )
            # now calculate Zs
            # max temperature
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMXVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            ZTMxRSum[:LastDay] = ZTMxRSum[:LastDay] + allZ
            ZTMxMax[:LastDay] = np.where( allZ > ZTMxMax[:LastDay], allZ, 
                                          ZTMxMax[:LastDay] )
            ZTMxMin[:LastDay] = np.where( allZ < ZTMxMin[:LastDay], allZ, 
                                          ZTMxMin[:LastDay] )
            TMxMax[:LastDay] = np.where( ctNew > TMxMax[:LastDay], ctNew, 
                                          TMxMax[:LastDay] )
            TMxMaxGrd[:LastDay] = np.where( ctNew > TMxMax[:LastDay], 
                                            gIDArray[:LastDay], 
                                            TMxMaxGrd[:LastDay] )
            TMxMin[:LastDay] = np.where( ctNew < TMxMin[:LastDay], ctNew, 
                                         TMxMin[:LastDay] )
            TMxMinGrd[:LastDay] = np.where( ctNew < TMxMin[:LastDay], 
                                            gIDArray[:LastDay], 
                                            TMxMinGrd[:LastDay] )
            # ave temp
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TAVEVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            ZTAvRSum[:LastDay] = ZTAvRSum[:LastDay] + allZ
            ZTAvMax[:LastDay] = np.where( allZ > ZTAvMax[:LastDay], allZ, 
                                          ZTAvMax[:LastDay] )
            ZTAvMin[:LastDay] = np.where( allZ < ZTAvMin[:LastDay], allZ, 
                                          ZTAvMin[:LastDay] )
            TAvMax[:LastDay] = np.where( ctNew > TAvMax[:LastDay], ctNew, 
                                          TAvMax[:LastDay] )
            TAvMaxGrd[:LastDay] = np.where( ctNew > TAvMax[:LastDay], 
                                            gIDArray[:LastDay], 
                                            TAvMaxGrd[:LastDay] )
            TAvMin[:LastDay] = np.where( ctNew < TAvMin[:LastDay], ctNew, 
                                         TAvMin[:LastDay] )
            TAvMinGrd[:LastDay] = np.where( ctNew < TAvMin[:LastDay], 
                                            gIDArray[:LastDay], 
                                            TAvMinGrd[:LastDay] )
            # min temp
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMNVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            ZTMnRSum[:LastDay] = ZTMnRSum[:LastDay] + allZ
            ZTMnMax[:LastDay] = np.where( allZ > ZTMnMax[:LastDay], allZ, 
                                          ZTMnMax[:LastDay] )
            ZTMnMin[:LastDay] = np.where( allZ < ZTMnMin[:LastDay], allZ, 
                                          ZTMnMin[:LastDay] )
            TMnMax[:LastDay] = np.where( ctNew > TMnMax[:LastDay], ctNew, 
                                          TMnMax[:LastDay] )
            TMnMaxGrd[:LastDay] = np.where( ctNew > TMnMax[:LastDay],  
                                            gIDArray[:LastDay], 
                                            TMnMaxGrd[:LastDay] )
            TMnMin[:LastDay] = np.where( ctNew < TMnMin[:LastDay], ctNew, 
                                         TMnMin[:LastDay] )
            TMnMinGrd[:LastDay] = np.where( ctNew < TMnMin[:LastDay],  
                                            gIDArray[:LastDay], 
                                            TMnMinGrd[:LastDay] )
            # dew point temperature
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TDPT], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            ZDpRSum[:LastDay] = ZDpRSum[:LastDay] + allZ
            ZDpMax[:LastDay] = np.where( allZ > ZDpMax[:LastDay], allZ, 
                                         ZDpMax[:LastDay] )
            ZDpMin[:LastDay] = np.where( allZ < ZDpMin[:LastDay], allZ, 
                                         ZDpMin[:LastDay] )
            DpMax[:LastDay] = np.where( ctNew > DpMax[:LastDay], ctNew, 
                                          DpMax[:LastDay] )
            DpMaxGrd[:LastDay] = np.where( ctNew > DpMax[:LastDay], 
                                           gIDArray[:LastDay], 
                                           DpMaxGrd[:LastDay] )
            DpMin[:LastDay] = np.where( ctNew < DpMin[:LastDay], ctNew, 
                                        DpMin[:LastDay] )
            DpMinGrd[:LastDay] = np.where( ctNew < DpMin[:LastDay], 
                                           gIDArray[:LastDay], 
                                           DpMinGrd[:LastDay] )
            # relative humidity
            ctNew = np.array( YrNodeDF[RELHUM], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            ZRHRSum[:LastDay] = ZRHRSum[:LastDay] + allZ
            ZRHMax[:LastDay] = np.where( allZ > ZRHMax[:LastDay], allZ, 
                                         ZRHMax[:LastDay] )
            ZRHMin[:LastDay] = np.where( allZ < ZRHMin[:LastDay], allZ, 
                                         ZRHMin[:LastDay] )
            RHMax[:LastDay] = np.where( ctNew > RHMax[:LastDay], ctNew, 
                                          RHMax[:LastDay] )
            RHMaxGrd[:LastDay] = np.where( ctNew > RHMax[:LastDay], 
                                           gIDArray[:LastDay], 
                                           RHMaxGrd[:LastDay] )
            RHMin[:LastDay] = np.where( ctNew < RHMin[:LastDay], ctNew, 
                                        RHMin[:LastDay] )
            RHMinGrd[:LastDay] = np.where( ctNew < RHMin[:LastDay], 
                                           gIDArray[:LastDay], 
                                           RHMinGrd[:LastDay] )
        # end of grid for
    # end of year for
    # calculate the day of the year averages and output
    AllStateCnt = WStateCnt + DStateCnt
    ZDDict = { "AllCounts" : AllStateCnt }
    ZMaxDict = { "AllCounts" : AllStateCnt,
                DBAD.FIELDN_TMXVAL : ZTMxMax,
                DBAD.FIELDN_TAVEVAL : ZTAvMax,
                DBAD.FIELDN_TMNVAL : ZTMnMax,
                DBAD.FIELDN_TDPT : ZDpMax,
                RELHUM : ZRHMax,
                }
    MaxDict = { "AllCounts" : AllStateCnt,
                DBAD.FIELDN_TMXVAL : TMxMax,
                "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMaxGrd,
                DBAD.FIELDN_TAVEVAL : TAvMax,
                "%s_GridId" % DBAD.FIELDN_TAVEVAL : TAvMaxGrd,
                DBAD.FIELDN_TMNVAL : TMnMax,
                "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMaxGrd,
                DBAD.FIELDN_TDPT : DpMax,
                "%s_GridId" % DBAD.FIELDN_TDPT : DpMaxGrd,
                RELHUM : RHMax,
                "%s_GridId" % RELHUM : RHMaxGrd,
                }
    ZMinDict = { "AllCounts" : AllStateCnt,
                DBAD.FIELDN_TMXVAL : ZTMxMin,
                DBAD.FIELDN_TAVEVAL : ZTAvMin,
                DBAD.FIELDN_TMNVAL : ZTMnMin,
                DBAD.FIELDN_TDPT : ZDpMin,
                RELHUM : ZRHMin,
                }
    MinDict = { "AllCounts" : AllStateCnt,
                DBAD.FIELDN_TMXVAL : TMxMin,
                "%s_GridId" % DBAD.FIELDN_TMXVAL : TMxMinGrd,
                DBAD.FIELDN_TAVEVAL : TAvMin,
                "%s_GridId" % DBAD.FIELDN_TAVEVAL : TAvMinGrd,
                DBAD.FIELDN_TMNVAL : TMnMin,
                "%s_GridId" % DBAD.FIELDN_TMNVAL : TMnMinGrd,
                DBAD.FIELDN_TDPT : DpMin,
                "%s_GridId" % DBAD.FIELDN_TDPT : DpMinGrd,
                RELHUM : RHMin,
                "%s_GridId" % RELHUM : RHMinGrd,
                }
    # get the wet and dry counts in fractional form for multiplication
    zDenom = np.where( AllStateCnt > 0, np.array( AllStateCnt, dtype=np.float32),
                       np.nan )
    zMulti = 1.0 / zDenom
    # max temp
    zAve = zMulti * ZTMxRSum
    ZDDict[DBAD.FIELDN_TMXVAL] = zAve
    # ave temp
    zAve = zMulti * ZTAvRSum
    ZDDict[DBAD.FIELDN_TAVEVAL] = zAve
    # min temp
    zAve = zMulti * ZTMnRSum
    ZDDict[DBAD.FIELDN_TMNVAL] = zAve
    # dew point
    zAve = zMulti * ZDpRSum
    ZDDict[DBAD.FIELDN_TDPT] = zAve
    # relative humidity
    zAve = zMulti * ZRHRSum
    ZDDict[RELHUM] = zAve
    # build our data frame
    DaysIndexer = [ x for x in range(1, (TOTYRDAYS + 1), 1)]
    ZAveDF = pd.DataFrame( index=DaysIndexer, data=ZDDict )
    ZMaxDF = pd.DataFrame( index=DaysIndexer, data=ZMaxDict )
    ZMinDF = pd.DataFrame( index=DaysIndexer, data=ZMinDict )
    MaxDF = pd.DataFrame( index=DaysIndexer, data=MaxDict )
    MinDF = pd.DataFrame( index=DaysIndexer, data=MinDict )
    # now we have our average daily Z score for each variable. Need to go
    #  back through and calculate our coefficients
    r0_12_numer = 0.0
    r0_12_1denom = 0.0
    r0_12_2denom = 0.0
    r0dp_13_numer = 0.0
    r0dp_13_1denom = 0.0
    r0dp_13_3denom = 0.0
    r0dp_23_numer = 0.0
    r0dp_23_2denom = 0.0
    r0dp_23_3denom = 0.0
    r0rh_13_numer = 0.0
    r0rh_13_1denom = 0.0
    r0rh_13_3denom = 0.0
    r0rh_23_numer = 0.0
    r0rh_23_2denom = 0.0
    r0rh_23_3denom = 0.0
    r1_11_numer = 0.0
    r1_11_0denom = 0.0
    r1_11_1denom = 0.0
    r1_12_numer = 0.0
    r1_12_1denom = 0.0
    r1_12_2denom = 0.0
    r1_21_numer = 0.0
    r1_21_1denom = 0.0
    r1_21_2denom = 0.0
    r1_22_numer = 0.0
    r1_22_0denom = 0.0
    r1_22_1denom = 0.0
    r1dp_33_numer = 0.0
    r1dp_33_0denom = 0.0
    r1dp_33_1denom = 0.0
    r1dp_13_numer = 0.0
    r1dp_13_1denom = 0.0
    r1dp_13_3denom = 0.0
    r1dp_31_numer = 0.0
    r1dp_31_1denom = 0.0
    r1dp_31_3denom = 0.0
    r1dp_23_numer = 0.0
    r1dp_23_2denom = 0.0
    r1dp_23_3denom = 0.0
    r1dp_32_numer = 0.0
    r1dp_32_2denom = 0.0
    r1dp_32_3denom = 0.0
    r1rh_33_numer = 0.0
    r1rh_33_0denom = 0.0
    r1rh_33_1denom = 0.0
    r1rh_13_numer = 0.0
    r1rh_13_1denom = 0.0
    r1rh_13_3denom = 0.0
    r1rh_31_numer = 0.0
    r1rh_31_1denom = 0.0
    r1rh_31_3denom = 0.0
    r1rh_23_numer = 0.0
    r1rh_23_2denom = 0.0
    r1rh_23_3denom = 0.0
    r1rh_32_numer = 0.0
    r1rh_32_2denom = 0.0
    r1rh_32_3denom = 0.0
    for yY in AllYrs:
        print("Working on correlation year: %d" % yY)
        for gG in range( 1, (NumGrid + 1), 1):
            cGridID = GridDF.at[ gG, DBAD.FIELDN_GRIDIND ]
            # get our query string
            ExSQL = DBAD.createSQLPRISMAllYear( gG, yY )
            # get the dataframe
            YrNodeDF = pd.read_sql( ExSQL, engine, columns=ExCols, 
                                    parse_dates=DBAD.FIELDN_DT, 
                                    index_col=DBAD.FIELDN_DT )
            # add in the day of year
            YrNodeDF[DOYR] = YrNodeDF.index.dayofyear
            NumDays = len( YrNodeDF )
            if NumDays > 365:
                LastDay = TOTYRDAYS
            else:
                LastDay = ( TOTYRDAYS - 1 )
            # determine the state for the year
            WetState = np.where( np.array( YrNodeDF[ExCols[1]], 
                                           dtype=np.float32 ) > WD_THRESH, 1, 0 )
            DryState = 1 - WetState
            WStateCnt[:LastDay] = WStateCnt[:LastDay] + WetState
            DStateCnt[:LastDay] = DStateCnt[:LastDay] + DryState
            # calculate relative humidty
            YrNodeDF[RELHUM] = YrNodeDF.apply( lambda row: 
                                    CRelHum2( row[DBAD.FIELDN_TDPT], 
                                              row[DBAD.FIELDN_TAVEVAL]), 
                                              axis=1 )
            MaxRelHum = YrNodeDF[RELHUM].max()
            YrNodeDF[RELHUM] = YrNodeDF.apply( lambda row: 
                                                 AdjustRelHm( MaxRelHum, 
                                                              row[RELHUM] ), 
                                                              axis=1 )
            # now calculate Zs
            # max temperature
            AveZ = np.array( ZAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                             dtype=np.float32 )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMXVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            DiffZ1_0 = allZ - AveZ
            DiffSqZ1_0 = (allZ - AveZ)**2.0
            DiffZ1_1 = ( np.roll( allZ, 1 ) - AveZ )
            # min temp
            AveZ = np.array( ZAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                             dtype=np.float32 )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMNVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            DiffZ2_0 = allZ - AveZ
            DiffSqZ2_0 = (allZ - AveZ)**2.0
            DiffZ2_1 = ( np.roll( allZ, 1 ) - AveZ )
            # dew point temperature
            AveZ = np.array( ZAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                             dtype=np.float32 )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TDPT], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            DiffZ3dp_0 = allZ - AveZ
            DiffSqZ3dp_0 = (allZ - AveZ)**2.0
            DiffZ3dp_1 = ( np.roll( allZ, 1 ) - AveZ )
            # relative humidity
            AveZ = np.array( ZAveDF.loc[:LastDay, RELHUM], 
                             dtype=np.float32 )
            ctNew = np.array( YrNodeDF[RELHUM], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctWStd = np.array( WetStdDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctDStd = np.array( DryStdDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            wZs = ( WetState * ( ( ctNew - ctWAve ) / ctWStd ) )
            dZs = ( DryState * ( ( ctNew - ctDAve ) / ctDStd ) )
            allZ = wZs + dZs
            DiffZ3rh_0 = allZ - AveZ
            DiffSqZ3rh_0 = (allZ - AveZ)**2.0
            DiffZ3rh_1 = ( np.roll( allZ, 1 ) - AveZ )
            # now do our running sums
            r0_12_numer = r0_12_numer + np.dot( DiffZ1_0, DiffZ2_0 )
            r0_12_1denom = r0_12_1denom + DiffSqZ1_0.sum()
            r0_12_2denom = r0_12_2denom + DiffSqZ2_0.sum()
            r0dp_13_numer = r0dp_13_numer + np.dot( DiffZ1_0, DiffZ3dp_0 )
            r0dp_13_1denom = r0dp_13_1denom + DiffSqZ1_0.sum()
            r0dp_13_3denom = r0dp_13_3denom + DiffSqZ3dp_0.sum()
            r0dp_23_numer = r0dp_23_numer + np.dot( DiffZ2_0, DiffZ3dp_0 )
            r0dp_23_2denom = r0dp_23_2denom + DiffSqZ2_0.sum()
            r0dp_23_3denom = r0dp_23_3denom + DiffSqZ3dp_0.sum()
            r0rh_13_numer =  r0rh_13_numer + np.dot( DiffZ1_0, DiffZ3rh_0 )
            r0rh_13_1denom = r0rh_13_1denom + DiffSqZ1_0.sum()
            r0rh_13_3denom = r0rh_13_3denom + DiffSqZ3rh_0.sum()
            r0rh_23_numer = r0rh_23_numer + np.dot( DiffZ2_0, DiffZ3rh_0 )
            r0rh_23_2denom = r0rh_23_2denom + DiffSqZ2_0.sum()
            r0rh_23_3denom = r0rh_23_3denom + DiffSqZ3rh_0.sum()
            r1_11_numer = r1_11_numer + np.dot( DiffZ1_0, DiffZ1_1 )
            r1_11_0denom = r1_11_0denom + DiffSqZ1_0.sum()
            r1_11_1denom = r1_11_1denom + DiffSqZ1_0.sum()
            r1_12_numer = r1_12_numer + np.dot( DiffZ1_0, DiffZ2_1 )
            r1_12_1denom = r1_12_1denom + DiffSqZ1_0.sum()
            r1_12_2denom = r1_12_2denom + DiffSqZ2_0.sum()
            r1_21_numer = r1_21_numer + np.dot( DiffZ2_0, DiffZ1_1 )
            r1_21_1denom = r1_21_1denom + DiffSqZ1_0.sum()
            r1_21_2denom = r1_21_2denom + DiffSqZ2_0.sum()
            r1_22_numer = r1_22_numer + np.dot( DiffZ2_0, DiffZ2_1 )
            r1_22_0denom = r1_22_0denom + DiffSqZ2_0.sum()
            r1_22_1denom = r1_22_1denom + DiffSqZ2_0.sum()
            r1dp_33_numer = r1dp_33_numer + np.dot( DiffZ3dp_0, DiffZ3dp_1 )
            r1dp_33_0denom = r1dp_33_0denom + DiffSqZ3dp_0.sum()
            r1dp_33_1denom = r1dp_33_1denom + DiffSqZ3dp_0.sum()
            r1dp_13_numer = r1dp_13_numer + np.dot( DiffZ1_0, DiffZ3dp_1 )
            r1dp_13_1denom = r1dp_13_1denom + DiffSqZ1_0.sum()
            r1dp_13_3denom = r1dp_13_3denom + DiffSqZ3dp_0.sum()
            r1dp_31_numer = r1dp_31_numer + np.dot( DiffZ3dp_0, DiffZ1_1 )
            r1dp_31_1denom = r1dp_31_1denom + DiffSqZ1_0.sum()
            r1dp_31_3denom = r1dp_31_3denom + DiffSqZ3dp_0.sum()
            r1dp_23_numer = r1dp_23_numer + np.dot( DiffZ2_0, DiffZ3dp_1 )
            r1dp_23_2denom = r1dp_23_2denom + DiffSqZ2_0.sum()
            r1dp_23_3denom = r1dp_23_3denom + DiffSqZ3dp_0.sum()
            r1dp_32_numer = r1dp_32_numer + np.dot( DiffZ3dp_0, DiffZ2_1 )
            r1dp_32_2denom = r1dp_32_2denom + DiffSqZ2_0.sum()
            r1dp_32_3denom = r1dp_32_3denom + DiffSqZ3dp_0.sum()
            r1rh_33_numer = r1rh_33_numer + np.dot( DiffZ3rh_0, DiffZ3rh_1 )
            r1rh_33_0denom = r1rh_33_0denom + DiffSqZ3rh_0.sum()
            r1rh_33_1denom = r1rh_33_1denom + DiffSqZ3rh_0.sum()
            r1rh_13_numer = r1rh_13_numer + np.dot( DiffZ1_0, DiffZ3rh_1 )
            r1rh_13_1denom = r1rh_13_1denom + DiffSqZ1_0.sum()
            r1rh_13_3denom = r1rh_13_3denom + DiffSqZ3rh_0.sum()
            r1rh_31_numer = r1rh_31_numer + np.dot( DiffZ3rh_0, DiffZ1_1 )
            r1rh_31_1denom = r1rh_31_1denom + DiffSqZ1_0.sum()
            r1rh_31_3denom = r1rh_31_3denom + DiffSqZ3rh_0.sum()
            r1rh_23_numer = r1rh_23_numer + np.dot( DiffZ2_0, DiffZ3rh_1 )
            r1rh_23_2denom = r1rh_23_2denom + DiffSqZ2_0.sum()
            r1rh_23_3denom = r1rh_23_3denom + DiffSqZ3rh_0.sum()
            r1rh_32_numer = r1rh_32_numer + np.dot( DiffZ3rh_0, DiffZ2_1 )
            r1rh_32_2denom = r1rh_32_2denom + DiffSqZ2_0.sum()
            r1rh_32_3denom = r1rh_32_3denom + DiffSqZ3rh_0.sum()
        # end of grid for
    # end of year for
    # calculate our coefficients
    r0_12 = r0_12_numer / ( sqrt(r0_12_1denom) * sqrt(r0_12_2denom))
    r0dp_13 = r0dp_13_numer / ( sqrt(r0dp_13_1denom) * sqrt(r0dp_13_3denom))
    r0rh_13 = r0rh_13_numer / ( sqrt(r0rh_13_1denom) * sqrt(r0rh_13_3denom))
    r0dp_23 = r0dp_23_numer / ( sqrt(r0dp_23_2denom) * sqrt(r0dp_23_3denom))
    r0rh_23 = r0rh_23_numer / ( sqrt(r0rh_23_2denom) * sqrt(r0rh_23_3denom))
    r1_11 = r1_11_numer / ( sqrt(r1_11_0denom) * sqrt(r1_11_1denom) )
    r1_22 = r1_22_numer / ( sqrt(r1_22_0denom) * sqrt(r1_22_1denom) )
    r1rh_33 = r1rh_33_numer / ( sqrt(r1rh_33_0denom) * sqrt(r1rh_33_1denom) )
    r1dp_33 = r1dp_33_numer / ( sqrt(r1dp_33_0denom) * sqrt(r1dp_33_1denom) )
    r1_12 = r1_12_numer / ( sqrt(r1_12_1denom) * sqrt(r1_12_2denom) )
    r1_21 = r1_21_numer / ( sqrt(r1_21_2denom) * sqrt(r1_21_1denom) )
    r1dp_13 = r1dp_13_numer / ( sqrt(r1dp_13_1denom) * sqrt(r1dp_13_3denom) )
    r1dp_31 = r1dp_31_numer / ( sqrt(r1dp_31_3denom) * sqrt(r1dp_31_1denom) )
    r1rh_13 = r1rh_13_numer / ( sqrt(r1rh_13_1denom) * sqrt(r1rh_13_3denom) )
    r1rh_31 = r1rh_31_numer / ( sqrt(r1rh_31_3denom) * sqrt(r1rh_31_1denom) )
    r1dp_23 = r1dp_23_numer / ( sqrt(r1dp_23_2denom) * sqrt(r1dp_23_3denom) )
    r1dp_32 = r1dp_32_numer / ( sqrt(r1dp_32_3denom) * sqrt(r1dp_32_2denom) )
    r1rh_23 = r1rh_23_numer / ( sqrt(r1rh_23_2denom) * sqrt(r1rh_23_3denom) )
    r1rh_32 = r1rh_32_numer / ( sqrt(r1rh_32_3denom) * sqrt(r1rh_32_2denom) )
    # now make our data frames
    # rho 0 correlation
    r0dpDDict = { "rho_X1" : [ 1.0, r0_12, r0dp_13],
                  "rho_X2" : [ r0_12, 1.0, r0dp_23],
                  "rho_X3" : [ r0dp_13, r0dp_23, 1.0 ],
                  }
    r0rhDDict = { "rho_X1" : [ 1.0, r0_12, r0rh_13],
                  "rho_X2" : [ r0_12, 1.0, r0rh_23],
                  "rho_X3" : [ r0rh_13, r0rh_23, 1.0 ],
                  }
    r0Ind = [ "rho_1X", "rho_2X", "rho_3X" ]
    r0dpDF = pd.DataFrame( index=r0Ind, data=r0dpDDict )
    r0rhDF = pd.DataFrame( index=r0Ind, data=r0rhDDict )
    # rho 1 cross-correlation
    r1dpDDict = { "rho_X1_L1" : [ r1_11, r1_12, r1dp_13],
                  "rho_X2_L1" : [ r1_21, r1_22, r1dp_23],
                  "rho_X3_L1" : [ r1dp_31, r1dp_32, r1dp_33 ],
                  }
    r1rhDDict = { "rho_X1_L1" : [ r1_11, r1_12, r1rh_13],
                  "rho_X2_L1" : [ r1_21, r1_22, r1rh_23],
                  "rho_X3_L1" : [ r1rh_31, r1rh_32, r1rh_33 ],
                  }
    r1dpDF = pd.DataFrame( index=r0Ind, data=r1dpDDict )
    r1rhDF = pd.DataFrame( index=r0Ind, data=r1rhDDict )
    # output to Excel
    OFNameRoot = "OWeather_Zs_%s-%s" % (StartYear, EndYear)
    OFName = "%s.xlsx" % OFNameRoot
    OutXLSX = os.path.normpath( os.path.join( OUT_DIR, OFName ))
    with pd.ExcelWriter(OutXLSX) as writer:
        r0dpDF.to_excel( writer, sheet_name="M0_dp", index=True )
        r0rhDF.to_excel( writer, sheet_name="M0_rh", index=True )
        r1dpDF.to_excel( writer, sheet_name="M1_dp", index=True )
        r1rhDF.to_excel( writer, sheet_name="M1_rh", index=True )
        ZAveDF.to_excel( writer, sheet_name="Z_Aves", index=True, 
                        index_label="Days", na_rep=str(np.nan))
        ZMaxDF.to_excel( writer, sheet_name="Z_Maxs", index=True, 
                        index_label="Days", na_rep=str(np.nan))
        ZMinDF.to_excel( writer, sheet_name="Z_Mins", index=True, 
                        index_label="Days", na_rep=str(np.nan))
        MaxDF.to_excel( writer, sheet_name="Maxs", index=True, 
                        index_label="Days", na_rep=str(np.nan))
        MinDF.to_excel( writer, sheet_name="Mins", index=True, 
                        index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeath_Z_M0dp_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    r0dpDF.to_pickle( OutPickle )
    OFNameRoot = "OWeath_Z_M0rh_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    r0rhDF.to_pickle( OutPickle )
    OFNameRoot = "OWeath_Z_M1dp_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    r1dpDF.to_pickle( OutPickle )
    OFNameRoot = "OWeath_Z_M1rh_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    r1rhDF.to_pickle( OutPickle )
    OFNameRoot = "OWeath_ZAve_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    ZAveDF.to_pickle( OutPickle )
    # end of work
    CurDT = dt.datetime.now()
    with open( LogFile, 'a' ) as LID:
        LID.write("Finished processing PRISM Zs from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
    # end of with block


#EOF