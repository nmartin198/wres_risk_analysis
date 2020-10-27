"""
Process mHSP2 outputs for a particular watershed

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
import datetime as dt
import pandas as pd
import numpy as np
import os

# parameters
DATA_PERIODS = [ [ dt.datetime(1980, 1, 1), dt.datetime(2010, 12, 31) ],
                ]
"""List of data periods with each sublist identifying an individual period.

Index 0 of the sublist is start dt and Index 1 is end dt"""

PROJ_PERIODS = [ [ dt.datetime(2011, 1, 1), dt.datetime(2040, 12, 31) ],
                 [ dt.datetime(2041, 1, 1), dt.datetime(2070, 12, 31) ],
                 [ dt.datetime(2071, 1, 1), dt.datetime(2100, 12, 31) ],
               ]
"""List of climate projection periods with each sublist indentifying an
individual period.

Index 0 of the sublist is start dt and Index 1 is end dt"""


#-------------------------------------------------------------------------------
# functions
def readAreaDicts( hdfname ):
    """Read in the area dictionaries that just output in the separate
    process simulations

    Args:
        hdfname (str): full path and name for sim HDF5 file
    
    Returns:
        tuple: with 3 dictionaries
                0. HRU dictionary
                1. PERV dictionary
                2. IMPERV dictionary
    
    """
    # imports
    import pickle
    # globals
    # parameter
    # locals
    # start
    pfTuple = os.path.split( hdfname )
    workDir = pfTuple[0]
    fileName = pfTuple[1]
    baseName = os.path.splitext( fileName )[0]
    # now read
    hruFName = os.path.normpath( os.path.join( workDir, 
                                 "%s_hArea.p" % baseName ) )
    with open( hruFName, 'rb' ) as oP:
        HAreas = pickle.load( oP )
    # end with
    pervFName = os.path.normpath( os.path.join( workDir, 
                                 "%s_pArea.p" % baseName ) )
    with open( pervFName, 'rb' ) as oP:
        PAreas = pickle.load( oP )
    # end with
    impFName = os.path.normpath( os.path.join( workDir, 
                                 "%s_iArea.p" % baseName ) )
    with open( impFName, 'rb' ) as oP:
        IAreas = pickle.load( oP )
    # end with
    # now return
    return ( HAreas, PAreas, IAreas )

def createHAreaDF( HADict, tIndex ):
    """Create a DataFrame with the areas over time for HRUs

    Args:
        HADict (dict): Holds area by HRU by analysis interval
        tIndex (pd.datetimeindex): simulation output date time index
    
    Returns:
        pd.DataFrame: Areas for HRU by time index

    """
    # imports
    # globals
    global PROJ_PERIODS
    # parameters
    # locals
    # start
    nRows = len( tIndex )
    tNames = list( HADict[1].keys() )
    DataDict = dict()
    for aName in tNames:
        DataDict[aName] = np.zeros( nRows, dtype=np.float32 )
    # end for
    areaDF = pd.DataFrame( index=tIndex, data=DataDict )
    # now fill our areas. Need to start with the Data Interval
    StartDT = areaDF.index[0].to_pydatetime()
    EndDT = PROJ_PERIODS[0][0] - dt.timedelta(days=1.0)
    cPer = 1
    for aName in tNames:
        areaDF.at[StartDT:EndDT, aName] = HADict[cPer][aName]
    # end for
    nPeriods = len( PROJ_PERIODS )
    cPer += 1
    for jJ in range(nPeriods):
        StartDT = PROJ_PERIODS[jJ][0]
        EndDT = PROJ_PERIODS[jJ][1]
        for aName in tNames:
            areaDF.at[StartDT:EndDT, aName] = HADict[cPer+jJ][aName]
        # end for
    # end for
    # our dataframe should be filled so return
    return areaDF


def procOuts( workDir, H0File, H1File, realNum ):
    """Process the simulation results

    Args:
        workDir (str): simulation directory
        H0File (str): filename and path for H0 HDF5 file
        H1File (str): filename and path for H1 HDF5 file
        realNum (int): the realization number
    
    """
    # imports
    from dc_setup_inputs import PERV_TARGS, IMP_TARGS, RR_TARGS
    from dc_setup_inputs import TS_DICT, START_DATE, END_DATE
    # parameters
    ROut = "R005"
    # locals
    H0_HRU_Dict = dict()
    H1_HRU_Dict = dict()
    # start
    NumHRU = len( PERV_TARGS )
    # H0 first
    retTuple = readAreaDicts( H0File )
    H0ADict = retTuple[0]
    WS_Area = sum( list( H0ADict[1].values() ) )
    H0PDict = retTuple[1]
    H0IDict = retTuple[2]
    for iI in range(NumHRU):
        cHRU = "HRU_%d" % ( iI + 1 )
        cPTarg = PERV_TARGS[iI]
        cITarg = IMP_TARGS[iI]
        InPreTSId = TS_DICT[cPTarg][0][1]
        cKey = "/TIMESERIES/%s/" % InPreTSId
        PrecSeries = pd.read_hdf( H0File, cKey )
        DataDict = { "Prec_in" : np.array( PrecSeries.values, dtype=np.float32 ), }
        PrecDF = pd.DataFrame( index=PrecSeries.index, data=DataDict )
        if iI == 0:
            # then create our area DataFrames
            H0ADF = createHAreaDF( H0ADict, PrecSeries.index )
            H0PDF = createHAreaDF( H0PDict, PrecSeries.index )
            H0IDF = createHAreaDF( H0IDict, PrecSeries.index )
            # now make sure have the right date ranges
            H0ADF = H0ADF.loc[START_DATE:END_DATE].copy()
            H0PDF = H0PDF.loc[START_DATE:END_DATE].copy()
            H0IDF = H0IDF.loc[START_DATE:END_DATE].copy()
        # end if
        HRUDF = PrecDF.loc[START_DATE:END_DATE].copy()
        HRUDF["Prec_af"] = ( HRUDF["Prec_in"] / 12.0 ) * H0ADF[cHRU]
        InPETTSId = TS_DICT[cPTarg][1][1]
        cKey = "/TIMESERIES/%s/" % InPETTSId
        PETSeries = pd.read_hdf( H0File, cKey )
        DataDict = { "PET_in" : np.array( PETSeries.values, dtype=np.float32 ), }
        PETDF = pd.DataFrame( index=PETSeries.index, data=DataDict )
        PETDF = PETDF.loc[START_DATE:END_DATE].copy()
        HRUDF["PET_in"] = PETDF["PET_in"].to_numpy()
        HRUDF["PET_af"] = ( HRUDF["PET_in"] / 12.0 ) * H0ADF[cHRU]
        cKey = "/RESULTS/PERLND_%s/PWATER/" % cPTarg
        pervDF = pd.read_hdf( H0File, cKey )
        HRUDF["IGWI"] = ( pervDF["IGWI"] / 12.0 ) * H0PDF[cPTarg]
        HRUDF["TAET"] = ( pervDF["TAET"] / 12.0 ) * H0PDF[cPTarg]
        HRUDF["PERO"] = ( pervDF["PERO"] / 12.0 ) * H0PDF[cPTarg]
        cKey = "/RESULTS/IMPLND_%s/IWATER/" % cITarg
        impDF = pd.read_hdf( H0File, cKey )
        HRUDF["IMPEV"] = ( impDF["IMPEV"] / 12.0 ) * H0IDF[cITarg]
        HRUDF["ISURO"] = ( impDF["SURO"] / 12.0 ) * H0IDF[cITarg]
        # now do some calcs
        HRUDF["TOT_Re_af"] = HRUDF["IGWI"]
        HRUDF["TOT_RO_af"] = HRUDF["PERO"] + HRUDF["ISURO"]
        HRUDF["TOT_AET_af"] = HRUDF["TAET"] + HRUDF["IMPEV"]
        # add to our dictionary
        H0_HRU_Dict[cHRU] = HRUDF
    # end for
    # H1
    retTuple = readAreaDicts( H1File )
    H1ADict = retTuple[0]
    H1PDict = retTuple[1]
    H1IDict = retTuple[2]
    for iI in range(NumHRU):
        cHRU = "HRU_%d" % ( iI + 1 )
        cPTarg = PERV_TARGS[iI]
        cITarg = IMP_TARGS[iI]
        InPreTSId = TS_DICT[cPTarg][0][1]
        cKey = "/TIMESERIES/%s/" % InPreTSId
        PrecSeries = pd.read_hdf( H1File, cKey )
        DataDict = { "Prec_in" : np.array( PrecSeries.values, dtype=np.float32 ), }
        PrecDF = pd.DataFrame( index=PrecSeries.index, data=DataDict )
        if iI == 0:
            # then create our area DataFrames
            H1ADF = createHAreaDF( H1ADict, PrecSeries.index )
            H1PDF = createHAreaDF( H1PDict, PrecSeries.index )
            H1IDF = createHAreaDF( H1IDict, PrecSeries.index )
            # now make sure have the right date ranges
            H1ADF = H1ADF.loc[START_DATE:END_DATE].copy()
            H1PDF = H1PDF.loc[START_DATE:END_DATE].copy()
            H1IDF = H1IDF.loc[START_DATE:END_DATE].copy()
        # end if
        HRUDF = PrecDF.loc[START_DATE:END_DATE].copy()
        HRUDF["Prec_af"] = ( HRUDF["Prec_in"] / 12.0 ) * H1ADF[cHRU]
        InPETTSId = TS_DICT[cPTarg][1][1]
        cKey = "/TIMESERIES/%s/" % InPETTSId
        PETSeries = pd.read_hdf( H1File, cKey )
        DataDict = { "PET_in" : np.array( PETSeries.values, dtype=np.float32 ), }
        PETDF = pd.DataFrame( index=PETSeries.index, data=DataDict )
        PETDF = PETDF.loc[START_DATE:END_DATE].copy()
        HRUDF["PET_in"] = PETDF["PET_in"].to_numpy()
        HRUDF["PET_af"] = ( HRUDF["PET_in"] / 12.0 ) * H1ADF[cHRU]
        cKey = "/RESULTS/PERLND_%s/PWATER/" % cPTarg
        pervDF = pd.read_hdf( H1File, cKey )
        HRUDF["IGWI"] = ( pervDF["IGWI"] / 12.0 ) * H1PDF[cPTarg]
        HRUDF["TAET"] = ( pervDF["TAET"] / 12.0 ) * H1PDF[cPTarg]
        HRUDF["PERO"] = ( pervDF["PERO"] / 12.0 ) * H1PDF[cPTarg]
        cKey = "/RESULTS/IMPLND_%s/IWATER/" % cITarg
        impDF = pd.read_hdf( H1File, cKey )
        HRUDF["IMPEV"] = ( impDF["IMPEV"] / 12.0 ) * H1IDF[cITarg]
        HRUDF["ISURO"] = ( impDF["SURO"] / 12.0 ) * H1IDF[cITarg]
        # now do some calcs
        HRUDF["TOT_Re_af"] = HRUDF["IGWI"]
        HRUDF["TOT_RO_af"] = HRUDF["PERO"] + HRUDF["ISURO"]
        HRUDF["TOT_AET_af"] = HRUDF["TAET"] + HRUDF["IMPEV"]
        # add to our dictionary
        H1_HRU_Dict[cHRU] = HRUDF
    # end for
    NumRows = len( H1_HRU_Dict["HRU_1"] )
    H0_AAPrecip_in = np.zeros( NumRows, dtype=np.float64 )
    H0_AAPrecip_af = np.zeros( NumRows, dtype=np.float64 )
    H0_AAPET_in = np.zeros( NumRows, dtype=np.float64 )
    H0_AAPET_af = np.zeros( NumRows, dtype=np.float64 )
    H0_TotAET = np.zeros( NumRows, dtype=np.float64 )
    H0_TotRO = np.zeros( NumRows, dtype=np.float64 )
    H0_TotRe = np.zeros( NumRows, dtype=np.float64 )
    H1_AAPrecip_in = np.zeros( NumRows, dtype=np.float64 )
    H1_AAPrecip_af = np.zeros( NumRows, dtype=np.float64 )
    H1_AAPET_in = np.zeros( NumRows, dtype=np.float64 )
    H1_AAPET_af = np.zeros( NumRows, dtype=np.float64 )
    H1_TotAET = np.zeros( NumRows, dtype=np.float64 )
    H1_TotRO = np.zeros( NumRows, dtype=np.float64 )
    H1_TotRe = np.zeros( NumRows, dtype=np.float64 )
    # now go through and fill these summary arrays
    H0_AETDDict = dict()
    H0_ReDDict = dict()
    H0_RODDict = dict()
    H0_PreDDict = dict()
    H0_PETDDict = dict()
    H1_AETDDict = dict()
    H1_ReDDict = dict()
    H1_RODDict = dict()
    H1_PreDDict = dict()
    H1_PETDDict = dict()
    for iI in range( NumHRU ):
        cHRU = "HRU_%d" % ( iI + 1 )
        H0_AAPrecip_in += ( H0_HRU_Dict[cHRU]["Prec_in"] * 
                            ( H0ADF[cHRU] / WS_Area ) )
        H1_AAPrecip_in += ( H1_HRU_Dict[cHRU]["Prec_in"] * 
                            ( H1ADF[cHRU] / WS_Area ) )
        H0_AAPrecip_af += H0_HRU_Dict[cHRU]["Prec_af"]
        H1_AAPrecip_af += H1_HRU_Dict[cHRU]["Prec_af"]
        H0_AAPET_in += ( H0_HRU_Dict[cHRU]["PET_in"] * 
                            ( H0ADF[cHRU] / WS_Area ) )
        H1_AAPET_in += ( H1_HRU_Dict[cHRU]["PET_in"] * 
                            ( H1ADF[cHRU] / WS_Area ) )
        H0_AAPET_af += H0_HRU_Dict[cHRU]["PET_af"]
        H1_AAPET_af += H1_HRU_Dict[cHRU]["PET_af"]
        H0_TotAET += H0_HRU_Dict[cHRU]["TOT_AET_af"]
        H1_TotAET += H1_HRU_Dict[cHRU]["TOT_AET_af"]
        H0_TotRe += H0_HRU_Dict[cHRU]["TOT_Re_af"]
        H1_TotRe += H1_HRU_Dict[cHRU]["TOT_Re_af"]
        H0_AETDDict[cHRU] = H0_HRU_Dict[cHRU]["TOT_AET_af"].to_numpy()
        H1_AETDDict[cHRU] = H1_HRU_Dict[cHRU]["TOT_AET_af"].to_numpy()
        H0_ReDDict[cHRU] = H0_HRU_Dict[cHRU]["TOT_Re_af"].to_numpy()
        H1_ReDDict[cHRU] = H1_HRU_Dict[cHRU]["TOT_Re_af"].to_numpy()
        H0_RODDict[cHRU] = H0_HRU_Dict[cHRU]["TOT_RO_af"].to_numpy()
        H1_RODDict[cHRU] = H1_HRU_Dict[cHRU]["TOT_RO_af"].to_numpy()
        H0_PreDDict[cHRU] = H0_HRU_Dict[cHRU]["Prec_af"].to_numpy()
        H1_PreDDict[cHRU] = H1_HRU_Dict[cHRU]["Prec_af"].to_numpy()
        H0_PETDDict[cHRU] = H0_HRU_Dict[cHRU]["PET_af"].to_numpy()
        H1_PETDDict[cHRU] = H1_HRU_Dict[cHRU]["PET_af"].to_numpy()
    # end for
    # now add in the RCHRES values
    H0_RRDict = dict()
    H1_RRDict = dict()
    for tKey in RR_TARGS:
        if tKey == ROut:
            continue
        # end if
        cKey = "/RESULTS/RCHRES_%s/HYDR/" % tKey
        H0trrDF = pd.read_hdf( H0File, cKey )
        H0rrDF = H0trrDF[["OVOL1", "OVOL2", "PRSUPY", "VOLEV"]].copy()
        H1trrDF = pd.read_hdf( H1File, cKey )
        H1rrDF = H1trrDF[["OVOL1", "OVOL2", "PRSUPY", "VOLEV"]].copy()
        H0_AETDDict[tKey] = H0rrDF["VOLEV"].to_numpy()
        H1_AETDDict[tKey] = H1rrDF["VOLEV"].to_numpy()
        H0_ReDDict[tKey] = H0rrDF["OVOL2"].to_numpy()
        H1_ReDDict[tKey] = H1rrDF["OVOL2"].to_numpy()
        H0_RODDict[tKey] = H0rrDF["OVOL1"].to_numpy()
        H1_RODDict[tKey] = H1rrDF["OVOL1"].to_numpy()
        H0_AAPrecip_af += H0rrDF["PRSUPY"].to_numpy()
        H1_AAPrecip_af += H1rrDF["PRSUPY"].to_numpy()
        H0_TotAET += H0rrDF["VOLEV"].to_numpy()
        H1_TotAET += H1rrDF["VOLEV"].to_numpy()
        H0_TotRe += H0rrDF["OVOL2"].to_numpy()
        H1_TotRe += H1rrDF["OVOL2"].to_numpy()
        H0_RRDict[tKey] = H0rrDF
        H1_RRDict[tKey] = H1rrDF
    # end for
    # Now do the special stuff for R005
    # first get the spring flow. This is the same for both 
    #  pathways
    InRRITSId = TS_DICT[ROut][2][1]
    cKey = "/TIMESERIES/%s/" % InRRITSId
    SpringSeries = pd.read_hdf( H0File, cKey )
    DataDict = { "Spring_af" : np.array( SpringSeries.values, 
                                dtype=np.float32 ), }
    SpringDF = pd.DataFrame( index=SpringSeries.index, 
                             data=DataDict )
    SpringDF = SpringDF.loc[START_DATE:END_DATE].copy()
    cKey = "/RESULTS/RCHRES_%s/HYDR/" % ROut
    H0trrDF = pd.read_hdf( H0File, cKey )
    H1trrDF = pd.read_hdf( H1File, cKey )
    H0rrDF = H0trrDF[["OVOL1", "PRSUPY", "VOLEV"]].copy()
    H1rrDF = H1trrDF[["OVOL1", "PRSUPY", "VOLEV"]].copy()
    H0rrDF["Spring_af"] = SpringDF["Spring_af"].to_numpy()
    H1rrDF["Spring_af"] = SpringDF["Spring_af"].to_numpy()
    H0rrDF["Net_RO"] = H0rrDF["OVOL1"] - H0rrDF["Spring_af"]
    H1rrDF["Net_RO"] = H1rrDF["OVOL1"] - H1rrDF["Spring_af"]
    H0_AETDDict[ROut] = H0rrDF["VOLEV"].to_numpy()
    H1_AETDDict[ROut] = H1rrDF["VOLEV"].to_numpy()
    H0_RODDict[ROut] = H0rrDF["OVOL1"].to_numpy()
    H1_RODDict[ROut] = H1rrDF["OVOL1"].to_numpy()
    H0_AAPrecip_af += H0rrDF["PRSUPY"].to_numpy()
    H1_AAPrecip_af += H1rrDF["PRSUPY"].to_numpy()
    H0_TotAET += H0rrDF["VOLEV"].to_numpy()
    H1_TotAET += H1rrDF["VOLEV"].to_numpy()
    H0_TotRO += H0rrDF["Net_RO"]
    H1_TotRO += H1rrDF["Net_RO"]
    H0_RRDict[ROut] = H0rrDF
    H1_RRDict[ROut] = H1rrDF
    H0AetDF = pd.DataFrame(index=SpringDF.index, data=H0_AETDDict )
    H1AetDF = pd.DataFrame(index=SpringDF.index, data=H1_AETDDict )
    H0RoDF = pd.DataFrame(index=SpringDF.index, data=H0_RODDict )
    H1RoDF = pd.DataFrame(index=SpringDF.index, data=H1_RODDict )
    H0ReDF = pd.DataFrame(index=SpringDF.index, data=H0_ReDDict )
    H1ReDF = pd.DataFrame(index=SpringDF.index, data=H1_ReDDict )
    H0PreDF = pd.DataFrame(index=SpringDF.index, data=H0_PreDDict )
    H1PreDF = pd.DataFrame(index=SpringDF.index, data=H1_PreDDict )
    H0PETDF = pd.DataFrame(index=SpringDF.index, data=H0_PETDDict )
    H1PETDF = pd.DataFrame(index=SpringDF.index, data=H1_PETDDict )
    H0DataDict = { "Tot_Prec" : H0_AAPrecip_af,
                   "Tot_PET" : H0_AAPET_af,
                   "Tot_AET" : H0_TotAET,
                   "Tot_Re" : H0_TotRe,
                   "Tot_RO" : H0_TotRO, }
    H0WBDF = pd.DataFrame( index=SpringDF.index, data=H0DataDict )
    H1DataDict = { "Tot_Prec" : H1_AAPrecip_af,
                   "Tot_PET" : H1_AAPET_af,
                   "Tot_AET" : H1_TotAET,
                   "Tot_Re" : H1_TotRe,
                   "Tot_RO" : H1_TotRO, }
    H1WBDF = pd.DataFrame( index=SpringDF.index, data=H1DataDict )
    DeltaDDict = { "Del_Prec" : ( H1_AAPrecip_af - H0_AAPrecip_af ),
                   "Del_PET" : ( H1_AAPET_af - H0_AAPET_af ),
                   "Del_AET" : ( H1_TotAET - H0_TotAET ),
                   "Del_Re" : ( H1_TotRe - H0_TotRe ),
                   "Del_RO" : ( H1_TotRO - H0_TotRO ), }
    DelWBDF = pd.DataFrame( index=SpringDF.index, data=DeltaDDict )
    # now output
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_WBTotals_DF.pickle" % realNum ) )
    H0WBDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_WBTotals_DF.pickle" % realNum ) )
    H1WBDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_WBDeltas_DF.pickle" % realNum ) )
    DelWBDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_AET_DF.pickle" % realNum ) )
    H0AetDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_AET_DF.pickle" % realNum ) )
    H1AetDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_RO_DF.pickle" % realNum ) )
    H0RoDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_RO_DF.pickle" % realNum ) )
    H1RoDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_Re_DF.pickle" % realNum ) )
    H0ReDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_Re_DF.pickle" % realNum ) )
    H1ReDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_Prec_DF.pickle" % realNum ) )
    H0PreDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_Prec_DF.pickle" % realNum ) )
    H1PreDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H0_PET_DF.pickle" % realNum ) )
    H0PETDF.to_pickle( OutFiler, compression='zip' )
    OutFiler = os.path.normpath( os.path.join( workDir, 
                                "R%d_H1_PET_DF.pickle" % realNum ) )
    H1PETDF.to_pickle( OutFiler, compression='zip' )
    # end so return
    return


#EOF