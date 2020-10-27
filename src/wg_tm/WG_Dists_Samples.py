# -*- coding: utf-8 -*-
"""
.. module:: WG_Dists_Samples
   :platform: Windows, Linux
   :synopsis: Contains collections of instantiated distributions and samplers.

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Contains instantiated distributions and samplers

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

# project imports
import WG_PrecipDepth as WGPD
import WG_SpellLength as WGSL
import WG_Inputs as WGI

# Distribution dictionaries
# spell distribution dictionaries
DDRY_SPELL_DISTS = dict()
PDRY_SPELL_DISTS = dict()
DWET_SPELL_DISTS = dict()
PWET_SPELL_DISTS = dict()
# precip depth distribution dictionaries
DP_DEPTH_DISTS = dict()
"""Dictionary of precipitation depth distributions for
data periods, applies to both pathways.
"""
PP_DEPTH_DISTS = dict()
"""Dictionary of precipitation depth distributions for projection
periods in the H1 pathway."""
H0_DEPTH_DISTS = dict()
"""Dictionary of precipitation depth distributions for projection
periods in the H0 pathway."""

# Sampling dictionaries
# spell samplers
DDRY_SPELL_SAMP = dict()
PDRY_SPELL_SAMP = dict()
DWET_SPELL_SAMP = dict()
PWET_SPELL_SAMP = dict()
# precip depth samplers
DP_DEPTH_SAMP = dict()
"""Dictionary of precipitation depth sampler for data periods,
applies to both pathways.
"""
PP_DEPTH_SAMP = dict()
"""Dictionary of precipitation depth samplers for projection
periods in the H1 pathway.
"""
H0_DEPTH_SAMP = dict()
"""Dictionary of  precipitation depth samplers for projection
periods in the H0 pathway.
"""

# sample trackers
ST_DATA_DRYSPELL = dict()
ST_DATA_WETSPELL = dict()
ST_DATA_PDEPTH = dict()
"""Dictionary of tracked sample values for data periods,
applies to both pathways.
"""
ST_PROJ_DRYSPELL = dict()
ST_PROJ_WETSPELL = dict()
ST_PROJ_PDEPTH = dict()
"""Dictionary of tracked sample values for projection periods,
applies to H1 pathway."""
ST_H0_PDEPTH = dict()
"""Dictionary of tracked sample values for projection periods,
applies to H0 pathway."""

#-----------------------------------------------------------------------
# convenience set-up functions
def setTrackers():
    """Set-up our sample tracking dictionaries
    """
    # globals
    global DDRY_SPELL_DISTS, PDRY_SPELL_DISTS, DWET_SPELL_DISTS
    global PWET_SPELL_DISTS, DP_DEPTH_DISTS, PP_DEPTH_DISTS
    global DDRY_SPELL_SAMP, PDRY_SPELL_SAMP, DWET_SPELL_SAMP
    global PWET_SPELL_SAMP, DP_DEPTH_SAMP, PP_DEPTH_SAMP, ST_DATA_DRYSPELL
    global ST_DATA_WETSPELL, ST_DATA_PDEPTH, ST_PROJ_DRYSPELL
    global ST_PROJ_WETSPELL, ST_PROJ_PDEPTH
    global H0_DEPTH_DISTS, H0_DEPTH_SAMP, ST_H0_PDEPTH
    # start
    MonthInts = list( range(1, 13, 1) )
    for iI in range(WGI.NUM_DATA_PERIODS):
        DrySYrDict = {}
        WetSYrDict = {}
        for jJ in MonthInts:
            dSamp = DDRY_SPELL_SAMP[iI][jJ]
            DrySYrDict[jJ] = DDRY_SPELL_DISTS[iI][jJ].ranval1(dSamp.ranstate)
            wSamp = DWET_SPELL_SAMP[iI][jJ]
            WetSYrDict[jJ] = DWET_SPELL_DISTS[iI][jJ].ranval1(wSamp.ranstate)
        # end of month for
        ST_DATA_DRYSPELL[iI] = DrySYrDict
        ST_DATA_WETSPELL[iI] = WetSYrDict
    # end of data periods for
    # data precip depth
    for iI in range(WGI.NUM_DATA_PERIODS):
        PDepDict = {}
        for jJ in WGI.LOCA_KEYS:
            PDMonDict = {}
            for kK in MonthInts:
                pdSamp = DP_DEPTH_SAMP[iI][jJ][kK]
                PDMonDict[kK] = DP_DEPTH_DISTS[iI][jJ][kK].ranval1( 
                                                    pdSamp.getSingleVal() )
            # end of month for
            PDepDict[jJ] = PDMonDict
        # end of region for
        ST_DATA_PDEPTH[iI] = PDepDict
    # end of data periods for
    for iI in range(WGI.NUM_PROJ_PERIODS):
        DrySGDict = {}
        WetSGDict = {}
        for kK in MonthInts:
            dsamp = PDRY_SPELL_SAMP[iI][kK]
            wsamp = PWET_SPELL_SAMP[iI][kK]
            DrySGDict[kK] = PDRY_SPELL_DISTS[iI][kK].ranval1(dsamp.ranstate)
            WetSGDict[kK] = PWET_SPELL_DISTS[iI][kK].ranval1(wsamp.ranstate)
        # end of months for
        ST_PROJ_DRYSPELL[iI] = DrySGDict
        ST_PROJ_WETSPELL[iI] = WetSGDict
    # end of proj periods for
    # do the projected precip depth
    for iI in range(WGI.NUM_PROJ_PERIODS):
        PDepDict = {}
        H0DepDict = {}
        for jJ in WGI.LOCA_KEYS:
            PDMonDict = {}
            H0PDMonDict = {}
            for kK in MonthInts:
                pdSamp = PP_DEPTH_SAMP[iI][jJ][kK]
                PDMonDict[kK] = PP_DEPTH_DISTS[iI][jJ][kK].ranval1(
                                                      pdSamp.getSingleVal() )
                h0pdSamp = H0_DEPTH_SAMP[iI][jJ][kK]
                H0PDMonDict[kK] = H0_DEPTH_DISTS[iI][jJ][kK].ranval1(
                                                      h0pdSamp.getSingleVal() )
            # end of months for
            PDepDict[jJ] = PDMonDict
            H0DepDict[jJ] = H0PDMonDict
        # end of grid for
        ST_PROJ_PDEPTH[iI] = PDepDict
        ST_H0_PDEPTH[iI] = H0DepDict
    # end of projecton period for
    # end
    return

def setDistributions( pdSampSeed, wetSSampSeed, drySSampSeed ):
    """Go through and create the objects for all distributions.
    The parameters are specified in the input module. A parallel dictionary structure of
    distributions is created for the inputs.

    Args:
        pdSampSeed (int): precipitation depth sampling seed
        wetSSampSeed (int): wet state sampling seed
        drySSampSeed (int): dry state sampling seed

    """
    # imports
    from WG_Inputs import DATAP_TRUNC_OPTION, PROJP_TRUNC_OPTION, SCEN_WET_SPELL_SWITCH
    from WG_Inputs import H0_TRUNC_OPTION
    # globals
    global DDRY_SPELL_DISTS, DWET_SPELL_DISTS, DDRY_SPELL_SAMP, DWET_SPELL_SAMP
    global DP_DEPTH_DISTS, DP_DEPTH_SAMP, PDRY_SPELL_DISTS, PWET_SPELL_DISTS
    global PDRY_SPELL_SAMP, PWET_SPELL_SAMP, PP_DEPTH_DISTS, PP_DEPTH_SAMP
    global H0_DEPTH_DISTS, H0_DEPTH_SAMP
    # start
    MonthInts = list( range(1, 13, 1) )
    for iI in range(WGI.NUM_DATA_PERIODS):
        DrySYrDict = dict()
        WetSYrDict = dict()
        DrySmpDict = dict()
        WetSmpDict = dict()
        for jJ in MonthInts:
            drydist = WGSL.NegBinomial( WGI.DATA_DRY_SPELL[iI][jJ][0],
                                        WGI.DATA_DRY_SPELL[iI][jJ][1],
                                        "Dry spell, data period %d, Month %d" % \
                                        (iI, jJ) )
            DrySYrDict[jJ] = drydist
            wetdist = WGSL.NegBinomial( WGI.DATA_WET_SPELL[iI][jJ][0],
                                        WGI.DATA_WET_SPELL[iI][jJ][1],
                                        "Wet spell, data period %d, Month %d" % \
                                        (iI, jJ) )
            WetSYrDict[jJ] = wetdist
            drysamp = WGSL.DryStateSampler(dry_state_seed=drySSampSeed)
            DrySmpDict[jJ] = drysamp
            wetsamp = WGSL.WetStateSampler(wet_state_seed=wetSSampSeed)
            WetSmpDict[jJ] = wetsamp
        # end of for
        DDRY_SPELL_DISTS[iI] = DrySYrDict
        DWET_SPELL_DISTS[iI] = WetSYrDict
        DDRY_SPELL_SAMP[iI] = DrySmpDict
        DWET_SPELL_SAMP[iI] = WetSmpDict
    # end of data period for
    # next do the data period precipitation depth
    for iI in range(WGI.NUM_DATA_PERIODS):
        PDepDict = dict()
        PSmpDict = dict()
        for jJ in WGI.LOCA_KEYS:
            PDMonDict = dict()
            PSMonDict = dict()
            for kK in MonthInts:
                cRegionID = WGI.LOCA_GRID_MAP[jJ][kK]
                depdist = WGPD.MixedExp( WGI.DATA_PDEPTH[iI][cRegionID][kK][0],
                                         WGI.DATA_PDEPTH[iI][cRegionID][kK][1],
                                         WGI.DATA_PDEPTH[iI][cRegionID][kK][2],
                                         jJ, kK, DATAP_TRUNC_OPTION, 1, 
                                         "Precip depth, data period %d, " \
                                         "Grid %d, Region %d, Month %d" % \
                                         ( iI, jJ, cRegionID, kK ) )
                PDMonDict[kK] = depdist
                depsamp = WGPD.PrecipSampler(pd_sample_seed=pdSampSeed)
                PSMonDict[kK] = depsamp
            # end of month for
            PDepDict[jJ] = PDMonDict
            PSmpDict[jJ] = PSMonDict
        # end of region for
        DP_DEPTH_DISTS[iI] = PDepDict
        DP_DEPTH_SAMP[iI] = PSmpDict
    # end of data periods for
    # now do the projected spells and samplers
    for iI in range(WGI.NUM_PROJ_PERIODS):
        DrySGDict = dict()
        WetSGDict = dict()
        DrySmpGDict = dict()
        WetSmpGDict = dict()
        for kK in MonthInts:
            if ( SCEN_WET_SPELL_SWITCH <= 1):
                drydist = WGSL.NegBinomial( WGI.PROJ_DRY_SPELL[iI][kK][0],
                                            WGI.PROJ_DRY_SPELL[iI][kK][1],
                                            "Dry spell, cproj period %d, Month %d" % \
                                            (iI, kK) )
            else:
                drydist = WGSL.NegBinomial( WGI.DATA_DRY_SPELL[0][kK][0],
                                            WGI.DATA_DRY_SPELL[0][kK][1],
                                            "Dry spell, cproj period %d, Month %d" % \
                                            (iI, kK) )
            DrySGDict[kK] = drydist
            if ( SCEN_WET_SPELL_SWITCH <= 1):
                wetdist = WGSL.NegBinomial( WGI.PROJ_WET_SPELL[iI][kK][0],
                                            WGI.PROJ_WET_SPELL[iI][kK][1],
                                            "Wet spell, cproj period %d, Month %d" % \
                                            (iI, kK) )
            else:
                wetdist = WGSL.NegBinomial( WGI.DATA_WET_SPELL[0][kK][0],
                                            WGI.DATA_WET_SPELL[0][kK][1],
                                            "Wet spell, data period %d, Month %d" % \
                                            (iI, jJ) )
            WetSGDict[kK] = wetdist
            drysamp = WGSL.DryStateSampler(dry_state_seed=drySSampSeed)
            DrySmpGDict[kK] = drysamp
            wetsamp = WGSL.WetStateSampler(wet_state_seed=wetSSampSeed)
            WetSmpGDict[kK] = wetsamp
        # end of month for
        PDRY_SPELL_DISTS[iI] = DrySGDict
        PWET_SPELL_DISTS[iI] = WetSGDict
        PDRY_SPELL_SAMP[iI] = DrySmpGDict
        PWET_SPELL_SAMP[iI] = WetSmpGDict
    # end of projection periods
    for iI in range(WGI.NUM_PROJ_PERIODS):
        PDepDict = dict()
        PSmpDict = dict()
        H0PDepDict = dict()
        H0PSmpDict = dict()
        for jJ in WGI.LOCA_KEYS:
            PDMonDict = dict()
            PSMonDict = dict()
            H0PDMonDict = dict()
            H0PSMonDict = dict()
            for kK in MonthInts:
                cRegionID = WGI.LOCA_GRID_MAP[jJ][kK]
                # H1 pathway
                depdist = WGPD.MixedExp( WGI.PROJ_PDEPTH[iI][jJ][kK][0],
                                         WGI.PROJ_PDEPTH[iI][jJ][kK][1],
                                         WGI.PROJ_PDEPTH[iI][jJ][kK][2],
                                         jJ, kK, PROJP_TRUNC_OPTION, iI + 1, 
                                         "Precip depth, H1 cproj period %d, " \
                                         "Grid %d, Month %d" % \
                                         ( iI, jJ, kK ) )
                PDMonDict[kK] = depdist
                depsamp = WGPD.PrecipSampler(pd_sample_seed=pdSampSeed)
                PSMonDict[kK] = depsamp
                # now H0 pathway
                # number of periods index is hard-coded here to 0 on 
                # assumption of 1 data period. This will break if more than
                # one data period
                h0depdist = WGPD.MixedExp( WGI.DATA_PDEPTH[0][cRegionID][kK][0],
                                           WGI.DATA_PDEPTH[0][cRegionID][kK][1],
                                           WGI.DATA_PDEPTH[0][cRegionID][kK][2],
                                           jJ, kK, H0_TRUNC_OPTION, iI + 1, 
                                           "Precip depth, H0 cproj period %d, " \
                                           "Grid %d, Region %d, Month %d" % \
                                           ( iI, jJ, cRegionID, kK ) )
                H0PDMonDict[kK] = h0depdist
                h0depsamp = WGPD.PrecipSampler(pd_sample_seed=pdSampSeed)
                H0PSMonDict[kK] = h0depsamp
            # end of month for
            PDepDict[jJ] = PDMonDict
            PSmpDict[jJ] = PSMonDict
            H0PDepDict[jJ] = H0PDMonDict
            H0PSmpDict[jJ] = H0PSMonDict
        # end of grid for
        PP_DEPTH_DISTS[iI] = PDepDict
        PP_DEPTH_SAMP[iI] = PSmpDict
        H0_DEPTH_DISTS[iI] = H0PDepDict
        H0_DEPTH_SAMP[iI] = H0PSmpDict
    # end of projection periods for
    # end
    return

def sampleAll():
    """Sample all distributions for every time step of every realization
    """
    # global
    global DDRY_SPELL_DISTS, PDRY_SPELL_DISTS, DWET_SPELL_DISTS
    global PWET_SPELL_DISTS, DP_DEPTH_DISTS, PP_DEPTH_DISTS
    global DDRY_SPELL_SAMP, PDRY_SPELL_SAMP, DWET_SPELL_SAMP
    global PWET_SPELL_SAMP, DP_DEPTH_SAMP, PP_DEPTH_SAMP, ST_DATA_DRYSPELL
    global ST_DATA_WETSPELL, ST_DATA_PDEPTH, ST_PROJ_DRYSPELL
    global ST_PROJ_WETSPELL, ST_PROJ_PDEPTH
    global H0_DEPTH_DISTS, H0_DEPTH_SAMP, ST_H0_PDEPTH
    # start
    MonthInts = list( range(1, 13, 1) )
    for iI in range(WGI.NUM_DATA_PERIODS):
        for jJ in MonthInts:
            dSamp = DDRY_SPELL_SAMP[iI][jJ]
            wSamp = DWET_SPELL_SAMP[iI][jJ]
            ST_DATA_DRYSPELL[iI][jJ] = DDRY_SPELL_DISTS[iI][jJ].ranval1(dSamp.ranstate)
            ST_DATA_WETSPELL[iI][jJ] = DWET_SPELL_DISTS[iI][jJ].ranval1(wSamp.ranstate)
        # end of month for
    # end of data periods for
    # data precip depth
    for iI in range(WGI.NUM_DATA_PERIODS):
        for jJ in WGI.LOCA_KEYS:
            for kK in MonthInts:
                pdSamp = DP_DEPTH_SAMP[iI][jJ][kK]
                ST_DATA_PDEPTH[iI][jJ][kK] = DP_DEPTH_DISTS[iI][jJ][kK].ranval1(
                                                        pdSamp.getSingleVal() )
            # end of month for
        # end of region for
    # end of data periods for
    for iI in range(WGI.NUM_PROJ_PERIODS):
        for kK in MonthInts:
            dsamp = PDRY_SPELL_SAMP[iI][kK]
            wsamp = PWET_SPELL_SAMP[iI][kK]
            ST_PROJ_DRYSPELL[iI][kK] = PDRY_SPELL_DISTS[iI][kK].ranval1(dsamp.ranstate)
            ST_PROJ_WETSPELL[iI][kK] = PWET_SPELL_DISTS[iI][kK].ranval1(wsamp.ranstate)
        # end of months for
    # end of proj periods for
    # do the projected precip depth
    for iI in range(WGI.NUM_PROJ_PERIODS):
        for jJ in WGI.LOCA_KEYS:
            for kK in MonthInts:
                pdSamp = PP_DEPTH_SAMP[iI][jJ][kK]
                ST_PROJ_PDEPTH[iI][jJ][kK] = PP_DEPTH_DISTS[iI][jJ][kK].ranval1(
                                                        pdSamp.getSingleVal() )
                # do H0
                h0pdSamp = H0_DEPTH_SAMP[iI][jJ][kK]
                ST_H0_PDEPTH[iI][jJ][kK] = H0_DEPTH_DISTS[iI][jJ][kK].ranval1( 
                                                        h0pdSamp.getSingleVal() )
            # end of months for
        # end of grid for
    # end of projecton period for
    # end
    return

def cleanAllEnd():
    """Convenience method to clean/delete all samplers at end

    """
    global DDRY_SPELL_DISTS, DWET_SPELL_DISTS, DDRY_SPELL_SAMP, DWET_SPELL_SAMP
    global DP_DEPTH_DISTS, DP_DEPTH_SAMP, PDRY_SPELL_DISTS, PWET_SPELL_DISTS
    global PDRY_SPELL_SAMP, PWET_SPELL_SAMP, PP_DEPTH_DISTS, PP_DEPTH_SAMP
    global ST_DATA_WETSPELL, ST_DATA_PDEPTH, ST_PROJ_DRYSPELL
    global ST_PROJ_WETSPELL, ST_PROJ_PDEPTH, ST_DATA_DRYSPELL
    global H0_DEPTH_DISTS, H0_DEPTH_SAMP, ST_H0_PDEPTH
    # now set to None
    DDRY_SPELL_DISTS = None
    DWET_SPELL_DISTS = None
    DDRY_SPELL_SAMP = None
    DWET_SPELL_SAMP = None
    DP_DEPTH_DISTS = None
    DP_DEPTH_SAMP = None
    PDRY_SPELL_DISTS = None
    PWET_SPELL_DISTS = None
    PDRY_SPELL_SAMP = None
    PWET_SPELL_SAMP = None
    PP_DEPTH_DISTS = None
    PP_DEPTH_SAMP = None
    ST_DATA_WETSPELL = None
    ST_DATA_PDEPTH = None
    ST_PROJ_DRYSPELL = None
    ST_PROJ_WETSPELL = None
    ST_PROJ_PDEPTH = None
    ST_DATA_DRYSPELL = None
    H0_DEPTH_DISTS = None
    H0_DEPTH_SAMP = None
    ST_H0_PDEPTH = None
    # now delete
    #del DDRY_SPELL_DISTS
    #del DWET_SPELL_DISTS
    #del DDRY_SPELL_SAMP
    #del DWET_SPELL_SAMP
    #del DP_DEPTH_DISTS
    #del DP_DEPTH_SAMP
    #del PDRY_SPELL_DISTS
    #del PWET_SPELL_DISTS
    #del PDRY_SPELL_SAMP
    #del PWET_SPELL_SAMP
    #del PP_DEPTH_DISTS
    #del PP_DEPTH_SAMP
    #del ST_DATA_WETSPELL
    #del ST_DATA_PDEPTH
    #del ST_PROJ_DRYSPELL
    #del ST_PROJ_WETSPELL
    #del ST_PROJ_PDEPTH
    #del ST_DATA_DRYSPELL
    # end
    return

def setAllBegin():
    """Convenience method to seta all at beginning

    """
    global DDRY_SPELL_DISTS, DWET_SPELL_DISTS, DDRY_SPELL_SAMP, DWET_SPELL_SAMP
    global DP_DEPTH_DISTS, DP_DEPTH_SAMP, PDRY_SPELL_DISTS, PWET_SPELL_DISTS
    global PDRY_SPELL_SAMP, PWET_SPELL_SAMP, PP_DEPTH_DISTS, PP_DEPTH_SAMP
    global ST_DATA_WETSPELL, ST_DATA_PDEPTH, ST_PROJ_DRYSPELL
    global ST_PROJ_WETSPELL, ST_PROJ_PDEPTH, ST_DATA_DRYSPELL
    global H0_DEPTH_DISTS, H0_DEPTH_SAMP, ST_H0_PDEPTH
    # now set to None
    DDRY_SPELL_DISTS = dict()
    DWET_SPELL_DISTS = dict()
    DDRY_SPELL_SAMP = dict()
    DWET_SPELL_SAMP = dict()
    DP_DEPTH_DISTS = dict()
    DP_DEPTH_SAMP = dict()
    PDRY_SPELL_DISTS = dict()
    PWET_SPELL_DISTS = dict()
    PDRY_SPELL_SAMP = dict()
    PWET_SPELL_SAMP = dict()
    PP_DEPTH_DISTS = dict()
    PP_DEPTH_SAMP = dict()
    ST_DATA_WETSPELL = dict()
    ST_DATA_PDEPTH = dict()
    ST_PROJ_DRYSPELL = dict()
    ST_PROJ_WETSPELL = dict()
    ST_PROJ_PDEPTH = dict()
    ST_DATA_DRYSPELL = dict()
    H0_DEPTH_DISTS = dict()
    H0_DEPTH_SAMP  = dict()
    ST_H0_PDEPTH = dict()
    # end
    return

#EOF