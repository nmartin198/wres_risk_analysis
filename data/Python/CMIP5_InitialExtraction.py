# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 09:51:17 2019

@author: nmartin <nick.martin@stanfordalumni.org>

Script to handle the initial extraction of model results. Memory issues 
because of the size.
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

# custom module import
import DBA_DClimComp as DBAD

# module level values for changing
#START_DT = dt.datetime( 2011, 1, 1, 0, 0, 0 )
#END_DT = dt.datetime( 2040, 12, 31, 0, 0, 0 )
#START_DT = dt.datetime( 2041, 1, 1, 0, 0, 0 )
#END_DT = dt.datetime( 2070, 12, 31, 0, 0, 0 )
START_DT = dt.datetime( 2071, 1, 1, 0, 0, 0 )
END_DT = dt.datetime( 2100, 12, 31, 0, 0, 0 )
# grid values and run descriptions
GD_START = 1
GD_END = 168
DS_DESC = "LOCA"
#GD_START = 169
#GD_END = 210
#DS_DESC = "BCCA"

# module level values that might not need to be changed
OUT_DIR = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Sto' \
          r'chastic_CC_Recharge\Data\JNotes\Processed\CMIP5'
WD_THRESH = 0.2   # in mm
LogFile = "Log_Start_%s_%s.txt" % (DS_DESC, START_DT.strftime("%Y%m%d"))

# standalone execution block
if __name__ == '__main__':
    # make a log file entry
    CurDT = dt.datetime.now()
    with open( LogFile, 'w+' ) as LID:
        LID.write("Start processing CMIP5 data from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
        LID.write("Downscaling method: %s\n" % DS_DESC)
        LID.write("Start date: %s\n" % START_DT.strftime("%m/%d/%Y") )
        LID.write("End date: %s\n\n" % END_DT.strftime("%m/%d/%Y") )
    # end of with block
    # first get our SQL connection
    engine = sqlalchemy.create_engine( DBAD.DSN_STRING )
    # acquire the grid definition as a Pandas dataframe
    GridSQL = DBAD.createSQLCMIP5Grid()
    GridDF = pd.read_sql( GridSQL, engine, index_col=DBAD.FIELDN_ID )
    # get the gridd columns
    GridCols = list( GridDF.columns )
    if len( GridCols ) < 1:
        print("Could not acquire grid dataframe!!!!")
        sys.exit([-1])
    # get the model definition
    ModelSQL = DBAD.createSQLCMIP5Model()
    ModelDF = pd.read_sql( ModelSQL, engine, index_col=DBAD.FIELDN_ID )
    ModelCols = list( ModelDF.columns )
    if len( ModelCols ) < 1:
        print("Could not acquire model dataframe!!!!")
        sys.exit([-1])
    # initialize our dictionaries
    DryDict = dict()
    WetDict = dict()
    NumGPts = len( GridDF )
    NumMods = len( ModelDF )
    with open( LogFile, 'a' ) as LID:
        LID.write("%d grid points and %d models\n\n" % (NumGPts, NumMods))
    # end of with
    # now main loop for data collation
    FirstModel = False
    for iI in range(GD_START, (GD_END + 1)):
        GridInd = iI
        GridUTMX = float( GridDF.at[iI, GridCols[2]] )
        GridUTMY = float( GridDF.at[iI, GridCols[3]] )
        for jJ in range(1, (NumMods + 1)):
            ModInd = jJ
            # make our joint index
            JntInd = "M%d_%d" % (ModInd, GridInd)
            # now are ready to get our precipitation values
            PreSQL = DBAD.createSQLCMIP5Pre( START_DT, END_DT, iI, jJ )
            PreDF = pd.read_sql( PreSQL, engine, index_col=DBAD.FIELDN_STRDT, 
                                 parse_dates=[DBAD.FIELDN_STRDT] )
            if len( PreDF ) < 1:
                #print("No values for %s" % JntInd)
                continue
            PreDF.index.name = DBAD.FIELDN_DT
            PreDF.index = PreDF.index.tz_convert( None )
            # now do the resample 
            MonDF = PreDF.resample( 'MS', axis=0, closed='left', label='left' ).sum()
            AnnDF = PreDF.resample( 'AS', axis=0, closed='left', label='left' ).sum()
            # change the column names
            MonDF.columns = ["Precip_mm"]
            AnnDF.columns = ["Precip_mm"]
            # now make our appends
            GMonDF = MonDF.copy()
            GMonDF.columns = [JntInd]
            GAnnDF = AnnDF.copy()
            GAnnDF.columns = [JntInd]
            # now check where we are
            if (iI == GD_START) and (not FirstModel):
                FirstModel = True
                AllMonDF = GMonDF.copy()
                AllAnnDF = GAnnDF.copy()
            else:
                AllMonDF = AllMonDF.merge( GMonDF, how='inner', 
                                           left_index=True, right_index=True)
                AllAnnDF = AllAnnDF.merge( GAnnDF, how='inner', 
                                           left_index=True, right_index=True)
            # the resampling is done so now want go through and get our counts 
            #  of contiguous wet days and contiguous dry days. Also track the 
            #  start date for the contiguous series and track the total depth 
            #  for wet series and the daily depth within the wet series.
            cNumDays = len( PreDF )
            inWet = False
            inDry = False
            cWetCnt = 0
            cDryCnt = 0
            DryList = list()
            WetList = list()
            for dD in range( cNumDays ):
                cTSInd = PreDF.index[dD]
                cDT = dt.datetime( cTSInd.year, cTSInd.month, cTSInd.day )
                if dD == 0:
                    cWStartDT = cDT
                    cDStartDT = cDT
                cPDepth = float( PreDF.at[cTSInd,'Precip_mmpd'] )
                if cPDepth >= WD_THRESH:
                    # this is the wet day case
                    if inWet:
                        cWetCnt += 1
                        totPrecip += cPDepth
                        dayPreL.append( cPDepth )
                    else:
                        inWet = True
                        inDry = False
                        cWStartDT = cDT
                        cWetCnt = 1
                        dayPreL = [ cPDepth ]
                        totPrecip = cPDepth
                        if dD > 0:
                            DryList.append( [ cDStartDT, cDryCnt ] )
                            cDryCnt = 0
                else:
                    # this is the dry day case
                    if inDry:
                        cDryCnt += 1
                    else:
                        inWet = False
                        inDry = True
                        cDStartDT = cDT
                        cDryCnt = 1
                        if dD > 0:
                            WetList.append( [ cWStartDT, cWetCnt, totPrecip, dayPreL ] )
                            cWetCnt = 0
                            totPrecip = 0.0
                            dayPreL = list()
                # end of outer depth if
            # end of the day for
            # check for the last entry
            if inWet:
                WetList.append( [ cWStartDT, cWetCnt, totPrecip, dayPreL ] )
            else:
                DryList.append( [ cDStartDT, cDryCnt ] )
            # add our state analysis lists to our dictionaries
            DryDict[JntInd] = DryList
            WetDict[JntInd] = WetList
        # end of inner for loop
        # output for logging
        with open( LogFile, 'a' ) as LID:
            LID.write("Finished grid index %d\n" % GridInd)
        # end of with block
    # end of outer for loop
    # now need to output the monthly and annual values
    CFName = "AllMonth_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    MonPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllMonDF.to_pickle( MonPCKF )
    CFName = "AllYears_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    AnnPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    AllAnnDF.to_pickle( AnnPCKF )
    CFName = "DryDict_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    DryPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    with open( DryPCKF, 'wb' ) as PCF:
        pickle.dump( DryDict, PCF, protocol=pickle.HIGHEST_PROTOCOL )
    CFName = "WetDict_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    WetPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    with open( WetPCKF, 'wb' ) as PCF:
        pickle.dump( WetDict, PCF, protocol=pickle.HIGHEST_PROTOCOL )
    # next need to modify for R output
    FAllMonDF = AllMonDF.copy()
    FAllAnnDF = AllAnnDF.copy()
    FAllMonDF = FAllMonDF.reset_index()
    FAllAnnDF = FAllAnnDF.reset_index()
    CFName = "AllMonth_%s_%d-%d.feather" % ( DS_DESC, START_DT.year, END_DT.year )
    MonFeatherF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    FAllMonDF.to_feather( MonFeatherF )
    CFName = "AllYears_%s_%d-%d.feather" % ( DS_DESC, START_DT.year, END_DT.year )
    AnnFeatherF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    FAllAnnDF.to_feather( AnnFeatherF )
    # finally output to Excel
    AllMonDF = AllMonDF.transpose()
    AllAnnDF = AllAnnDF.transpose()
    CFName = "Precip_Agg_%s_%d-%d.xlsx" % ( DS_DESC, START_DT.year, END_DT.year )
    OutXLSX = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    with pd.ExcelWriter(OutXLSX) as writer:
        GridDF.to_excel( writer, sheet_name="Grid_Metadata", na_rep=str(np.nan),
                         index=True, index_label="Id" )
        AllMonDF.to_excel( writer, sheet_name="Monthly", na_rep=str(np.nan),
                           index=True, index_label="Model_and_Grid" )
        AllAnnDF.to_excel( writer, sheet_name="Annual", na_rep=str(np.nan),
                           index=True, index_label="Model_and_Grid" )
    # end of with and write output
    # next delete some DataFrames to try to save memory
    del AllMonDF
    del AllAnnDF
    del FAllAnnDF
    del FAllMonDF
    # now go through our wet and dry days dictionaries 
    AllKeys = sorted( WetDict.keys() )
    NumAKeys = len( AllKeys )
    if NumAKeys < 1:
        print("Do not have keys in wet and dry dictionaries!!!!")
        sys.exit([-1])
    if AllKeys != sorted( DryDict.keys() ):
        # this is an error
        print("Different keys for wet and dry dictionaries!!!!")
        sys.exit([-1])
    # determine the MaxWetDays
    MaxWetDays = 0
    TotWetSeqs = 0
    for tKey in AllKeys:
        TotWetSeqs = TotWetSeqs + len( WetDict[tKey] )
        NewWetDays = max( [x[1] for x in WetDict[tKey]] )
        if NewWetDays > MaxWetDays:
            MaxWetDays = NewWetDays
    # end of for
    # output for logging
    with open( LogFile, 'a' ) as LID:
        LID.write("Have %d wet sequences with max num wet days of %d \n\n" %
                   ( TotWetSeqs, MaxWetDays ) )
    # end of with block
    # initialize our lists
    DDFList = list()
    WDFList = list()
    # now loopt through and collate
    for tKey in AllKeys:
        # get the key parts
        tKList = tKey.split("_")
        ModInd = int( tKList[0].strip('M') )
        GridInd = int( tKList[1] )
        tDryList = DryDict[tKey]
        dNEnts = len( tDryList )
        ShortOnes = np.ones( dNEnts, dtype=np.short )
        DataDict = { "MGrid_Id" : [ tKey for x in range(dNEnts) ],
                     "Grid_Id" : ShortOnes * GridInd,
                     "Mod_Id" : ShortOnes * ModInd,
                     "Year" : [x[0].year for x in tDryList],
                     "Month" : [x[0].month for x in tDryList],
                     "Day" : [x[0].day for x in tDryList],
                     "Dry_Count" : [x[1] for x in tDryList], }
        tDryDF = pd.DataFrame( data=DataDict )
        DDFList.append( tDryDF )
        tWetList = WetDict[tKey]
        wNEnts = len( tWetList )
        ShortOnes = np.ones( wNEnts, dtype=np.short )
        WDaysArray = np.zeros( (wNEnts, MaxWetDays), dtype=np.float32 )
        # fill in the wet days array
        for iI in range(wNEnts):
            wdsList = tWetList[iI][3]
            cNDays = len( wdsList )
            for jJ in range( cNDays ):
                cdDep = wdsList[jJ]
                WDaysArray[iI, jJ] = cdDep
            # end of days for
        # end of rows for
        # now can create our DataFrame
        DataDict = { "MGrid_Id" : [ tKey for x in range(wNEnts) ],
                     "Grid_Id" : ShortOnes * GridInd,
                     "Mod_Id" : ShortOnes * ModInd,
                     "Year" : [x[0].year for x in tWetList],
                     "Month" : [x[0].month for x in tWetList],
                     "Day" : [x[0].day for x in tWetList],
                     "Wet_Count" : [x[1] for x in tWetList], 
                     "Total_Depth" : [x[2] for x in tWetList], }
        for dD in range(1, (MaxWetDays + 1)):
            DayLabel = "Day_%d" % dD
            DataDict[DayLabel] = WDaysArray[:, (dD-1)]
        # end of day label for
        tWetDF = pd.DataFrame( data=DataDict )
        WDFList.append( tWetDF )
    # end of outer for
    # work on wet and dry days separately
    DryDayDF = pd.concat( DDFList, ignore_index=True )
    TotDryDays = DryDayDF['Dry_Count'].sum()
    CFName = "DryDays_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    DryPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    DryDayDF.to_pickle( DryPCKF )
    CFName = "DryDays_%s_%d-%d.feather" % ( DS_DESC, START_DT.year, END_DT.year )
    DryFeatherF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    DryDayDF.to_feather( DryFeatherF )
    # now need to drop some data structures for memory considerations
    del DryDict
    del DDFList
    del DryDayDF
    # next work on the wet days
    WetDayDF = pd.concat( WDFList, ignore_index=True )
    TotWetDays = WetDayDF['Wet_Count'].sum()
    CFName = "WetDays_%s_%d-%d.pickle" % ( DS_DESC, START_DT.year, END_DT.year )
    WetPCKF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    WetDayDF.to_pickle( WetPCKF )
    CFName = "WetDays_%s_%d-%d.feather" % ( DS_DESC, START_DT.year, END_DT.year )
    WetFeatherF = os.path.normpath( os.path.join( OUT_DIR, CFName ) )
    WetDayDF.to_feather( WetFeatherF )
    TotDays = TotDryDays + TotWetDays
    CurDT = dt.datetime.now()
    with open( LogFile, 'a' ) as LID:
        LID.write("Processed %d days\n\n" % TotDays)
        LID.write("End processing CMIP5 data from database at %s\n\n" %
                  CurDT.strftime("%m/%d/%Y %H:%M:%S") )
    # end of with block
    # end of processing

