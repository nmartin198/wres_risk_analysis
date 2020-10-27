# -*- coding: utf-8 -*-
"""
Created on Fri May 22 15:31:36 2020

@author: nmartin <nick.martin@stanfordalumni.org>

Process weather generator outputs for display and comparison.
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

import pandas as pd
import numpy as np
import datetime as dt
import os
import pickle

# parameters
#OUT_LABEL = "DC_WGMN1"
#OUT_LABEL = "DC_WGMN2"
#OUT_LABEL = "DC_WGMN3"
OUT_LABEL = "DC_WGMN4"
#IN_DIR = r'C:\Temp\WG_Test_Out\Test1'
#IN_DIR = r'C:\Temp\WG_Test_Out\Test2'
#IN_DIR = r'C:\Temp\WG_Test_Out\Test3'
IN_DIR = r'C:\Temp\WG_Test_Out\Final'
IN_NAME = "WS_H1_%s_R%d_DF.pickle"
NUM_REAL = 10000
#OUT_DIR = r'C:\Temp\WG_Test_Out\Test1\Processed'
#OUT_DIR = r'C:\Temp\WG_Test_Out\Test2\Processed'
#OUT_DIR = r'C:\Temp\WG_Test_Out\Test3\Processed'
OUT_DIR = r'C:\Temp\WG_Test_Out\Final\Processed'
All_Periods = [ [ dt.datetime(1980, 1, 1), dt.datetime(2010, 12, 31) ],
                [ dt.datetime(2011, 1, 1), dt.datetime(2040, 12, 31) ],
                [ dt.datetime(2041, 1, 1), dt.datetime(2070, 12, 31) ],
                [ dt.datetime(2071, 1, 1), dt.datetime(2100, 12, 31) ],
              ]
WS_COLS = [ "Tmax_C", #0
            "Tmin_C", #1
            "Tave_C", #2
            "Precip_mm", #3
            "ETo_mm", #4
]
PreCol = WS_COLS[3]

if __name__ == "__main__":
    # initialize our data structure
    DP_MPrecipD = dict()
    P1_MPrecipD = dict()
    P2_MPrecipD = dict()
    P3_MPrecipD = dict()
    DP_AMaxPreL = list()
    P1_AMaxPreL = list()
    P2_AMaxPreL = list()
    P3_AMaxPreL = list()
    DP_ATotPreL = list()
    P1_ATotPreL = list()
    P2_ATotPreL = list()
    P3_ATotPreL = list()
    # use a collection of nested loops to process through everything
    for rR in range( NUM_REAL ):
        rInd = rR + 1
        if (rInd % 500 == 0):
            print( "Work on realization %d" % rInd )
        # end if
        InFile = os.path.normpath( os.path.join( IN_DIR, 
                                   IN_NAME % ( OUT_LABEL, rInd ) ) )
        InDF = pd.read_pickle(InFile, compression='zip' )
        InDF = InDF[[PreCol]].copy()
        for iI in range(4):
            cPeriod = All_Periods[iI]
            cDF = InDF.loc[cPeriod[0]:cPeriod[1]].copy()
            cAnnDF = cDF.resample( 'AS', closed='left', label='left' ).max()
            cTotDF = cDF.resample( 'AS', closed='left', label='left' ).sum()
            if iI == 0:
                DP_AMaxPreL.append( cAnnDF[PreCol].to_numpy() )
                DP_ATotPreL.append( np.array( cTotDF[PreCol].tolist(), 
                                              dtype=np.float32 ) )
            elif iI == 1:
                P1_AMaxPreL.append( cAnnDF[PreCol].to_numpy() )
                P1_ATotPreL.append( np.array( cTotDF[PreCol].tolist(), 
                                              dtype=np.float32 ) )
            elif iI == 2:
                P2_AMaxPreL.append( cAnnDF[PreCol].to_numpy() )
                P2_ATotPreL.append( np.array( cTotDF[PreCol].tolist(), 
                                              dtype=np.float32 ) )
            elif iI == 3:
                P3_AMaxPreL.append( cAnnDF[PreCol].to_numpy() )
                P3_ATotPreL.append( np.array( cTotDF[PreCol].tolist(), 
                                              dtype=np.float32 ) )
            # end if
            cMonDF = cDF.resample( 'MS', closed='left', label='left' ).sum()
            cMonDF["Month"] = cMonDF.index.month
            for jJ in range(1, 13, 1):
                cCMon = cMonDF[cMonDF["Month"] == jJ].copy()
                if ( rR == 0 ):
                    if iI == 0:
                        DP_MPrecipD[jJ] = [ cCMon[PreCol].to_numpy() ]
                    elif iI == 1:
                        P1_MPrecipD[jJ] = [ cCMon[PreCol].to_numpy() ]
                    elif iI == 2:
                        P2_MPrecipD[jJ] = [ cCMon[PreCol].to_numpy() ]
                    elif iI == 3:
                        P3_MPrecipD[jJ] = [ cCMon[PreCol].to_numpy() ]
                    # end inner if
                else:
                    if iI == 0:
                        DP_MPrecipD[jJ].append( cCMon[PreCol].to_numpy() )
                    elif iI == 1:
                        P1_MPrecipD[jJ].append( cCMon[PreCol].to_numpy() )
                    elif iI == 2:
                        P2_MPrecipD[jJ].append( cCMon[PreCol].to_numpy() )
                    elif iI == 3:
                        P3_MPrecipD[jJ].append( cCMon[PreCol].to_numpy() )
                    # end inner if
                # end if
            # end for month
        # end for analysis period
    # end for realization
    # go through and make aggregated numpy arrays
    DP_MPD = dict()
    P1_MPD = dict()
    P2_MPD = dict()
    P3_MPD = dict()
    for jJ in range( 1, 13, 1 ):
        DP_MPD[jJ] = np.concatenate( DP_MPrecipD[jJ] )
        P1_MPD[jJ] = np.concatenate( P1_MPrecipD[jJ] )
        P2_MPD[jJ] = np.concatenate( P2_MPrecipD[jJ] )
        P3_MPD[jJ] = np.concatenate( P3_MPrecipD[jJ] )
    # end for
    del DP_MPrecipD
    del P1_MPrecipD
    del P2_MPrecipD
    del P3_MPrecipD
    # now output
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                 "DP_%s_PreMonTotal_Dict.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( DP_MPD, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                "P1_%s_PreMonTotal_Dict.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P1_MPD, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                "P2_%s_PreMonTotal_Dict.pickle" % OUT_LABEL) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P2_MPD, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                "P3_%s_PreMonTotal_Dict.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P3_MPD, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    del DP_MPD
    del P1_MPD
    del P2_MPD
    del P3_MPD
    # now do the annual maxes
    DP_npAnnMax = np.concatenate( DP_AMaxPreL )
    P1_npAnnMax = np.concatenate( P1_AMaxPreL )
    P2_npAnnMax = np.concatenate( P2_AMaxPreL )
    P3_npAnnMax = np.concatenate( P3_AMaxPreL )
    del DP_AMaxPreL
    del P1_AMaxPreL
    del P2_AMaxPreL
    del P3_AMaxPreL
    DP_npAnnTot = np.concatenate( DP_ATotPreL )
    P1_npAnnTot = np.concatenate( P1_ATotPreL )
    P2_npAnnTot = np.concatenate( P2_ATotPreL )
    P3_npAnnTot = np.concatenate( P3_ATotPreL )
    del DP_ATotPreL
    del P1_ATotPreL
    del P2_ATotPreL
    del P3_ATotPreL
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "DP_%s_PreAnnMax_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( DP_npAnnMax, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P1_%s_PreAnnMax_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P1_npAnnMax, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P2_%s_PreAnnMax_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P2_npAnnMax, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P3_%s_PreAnnMax_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P3_npAnnMax, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "DP_%s_PreAnnTot_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( DP_npAnnTot, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P1_%s_PreAnnTot_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P1_npAnnTot, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P2_%s_PreAnnTot_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P2_npAnnTot, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    OutFileP = os.path.normpath( os.path.join( OUT_DIR, 
                                    "P3_%s_PreAnnTot_npa.pickle" % OUT_LABEL ) )
    with open( OutFileP, 'wb' ) as OP:
        pickle.dump( P3_npAnnTot, OP, protocol=pickle.HIGHEST_PROTOCOL )
    # end with
    # 
