# -*- coding: utf-8 -*-
"""
.. module:: WG_OtherWeaterh
   :platform: Windows, Linux
   :synopsis: Provides the logic for the other, non-precipitation, weather parameters

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Handles the calculation of daily values using helper functions from other modules. Also
sends the daily values elsewhere for archive.
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
import pickle
import WG_Inputs as WGI

# numpy set err
#np.seterr(all='raise')

# module level parameters
NUM_OTHER = 2
"""Number of other weather parameters in this case we are only dealing with
Min and max temperature"""
NUM_DAYS_YR = 366
"""Number of days in the year, maximum number"""
NUM_DATA_PER = WGI.NUM_DATA_PERIODS
"""Number of data periods in this formulation """
NUM_PROJ_PER = WGI.NUM_PROJ_PERIODS
"""Number of projection periods in this formulation"""
SIGMA_THRESH = 4.0
"""Sigma multiplier threshold for standard deviations"""

# module level variables
A_DATA = np.ones( (NUM_DATA_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""A array for calculating or projecting the daily residual or error term."""
B_DATA = np.ones( (NUM_DATA_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""B array for calculating or projecting the daily residual or error term."""
A_PROJ = np.ones( (NUM_PROJ_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""A array for calculating or projecting the daily residual or error term."""
B_PROJ = np.ones( (NUM_PROJ_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""B array for calculating or projecting the daily residual or error term."""
M0 = np.ones( (NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""M0 array for calculating A and B matrices. Not currently used"""
M1 = np.ones( (NUM_OTHER, NUM_OTHER), dtype=np.float64 )
"""M1 array for calculating A and B matrices. Not currently used"""
DATA_WET_TMAX_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average wet state daily Tmax, smoothed from PRISM 1981-2010"""
DATA_WET_TMAX_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily wet state standard deviation of Tmax, smoothed from PRISM 1981-2010"""
DATA_WET_TMIN_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily wet state Tmin, smoothed from PRISM 1981-2010"""
DATA_WET_TMIN_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily wet state standard deviation of Tmin, smoothed from PRISM 1981-2010"""
DATA_DRY_TMAX_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average dry state daily Tmax, smoothed from PRISM 1981-2010"""
DATA_DRY_TMAX_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily dry state standard deviation of Tmax, smoothed from PRISM 1981-2010"""
DATA_DRY_TMIN_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily dry state Tmin, smoothed from PRISM 1981-2010"""
DATA_DRY_TMIN_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily dry state standard deviation of Tmin, smoothed from PRISM 1981-2010"""
PROJ_WET_TMAX_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily wet state Tmax, for climate projection periods. Calculated as 
PRISM value plus the difference between the CMIP5, LOCA values for the 
pertinent projection period from the prior period."""
PROJ_WET_TMAX_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily wet state standard deviation of Tmax, for climate projection periods. 
Calculatedas PRISM value plus the difference between the CMIP5, LOCA values 
for the pertinent projection period from the prior period."""
PROJ_WET_TMIN_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily wet state Tmin, for climate projection periods. Calculated as 
PRISM value plus the difference between the CMIP5, LOCA values for the 
pertinent projection period from the prior period."""
PROJ_WET_TMIN_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily wet state standard deviation of Tmin, for climate projection periods. 
Calculatedas PRISM value plus the difference between the CMIP5, LOCA values 
for the pertinent projection period from the prior period."""
PROJ_DRY_TMAX_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily dry state Tmax, for climate projection periods. Calculated as 
PRISM value plus the difference between the CMIP5, LOCA values for the 
pertinentprojection period from the prior period."""
PROJ_DRY_TMAX_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily dry state standard deviation of Tmax, for climate projection periods. 
Calculatedas PRISM value plus the difference between the CMIP5, LOCA values 
for the pertinent projection period from the prior period."""
PROJ_DRY_TMIN_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Average daily dry state Tmin, for climate projection periods. Calculated as 
PRISM value plus the difference between the CMIP5, LOCA values for the 
pertinent projection period from the prior period."""
PROJ_DRY_TMIN_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
"""Daily dry state standard deviation of Tmin, for climate projection periods. 
Calculated as PRISM value plus the difference between the CMIP5, LOCA values 
for the pertinent projection period from the prior period."""
EPS_STD_NORMAL = list()
"""The list of standard normal error variates"""
EPS_NORM_SAMP = list()
"""The list of samplers for the standard normal error variates."""
EPSI_2 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
"""Tracker for actual epsilon values"""
CHI0M0 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
"""Current day Chi matrix for H0"""
CHIL1M0 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
"""Previous day Chi matrix for H0"""
CHI0M1 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
"""Current day Chi matrix for H1"""
CHIL1M1 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
"""Previous day Chi matrix for H1"""

#--------------------------------------------------------------------------
# functions
def populateMmats():
    """Convenience function to read in and populate the M0 and M1 matrices
    
    """
    # globals
    global M0, M1
    # start of function
    # do the M0
    with open(WGI.OW_M0_IN, 'rb') as InP:
        M0_long = pickle.load( InP )
    # end of with block
    M0[0,0] = M0_long.at['rho_1X', 'rho_X1']
    M0[1,0] = M0_long.at['rho_2X', 'rho_X1']
    M0[0,1] = M0_long.at['rho_1X', 'rho_X2']
    M0[1,1] = M0_long.at['rho_2X', 'rho_X2']
    # then the M1
    with open(WGI.OW_M1_IN, 'rb') as InP:
        M1_long = pickle.load( InP )
    # end of with block
    M1[0,0] = M1_long.at['rho_1X', 'rho_X1_L1']
    M1[1,0] = M1_long.at['rho_2X', 'rho_X1_L1']
    M1[0,1] = M1_long.at['rho_1X', 'rho_X2_L1']
    M1[1,1] = M1_long.at['rho_2X', 'rho_X2_L1']
    # end of function
    return

def constructDataPeriodArrays():
    """Convenience method to construct data period arrays. 
    
    Because of the way
    the input variables are currently structured, this is hard coded for
    one data period.
    """
    # globals
    global DATA_WET_TMAX_AVE, DATA_WET_TMAX_STD, DATA_WET_TMIN_AVE
    global DATA_WET_TMIN_STD, DATA_DRY_TMAX_AVE, DATA_DRY_TMAX_STD
    global DATA_DRY_TMIN_AVE, DATA_DRY_TMIN_STD, NUM_DATA_PER, A_DATA
    global B_DATA
    # Now read in our values/files and construct
    WAveDF = pd.read_pickle( WGI.OW_WET_AVE_PRISM )
    DATA_WET_TMAX_AVE[(NUM_DATA_PER - 1), :] = np.array( WAveDF['Tmax_C'],
                                                         dtype=np.float64 )
    DATA_WET_TMIN_AVE[(NUM_DATA_PER - 1), :] = np.array( WAveDF['Tmin_C'],
                                                         dtype=np.float64 )
    WStdDF = pd.read_pickle( WGI.OW_WET_STD_PRISM )
    DATA_WET_TMAX_STD[(NUM_DATA_PER - 1), :] = np.array( WStdDF['Tmax_C'],
                                                         dtype=np.float64 )
    DATA_WET_TMIN_STD[(NUM_DATA_PER - 1), :] = np.array( WStdDF['Tmin_C'],
                                                         dtype=np.float64 )
    DAveDF = pd.read_pickle( WGI.OW_DRY_AVE_PRISM )
    DATA_DRY_TMAX_AVE[(NUM_DATA_PER - 1), :] = np.array( DAveDF['Tmax_C'],
                                                         dtype=np.float64 )
    DATA_DRY_TMIN_AVE[(NUM_DATA_PER - 1), :] = np.array( DAveDF['Tmin_C'],
                                                         dtype=np.float64 )
    DStdDF = pd.read_pickle( WGI.OW_DRY_STD_PRISM )
    DATA_DRY_TMAX_STD[(NUM_DATA_PER - 1), :] = np.array( DStdDF['Tmax_C'],
                                                         dtype=np.float64 )
    DATA_DRY_TMIN_STD[(NUM_DATA_PER - 1), :] = np.array( DStdDF['Tmin_C'],
                                                         dtype=np.float64 )
    # next do the A and B data
    A_DATA[(NUM_DATA_PER - 1), :, :] = np.array( WGI.A_DATA_LIST, 
                                                 dtype=np.float64 )
    B_DATA[(NUM_DATA_PER - 1), :, :] = np.array( WGI.B_DATA_LIST, 
                                                 dtype=np.float64 )
    # end of function
    return

def constructCProjPeriodArrays():
    """Convenience method to load smoothed climate projection period arrays.

    Because of the way the input variables are currently structured, this is 
    hard coded for three projection period.
    """
    # globals
    global PROJ_WET_TMAX_AVE, PROJ_WET_TMIN_AVE, PROJ_DRY_TMAX_AVE
    global PROJ_DRY_TMIN_AVE, PROJ_WET_TMAX_STD, PROJ_WET_TMIN_STD
    global PROJ_DRY_TMAX_STD, PROJ_DRY_TMIN_STD, A_PROJ, B_PROJ
    # Now read in our values/files and construct
    # cliamte projection period 1
    WAve1DF = pd.read_pickle( WGI.OW_WET_AVE_PROJ1 )
    PROJ_WET_TMAX_AVE[0, :] = np.array( WAve1DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_AVE[0, :] = np.array( WAve1DF['Tmin_C'], dtype=np.float64 )
    DAve1DF = pd.read_pickle( WGI.OW_DRY_AVE_PROJ1 )
    PROJ_DRY_TMAX_AVE[0, :] = np.array( DAve1DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_AVE[0, :] = np.array( DAve1DF['Tmin_C'], dtype=np.float64 )
    WStd1DF = pd.read_pickle( WGI.OW_WET_STD_PROJ1 )
    PROJ_WET_TMAX_STD[0, :] = np.array( WStd1DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_STD[0, :] = np.array( WStd1DF['Tmin_C'], dtype=np.float64 )
    DStd1DF = pd.read_pickle( WGI.OW_DRY_STD_PROJ1 )
    PROJ_DRY_TMAX_STD[0, :] = np.array( DStd1DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_STD[0, :] = np.array( DStd1DF['Tmin_C'], dtype=np.float64 )
    # climate projection period 2
    WAve2DF = pd.read_pickle( WGI.OW_WET_AVE_PROJ2 )
    PROJ_WET_TMAX_AVE[1, :] = np.array( WAve2DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_AVE[1, :] = np.array( WAve2DF['Tmin_C'], dtype=np.float64 )
    DAve2DF = pd.read_pickle( WGI.OW_DRY_AVE_PROJ2 )
    PROJ_DRY_TMAX_AVE[1, :] = np.array( DAve2DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_AVE[1, :] = np.array( DAve2DF['Tmin_C'], dtype=np.float64 )
    WStd2DF = pd.read_pickle( WGI.OW_WET_STD_PROJ2 )
    PROJ_WET_TMAX_STD[1, :] = np.array( WStd2DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_STD[1, :] = np.array( WStd2DF['Tmin_C'], dtype=np.float64 )
    DStd2DF = pd.read_pickle( WGI.OW_DRY_STD_PROJ2 )
    PROJ_DRY_TMAX_STD[1, :] = np.array( DStd2DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_STD[1, :] = np.array( DStd2DF['Tmin_C'], dtype=np.float64 )
    # climate projection period 3
    WAve3DF = pd.read_pickle( WGI.OW_WET_AVE_PROJ3 )
    PROJ_WET_TMAX_AVE[2, :] = np.array( WAve3DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_AVE[2, :] = np.array( WAve3DF['Tmin_C'], dtype=np.float64 )
    DAve3DF = pd.read_pickle( WGI.OW_DRY_AVE_PROJ3 )
    PROJ_DRY_TMAX_AVE[2, :] = np.array( DAve3DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_AVE[2, :] = np.array( DAve3DF['Tmin_C'], dtype=np.float64 )
    WStd3DF = pd.read_pickle( WGI.OW_WET_STD_PROJ3 )
    PROJ_WET_TMAX_STD[2, :] = np.array( WStd3DF['Tmax_C'], dtype=np.float64 )
    PROJ_WET_TMIN_STD[2, :] = np.array( WStd3DF['Tmin_C'], dtype=np.float64 )
    DStd3DF = pd.read_pickle( WGI.OW_DRY_STD_PROJ3 )
    PROJ_DRY_TMAX_STD[2, :] = np.array( DStd3DF['Tmax_C'], dtype=np.float64 )
    PROJ_DRY_TMIN_STD[2, :] = np.array( DStd3DF['Tmin_C'], dtype=np.float64 )
    # next do the A and B
    A_PROJ[0, :, :] = np.array( WGI.A_PROJ1_LIST, dtype=np.float64 )
    B_PROJ[0, :, :] = np.array( WGI.B_PROJ1_LIST, dtype=np.float64 )
    A_PROJ[1, :, :] = np.array( WGI.A_PROJ2_LIST, dtype=np.float64 )
    B_PROJ[1, :, :] = np.array( WGI.B_PROJ2_LIST, dtype=np.float64 )
    A_PROJ[2, :, :] = np.array( WGI.A_PROJ3_LIST, dtype=np.float64 )
    B_PROJ[2, :, :] = np.array( WGI.B_PROJ3_LIST, dtype=np.float64 )
    # end of function
    return

def setupDistsSamples(seed_std_norm=None):
    """Setup the distributions and samplers for the white noise term.

    KWargs:
        seed_std_norm (int): standard normal sampler seed

    """
    # imports
    import WG_StdNormal as WGSN
    # globals
    global EPS_STD_NORMAL, EPS_NORM_SAMP
    # start of function
    EPS_STD_NORMAL.append( WGSN.StdNormal() )
    EPS_NORM_SAMP.append( WGSN.ErrorTSampler(seed=seed_std_norm) )
    EPS_STD_NORMAL.append( WGSN.StdNormal() )
    EPS_NORM_SAMP.append( WGSN.ErrorTSampler(seed=seed_std_norm) )
    # end of for
    # end of function
    return

def updateTracker():
    """Update the epsilon value tracker array"""
    # globals
    global EPSI_2, EPS_STD_NORMAL, EPS_NORM_SAMP
    # start of function
    EPSI_2[0, 0] = EPS_STD_NORMAL[0].ranval1( EPS_NORM_SAMP[0].ranstate )
    EPSI_2[0, 1] = EPS_STD_NORMAL[1].ranval1( EPS_NORM_SAMP[1].ranstate )
    # now make some checks
    EPSI_2 = np.where( np.isnan( EPSI_2 ), 0.25, EPSI_2 )
    EPSI_2 = np.where( np.isinf( EPSI_2 ), 0.25, EPSI_2 )
    # end of function
    return

def calculateUpdate( curIndex, DayOYear, h0state, h0pindex, h1state, 
                     h1ptype, h1pindex ):
    """Calculate the current day and update
    
    Args:
        curIndex (int): current date index
        DayOYear (int): day of the year
        h0state (string): wet or dry state for data path
        h0pindex(int): index for data period array
        h1state (str): wet or dry state for projecton path
        h1ptype (str): type of projection period
        h1pindex (int): index for projection period
    
    """
    # imports
    import WG_HighRealResults as WGHRR
    # globals
    global DATA_WET_TMAX_AVE, DATA_WET_TMAX_STD, DATA_WET_TMIN_AVE
    global DATA_WET_TMIN_STD, DATA_DRY_TMAX_AVE, DATA_DRY_TMAX_STD
    global DATA_DRY_TMIN_AVE, DATA_DRY_TMIN_STD
    global PROJ_WET_TMAX_STD, PROJ_WET_TMIN_AVE, PROJ_WET_TMIN_STD
    global PROJ_DRY_TMAX_AVE, PROJ_DRY_TMAX_STD, PROJ_DRY_TMIN_AVE
    global PROJ_DRY_TMIN_STD, CHI0M0, CHI0M1
    # start of function
    np.seterr(all='raise')
    if h0state == WGI.WET_STATE:
        try:
            cMaxT0 = ( (CHI0M0[0,0] * DATA_WET_TMAX_STD[h0pindex, (DayOYear - 1)]) + 
                         DATA_WET_TMAX_AVE[h0pindex, (DayOYear - 1)] )
        except:
            cMaxT0 = DATA_WET_TMAX_AVE[h0pindex, (DayOYear - 1)]
        try:
            cMinT0 = ( (CHI0M0[0,1] * DATA_WET_TMIN_STD[h0pindex, (DayOYear - 1)]) + 
                          DATA_WET_TMIN_AVE[h0pindex, (DayOYear - 1)] )
        except:
            cMinT0 = DATA_WET_TMIN_AVE[h0pindex, (DayOYear - 1)]
    else:
        try:
            cMaxT0 = ( (CHI0M0[0,0] * DATA_DRY_TMAX_STD[h0pindex, (DayOYear - 1)]) + 
                      DATA_DRY_TMAX_AVE[h0pindex, (DayOYear - 1)] )
        except:
            cMaxT0 = DATA_DRY_TMAX_AVE[h0pindex, (DayOYear - 1)]
        try:
            cMinT0 = ( (CHI0M0[0,1] * DATA_DRY_TMIN_STD[h0pindex, (DayOYear - 1)]) + 
                        DATA_DRY_TMIN_AVE[h0pindex, (DayOYear - 1)] )
        except:
            cMinT0 = DATA_DRY_TMIN_AVE[h0pindex, (DayOYear - 1)]
    # next do the proj side
    if h1state == WGI.WET_STATE:
        if h1ptype == WGI.DATA_KEYW:
            try:
                cMaxT1 = ( (CHI0M1[0,0] * DATA_WET_TMAX_STD[h1pindex, (DayOYear - 1)]) + 
                          DATA_WET_TMAX_AVE[h0pindex, (DayOYear - 1)] )
            except:
                cMaxT1 = DATA_WET_TMAX_AVE[h0pindex, (DayOYear - 1)]
            try:
                cMinT1 = ( (CHI0M1[0,1] * DATA_WET_TMIN_STD[h1pindex, (DayOYear - 1)]) + 
                            DATA_WET_TMIN_AVE[h0pindex, (DayOYear - 1)] )
            except:
                cMinT1 = DATA_WET_TMIN_AVE[h0pindex, (DayOYear - 1)]
        else:
            try:
                cMaxT1 = ( (CHI0M1[0,0] * PROJ_WET_TMAX_STD[h1pindex, (DayOYear - 1)]) + 
                            PROJ_WET_TMAX_AVE[h1pindex, (DayOYear - 1)] )
            except:
                cMaxT1 = PROJ_WET_TMAX_AVE[h1pindex, (DayOYear - 1)]
            try:
                cMinT1 = ( (CHI0M1[0,1] * PROJ_WET_TMIN_STD[h1pindex, (DayOYear - 1)]) + 
                            PROJ_WET_TMIN_AVE[h1pindex, (DayOYear - 1)] )
            except:
                cMinT1 = PROJ_WET_TMIN_AVE[h1pindex, (DayOYear - 1)]
    else:
        if h1ptype == WGI.DATA_KEYW:
            try:
                cMaxT1 = ( (CHI0M1[0,0] * DATA_DRY_TMAX_STD[h1pindex, (DayOYear - 1)]) + 
                            DATA_DRY_TMAX_AVE[h0pindex, (DayOYear - 1)] )
            except:
                cMaxT1 = DATA_DRY_TMAX_AVE[h0pindex, (DayOYear - 1)]
            try:
                cMinT1 = ( (CHI0M1[0,1] * DATA_DRY_TMIN_STD[h1pindex, (DayOYear - 1)]) + 
                            DATA_DRY_TMIN_AVE[h0pindex, (DayOYear - 1)] )
            except:
                cMinT1 = DATA_DRY_TMIN_AVE[h0pindex, (DayOYear - 1)]
        else:
            try:
                cMaxT1 = ( (CHI0M1[0,0] * PROJ_DRY_TMAX_STD[h1pindex, (DayOYear - 1)]) + 
                            PROJ_DRY_TMAX_AVE[h1pindex, (DayOYear - 1)] )
            except:
                cMaxT1 = PROJ_DRY_TMAX_AVE[h1pindex, (DayOYear - 1)]
            try:
                cMinT1 = ( (CHI0M1[0,1] * PROJ_DRY_TMIN_STD[h1pindex, (DayOYear - 1)]) + 
                            PROJ_DRY_TMIN_AVE[h1pindex, (DayOYear - 1)] )
            except:
                cMinT1 = PROJ_DRY_TMIN_AVE[h1pindex, (DayOYear - 1)]
    # toggle back
    np.seterr(all='warn')
    acMaxT0 = np.array( cMaxT0, dtype=np.float64 )
    acMaxT0 = np.where( np.isnan( acMaxT0 ), 
                        DATA_DRY_TMAX_AVE[0, (DayOYear - 1)], acMaxT0 )
    acMaxT0 = np.where( np.isinf( acMaxT0 ), 
                        DATA_DRY_TMAX_AVE[0, (DayOYear - 1)], acMaxT0 )
    acMinT0 = np.array( cMinT0, dtype=np.float64 )
    acMinT0 = np.where( np.isnan( acMinT0 ), 
                        DATA_DRY_TMIN_AVE[0, (DayOYear - 1)], acMinT0 )
    acMinT0 = np.where( np.isinf( acMinT0 ), 
                        DATA_DRY_TMIN_AVE[0, (DayOYear - 1)], acMinT0 )
    acMaxT1 = np.array( cMaxT1, dtype=np.float64 )
    acMaxT1 = np.where( np.isnan( acMaxT1 ), 
                        DATA_DRY_TMAX_AVE[0, (DayOYear - 1)], acMaxT1 )
    acMaxT1 = np.where( np.isinf( acMaxT1 ), 
                        DATA_DRY_TMAX_AVE[0, (DayOYear - 1)], acMaxT1 )
    acMinT1 = np.array( cMinT1, dtype=np.float64 )
    acMinT1 = np.where( np.isnan( acMinT1 ), 
                        DATA_DRY_TMIN_AVE[0, (DayOYear - 1)], acMinT1 )
    acMinT1 = np.where( np.isinf( acMinT1 ), 
                        DATA_DRY_TMIN_AVE[0, (DayOYear - 1)], acMinT1 )
    # now are ready to update
    WGHRR.assignTempData( curIndex, float(acMaxT0), float(acMinT0) )
    WGHRR.assignTempCProj( curIndex, float(acMaxT1), float(acMinT1) )
    # end of function
    return

def rollOverChis():
    """Convenience function to roll over the Chi squared values
    """
    # local imports
    from copy import deepcopy
    # globals
    global CHI0M0, CHIL1M0, CHI0M1, CHIL1M1, NUM_OTHER
    # start of function
    for iI in range(NUM_OTHER):
        CHIL1M0[0, iI] = deepcopy( CHI0M0[0, iI] )
        CHIL1M1[0, iI] = deepcopy( CHI0M1[0, iI] )
    # end for
    # end of function
    return

def calcCHI0( h0pindex, h1ptype, h1pindex ):
    """Calculate the current Chi no lag
    
    Args:
        h0pindex(int): index for data period array
        h1ptype (str): type of projection period
        h1pindex (int): index for projection period
    """
    # globals
    global CHI0M0, CHIL1M0, CHI0M1, CHIL1M1, EPSI_2, A_DATA, B_DATA
    global SIGMA_THRESH, A_PROJ, B_PROJ
    # calculations
    # first set our A and B
    A_0 = A_DATA[h0pindex, :, :].copy()
    B_0 = B_DATA[h0pindex, :, :].copy()
    if h1ptype == WGI.DATA_KEYW:
        A_1 = A_DATA[h1pindex, :, :].copy()
        B_1 = B_DATA[h1pindex, :, :].copy()
    else:
        A_1 = A_PROJ[h1pindex, :, :].copy()
        B_1 = B_PROJ[h1pindex, :, :].copy()
    # 
    np.seterr(all='raise')
    try:
        CHI0M0[:,:] = (np.matmul(CHIL1M0, A_0) + np.matmul( EPSI_2, B_0 ))[:,:]
    except:
        CHI0M0[:,:] = 1.0
    try:
        CHI0M1[:,:] = (np.matmul(CHIL1M1, A_1) + np.matmul( EPSI_2, B_1 ))[:,:]
    except:
        CHI0M1[:,:] = 1.0
    # do some checks
    np.seterr(all='warn')
    # first check to make sure that we actually got the calculation done
    CHI0M0 = np.where( np.isnan( CHI0M0 ), 1.0, CHI0M0 )
    CHI0M0 = np.where( np.isinf( CHI0M0 ), 1.0, CHI0M0 )
    CHI0M1 = np.where( np.isnan( CHI0M1 ), 1.0, CHI0M1 )
    CHI0M1 = np.where( np.isinf( CHI0M1 ), 1.0, CHI0M1 )
    # next we need to provide a sigma threshold
    CHI0M0 = np.where( CHI0M0 > SIGMA_THRESH, SIGMA_THRESH, CHI0M0 )
    CHI0M0 = np.where( CHI0M0 < (-1.0*SIGMA_THRESH), (-1.0*SIGMA_THRESH), 
                       CHI0M0 )
    CHI0M1 = np.where( CHI0M1 > SIGMA_THRESH, SIGMA_THRESH, CHI0M0 )
    CHI0M1 = np.where( CHI0M1 < (-1.0*SIGMA_THRESH), (-1.0*SIGMA_THRESH), 
                       CHI0M1 )
    # end of function
    return

def cleanAllEnd():
    """Convenience method to clean or delete all trackers at the end """
    global A_DATA, B_DATA, A_PROJ, B_PROJ, M0, M1, DATA_WET_TMAX_AVE
    global DATA_WET_TMAX_STD, DATA_WET_TMIN_AVE, DATA_WET_TMIN_STD
    global DATA_DRY_TMAX_AVE, DATA_DRY_TMAX_STD, DATA_DRY_TMIN_AVE
    global DATA_DRY_TMIN_STD, PROJ_WET_TMAX_AVE, PROJ_WET_TMAX_STD
    global PROJ_WET_TMIN_AVE, PROJ_WET_TMIN_STD, PROJ_DRY_TMAX_AVE
    global PROJ_DRY_TMAX_STD, PROJ_DRY_TMIN_AVE, PROJ_DRY_TMIN_STD
    global EPS_STD_NORMAL, EPS_NORM_SAMP, EPSI_2, CHI0M0
    global CHIL1M0, CHI0M1, CHIL1M1
    # set to none
    A_DATA = None
    B_DATA = None
    A_PROJ = None
    B_PROJ = None
    M0 = None
    M1 = None
    DATA_WET_TMAX_AVE = None
    DATA_WET_TMAX_STD = None
    DATA_WET_TMIN_AVE = None
    DATA_WET_TMIN_STD = None
    DATA_DRY_TMAX_AVE = None
    DATA_DRY_TMAX_STD = None
    DATA_DRY_TMIN_AVE = None
    DATA_DRY_TMIN_STD = None
    PROJ_WET_TMAX_AVE = None
    PROJ_WET_TMAX_STD = None
    PROJ_WET_TMIN_AVE = None
    PROJ_WET_TMIN_STD = None
    PROJ_DRY_TMAX_AVE = None
    PROJ_DRY_TMAX_STD = None
    PROJ_DRY_TMIN_AVE = None
    PROJ_DRY_TMIN_STD = None
    EPS_STD_NORMAL = None
    EPS_NORM_SAMP = None
    EPSI_2 = None
    CHI0M0 = None
    CHIL1M0 = None
    CHI0M1 = None
    CHIL1M1 = None
    # then delete
    #del A_DATA
    #del B_DATA
    #del A_PROJ
    #del B_PROJ
    #del M0
    #del M1
    #del DATA_WET_TMAX_AVE
    #del DATA_WET_TMAX_STD
    #del DATA_WET_TMIN_AVE
    #del DATA_WET_TMIN_STD
    #del DATA_DRY_TMAX_AVE
    #del DATA_DRY_TMAX_STD
    #del DATA_DRY_TMIN_AVE
    #del DATA_DRY_TMIN_STD
    #del PROJ_WET_TMAX_AVE
    #del PROJ_WET_TMAX_STD
    #del PROJ_WET_TMIN_AVE
    #del PROJ_WET_TMIN_STD
    #del PROJ_DRY_TMAX_AVE
    #del PROJ_DRY_TMAX_STD
    #del PROJ_DRY_TMIN_AVE
    #del PROJ_DRY_TMIN_STD
    #del EPS_STD_NORMAL
    #del EPS_NORM_SAMP
    #del EPSI_2
    #del CHI0M0
    #del CHIL1M0
    #del CHI0M1
    #del CHIL1M1 
    # end
    return

def setAllBegin():
    """Convenience method to reset all at the beginning of a realization """
    global NUM_OTHER, NUM_DAYS_YR, NUM_DATA_PER, NUM_PROJ_PER, SIGMA_THRESH
    global A_DATA, B_DATA, A_PROJ, B_PROJ, M0, M1, DATA_WET_TMAX_AVE
    global DATA_WET_TMAX_STD, DATA_WET_TMIN_AVE, DATA_WET_TMIN_STD
    global DATA_DRY_TMAX_AVE, DATA_DRY_TMAX_STD, DATA_DRY_TMIN_AVE
    global DATA_DRY_TMIN_STD, PROJ_WET_TMAX_AVE, PROJ_WET_TMAX_STD
    global PROJ_WET_TMIN_AVE, PROJ_WET_TMIN_STD, PROJ_DRY_TMAX_AVE
    global PROJ_DRY_TMAX_STD, PROJ_DRY_TMIN_AVE, PROJ_DRY_TMIN_STD
    global EPS_STD_NORMAL, EPS_NORM_SAMP, EPSI_2, CHI0M0
    global CHIL1M0, CHI0M1, CHIL1M1
    # now do the setting
    A_DATA = np.ones( (NUM_DATA_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    B_DATA = np.ones( (NUM_DATA_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    A_PROJ = np.ones( (NUM_PROJ_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    B_PROJ = np.ones( (NUM_PROJ_PER, NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    M0 = np.ones( (NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    M1 = np.ones( (NUM_OTHER, NUM_OTHER), dtype=np.float64 )
    DATA_WET_TMAX_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_WET_TMAX_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_WET_TMIN_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_WET_TMIN_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_DRY_TMAX_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_DRY_TMAX_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_DRY_TMIN_AVE = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    DATA_DRY_TMIN_STD = np.ones( (NUM_DATA_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_WET_TMAX_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_WET_TMAX_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_WET_TMIN_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_WET_TMIN_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_DRY_TMAX_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_DRY_TMAX_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_DRY_TMIN_AVE = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    PROJ_DRY_TMIN_STD = np.ones( (NUM_PROJ_PER, NUM_DAYS_YR), dtype=np.float64 )
    EPS_STD_NORMAL = list()
    EPS_NORM_SAMP = list()
    EPSI_2 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
    CHI0M0 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
    CHIL1M0 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
    CHI0M1 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
    CHIL1M1 = np.ones( (1, NUM_OTHER), dtype=np.float64 )
    # end
    return

# EOF