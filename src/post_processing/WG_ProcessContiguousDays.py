# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 18:26:34 2019

Edited on 1/22/2020 to make more memory efficient
@author: nmartin <nick.martin@stanfordalumni.org>

Process precipitation results for contiguous days

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

import WG_Inputs as WGI
from WG_PrecipDepth import WD_THRESH
from os import path
import pandas as pd
import datetime as dt

NUM_REAL = 10000

# inputs
#IN_DIR = r'C:\Temp\WG_Test_Out\Test1\Processed'
#IN_DIR = r'C:\Temp\WG_Test_Out\Test2\Processed'
#IN_DIR = r'C:\Temp\WG_Test_Out\Test3\Processed'
IN_DIR = r'C:\Temp\WG_Test_Out\Final\Processed'
H0_ROOT = "H0PrecipAllReal_G"
H0P1_ROOT = "H0P1PrecipAllReal_G"
H0P2_ROOT = "H0P2PrecipAllReal_G"
H0P3_ROOT = "H0P3PrecipAllReal_G"
H1_ROOT = "H1PrecipAllReal_G"
H1P1_ROOT = "H1P1PrecipAllReal_G"
H1P2_ROOT = "H1P2PrecipAllReal_G"
H1P3_ROOT = "H1P3PrecipAllReal_G"
Sim_Dict = { 1 : [ H0_ROOT, "H0_Data_DryDays_G", "H0_Data_WetDays_G", "H0_Data_Depth_G"],
             2 : [ H0P1_ROOT, "H0P1_DryDays_G", "H0P1_WetDays_G", "H0P1_Depth_G"],
             3 : [ H0P2_ROOT, "H0P2_DryDays_G", "H0P2_WetDays_G", "H0P2_Depth_G"],
             4 : [ H0P3_ROOT, "H0P3_DryDays_G", "H0P3_WetDays_G", "H0P3_Depth_G"],
             5 : [ H1_ROOT, "H1_Data_DryDays_G", "H1_Data_WetDays_G", "H1_Data_Depth_G"],
             6 : [ H1P1_ROOT, "H1P1_DryDays_G", "H1P1_WetDays_G", "H1P1_Depth_G"],
             7 : [ H1P2_ROOT, "H1P2_DryDays_G", "H1P2_WetDays_G", "H1P2_Depth_G"],
             8 : [ H1P3_ROOT, "H1P3_DryDays_G", "H1P3_WetDays_G", "H1P3_Depth_G"],
}
PICKLE_EXT = "pickle"

# standalone run block
if __name__ == "__main__":
    # go through our dictionary, one at a time 
    for sS in range( 1, 9, 1 ):
        CurSimValues = Sim_Dict[sS]
        # start out with H0Data
        Our_Root = CurSimValues[0]
        Out_RootDD = CurSimValues[1]
        Out_RootWD = CurSimValues[2]
        Out_RootDE = CurSimValues[3]
        # get ready to go through grids
        gCnt = 0
        print("Working on %s" % Our_Root )
        # go through one grid cell at a time ...
        for gG in WGI.LOCA_KEYS:
            print("   Working on grid cell %d" % gG)
            InFName = "%s%d.%s" % ( Our_Root, gG, PICKLE_EXT )
            InFile = path.normpath( path.join( IN_DIR, InFName ) )
            cDF = pd.read_pickle( InFile, compression='zip' )
            cNumDays = len( cDF )
            DryList = list()
            WetList = list()
            WetDep = list()
            for iI in range(1, NUM_REAL + 1, 1):
                curReal = "R%d" % iI
                inWet = False
                inDry = False
                cWetCnt = 0
                cDryCnt = 0
                for dD in range( cNumDays ):
                    cTSInd = cDF.index[dD]
                    cMonth = cTSInd.month
                    cDT = dt.datetime( cTSInd.year, cTSInd.month, cTSInd.day )
                    if dD == 0:
                        cWStartDT = cDT
                        cDStartDT = cDT
                    cPDepth = float( cDF.at[cTSInd, curReal] )
                    if cPDepth >= WD_THRESH:
                        # this is the wet day case
                        if inWet:
                            cWetCnt += 1
                            WetDep.append( [cDT, cPDepth] )
                        else:
                            inWet = True
                            inDry = False
                            cWStartDT = cDT
                            cWetCnt = 1
                            WetDep.append( [cDT, cPDepth] )
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
                                WetList.append( [ cWStartDT, cWetCnt ] )
                                cWetCnt = 0
                                totPrecip = 0.0
                                dayPreL = list()
                    # end of outer depth if
                # end of the day for
                # check for the last entry
                if inWet:
                    WetList.append( [ cWStartDT, cWetCnt ] )
                else:
                    DryList.append( [ cDStartDT, cDryCnt ] )
            # end of realizations for
            # make DataFrames from our lists
            DataDict = { "Year" : [x[0].year for x in DryList],
                         "Month" : [x[0].month for x in DryList],
                         "Day" : [x[0].day for x in DryList],
                         "Dry_Count" : [x[1] for x in DryList], }
            tDryDF = pd.DataFrame( data=DataDict )
            DataDict = { "Year" : [x[0].year for x in WetList],
                         "Month" : [x[0].month for x in WetList],
                         "Day" : [x[0].day for x in WetList],
                         "Dry_Count" : [x[1] for x in WetList], }
            tWetDF = pd.DataFrame( data=DataDict )
            DataDict = { "Year" : [x[0].year for x in WetDep],
                         "Month" : [x[0].month for x in WetDep],
                         "Day" : [x[0].day for x in WetDep],
                         "PDepth_mm" : [x[1] for x in WetDep], }
            tDepDF = pd.DataFrame( data=DataDict )
            # now write out our DataFrames
            OutFileName = "%s%d.%s" % ( Out_RootDD, gG, PICKLE_EXT )
            OutFP = path.normpath( path.join( IN_DIR, OutFileName ) )
            tDryDF.to_pickle( OutFP )
            OutFileName = "%s%d.%s" % ( Out_RootWD, gG, PICKLE_EXT )
            OutFP = path.normpath( path.join( IN_DIR, OutFileName ) )
            tWetDF.to_pickle( OutFP )
            OutFileName = "%s%d.%s" % ( Out_RootDE, gG, PICKLE_EXT )
            OutFP = path.normpath( path.join( IN_DIR, OutFileName ) )
            tDepDF.to_pickle( OutFP )
            # increment our counter
            gCnt += 1
        # end of gG grid cell outer for
    # end of sim dictionary for
    # end of function
