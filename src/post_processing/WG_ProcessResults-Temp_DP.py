# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:58:27 2019

@author: nmartin <nick.martin@stanfordalumni.org>

Process the WG temperature results. Broken out by projection interval 
for memory considerations
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
import pandas as pd
from WG_PrecipDepth import WD_THRESH
from WG_HighRealResults import PRE_START_IND
from os import path

NUM_REAL = 10000

def returnRealFileNames( curReal ):
    """Take the current realization and return the output realization file
    names
    """
    # local imports
    # start of function
    H0FileName = "H0_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, curReal)
    H1FileName = "H1_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, curReal)
    H0OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H0FileName ) )
    H1OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H1FileName ) )
    return ( H0OutFP, H1OutFP )

def makeDFColumnsList():
    """Make the list for the data frame columns
    
    Returns Tuple T:
        T[0] - ColsList(list): list of column headers in order
        T[1] - GridDict(dict): dictionary of grid column headers, values, by
                Grid Id, keys.
    """
    # imports
    # globals
    # start
    TotNum = PRE_START_IND + WGI.NUM_LOCA_GRID
    ColsList = [ "Tmax_C", "Tmin_C" ]
    GridDict = dict()
    for iI in range( PRE_START_IND, TotNum, 1):
        cGID = WGI.LOCA_KEYS[iI - PRE_START_IND]
        ColName = "Precip_mm_%d" % cGID
        ColsList.append( ColName )
        GridDict[cGID] = ColName
    # end of for
    return (ColsList, GridDict)


# standalone run block
if __name__ == "__main__":
    # get our data periods
    DataStart = WGI.DATA_PERIODS[0][0]
    DataEnd = WGI.DATA_PERIODS[0][1]
    # next get our cols and dict
    OutColsList, GridDict = makeDFColumnsList()
    # get the total number of columns
    TotNum = len( OutColsList )
    # start with the realization loop
    for iI in range(1, NUM_REAL + 1, 1):
        curReal = "R%d" % iI
        # some interim output
        if iI % 100 == 0:
            print("Working on realization %d" % iI)
        # the idea is to load the realizations, one at a time, and compile
        # to different data structures and to output at the end
        # get filenames
        H0File, H1File = returnRealFileNames( iI )
        # now read in the dataframes
        H0DF = pd.read_pickle( H0File, compression='zip' )
        H1DF = pd.read_pickle( H1File, compression='zip' )
        # now split up
        # start with H0 case
        #    statistics for H0 case should be the same for each period
        H0TmpData = H0DF.loc[ DataStart:DataEnd, OutColsList[:PRE_START_IND] ].copy()
        # now split out our realization values
        if iI == 1:
            # H0 data
            H0TmaxAR = H0TmpData[[OutColsList[0]]].copy()
            H0TmaxAR.columns = [curReal]
            H0TminAR = H0TmpData[[OutColsList[1]]].copy()
            H0TminAR.columns = [curReal]
        else:
            # H0 data
            tH0TmaxAR = H0TmpData[[OutColsList[0]]].copy()
            tH0TmaxAR.columns = [curReal]
            H0TmaxAR = H0TmaxAR.merge( tH0TmaxAR, how='inner', left_index=True, 
                                       right_index=True )
            tH0TminAR = H0TmpData[[OutColsList[1]]].copy()
            tH0TminAR.columns = [curReal]
            H0TminAR = H0TminAR.merge( tH0TminAR, how='inner', left_index=True,
                                       right_index=True )
        # then H1 case
        #    statistics for H1 case should be the same for each period
        H1TmpData = H1DF.loc[ DataStart:DataEnd, OutColsList[:PRE_START_IND] ].copy()
        # now split out our realization values
        if iI == 1:
            # H0 data
            H1TmaxAR = H1TmpData[[OutColsList[0]]].copy()
            H1TmaxAR.columns = [curReal]
            H1TminAR = H1TmpData[[OutColsList[1]]].copy()
            H1TminAR.columns = [curReal]
        else:
            # H0 data
            tH1TmaxAR = H1TmpData[[OutColsList[0]]].copy()
            tH1TmaxAR.columns = [curReal]
            H1TmaxAR = H1TmaxAR.merge( tH1TmaxAR, how='inner', left_index=True, 
                                       right_index=True )
            tH1TminAR = H1TmpData[[OutColsList[1]]].copy()
            tH1TminAR.columns = [curReal]
            H1TminAR = H1TminAR.merge( tH1TminAR, how='inner', left_index=True,
                                       right_index=True )
    # end of realization for
    # outputs
    # H0 by category
    cOutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                       'Processed', 'H0TmaxAllReal_DP.pickle' ) )
    H0TmaxAR.to_pickle( cOutFP, compression='zip' )
    cOutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                       'Processed', 'H0TminAllReal_DP.pickle' ) )
    H0TminAR.to_pickle( cOutFP, compression='zip' )
    # H1 by category
    cOutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                       'Processed', 'H1TmaxAllReal_DP.pickle' ) )
    H1TmaxAR.to_pickle( cOutFP, compression='zip' )
    cOutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                       'Processed', 'H1TminAllReal_DP.pickle' ) )
    H1TminAR.to_pickle( cOutFP, compression='zip' )

