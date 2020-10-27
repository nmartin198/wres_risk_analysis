# -*- coding: utf-8 -*-
"""
.. module:: WG_Worker_Main
   :platform: Windows, Linux
   :synopsis: The main entry point for the worker code that is excecuted by each worker.

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumi.org>

This module is not used in the multiprocessing-capable version. All of this 
code is superseded by WGmp.py.

This module holds the original "main" program functionality and entry point for 
an individual weather generator (WG) realization or simulation.

Program flow chart functionality

I. Initialization and prep of all variables and structures
    - WG_Inputs provides for parameter definitions and domain specification
    - Functions in this module for startup and shutdown

II. Loop through all realizations: for each realization make a time series of
weather parameters.
    1. Loop through all days in the simulation period and determine a daily
        weather parameter
        - precipitation
        - maximum air temperature
        - minimum air temperature
        a) within day logic provided by the flow chart that is Figure 2b of
            Wilks and Wilby (1999)

III. Probabilistic processing of full collection of time series includes 
statistical processing for comparison with the inputs.
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


def detH0Period(curDate):
    """Determine the null pathway current data period index.
    The null pathway is always based on data so only need to return the 
    data index.
    
    Args:
        curDate (dt.datetime): current date

    """
    import WG_Inputs as WGI
    # start
    NumDataPeriods = len( WGI.DATA_PERIODS )
    if NumDataPeriods <= 0:
        # should never be triggered
        return -1
    if NumDataPeriods == 1:
        return 0
    # now check which one are in
    if curDate < WGI.DATA_PERIODS[0][0]:
        return 0
    if curDate > WGI.DATA_PERIODS[NumDataPeriods-1][1]:
        return NumDataPeriods-1
    # now find which period it is in
    cPeriod = 0
    for tPer in WGI.DATA_PERIODS:
        if (curDate >= tPer[0]) and (curDate <= tPer[1]):
            return cPeriod
        cPeriod += 1
    # end of for
    return -1

def detH1Period(curDate):
    """
    Determine the climate pathway current period index.
    This could be either a data period or a climate projection period depending on 
    the various intervals. Consequently return a tuple with a keyword at index 
    0 and the period index at index 1.
    
    Args:
        curDate (dt.datetime): current simulation date

    """
    import WG_Inputs as WGI
    # start
    NumDataPeriods = len( WGI.DATA_PERIODS )
    if NumDataPeriods <= 0:
        return (WGI.DATA_KEYW, -1)
    # now go through and see if are in a data period
    cPeriod = 0
    for tPer in WGI.DATA_PERIODS:
        if (curDate >= tPer[0]) and (curDate <= tPer[1]):
            return (WGI.DATA_KEYW, cPeriod)
        cPeriod += 1
    # end of for
    # next look through the PROJ_PERIODS
    NumProjPeriods = len( WGI.PROJ_PERIODS )
    if NumProjPeriods <= 0:
        # should never be triggered
        return (WGI.PROJ_KEYW, -1)
    if NumProjPeriods == 1:
        return (WGI.PROJ_KEYW, 0)
    if curDate < WGI.PROJ_PERIODS[0][0]:
        return (WGI.PROJ_KEYW, 0)
    if curDate > WGI.PROJ_PERIODS[NumProjPeriods-1][1]:
        return (WGI.PROJ_KEYW, NumProjPeriods-1)
    # now find which period it is in
    cPeriod = 0
    for tPer in WGI.PROJ_PERIODS:
        if (curDate >= tPer[0]) and (curDate <= tPer[1]):
            return (WGI.PROJ_KEYW, cPeriod)
        cPeriod += 1
    # end of for
    return (WGI.PROJ_KEYW, -1)


def WG_Worker_Main( RealNum, SNSeed, PDSeed, WSLSeed, DSLSeed ):
    """ Main functionality to run a single realization

    Args:
        RealNum (int): the current realization number
        SNSeed (int): base seed for the standard normal sampler
        PDSeed (int): the precipitation depth sampler seed
        WSLSeed (int): wet state spell length sampling seed
        DSLSeed (int): dry state spell length sampling seed

    Returns:
        int. The return code::
            0 -- Success!
            1 -- Failure, generic

    """
    # imports
    import pandas as pd
    import WG_Inputs as WGI
    import WG_Dists_Samples as WGDS
    import WG_PrecipDepth as WGPD
    import WG_OtherWeather as WGOW
    import WG_HighRealResults as WGHRR
    # 
    # set our local seeds
    pdSampSeed = PDSeed + RealNum
    sndSampSeed = SNSeed + RealNum
    wetSSampSeed = WSLSeed + RealNum
    drySSampSeed = DSLSeed + RealNum
    # get our start and end
    start_date = WGI.START_DATE
    end_date = WGI.END_DATE
    # calculate our total days and set up our time index for output
    timeD = end_date - start_date
    TOTAL_DAYS = int( timeD.days + 1 )
    DT_INDEX = pd.date_range( start=start_date, end=end_date, freq='D' )
    # with the time index set, then we have everything that we need to
    # set-up our structures
    WGOW.constructDataPeriodArrays()
    WGOW.constructCProjPeriodArrays()
    # set-up the sampling and other things
    WGDS.setDistributions( pdSampSeed, wetSSampSeed, drySSampSeed )
    WGDS.setTrackers()
    WGOW.setupDistsSamples(seed_std_norm=sndSampSeed)
    WGOW.updateTracker()
    # get our starting state sampler
    StarterSamp = WGPD.PrecipSampler(pd_sample_seed=(pdSampSeed - 1))
    # get our time index in a list for an iterator
    TimesList = DT_INDEX.to_pydatetime().tolist()
    # no loop at the realization level
    # determine what kind of period and which one is for starting time
    h0pindex = detH0Period( start_date )
    h1ptype, h1pindex = detH1Period( end_date )
    curMonth = start_date.month
    # now get the starting state
    TestVal = StarterSamp.getSingleVal()
    if TestVal > 0.5:
        h0State = WGI.WET_STATE
        h1State = WGI.WET_STATE
        h0remdur = WGDS.ST_DATA_WETSPELL[h0pindex][curMonth]
        if h1ptype == WGI.DATA_KEYW:
            h1remdur = WGDS.ST_DATA_WETSPELL[h1pindex][curMonth]
        else:
            h1remdur = WGDS.ST_PROJ_WETSPELL[h1pindex][curMonth]
    else:
        h0State = WGI.DRY_STATE
        h1State = WGI.DRY_STATE
        h0remdur = WGDS.ST_DATA_DRYSPELL[h0pindex][curMonth]
        if h1ptype == WGI.DATA_KEYW:
            h1remdur = WGDS.ST_DATA_DRYSPELL[h1pindex][curMonth]
        else:
            h1remdur = WGDS.ST_PROJ_DRYSPELL[h1pindex][curMonth]
    # now create/set our realization tracking array
    WGHRR.createSimStructures(TOTAL_DAYS)
    # inner loop over times
    for jJ in range(TOTAL_DAYS):
        cTime = TimesList[jJ]
        # sample all every time step
        WGDS.sampleAll()
        WGOW.updateTracker()
        # get the current month
        curMonth = cTime.month
        # get the current day of the year
        curDayoYr = cTime.timetuple().tm_yday
        # determine our period for sampling
        h0pindex = detH0Period( cTime )
        h1ptype, h1pindex = detH1Period( cTime )
        # now that everything is sampled check our state and if wet
        # then we get a precip depth
        if h0State == WGI.WET_STATE:
            if h0remdur <= 0:
                # then need to change state to dry
                h0State = WGI.DRY_STATE
                h0remdur = WGDS.ST_DATA_DRYSPELL[h0pindex][curMonth]
                WGHRR.assignDryDepData( jJ )
            else:
                # then need to assign the sampled precipitation depth
                # for each grid 
                #pVals = WGHRR.createDepArrayData( curMonth, h0pindex, 
                #                                    WGDS.ST_DATA_PDEPTH )
                pVals = WGHRR.createDepArrayCProj( curMonth, h1ptype, 
                                                    h1pindex, 
                                                    WGDS.ST_DATA_PDEPTH, 
                                                    WGDS.ST_H0_PDEPTH )
                WGHRR.assignWetDepData( jJ, pVals )
        else:
            # then the H0 branch is currently dry
            # check if time to toggle states
            if h0remdur <= 0:
                h0State = WGI.WET_STATE
                h0remdur = WGDS.ST_DATA_WETSPELL[h0pindex][curMonth]
                #pVals = WGHRR.createDepArrayData( curMonth, h0pindex, 
                #                                    WGDS.ST_DATA_PDEPTH )
                pVals = WGHRR.createDepArrayCProj( curMonth, h1ptype, 
                                                    h1pindex, 
                                                    WGDS.ST_DATA_PDEPTH, 
                                                    WGDS.ST_H0_PDEPTH )
                WGHRR.assignWetDepData( jJ, pVals )
            else:
                WGHRR.assignDryDepData( jJ )
        # next look at the H1 or climate change projection branch
        if h1State == WGI.WET_STATE:
            if h1remdur <= 0:
                # then need to change state to dry
                h1State = WGI.DRY_STATE
                if h1ptype == WGI.DATA_KEYW:
                    h1remdur = WGDS.ST_DATA_DRYSPELL[h1pindex][curMonth]
                else:
                    h1remdur = WGDS.ST_PROJ_DRYSPELL[h1pindex][curMonth]
                # now assign the dry depth
                WGHRR.assignDryDepCProj( jJ )
            else:
                # assign the sampled precipitation depth for each grid
                pVals = WGHRR.createDepArrayCProj( curMonth, h1ptype, 
                                                    h1pindex, 
                                                    WGDS.ST_DATA_PDEPTH, 
                                                    WGDS.ST_PROJ_PDEPTH )
                WGHRR.assignWetDepCProj( jJ, pVals )
        else:
            # then the H1 branch is currently dry
            # check if time to toggle states
            if h1remdur <= 0:
                h1State = WGI.WET_STATE
                if h1ptype == WGI.DATA_KEYW:
                    h1remdur = WGDS.ST_DATA_WETSPELL[h1pindex][curMonth]
                else:
                    h1remdur = WGDS.ST_PROJ_WETSPELL[h1pindex][curMonth]
                # now assign sampled precipitation
                pVals = WGHRR.createDepArrayCProj( curMonth, h1ptype, 
                                                    h1pindex, 
                                                    WGDS.ST_DATA_PDEPTH, 
                                                    WGDS.ST_PROJ_PDEPTH )
                WGHRR.assignWetDepCProj( jJ, pVals )
            else:
                # assign dry depth
                WGHRR.assignDryDepCProj( jJ )
        # do the other parameters
        WGOW.calcCHI0( h0pindex, h1ptype, h1pindex )
        # now update our temp values
        WGOW.calculateUpdate( jJ, curDayoYr, h0State, h0pindex, 
                                h1State, h1ptype, h1pindex )
        # decrement counters before moving on
        h0remdur -= 1
        h1remdur -= 1
        # copy our array
        WGOW.rollOverChis()
    # end of time for loop
    # now output the realization
    WGHRR.outputRealResults( RealNum, DT_INDEX)
    WGHRR.outputWSResults( RealNum, DT_INDEX, TOTAL_DAYS )
    # end of realizations loop
    # end
    return 0

#EOF