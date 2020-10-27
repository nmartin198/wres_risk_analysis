"""
Setup mHSP2 inputs for multiple realizations run off of the same model
with different weather parameter forcing.

The idea is to read the input files that were output from the weather
generator and update and copy the HDF5 file to use these inputs.

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

# imports
import os
import pandas as pd 
import datetime as dt

# parameters
INPUT_HDF5 = r'DC_CalibmHSP2.h5'
"""The base HDF5 input file.

This file needs to have the weather forcing updated for each realization.
"""

ADJ_PERV_AREAS = [ "P001", "P002" ]
"""Pervious areas to be adjusted for 'basin' run type

These are the locations that will have impervious area increased and
pervious area decreased to represent development considerations.
"""

WG_SIM_ROOT = "DC_WGMN4"
"""Weather generator simulation root name.
"""

SIM_START_KEY = "sim_start"
"""Simulation start time
"""

SIM_END_KEY = "sim_end"
"""Simulation end time
"""

PRECIP_HDR = "Precip_mm_%d"
"""Precipitation header format string for weather generator precipitation 
output.

Output is by LOCA grid cell and the format string requires that the grid
cell be specified. Note that this value is in millimeters and mHSPF 
inputs require inches.
"""

K_c = 0.730
"""Crop coefficient to go from ETo to PET.

Coefficient derived by comparing calculated ETo to independently 
calculated/measured PET from "station" data.
"""

RDAY_ET = 0.25
"""PET percentage for rainy days.

Scaling factor to reduce PET for rainy days
"""


START_DATE = dt.datetime(1980, 1, 1)
"""Starting time for production of the stochastic synthetic time series"""

END_DATE = dt.datetime( 2100, 12, 31)
"""Ending time for the production of the stochastic synthetic time series"""

PROJ_PERIODS = [ [ dt.datetime(2011, 1, 1), dt.datetime(2040, 12, 31) ],
                 [ dt.datetime(2041, 1, 1), dt.datetime(2070, 12, 31) ],
                 [ dt.datetime(2071, 1, 1), dt.datetime(2100, 12, 31) ],
               ]
"""List of climate projection periods with each sublist indentifying an
individual period. Index 0 of the sublist is start dt and Index 1 is end dt"""

PERV_TARGS = [ "P001", "P002", "P003", "P004", "P005", "P006", "P007", 
               "P008", "P009", "P010", "P011", "P012" ]
"""Pervious land segment target Ids

These are the target IDs in the existing mHSP2 model. Each HRU has both
a pervious and an impervious portion.
"""

IMP_TARGS = [ "I001", "I002", "I003", "I004", "I005", "I006", "I007", 
              "I008", "I009", "I010", "I011", "I012" ]
"""Impervious land segment target ids

These are the target IDs in the existing mHSP2 model. Each HRU has both
a pervious and an impervious portion.
"""

RR_TARGS = [ "R001", "R002", "R003", "R004", "R005" ]
"""Stream segment target ids

These are the existing target IDs in the input mHSP2 model.
"""

TS_DICT = { "R001" : [ [ "PREC", "TS102" ], [ "POTEV", "TS103"] ],
            "R002" : [ [ "PREC", "TS104" ], [ "POTEV", "TS105"] ],  
            "R003" : [ [ "PREC", "TS106" ], [ "POTEV", "TS107"] ],  
            "R004" : [ [ "PREC", "TS108" ], [ "POTEV", "TS109"] ],  
            "R005" : [ [ "PREC", "TS110" ], [ "POTEV", "TS111"], ["IVOL", "TS136"]],  
            "P001" : [ [ "PREC", "TS112" ], [ "PETINP", "TS113"] ],  
            "P002" : [ [ "PREC", "TS114" ], [ "PETINP", "TS115"] ],  
            "P003" : [ [ "PREC", "TS116" ], [ "PETINP", "TS117"] ],  
            "P004" : [ [ "PREC", "TS118" ], [ "PETINP", "TS119"] ],  
            "P005" : [ [ "PREC", "TS120" ], [ "PETINP", "TS121"] ],  
            "P006" : [ [ "PREC", "TS122" ], [ "PETINP", "TS123"] ],  
            "P007" : [ [ "PREC", "TS124" ], [ "PETINP", "TS125"] ],  
            "P008" : [ [ "PREC", "TS126" ], [ "PETINP", "TS127"] ],  
            "P009" : [ [ "PREC", "TS128" ], [ "PETINP", "TS129"] ],  
            "P010" : [ [ "PREC", "TS130" ], [ "PETINP", "TS131"] ],  
            "P011" : [ [ "PREC", "TS132" ], [ "PETINP", "TS133"] ],  
            "P012" : [ [ "PREC", "TS134" ], [ "PETINP", "TS135"] ],  
            "I001" : [ [ "PREC", "TS112" ], [ "PETINP", "TS113"] ],  
            "I002" : [ [ "PREC", "TS114" ], [ "PETINP", "TS115"] ],  
            "I003" : [ [ "PREC", "TS116" ], [ "PETINP", "TS117"] ],  
            "I004" : [ [ "PREC", "TS118" ], [ "PETINP", "TS119"] ],  
            "I005" : [ [ "PREC", "TS120" ], [ "PETINP", "TS121"] ],  
            "I006" : [ [ "PREC", "TS122" ], [ "PETINP", "TS123"] ],  
            "I007" : [ [ "PREC", "TS124" ], [ "PETINP", "TS125"] ],  
            "I008" : [ [ "PREC", "TS126" ], [ "PETINP", "TS127"] ],  
            "I009" : [ [ "PREC", "TS128" ], [ "PETINP", "TS129"] ],  
            "I010" : [ [ "PREC", "TS130" ], [ "PETINP", "TS131"] ],  
            "I011" : [ [ "PREC", "TS132" ], [ "PETINP", "TS133"] ],  
            "I012" : [ [ "PREC", "TS134" ], [ "PETINP", "TS135"] ],  
          }
"""Time series identifier dictionary

Identifies the time series ID for each HRU location
"""

HRU_LOCA_GRID_WT = { "HRU_1" : { 93 : 0.038083,
                                 94 : 0.043335,
                                 106 : 0.002522,
                                 107 : 0.362835,
                                 108 : 0.248855,
                                 121 : 0.039553,
                                 122 : 0.219238,
                                 123 : 0.037873,
                                 137 : 0.007707, },
                     "HRU_2" : { 79 : 0.020826,
                                 92 : 0.250947,
                                 93 : 0.717863,
                                 107 : 0.010364, }, 
                     "HRU_3" : { 92 : 0.312914,
                                 93 : 0.024435,
                                106 : 0.531295,
                                107 : 0.113374, 
                                120 : 0.014921,
                                121 : 0.003062, },
                     "HRU_4" : { 77 : 0.006029,
                                 78 : 0.597602,
                                 79 : 0.098011,
                                 92 : 0.291301,
                                 93 : 0.007057, },
                     "HRU_5" : { 91 : 0.143279,
                                 92 : 0.172609,
                                 105 : 0.363965,
                                 106 : 0.320147, },
                     "HRU_6" : { 77 : 0.543345, 
                                 78 : 0.034081,
                                 91 : 0.358011,
                                 92 : 0.064562, },
                     "HRU_7" : { 76 : 0.116728, 
                                 77 : 0.104388,
                                 90 : 0.314748,
                                 91 : 0.348857,
                                 104 : 0.037258,
                                 105 : 0.078021, },
                     "HRU_8" : { 63 : 0.625088,
                                 64 : 0.374912, },
                     "HRU_9" : { 63 : 0.054902,
                                 64 : 0.039684,
                                 77 : 0.438075,
                                 78 : 0.467338, },
                     "HRU_10" : { 63 : 1.0000, },
                     "HRU_11" : { 63 : 0.142750, 
                                  76 : 0.363641,
                                  77 : 0.493609, },
                     "HRU_12" : { 62 : 0.249204,
                                  63 : 0.249740, 
                                  76 : 0.492883,
                                  77 : 0.008173, },
}
"""Weighting by HRU to calculate HRU-specific precipitation from LOCA 
grid cells

Area-weighting for HRU precipitation. HRU precipitation applies to both
pervious and impervious land areas.
"""

#-------------------------------------------------------------------------------------
# functions
def adjustETo( Ks, RRDay, ETo, Precip ):
    """ Function to adjust ETo using a crop coefficient and if there was precipitation.
    Designed to be used in a apply( lambda row: )
    
    Args:
        Ks (float): crop coefficient
        RRDay (float): reduction factor for ET on rainy days
        ETo (float): current day's ETo in depth units
        Precip (float): current day's precip in depth units
    
    Returns:
        float: calculated potential evapotranspiration (PET)
        
    """
    PET = ETo * Ks
    if Precip > 0.0:
        PET = PET * RRDay
    # return
    return PET


def makeH0Input( workDir, H0File, realNum ):
    """Make the H0 pathway input HDF5 file

    This involves creating a precipitation time series
    for each HRU and RCHRES and an evaporation time series
    for each HRU and RCHRES. These time series replace 
    the existing time series in the HDF5 file.

    Args:
        workDir (str): directory for all input files
        H0File (str): HDF5 file for H0 pathway
        realNum (int): the realization number
    
    Returns:
        int: status; 0 == success
    """
    # imports
    import numpy as np
    # globals
    global WG_SIM_ROOT, PERV_TARGS, IMP_TARGS, HRU_LOCA_GRID_WT
    global TS_DICT, PRECIP_HDR, RDAY_ET, K_c, RR_TARGS
    global SIM_START_KEY, SIM_END_KEY, START_DATE, END_DATE
    # parameters
    goodReturn = 0
    badReturn = 1
    # locals
    # start
    # first update the simulation start and end dates
    with pd.HDFStore( H0File ) as store:
        gCont = store.get( key= r'/CONTROL/GLOBAL/' )
        gCont.at[ SIM_START_KEY, 'Data' ] = START_DATE.strftime( "%Y-%m-%d %H:%M" )
        gCont.at[ SIM_END_KEY, 'Data' ] = END_DATE.strftime( "%Y-%m-%d %H:%M" )
        store.put( key= r'/CONTROL/GLOBAL/', value=gCont, format='table', 
                   data_columns=True )
    # end with and start and end dates updated
    # read in the existing wg output
    wgH0File = "H0_%s_R%d_DF.pickle" % ( WG_SIM_ROOT, realNum )
    wgH0FPath = os.path.normpath( os.path.join( workDir, wgH0File) )
    if not os.path.isfile( wgH0FPath ):
        # this is an error
        errMsg = "WG realization file %s does not exist !!!" % wgH0FPath
        print("%s" % errMsg)
        return badReturn
    # end if
    H0DF = pd.read_pickle( wgH0FPath, compression='zip' )
    totLen = len( H0DF )
    #
    # PRECIP - HRU
    # Go through all of our HRU precipitation time series
    #  calculate the HRU time series and update the HDF5 file.
    iCnt = 0
    for pTarg in PERV_TARGS:
        iTarg = IMP_TARGS[iCnt]
        cHRU_id = int( pTarg.strip("P") )
        cHRU = "HRU_%d" % cHRU_id
        weightD = HRU_LOCA_GRID_WT[cHRU]
        cPreA = np.zeros( totLen, dtype=np.float64 )
        cGrids = sorted( weightD.keys() )
        for cG in cGrids:
            cHdr = PRECIP_HDR % cG
            cPreA += ( H0DF[cHdr].to_numpy() * (1.0/25.4) * weightD[cG] )
        # end for
        scPreDF = pd.Series( cPreA, index=H0DF.index )
        ptsLabel = TS_DICT[ pTarg ][0][1]
        itsLabel = TS_DICT[ iTarg ][0][1]
        phKey = "/TIMESERIES/%s/" % ptsLabel
        ihKey = "/TIMESERIES/%s/" % itsLabel
        # now write
        scPreDF.to_hdf( H0File, key=phKey )
        scPreDF.to_hdf( H0File, key=ihKey )
        # increment the counter
        iCnt += 1
    # end for
    #
    # PET
    # Extract already calculated PET for the entire watershed
    # apply to HRUs and to RCHRES
    # For this we need the watershed, or WS, outputs
    wsH0File = "WS_H0_%s_R%d_DF.pickle" % ( WG_SIM_ROOT, realNum )
    wsH0FPath = os.path.normpath( os.path.join( workDir, wsH0File) )
    if not os.path.isfile( wsH0FPath ):
        # this is an error
        errMsg = "Watershed realization file %s does not exist !!!" \
                    % wsH0FPath
        print("%s" % errMsg)
        return badReturn
    # end if
    WSH0DF = pd.read_pickle( wsH0FPath, compression='zip' )
    totLen = len( WSH0DF )
    # calculate PET from ETo and prepare WS precip
    WSH0DF["PET_mm"] = WSH0DF.apply( lambda row: adjustETo( K_c, 
                                     RDAY_ET, row['ETo_mm'], 
                                     row['Precip_mm'] ), axis= 1 )
    cPET_in = np.zeros( totLen, dtype=np.float64 )
    cPre_in = np.zeros( totLen, dtype=np.float64 )
    cPET_in += ( WSH0DF["PET_mm"].to_numpy() * ( 1.0/25.4) )
    cPre_in += ( WSH0DF["Precip_mm"].to_numpy() * ( 1.0/25.4) )
    scPET_in = pd.Series( cPET_in, index=WSH0DF.index )
    scPre_in = pd.Series( cPre_in, index=WSH0DF.index )
    # now write this PET to all of the places required in the
    # input HDF5 file.
    # First write to HRUs
    iCnt = 0
    for pTarg in PERV_TARGS:
        iTarg = IMP_TARGS[iCnt]
        cHRU_id = int( pTarg.strip("P") )
        cHRU = "HRU_%d" % cHRU_id
        ptsLabel = TS_DICT[ pTarg ][1][1]
        itsLabel = TS_DICT[ iTarg ][1][1]
        phKey = "/TIMESERIES/%s/" % ptsLabel
        ihKey = "/TIMESERIES/%s/" % itsLabel
        # now write
        scPET_in.to_hdf( H0File, key=phKey )
        scPET_in.to_hdf( H0File, key=ihKey )
        # increment the counter
        iCnt += 1
    # end for
    # now do the RCHRES. 
    #   RCHRES do both precip and PET
    for rTarg in RR_TARGS:
        preLabel = TS_DICT[ rTarg ][0][1]
        petLabel = TS_DICT[ rTarg ][1][1]
        preKey = "/TIMESERIES/%s/" % preLabel
        petKey = "/TIMESERIES/%s/" % petLabel
        scPre_in.to_hdf( H0File, key=preKey )
        scPET_in.to_hdf( H0File, key=petKey )
    # end for
    # return
    return goodReturn


def makeH1Input( workDir, H1File, realNum ):
    """Make the H1pathway input HDF5 file

    This involves creating a precipitation time series
    for each HRU and RCHRES and an evaporation time series
    for each HRU and RCHRES. These time series replace 
    the existing time series in the HDF5 file.

    Args:
        workDir (str): directory for all input files
        H1File (str): HDF5 file for H1 pathway
        realNum (int): the realization number
    
    Returns:
        int: status; 0 == success
    """
    # imports
    import numpy as np
    # globals
    global WG_SIM_ROOT, PERV_TARGS, IMP_TARGS, HRU_LOCA_GRID_WT
    global TS_DICT, PRECIP_HDR, RDAY_ET, K_c, RR_TARGS
    global SIM_START_KEY, SIM_END_KEY, START_DATE, END_DATE
    # parameters
    goodReturn = 0
    badReturn = 1
    # locals
    # start
    # first update the simulation start and end dates
    with pd.HDFStore( H1File ) as store:
        gCont = store.get( key= r'/CONTROL/GLOBAL/' )
        gCont.at[ SIM_START_KEY, 'Data' ] = START_DATE.strftime( "%Y-%m-%d %H:%M" )
        gCont.at[ SIM_END_KEY, 'Data' ] = END_DATE.strftime( "%Y-%m-%d %H:%M" )
        store.put( key= r'/CONTROL/GLOBAL/', value=gCont, format='table', 
                   data_columns=True )
    # end with and start and end dates updated
    # read in the existing wg output
    wgH1File = "H1_%s_R%d_DF.pickle" % ( WG_SIM_ROOT, realNum )
    wgH1FPath = os.path.normpath( os.path.join( workDir, wgH1File) )
    if not os.path.isfile( wgH1FPath ):
        # this is an error
        errMsg = "WG realization file %s does not exist !!!" % wgH1FPath
        print("%s" % errMsg)
        return badReturn
    # end if
    H1DF = pd.read_pickle( wgH1FPath, compression='zip' )
    totLen = len( H1DF )
    #
    # PRECIP - HRU
    # Go through all of our HRU precipitation time series
    #  calculate the HRU time series and update the HDF5 file.
    iCnt = 0
    for pTarg in PERV_TARGS:
        iTarg = IMP_TARGS[iCnt]
        cHRU_id = int( pTarg.strip("P") )
        cHRU = "HRU_%d" % cHRU_id
        weightD = HRU_LOCA_GRID_WT[cHRU]
        cPreA = np.zeros( totLen, dtype=np.float64 )
        cGrids = sorted( weightD.keys() )
        for cG in cGrids:
            cHdr = PRECIP_HDR % cG
            cPreA += ( H1DF[cHdr].to_numpy() * (1.0/25.4) * weightD[cG] )
        # end for
        scPreDF = pd.Series( cPreA, index=H1DF.index )
        ptsLabel = TS_DICT[ pTarg ][0][1]
        itsLabel = TS_DICT[ iTarg ][0][1]
        phKey = "/TIMESERIES/%s/" % ptsLabel
        ihKey = "/TIMESERIES/%s/" % itsLabel
        # now write
        scPreDF.to_hdf( H1File, key=phKey )
        scPreDF.to_hdf( H1File, key=ihKey )
        # increment the counter
        iCnt += 1
    # end for
    #
    # PET
    # Extract already calculated PET for the entire watershed
    # apply to HRUs and to RCHRES
    # For this we need the watershed, or WS, outputs
    wsH1File = "WS_H1_%s_R%d_DF.pickle" % ( WG_SIM_ROOT, realNum )
    wsH1FPath = os.path.normpath( os.path.join( workDir, wsH1File) )
    if not os.path.isfile( wsH1FPath ):
        # this is an error
        errMsg = "Watershed realization file %s does not exist !!!" \
                    % wsH1FPath
        print("%s" % errMsg)
        return badReturn
    # end if
    WSH1DF = pd.read_pickle( wsH1FPath, compression='zip' )
    totLen = len( WSH1DF )
    # calculate PET from ETo and prepare WS precip
    WSH1DF["PET_mm"] = WSH1DF.apply( lambda row: adjustETo( K_c, 
                                     RDAY_ET, row['ETo_mm'], 
                                     row['Precip_mm'] ), axis= 1 )
    cPET_in = np.zeros( totLen, dtype=np.float64 )
    cPre_in = np.zeros( totLen, dtype=np.float64 )
    cPET_in += ( WSH1DF["PET_mm"].to_numpy() * ( 1.0/25.4) )
    cPre_in += ( WSH1DF["Precip_mm"].to_numpy() * ( 1.0/25.4) )
    scPET_in = pd.Series( cPET_in, index=WSH1DF.index )
    scPre_in = pd.Series( cPre_in, index=WSH1DF.index )
    # now write this PET to all of the places required in the
    # input HDF5 file.
    # First write to HRUs
    iCnt = 0
    for pTarg in PERV_TARGS:
        iTarg = IMP_TARGS[iCnt]
        cHRU_id = int( pTarg.strip("P") )
        cHRU = "HRU_%d" % cHRU_id
        ptsLabel = TS_DICT[ pTarg ][1][1]
        itsLabel = TS_DICT[ iTarg ][1][1]
        phKey = "/TIMESERIES/%s/" % ptsLabel
        ihKey = "/TIMESERIES/%s/" % itsLabel
        # now write
        scPET_in.to_hdf( H1File, key=phKey )
        scPET_in.to_hdf( H1File, key=ihKey )
        # increment the counter
        iCnt += 1
    # end for
    # now do the RCHRES. 
    #   RCHRES do both precip and PET
    for rTarg in RR_TARGS:
        preLabel = TS_DICT[ rTarg ][0][1]
        petLabel = TS_DICT[ rTarg ][1][1]
        preKey = "/TIMESERIES/%s/" % preLabel
        petKey = "/TIMESERIES/%s/" % petLabel
        scPre_in.to_hdf( H1File, key=preKey )
        scPET_in.to_hdf( H1File, key=petKey )
    # end for
    # return
    return goodReturn


def createHDF5Inputs( workDir, realNum, Run_Type ):
    """Create HDF5 input files for each pathway

    Args:
        workDir (str): working directory where all files go
        realNum (int): current realization number
        Run_Type (str): the type of simulation, either 'climate' or
                        'basin'

    Returns:
        tuple: HDF5 input file names for each pathway
            0. H0 pathway HDF5 file
            1. H1 pathway HDF5 file
    
    """
    # imports
    import shutil
    # globals
    global INPUT_HDF5
    # parameters
    # locals
    # start
    # check that our template HDF5 file exists
    tempH5 = os.path.normpath( os.path.join( workDir, INPUT_HDF5 ) )
    if not os.path.isfile( tempH5 ):
        # this is an error
        errMsg = "mHSP2 template file %s does not exist !!!" % tempH5
        print("%s" % errMsg)
        return ()
    # end if
    destH0 = os.path.normpath( os.path.join( workDir, "H0_Current.h5" ) )
    destH1 = os.path.normpath( os.path.join( workDir, "H1_Current.h5" ) )
    # now copy
    outF = shutil.copyfile( tempH5, destH0 )
    outF = shutil.copyfile( tempH5, destH1 )
    # now work on modifying these files
    # these files are created differently depending on the run type
    # For a climate type run, H0 is H0 weather generator output
    #   and H1 is H1 weather generator output. For a basin type
    #   simulation, H0 and H1 are both H1 weather generator output.
    #   The HSPF model in the H1 pathway is modified as part of the
    #   the basin type simulation.
    if Run_Type == "climate":
        retStatus = makeH0Input( workDir, destH0, realNum )
        if retStatus != 0:
            # then we have an error
            return ()
        # end if
        retStatus = makeH1Input( workDir, destH1, realNum )
        if retStatus != 0:
            # then we have an error
            return ()
        # end if
    else:
        retStatus = makeH1Input( workDir, destH0, realNum )
        if retStatus != 0:
            # then we have an error
            return ()
        # end if
        retStatus = makeH1Input( workDir, destH1, realNum )
        if retStatus != 0:
            # then we have an error
            return ()
        # end if
    # return
    return ( destH0, destH1 )


#EOF