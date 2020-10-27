# -*- coding: utf-8 -*-
"""
.. module:: WG_HighRealResults
   :platform: Windows, Linux
   :synopsis: Provides logic for handling one realization per process worker

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Stores two results for each realization, the H0 or null branch, and the H1 or
alterantive branch. For precipitation, store daily precip depth for each
grid cell. For other parameters, store a single value per day for the entire
domain.
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
import pandas as pd
import numpy as np
import WG_Inputs as WGI


#------------------------------------------------------------------------
TMAX_IND = 0
TMIN_IND = 1
PRE_START_IND = 2

# Program, global data structures
H0_REAL = None
"""Single realization output for H0 case"""
H1_REAL = None
"""Single realization output for H1 case"""

#--------------------------------------------------------------------------
# python functions
def createSimStructures(TotDays):
    """Convenience method to create and set the simulation structures
    """
    # imports
    # globals
    global H0_REAL, H1_REAL, PRE_START_IND
    # start of function
    TotNum = PRE_START_IND + WGI.NUM_LOCA_GRID
    H0_REAL = np.zeros( (TotDays, TotNum), dtype=np.float32 )
    H1_REAL = np.zeros( (TotDays, TotNum), dtype=np.float32 )
    # end

def createDepArrayData( curMonth, h0pindex, DataPDepTrack ):
    """Assign precipitation depth (i.e. 0) to an array to use to assign values
    
    Args:
        curMonth (int): the current month
        h0pIndex (int): the index within the period type of the distribution
        DataPDepTrack (dict): data tracking precip depth
    
    Returns:
        preVals (np.array): precipitation depth values
    """
    # imports
    # start
    preVals = np.zeros( WGI.NUM_LOCA_GRID, dtype=np.float32 )
    iCnt = 0
    for tGId in WGI.LOCA_KEYS:
        preVals[iCnt] = DataPDepTrack[h0pindex][tGId][curMonth]
        # 
        iCnt += 1
    # end for
    return preVals

def createDepArrayCProj( curMonth, pType, pIndex, DataPDepTrack, ProjPDepTrack ):
    """Assign precipitation depth (i.e. 0) to an array to use to assign values
    
    Args:
        curMonth (int): the current month
        pType (str): the current period type == data or cproj
        pIndex (int): the index within the period type of the distribution
        DataPDepTrack (dict): data tracking precip depth
        ProjPDepTrack (dict): climate projection tracking precip depth
    
    Returns:
        preVals (np.array): precipitation depth values
    """
    # imports
    # start
    preVals = np.zeros( WGI.NUM_LOCA_GRID, dtype=np.float32 )
    iCnt = 0
    for tGId in WGI.LOCA_KEYS:
        if pType == WGI.DATA_KEYW:
            preVals[iCnt] = DataPDepTrack[pIndex][tGId][curMonth]
        else:
            preVals[iCnt] = ProjPDepTrack[pIndex][tGId][curMonth]
        # 
        iCnt += 1
    # end for
    return preVals

def assignDryDepData( tIndex ):
    """Assign dry precipitation depth (i.e. 0) to the correct time interval
    
    Args:
        tIndex (int): current time interval
    
    """
    # imports
    # start
    global H0_REAL, PRE_START_IND
    # start function
    H0_REAL[tIndex, PRE_START_IND:] = np.zeros( WGI.NUM_LOCA_GRID, 
                                                dtype=np.float32 )
    # end of function

def assignWetDepData( tIndex, PDepArray ):
    """Assign precipitation depth (i.e. 0) to the H0 data structure.
    
    Args:
        tIndex (int): current time interval
        PDepArray (np.array): precip depth
    
    """
    # globals
    global H0_REAL, PRE_START_IND
    # start
    H0_REAL[tIndex, PRE_START_IND:] = PDepArray
    # end of function

def assignDryDepCProj( tIndex ):
    """Assign dry precipitation depth (i.e. 0) to the projection data 
    structure
    
    Args:
        tIndex (int): current time interval
        
    """
    # globals
    global H1_REAL, PRE_START_IND
    # start of function
    H1_REAL[tIndex, PRE_START_IND:] = np.zeros( WGI.NUM_LOCA_GRID, 
                                                dtype=np.float32 )
    # end of function

def assignWetDepCProj( tIndex, PDepArray ):
    """Assign precipitation depth (i.e. 0) to the projection data structure
    
    Args:
        tIndex (int): current time interval
        PDepArray (np.array): precip depth
    
    """
    # globals
    global H1_REAL, PRE_START_IND
    # start
    H1_REAL[tIndex, PRE_START_IND:] = PDepArray
    # end of function

def assignTempData( tIndex, MaxT, MinT ):
    """Convenience function to assign simulated temperature values to the
    data side of the structures.
    
    Args:
        tIndex (int): the time index
        MaxT (float): max temp
        MinT (float): min temp
    
    """
    # globals
    global H0_REAL, TMAX_IND, TMIN_IND
    # start
    H0_REAL[tIndex, TMAX_IND] = MaxT
    H0_REAL[tIndex, TMIN_IND] = MinT
    # end

def assignTempCProj( tIndex, MaxT, MinT ):
    """Convenience function to assign simulated temperature values to the
    projection side of the structures.
    
    Args:
        tIndex (int): the time index
        MaxT (float): max temp
        MinT (float): min temp
    """
    # globals
    global H1_REAL, TMAX_IND, TMIN_IND
    # start
    H1_REAL[tIndex, TMAX_IND] = MaxT
    H1_REAL[tIndex, TMIN_IND] = MinT
    # end

def outputRealResults(RealNum, DT_INDEX):
    """Output the results for the current realization. Use Pandas DataFrames
    and pickles.
    
    Args:
        RealNum (int): current realization number.
        DT_INDEX (pd.DateTimeIndex): index for all outputs
    """
    # imports
    import pandas as pd
    from os import path
    # globals
    global H0_REAL, H1_REAL, PRE_START_IND, TMAX_IND, TMIN_IND
    # start
    # file names
    H0FileName = "H0_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H1FileName = "H1_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H0OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H0FileName ) )
    H1OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H1FileName ) )
    # make our DataFrames
    TotNum = PRE_START_IND + WGI.NUM_LOCA_GRID
    H0DDict = { "Tmax_C" : H0_REAL[:,TMAX_IND],
                "Tmin_C" : H0_REAL[:,TMIN_IND],
              }
    for iI in range( PRE_START_IND, TotNum, 1):
        cGID = WGI.LOCA_KEYS[iI - PRE_START_IND]
        H0DDict[ "Precip_mm_%d" % cGID] = H0_REAL[:,iI]
    # end of for
    H0DF = pd.DataFrame( index=DT_INDEX, data=H0DDict )
    H1DDict = { "Tmax_C" : H1_REAL[:,TMAX_IND],
                "Tmin_C" : H1_REAL[:,TMIN_IND],
              }
    for iI in range( PRE_START_IND, TotNum, 1):
        cGID = WGI.LOCA_KEYS[iI - PRE_START_IND]
        H1DDict[ "Precip_mm_%d" % cGID] = H1_REAL[:,iI]
    # end of for
    H1DF = pd.DataFrame( index=DT_INDEX, data=H1DDict )
    H0DF.to_pickle( H0OutFP, compression='zip' )
    H1DF.to_pickle( H1OutFP, compression='zip' )
    # end
    return

def outputWSResults(RealNum, DT_INDEX, TotDays):
    """Output the watershed results for the current realizationn. Use Pandas DataFrames
    and pickles. Uses area average of precipitation grid cells to calc the WS precip.
    
    Args:
        RealNum (int): current realization number.
        DT_INDEX (pd.DateTimeIndex): index for all outputs
        TotDays (int): total number of days in realization
    """
    # imports
    import pandas as pd
    from os import path
    # globals
    global H0_REAL, H1_REAL, PRE_START_IND, TMAX_IND, TMIN_IND
    # start
    # file names
    H0FileName = "WS_H0_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H1FileName = "WS_H1_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H0OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H0FileName ) )
    H1OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H1FileName ) )
    # make our DataFrames
    TotNum = PRE_START_IND + WGI.NUM_LOCA_GRID
    H0DDict = { "Tmax_C" : H0_REAL[:,TMAX_IND],
                "Tmin_C" : H0_REAL[:,TMIN_IND],
              }
    TAve = 0.5 * ( H0_REAL[:,TMAX_IND] + H0_REAL[:,TMIN_IND] )
    H0DDict["Tave_C"] = TAve
    PrecipAve = np.zeros( TotDays, dtype=np.float64 )
    for iI in range( PRE_START_IND, TotNum, 1):
        cGID = WGI.LOCA_KEYS[iI - PRE_START_IND]
        PrecipAve = PrecipAve + ( H0_REAL[:,iI] * WGI.GRID_AREA_WT[cGID] )
    # end of for
    H0DDict[ "Precip_mm"] = PrecipAve
    H0DDict[ "ETo_mm" ] = calcPET_HS( DT_INDEX, TAve )
    H0DF = pd.DataFrame( index=DT_INDEX, data=H0DDict )
    # now H1
    H1DDict = { "Tmax_C" : H1_REAL[:,TMAX_IND],
                "Tmin_C" : H1_REAL[:,TMIN_IND],
              }
    TAve = 0.5 * ( H1_REAL[:,TMAX_IND] + H1_REAL[:,TMIN_IND] )
    H1DDict["Tave_C"] = TAve
    PrecipAve = np.zeros( TotDays, dtype=np.float64 )
    for iI in range( PRE_START_IND, TotNum, 1):
        cGID = WGI.LOCA_KEYS[iI - PRE_START_IND]
        PrecipAve = PrecipAve + ( H1_REAL[:,iI] * WGI.GRID_AREA_WT[cGID] )
    # end of for
    H1DDict[ "Precip_mm" ] = PrecipAve
    H1DDict[ "ETo_mm" ] = calcPET_HS( DT_INDEX, TAve )
    H1DF = pd.DataFrame( index=DT_INDEX, data=H1DDict )
    # calculate the monthly water balance
    H0DFMon, H1DFMon = calcTMMonthlyWB( H0DF, H1DF )
    # calculate the differences
    DeltaDF = calcDeltaDF( H0DFMon, H1DFMon )
    # write out all of our waterbalance related DataFrames
    H0DF.to_pickle( H0OutFP, compression='zip' )
    H1DF.to_pickle( H1OutFP, compression='zip' )
    # get some new filenames
    H0FileName = "WB_H0_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H1FileName = "WB_H1_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    H0OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H0FileName ) )
    H1OutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                        H1FileName ) )
    H0DFMon.to_pickle( H0OutFP, compression='zip' )
    H1DFMon.to_pickle( H1OutFP, compression='zip' )
    # delta filename
    DelFileName = "Delta_%s_R%d_DF.pickle" % (WGI.OUT_LABEL, RealNum)
    DelOutFP = path.normpath( path.join( WGI.OUT_DIR, WGI.OUT_SUB_DIR, 
                                         DelFileName ) )
    DeltaDF.to_pickle( DelOutFP, compression='zip' )
    # end
    return

def calcPET_HS( DT_INDEX, TAve ):
    """Calculate PET in mm using Hargreaves-Samani

    Args:
        DT_INDEX (pd.DateTimeIndex): index for all outputs
        TAve (np.array): simulated daily average temperature
    
    Returns:
        ETo_mmd (np.array): PET depths per day in mm
    """
    # imports
    import math
    # parameters
    LAT_DEG = 30.0  # degrees latitute
    # start of function
    # solar rad calcs
    DayOYr = DT_INDEX.dayofyear.to_numpy()
    SDec_rad = 0.4093 * np.sin( ( ( ( 2.0 * math.pi ) / 365.0 ) * DayOYr ) - 1.405 )
    SunS_rad = np.arccos( -1.0 * math.tan(math.radians(LAT_DEG)) * np.tan(SDec_rad) )
    RelDEtoS = 1.0 + 0.033 * np.cos( ( ( 2.0 * math.pi ) / 365.0 ) *DayOYr )
    #MaxDayHrs = (24.0/math.pi) * SunS_rad
    S_o_mmd = 15.392 * RelDEtoS * ( ( SunS_rad * math.sin( math.radians(LAT_DEG) ) * np.sin( SDec_rad ) ) + 
                ( math.cos( math.radians(LAT_DEG) ) * np.cos( SDec_rad ) * np.sin( SunS_rad ) ) ) 
    # now for the PET calc
    MonthA = DT_INDEX.month.tolist()
    Delta_T = np.array( [ WGI.PET_MON_NORMS[x] for x in MonthA ], dtype=np.float64 )
    ETo_mmd = 0.0023 * S_o_mmd * Delta_T * ( TAve + 17.8 )
    # return
    return ETo_mmd

def calcTMMonthlyWB( H0Daily, H1Daily ):
    """ Calculate Thornthwaite-Mather monthly water balance using ETo and Precip as simulated 
    from the weather generators.

    Args:
        H0Daily (pd.DataFrame): pandas DataFrame with daily precip and ETo for path 0
        H1Daily (pd.DataFrame): pandas DataFrame with daily precip and ETo for path 1
    """
    # imports
    import math
    from WG_Inputs import K_c, RDAY_ET, RTM_EXP_TERM, RTM_SLOPE, AVAIL_WS
    from WG_Inputs import MON_DETENTION_RE, MON_SURPLUS_RO
    # globals
    # parameters
    # locals
    # start
    # make copies of the argument DataFrames for modifications.
    cH0DF = H0Daily[['Precip_mm', 'ETo_mm']].copy()
    cH1DF = H1Daily[['Precip_mm', 'ETo_mm']].copy()
    # adjust our output dates slightly for the water balance calcs
    Start_DT = pd.Timestamp( 1981, 1, 1, 0 )
    End_DT = cH1DF.index[ len(cH1DF) - 2 ]
    cH0DF = cH0DF.loc[Start_DT:End_DT].copy()
    cH1DF = cH1DF.loc[Start_DT:End_DT].copy()
    # calculate PET
    cH0DF["PET_mm"] = cH0DF.apply( lambda row: adjustETo( K_c, RDAY_ET, row['ETo_mm'], 
                                                          row['Precip_mm'] ), axis= 1 )
    cH1DF["PET_mm"] = cH1DF.apply( lambda row: adjustETo( K_c, RDAY_ET, row['ETo_mm'], 
                                                          row['Precip_mm'] ), axis= 1 )
    # resample to monthly
    H0DFMon = cH0DF.resample( 'MS', closed='left', label='left' ).sum()
    H1DFMon = cH1DF.resample( 'MS', closed='left', label='left' ).sum()
    # calculate excess precipitation
    H0DFMon["P-PET_mm"] = H0DFMon["Precip_mm"] - H0DFMon["PET_mm"]
    H1DFMon["P-PET_mm"] = H1DFMon["Precip_mm"] - H1DFMon["PET_mm"]
    # get the total number of months in our DataFrames
    TotMon = len( H0DFMon )
    # Accumulated potential water loss (APWL) needs to refer to previous month's values
    # Use a for loop for this now - could be vectorized later
    H0DFMon["APWL_mm"] = 0.0
    H1DFMon["APWL_mm"] = 0.0
    for iI in range(TotMon):
        cInd = H0DFMon.index[iI]
        if iI == 0:
            prevH0 = 0.0
            prevH1 = 0.0
        # now do the calculation
        cH0EP = H0DFMon.at[cInd, "P-PET_mm"]
        cH1EP = H1DFMon.at[cInd, "P-PET_mm"]
        if cH0EP <= 0.0:
            cH0APWL = cH0EP + prevH0
        else:
            cH0APWL = 0.0
        if cH1EP <= 0.0:
            cH1APWL = cH1EP + prevH1
        else:
            cH1APWL = 0.0
        # set the values
        H0DFMon.at[cInd, "APWL_mm"] = cH0APWL
        H1DFMon.at[cInd, "APWL_mm"] = cH1APWL
        # archive the previous
        prevH0 = cH0APWL
        prevH1 = cH1APWL
    # end for
    # Soil moisture also requires previous month's values. Calculate delta SM
    # at the same time
    H0DFMon["SM_mm"] = 0.0
    H1DFMon["SM_mm"] = 0.0
    H0DFMon["DelSM_mm"] = 0.0
    H1DFMon["DelSM_mm"] = 0.0
    for iI in range(TotMon):
        cInd = H0DFMon.index[iI]
        if iI == 0:
            prevH0 = 0.0
            prevH1 = 0.0
        # now do the calculation
        cH0EP = H0DFMon.at[cInd, "P-PET_mm"]
        cH0APWL = H0DFMon.at[cInd, "APWL_mm"]
        cH1EP = H1DFMon.at[cInd, "P-PET_mm"]
        cH1APWL = H1DFMon.at[cInd, "APWL_mm"]
        if cH0EP > 0:
            H0SM = min( AVAIL_WS, ( cH0EP + prevH0 ) )
        else:
            H0SM = ( math.pow( 10.0, ( math.log10( AVAIL_WS / 25.4 ) - ( 
                    ( abs( cH0APWL ) / 25.4 ) * RTM_SLOPE * 
                    ( ( AVAIL_WS / 25.4 )**( RTM_EXP_TERM ) ) ) ) ) * 25.4 )
        if cH1EP > 0:
            H1SM = min( AVAIL_WS, ( cH1EP + prevH1 ) )
        else:
            H1SM = ( math.pow( 10.0, ( math.log10( AVAIL_WS / 25.4 ) - ( 
                    ( abs( cH1APWL ) / 25.4 ) * RTM_SLOPE * 
                    ( ( AVAIL_WS / 25.4 )**( RTM_EXP_TERM ) ) ) ) ) * 25.4 )
        # now update
        # set the values
        H0DFMon.at[cInd, "SM_mm"] = H0SM
        H1DFMon.at[cInd, "SM_mm"] = H1SM
        H0DFMon.at[cInd, "DelSM_mm"] = H0SM - prevH0
        H1DFMon.at[cInd, "DelSM_mm"] = H1SM - prevH1
        # archive the previous
        prevH0 = H0SM
        prevH1 = H1SM
    # end for
    # AET can be calculated with a lambda
    H0DFMon["AET_mm"] = H0DFMon.apply( lambda row: calcAET( row["P-PET_mm"], row["PET_mm"], 
                                                        row["Precip_mm"], row["DelSM_mm"] ), 
                                       axis=1 )
    H1DFMon["AET_mm"] = H1DFMon.apply( lambda row: calcAET( row["P-PET_mm"], row["PET_mm"], 
                                                            row["Precip_mm"], row["DelSM_mm"] ), 
                                       axis=1 )
    # calculate the monthly deficit
    H0DFMon["Def_mm"] = H0DFMon["PET_mm"] - H0DFMon["AET_mm"]
    H1DFMon["Def_mm"] = H1DFMon["PET_mm"] - H1DFMon["AET_mm"]
    # for surplus calculation can use a lambda
    H0DFMon["Surp_mm"] = H0DFMon.apply( lambda row: calcSurplus( row["SM_mm"], AVAIL_WS, 
                                                             row["Precip_mm"], row["AET_mm"] ), 
                                        axis=1 )
    H1DFMon["Surp_mm"] = H1DFMon.apply( lambda row: calcSurplus( row["SM_mm"], AVAIL_WS, 
                                                                row["Precip_mm"], row["AET_mm"] ), 
                                        axis=1 )
    # because need multiple values from multiple months use a loop to calculate the remaining
    H0DFMon["TotAvail_mm"] = 0.0
    H1DFMon["TotAvail_mm"] = 0.0
    H0DFMon["RO_mm"] = 0.0
    H1DFMon["RO_mm"] = 0.0
    H0DFMon["Detent_mm"] = 0.0
    H1DFMon["Detent_mm"] = 0.0
    H0DFMon["Re_mm"] = 0.0
    H1DFMon["Re_mm"] = 0.0
    for iI in range(TotMon):
        cInd = H0DFMon.index[iI]
        if iI == 0:
            prevH0 = 0.0
            prevH1 = 0.0
        # now do the calculation
        cH0Surp = H0DFMon.at[cInd, "Surp_mm"]
        cH1Surp = H1DFMon.at[cInd, "Surp_mm"]
        cH0TotA = cH0Surp + prevH0
        cH1TotA = cH1Surp + prevH1
        cH0RO = cH0TotA * MON_SURPLUS_RO
        cH1RO = cH1TotA * MON_SURPLUS_RO
        cH0Re = ( cH0TotA - cH0RO ) * MON_DETENTION_RE
        cH1Re = ( cH1TotA - cH1RO ) * MON_DETENTION_RE
        cH0Det =  cH0TotA - ( cH0RO + cH0Re )
        cH1Det =  cH1TotA - ( cH1RO + cH1Re )
        # assign
        H0DFMon.at[cInd, "TotAvail_mm"] = cH0TotA
        H1DFMon.at[cInd, "TotAvail_mm"] = cH1TotA
        H0DFMon.at[cInd, "RO_mm"] = cH0RO
        H1DFMon.at[cInd, "RO_mm"] = cH1RO
        H0DFMon.at[cInd, "Detent_mm"] = cH0Det
        H1DFMon.at[cInd, "Detent_mm"] = cH1Det
        H0DFMon.at[cInd, "Re_mm"] = cH0Re
        H1DFMon.at[cInd, "Re_mm"] = cH1Re
        # now carry forward
        prevH0 = cH0Det
        prevH1 = cH1Det
    # end of for
    # now have the complete monthly water balance calculated for this realization and both
    # pathways
    return ( H0DFMon, H1DFMon )

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

def calcAET( EP, PET, P, delSM ):
    """ Calculate AET from excess precipitation (EP), potential evapotranspiration
    (PET), precipitation (P), and change in soil moisture (delSM)
    
    Args:
        EP (float): excess precipitation
        PET (float): potential evapotranspiration
        P (float): precipitation
        delSM (float): change in soil moisture
    """
    if EP >= 0.0:
        AET = PET
    else:
        AET = P - delSM
    # return
    return AET

def calcSurplus( SM, AvailWS, P, AET ):
    """Calculate soil moisture surplus
    
    Args:
        SM (float): soil moisture in depth
        AvailWS (float): soil column available water storage in depth
        P (float): precipitation in depth
        AET (float): actual evapotranspiration in depth
        
    """
    if SM >= AvailWS:
        surPl = P - AET
    else:
        surPl = 0.0
    # return
    return surPl

def calcDeltaDF( H0DFMon, H1DFMon ):
    """ Calculate the differences between the two pathways for the 
    key watershed water balance constituents and return this as a new
    DataFrame.

    Args:
        H0DFMon (pd.DataFrame): monthly water balance H0
        H1DFMon (pd.DataFrame): monthly water balance H1

    Returns:
        pd.DataFrame with deltas for precip, PET, AET, RO, and RE
    """
    # first extract our differences
    delta_Precip = ( H1DFMon["Precip_mm"] - H0DFMon["Precip_mm"] ).to_numpy()
    delta_PET = ( H1DFMon["PET_mm"] - H0DFMon["PET_mm"] ).to_numpy()
    delta_AET = ( H1DFMon["AET_mm"] - H0DFMon["AET_mm"] ).to_numpy()
    delta_RO = ( H1DFMon["RO_mm"] - H0DFMon["RO_mm"] ).to_numpy()
    delta_Re = ( H1DFMon["Re_mm"] - H0DFMon["Re_mm"] ).to_numpy()
    # get the index
    DeltaInd = H1DFMon.index.tolist()
    # make the dataframe
    DataDict = { "Precip_mm" : delta_Precip,
                 "PET_mm" : delta_PET,
                 "AET_mm" : delta_AET,
                 "RO_mm" : delta_RO,
                 "Re_mm" : delta_Re,
            }
    DeltaDF = pd.DataFrame( data=DataDict, index=DeltaInd )
    # return
    return DeltaDF

def cleanAllEnd():
    """Convenience method to clean up at the end"""
    global H0_REAL, H1_REAL
    # start
    H0_REAL = None
    H1_REAL = None

# EOF