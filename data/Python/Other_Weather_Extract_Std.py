# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 11:00:22 2019

@author: nmartin <nick.martin@stanfordalumni.org>

The purpose of this module is to extract the "other", non precipitation time 
series along with the wet state for the day and to produce day of the year 
standard deviations (for each state).

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
LogFile = "PRISMOWEx_Start_%s.txt" % START_DT.strftime("%Y%m%d")
IN_WET_AVE = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Wet_Smooth_Ave_1981-2010.pickle'
IN_DRY_AVE = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
             r'hastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weat' \
             r'her\OWeath_Dry_Smooth_Ave_1981-2010.pickle'

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
    DryAveDF = pd.read_pickle( IN_DRY_AVE )
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
    TMxWRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TAvWRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnWRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    DpWRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    RHWRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMxDRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TAvDRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    TMnDRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    RHDRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    DpDRSum = np.zeros( TOTYRDAYS, dtype=np.float32 )
    ExSQL = DBAD.createSQLPRISMAllYear( 2, 1982 )
    # Set up our extraction columns
    ExCols = [ DBAD.FIELDN_DT, DBAD.FIELDN_PVAL, DBAD.FIELDN_TMXVAL,
               DBAD.FIELDN_TAVEVAL, DBAD.FIELDN_TMNVAL, DBAD.FIELDN_TDPT ]
    # now loop through so that can compile our means
    for yY in AllYrs:
        print("Working on year: %d" % yY)
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
            # now can add values to our running sum
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMXVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMXVAL], 
                               dtype=np.float32 )
            TMxWRSum[:LastDay] = ( TMxWRSum[:LastDay] + ( WetState *
                                   ( ctNew - ctWAve )**2.0 ) )
            TMxDRSum[:LastDay] = ( TMxDRSum[:LastDay] + ( DryState *
                                   ( ctNew - ctDAve )**2.0 ) )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TAVEVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TAVEVAL], 
                               dtype=np.float32 )
            TAvWRSum[:LastDay] = ( TAvWRSum[:LastDay] + ( WetState *
                                   ( ctNew - ctWAve )**2.0 ) )
            TAvDRSum[:LastDay] = ( TAvDRSum[:LastDay] + ( DryState *
                                   ( ctNew - ctDAve )**2.0 ) )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TMNVAL], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TMNVAL], 
                               dtype=np.float32 )
            TMnWRSum[:LastDay] = ( TMnWRSum[:LastDay] + ( WetState *
                                   ( ctNew - ctWAve )**2.0 ) )
            TMnDRSum[:LastDay] = ( TMnDRSum[:LastDay] + ( DryState *
                                   ( ctNew - ctDAve )**2.0 ) )
            ctNew = np.array( YrNodeDF[DBAD.FIELDN_TDPT], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, DBAD.FIELDN_TDPT], 
                               dtype=np.float32 )
            DpWRSum[:LastDay] = ( DpWRSum[:LastDay] + ( WetState *
                                   ( ctNew - ctWAve )**2.0 ) )
            DpDRSum[:LastDay] = ( DpDRSum[:LastDay] + ( DryState *
                                   ( ctNew - ctDAve )**2.0 ) )
            ctNew = np.array( YrNodeDF[RELHUM], dtype=np.float32 )
            ctWAve = np.array( WetAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            ctDAve = np.array( DryAveDF.loc[:LastDay, RELHUM], 
                               dtype=np.float32 )
            RHWRSum[:LastDay] = ( RHWRSum[:LastDay] + ( WetState *
                                   ( ctNew - ctWAve )**2.0 ) )
            RHDRSum[:LastDay] = ( RHDRSum[:LastDay] + ( DryState *
                                   ( ctNew - ctDAve )**2.0 ) )
        # end of grid for
    # end of year for
    # calculate the day of the year averages and output
    WDDict = { "Wet Counts" : WStateCnt }
    DDDict = { "Dry Counts" : DStateCnt }
    # get the wet and dry counts in fractional form for multiplication
    wDenom = np.where( WStateCnt > 0, np.array( WStateCnt, dtype=np.float32),
                       np.nan )
    wDenom = wDenom - 1
    wMulti = 1.0 / wDenom
    dDenom = np.where( DStateCnt > 0, np.array( DStateCnt, dtype=np.float32),
                       np.nan )
    dDenom = dDenom - 1
    dMulti = 1.0 / dDenom
    # max temp
    tWAve = wMulti * TMxWRSum
    tDAve = dMulti * TMxDRSum
    WDDict[DBAD.FIELDN_TMXVAL] = np.sqrt( tWAve )
    DDDict[DBAD.FIELDN_TMXVAL] = np.sqrt( tDAve )
    # ave temp
    tWAve = wMulti * TAvWRSum
    tDAve = dMulti * TAvDRSum
    WDDict[DBAD.FIELDN_TAVEVAL] = np.sqrt( tWAve )
    DDDict[DBAD.FIELDN_TAVEVAL] = np.sqrt( tDAve )
    # min temp
    tWAve = wMulti * TMnWRSum
    tDAve = dMulti * TMnDRSum
    WDDict[DBAD.FIELDN_TMNVAL] = np.sqrt( tWAve )
    DDDict[DBAD.FIELDN_TMNVAL] = np.sqrt( tDAve )
    # dew point
    tWAve = wMulti * DpWRSum
    tDAve = dMulti * DpDRSum
    WDDict[DBAD.FIELDN_TDPT] = np.sqrt( tWAve )
    DDDict[DBAD.FIELDN_TDPT] = np.sqrt( tDAve )
    # relative humidity
    tWAve = wMulti * RHWRSum
    tDAve = dMulti * RHDRSum
    WDDict[RELHUM] = np.sqrt( tWAve )
    DDDict[RELHUM] = np.sqrt( tDAve )
    # build our data frames
    DaysIndexer = [ x for x in range(1, (TOTYRDAYS + 1), 1)]
    WetDF = pd.DataFrame( index=DaysIndexer, data=WDDict )
    DryDF = pd.DataFrame( index=DaysIndexer, data=DDDict )
    # output to Excel
    OFNameRoot = "OWeather_Std_%s-%s" % (StartYear, EndYear)
    OFName = "%s.xlsx" % OFNameRoot
    OutXLSX = os.path.normpath( os.path.join( OUT_DIR, OFName ))
    with pd.ExcelWriter(OutXLSX) as writer:
        WetDF.to_excel( writer, sheet_name="Wet Days", index=True, 
                        index_label="Days", na_rep=str(np.nan))
        DryDF.to_excel( writer, sheet_name="Dry Days", index=True, 
                        index_label="Days", na_rep=str(np.nan))
    # now write some pickle files
    OFNameRoot = "OWeathWetDF_Std_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    WetDF.to_pickle( OutPickle )
    OFNameRoot = "OWeathDryDF_Std_%s-%s" % (StartYear, EndYear)
    OFName = "%s.pickle" % OFNameRoot
    OutPickle = os.path.normpath( os.path.join( OUT_DIR, OFName ) )
    DryDF.to_pickle( OutPickle )
    # end of work


#EOF