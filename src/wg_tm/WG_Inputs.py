# -*- coding: utf-8 -*-
"""
.. module:: WG_Inputs
   :platform: Windows, Linux
   :synopsis: Provides input specification and shared module information

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Provides the inputs module where all input values and shared parameters can
be entered. This functionality can be replaced with a GUI in the future. Also holds the shared 
data structures.

For our 3 scenarios, need to set the following switch configurations

Changed back to 3 scenarios on 26 May 2020

Scenario 2: Maximums based on point recurrence
DATAP_TRUNC_OPTION = 1; H0_TRUNC_OPTION = 1; PROJP_TRUNC_OPTION = 3; and SCEN_WET_SPELL_SWITCH = 1

Scenario 1: Maximums based on LOCA
DATAP_TRUNC_OPTION = 1; H0_TRUNC_OPTION = 1; PROJP_TRUNC_OPTION = 2; and SCEN_WET_SPELL_SWITCH = 1

Scenario 3: PRISM wet spell for projection periods, otherwise LOCA
DATAP_TRUNC_OPTION = 1; H0_TRUNC_OPTION = 1; PROJP_TRUNC_OPTION = 2; and SCEN_WET_SPELL_SWITCH = 2

Changed to 2 scenarios 7 April 2020

Scenario 2: All LOCA 
DATAP_TRUNC_OPTION = 1; PROJP_TRUNC_OPTION = 2; and SCEN_WET_SPELL_SWITCH = 1

Scenario 3: Adjust wet spell to counteract drizzle
DATAP_TRUNC_OPTION = 1; PROJP_TRUNC_OPTION = 2; and SCEN_WET_SPELL_SWITCH = 2
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

import datetime as dt

#------------------------------------------------------------------------
# Global simulation settings - these generally need to be changed
OUT_DIR = r'C:\Temp\WG_Test_Out'
"""Location for model outputs"""
OUT_LABEL = r'DC_WGMN4'
"""Label to use for outputting files to OUT_DIR"""
OUT_SUB_DIR = "Final"
"""Output subdirectory"""
START_DATE = dt.datetime(1980, 1, 1)
"""Starting time for production of the stochastic synthetic time series"""
END_DATE = dt.datetime( 2100, 12, 31)
"""Ending time for the production of the stochastic synthetic time series"""
WET_STATE = "wet"
"""Keyword for wet state"""
DRY_STATE = "dry"
"""Keyword for dry state"""
NUM_PROJ_PERIODS = 3
"""Number of projection periods"""
NUM_DATA_PERIODS = 1
"""Number of data periods"""
DATA_KEYW = "data"
"""Key word to use to tell that is in a data period"""
PROJ_KEYW = "cproj"
"""Key word to use to tell that are in a climate projection period"""
DATA_PERIODS = [ [ dt.datetime(1980, 1, 1), dt.datetime(2010, 12, 31) ],
                ]
"""List of data periods with each sublist identifying an individual period. 
Index 0 of the sublist is start dt and Index 1 is end dt"""
PROJ_PERIODS = [ [ dt.datetime(2011, 1, 1), dt.datetime(2040, 12, 31) ],
                 [ dt.datetime(2041, 1, 1), dt.datetime(2070, 12, 31) ],
                 [ dt.datetime(2071, 1, 1), dt.datetime(2100, 12, 31) ],
               ]
"""List of climate projection periods with each sublist indentifying an
individual period. Index 0 of the sublist is start dt and Index 1 is end dt"""
K_c = 0.730
"""Crop coefficient to go from ETo to PET. Coefficient derived by comparing
calculated ETo to independently calculated/measured PET from "station" data."""
RDAY_ET = 0.25
"""PET percentage for rainy days. Scaling factor to reduce PET for rainy days"""
RTM_SLOPE = 0.478769194198665
""" Slope part of equation for Accumulated Potential Water Loss (APWL) in the 
Thornthwaite-Mather method. Extracted from USGS SWB code."""
RTM_EXP_TERM = -1.03678439421169
""" Exponent part of the equation for APWL in the Thornthwaite-Mather method.
Extracted from USGS SWB Code."""
MON_SURPLUS_RO = 0.025
""" Percentage of monthly surplus in the Thornthwaite-Mather approach that goes
to runoff (RO) during that month. Calibrated to Dolan Creek gauge data.
"""
MON_DETENTION_RE = 0.038
""" Percentage of monthly detention that goes to recharge or infiltrates 
below the water balance model to water table. Hypothetical value that was
calibrated to Dolan Creek gauge data.
"""
AVAIL_WS = 18.1
"""Watershed average available water supply from SSURGO in millimeters """
DATAP_TRUNC_OPTION = 1
"""Selection option for truncating mixed exponentials for the data period
Should always be 1
1 == PRISM (always for data period); MON_MAX_BY_REGION
2 == LOCA (option for projection periods); MON_MAX_BY_PP
3 == PRISM in projection period format (option for projection periods);
            MON_MAX_BY_PP_PRISM
4 == PRISM scaled to 100-yr, daily precipitation depth; H0_MAX_BY_PP
5 == PRISM scaled to 200-yr, daily precipitation depth; H1_MAX_BY_PP
"""
PROJP_TRUNC_OPTION = 5
"""Selection option for truncating mixed exponentials for projection periods
Should always be 2 or 3
1 == PRISM (always for data period); MON_MAX_BY_REGION
2 == LOCA (option for projection periods); MON_MAX_BY_PP
3 == PRISM in projection period format (option for projection periods);
            MON_MAX_BY_PP_PRISM
4 == PRISM scaled to 100-yr, daily precipitation depth; H0_MAX_BY_PP
5 == PRISM scaled to 200-yr, daily precipitation depth; H1_MAX_BY_PP
"""
H0_TRUNC_OPTION = 4
"""Selection option for truncating mixed exponentials for projection periods
Should always be 2 or 3
1 == PRISM (always for data period); MON_MAX_BY_REGION
2 == LOCA (option for projection periods); MON_MAX_BY_PP
3 == PRISM in projection period format (option for projection periods);
            MON_MAX_BY_PP_PRISM
4 == PRISM scaled to 100-yr, daily precipitation depth; H0_MAX_BY_PP
5 == PRISM scaled to 200-yr, daily precipitation depth; H1_MAX_BY_PP
"""
SCEN_WET_SPELL_SWITCH = 2
"""Selection option for wet spell length distribution
Less than or equal to 1 means to use the LOCA projected wet spell distribution
Greater than 1 means to use PRISM data spell distribution for projection periods
"""

#------------------------------------------------------------------------
# Other weather parameter model files
OW_WET_AVE_PRISM = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_W' \
                   r'eather\OWeath_Dry_Smooth_Ave_1981-2010.pickle'
"""Average wet day quantities by day of the year. Contains Tmax, Tmin, Tave,
RH, and Dewpoint"""
OW_DRY_AVE_PRISM = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_W' \
                   r'eather\OWeath_Wet_Smooth_Ave_1981-2010.pickle'
"""Average dry day quantities by day of the year. Contains Tmax, Tmin, Tave,
RH, and Dewpoint"""
OW_WET_STD_PRISM = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_W' \
                   r'eather\OWeath_Dry_Smooth_Std_1981-2010.pickle'
"""Average wet day quantities by day of the year. Contains Tmax, Tmin, Tave,
RH, and Dewpoint"""
OW_DRY_STD_PRISM = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\PRISM\Other_W' \
                   r'eather\OWeath_Wet_Smooth_Std_1981-2010.pickle'
"""Average dry day quantities by day of the year. Contains Tmax, Tmin, Tave,
RH, and Dewpoint"""
OW_WET_AVE_PROJ1 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
                    r'hastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWea' \
                    r'ther_2011-2040\OWeath_LOCA_Wet_Smooth_Ave_2011-2040.pickle'
"""Average wet day quantities by day of the year from LOCA downscaling. 
Contains Tmax and Tmin for projection period 1."""
OW_DRY_AVE_PROJ1 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_S' \
                    r'tochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Ot' \
                    r'herWeather_2011-2040\OWeath_LOCA_Dry_Smooth_Ave_20' \
                    r'11-2040.pickle'
"""Average dry day quantities by day of the year for projection period 1 from
LOCA downscaling. Contains Tmax and Tmin for projection period 1."""
OW_WET_STD_PROJ1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2011-2040\OWeath_LOCA_Wet_Smooth_Std_20' \
                   r'11-2040.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 1."""
OW_DRY_STD_PROJ1 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2011-2040\OWeath_LOCA_Dry_Smooth_Std_20' \
                   r'11-2040.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 1."""
OW_WET_AVE_PROJ2 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
                    r'hastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWea' \
                    r'ther_2041-2070\OWeath_LOCA_Wet_Smooth_Ave_2041-2070.pickle'
"""Average wet day quantities by day of the year from LOCA downscaling. 
Contains Tmax and Tmin for projection period 2."""
OW_DRY_AVE_PROJ2 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_S' \
                    r'tochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Ot' \
                    r'herWeather_2041-2070\OWeath_LOCA_Dry_Smooth_Ave_20' \
                    r'41-2070.pickle'
"""Average dry day quantities by day of the year for projection period 1 from
LOCA downscaling. Contains Tmax and Tmin for projection period 2."""
OW_WET_STD_PROJ2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2041-2070\OWeath_LOCA_Wet_Smooth_Std_20' \
                   r'41-2070.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 2."""
OW_DRY_STD_PROJ2 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2041-2070\OWeath_LOCA_Dry_Smooth_Std_20' \
                   r'41-2070.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 2."""
OW_WET_AVE_PROJ3 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stoc' \
                    r'hastic_CC_Recharge\Data\JNotes\Processed\CMIP5\OtherWea' \
                    r'ther_2071-2100\OWeath_LOCA_Wet_Smooth_Ave_2071-2100.pickle'
"""Average wet day quantities by day of the year from LOCA downscaling. 
Contains Tmax and Tmin for projection period 3."""
OW_DRY_AVE_PROJ3 =  r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_S' \
                    r'tochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Ot' \
                    r'herWeather_2071-2100\OWeath_LOCA_Dry_Smooth_Ave_20' \
                    r'71-2100.pickle'
"""Average dry day quantities by day of the year for projection period 3 from
LOCA downscaling. Contains Tmax and Tmin for projection period 3."""
OW_WET_STD_PROJ3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2071-2100\OWeath_LOCA_Wet_Smooth_Std_20' \
                   r'71-2100.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 3."""
OW_DRY_STD_PROJ3 = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_St' \
                   r'ochastic_CC_Recharge\Data\JNotes\Processed\CMIP5\Oth' \
                   r'erWeather_2071-2100\OWeath_LOCA_Dry_Smooth_Std_20' \
                   r'71-2100.pickle'
"""Average wet day standard deviation by day of the year. Contains Tmax and
Tmin for projection period 3."""


A_DATA_LIST = [ [0.61683454, 0.0860823],
                [0.10615798, 0.66408471],
              ]
"""A matrix calculated from PRISM for Tmax and Tmin"""
OW_M0_IN = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochasti' \
           r'c_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weather\OWea' \
           r'th_Z_M0rh_1981-2010.pickle'
"""M0 matrix for calculating daily error or residual term"""
B_DATA_LIST = [ [0.74574768, 0.0],
                [0.24627435, 0.64246926],
              ]
""" B matrix, calculated from PRISM for Tmax and Tmin"""
OW_M1_IN = r'\\augustine.space.swri.edu\jdrive\Groundwater\R8937_Stochasti' \
           r'c_CC_Recharge\Data\JNotes\Processed\PRISM\Other_Weather\OWea' \
           r'th_Z_M1rh_1981-2010.pickle'
"""M1 matrix for calculating daily error or residual term"""
A_PROJ1_LIST = [ [0.6232303 , 0.1474739 ],
                 [0.08809282, 0.63728267],
                ]
"""A matrix calculated from LOCA, 2011-2040 for Tmax and Tmin from projection
period 1."""
B_PROJ1_LIST = [ [0.69258303, 0.0 ],
                 [0.29542339, 0.65692135]
               ]
""" B matrix, calculated from LOCA, 2011-2040 for Tmax and Tmin from 
projection period 1."""
A_PROJ2_LIST = [ [0.62576301, 0.15244654],
                 [0.0887346 , 0.64952574]
                ]
"""A matrix calculated from LOCA, 2041-2070 for Tmax and Tmin from projection
period 2."""
B_PROJ2_LIST = [ [0.68365113, 0.        ],
                 [0.29779058, 0.64061725]
               ]
""" B matrix, calculated from LOCA, 2041-2070 for Tmax and Tmin from 
projection period 2."""
A_PROJ3_LIST = [ [0.6333683 , 0.16722986],
                 [0.09390023, 0.6749836]
                ]
"""A matrix calculated from LOCA, 2071-2100 for Tmax and Tmin from projection
period 3."""
B_PROJ3_LIST = [ [0.65746134, 0.        ],
                 [0.29203635, 0.6060881]
               ]
""" B matrix, calculated from LOCA, 2071-2100 for Tmax and Tmin from 
projection period 3."""

#------------------------------------------------------------------------
# parameter grid specifications - the LOCA grid is used to provide 
#  regionalization. For the null case WG (i.e. historical statistics),
#  PRISM regionalization into four regions is used to group the grid cells
#  and to only calculate statistics for four regions.
LOCA_GRID_MAP = { 137 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 1,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 4,
                          10 : 4,
                          11 : 1,
                          12 : 1,
                        },
                  120 : { 1 : 4,
                          2 : 3,
                          3 : 1,
                          4 : 4,
                          5 : 3,
                          6 : 4,
                          7 : 1,
                          8 : 1,
                          9 : 4,
                          10 : 4,
                          11 : 1,
                          12 : 4,
                        },
                  121 : { 1 : 4,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 1,
                          6 : 4,
                          7 : 1,
                          8 : 1,
                          9 : 4,
                          10 : 4,
                          11 : 1,
                          12 : 4,
                        },
                  122 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 1,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 4,
                          10 : 4,
                          11 : 1,
                          12 : 4,
                        },
                  123 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 1,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 1,
                          10 : 1,
                          11 : 1,
                          12 : 4,
                        },
                  104 : { 1 : 3,
                          2 : 3,
                          3 : 4,
                          4 : 4,
                          5 : 4,
                          6 : 3,
                          7 : 3,
                          8 : 4,
                          9 : 3,
                          10 : 3,
                          11 : 3,
                          12 : 3,
                        },
                  105 : { 1 : 4,
                          2 : 3,
                          3 : 4,
                          4 : 4,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 4,
                          9 : 3,
                          10 : 1,
                          11 : 4,
                          12 : 3,
                        },
                  106 : { 1 : 4,
                          2 : 1,
                          3 : 1,
                          4 : 4,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 4,
                          10 : 1,
                          11 : 1,
                          12 : 4,
                        },
                  107 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 4,
                        },
                  108 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 4,
                        },
                  90 : { 1 : 3,
                          2 : 3,
                          3 : 4,
                          4 : 4,
                          5 : 4,
                          6 : 3,
                          7 : 3,
                          8 : 4,
                          9 : 3,
                          10 : 3,
                          11 : 3,
                          12 : 3,
                        },
                  91 : { 1 : 4,
                          2 : 3,
                          3 : 1,
                          4 : 4,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 4,
                          9 : 3,
                          10 : 1,
                          11 : 4,
                          12 : 3,
                        },
                  92 : { 1 : 4,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 3,
                          10 : 1,
                          11 : 1,
                          12 : 3,
                        },
                  93 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 3,
                        },
                  94 : { 1 : 1,
                          2 : 1,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 1,
                          7 : 1,
                          8 : 1,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 1,
                        },
                  76 : { 1 : 3,
                          2 : 3,
                          3 : 4,
                          4 : 4,
                          5 : 4,
                          6 : 3,
                          7 : 3,
                          8 : 4,
                          9 : 3,
                          10 : 3,
                          11 : 3,
                          12 : 3,
                        },
                  77 : { 1 : 1,
                          2 : 3,
                          3 : 1,
                          4 : 1,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 4,
                          9 : 3,
                          10 : 1,
                          11 : 1,
                          12 : 3,
                        },
                  78 : { 1 : 1,
                          2 : 3,
                          3 : 1,
                          4 : 2,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 2,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 3,
                        },
                  79 : { 1 : 1,
                          2 : 1,
                          3 : 3,
                          4 : 1,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 2,
                          9 : 2,
                          10 : 1,
                          11 : 1,
                          12 : 1,
                        },
                  62 : { 1 : 3,
                          2 : 3,
                          3 : 4,
                          4 : 4,
                          5 : 4,
                          6 : 3,
                          7 : 3,
                          8 : 4,
                          9 : 3,
                          10 : 3,
                          11 : 3,
                          12 : 3,
                        },
                  63 : { 1 : 1,
                          2 : 3,
                          3 : 3,
                          4 : 3,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 4,
                          9 : 4,
                          10 : 2,
                          11 : 3,
                          12 : 3,
                        },
                  64 : { 1 : 1,
                          2 : 3,
                          3 : 3,
                          4 : 3,
                          5 : 3,
                          6 : 3,
                          7 : 1,
                          8 : 2,
                          9 : 4,
                          10 : 2,
                          11 : 1,
                          12 : 3,
                        },
                 }
LOCA_KEYS = sorted( LOCA_GRID_MAP.keys() )
NUM_LOCA_GRID = len( LOCA_KEYS )

#------------------------------------------------------------------------
# distribution specifications
# For spell length distributions assume that one distribution applies to
#  the entire study area
DATA_DRY_SPELL = [ { 1 : [ 1.3836124073, 0.1376607914 ], 
                     2 : [ 1.4471991130, 0.1492670095 ], 
                     3 : [ 1.7447455918, 0.1756684530 ], 
                     4 : [ 1.9524562993, 0.2019793661 ], 
                     5 : [ 1.6818592955, 0.2150610872 ], 
                     6 : [ 1.1477355165, 0.1411975399 ], 
                     7 : [ 1.1810416919, 0.1159559009 ], 
                     8 : [ 1.6121787517, 0.1919434663 ], 
                     9 : [ 1.4022132092, 0.1550580229 ], 
                    10 : [ 0.9832842401, 0.0909767528 ], 
                    11 : [ 1.2676187241, 0.1025777077 ], 
                    12 : [ 1.0783552973, 0.0873009291 ], 
        }, # Data Period 1
        ]
"""List of monthly parameters for negative binomial distributions for each 
month to simulate dry spell durations. Each data period is represented by
a dictionary with integer month as keys."""
PROJ_DRY_SPELL = [ { 1 : [ 1.4152085834, 0.1444528186 ], 
                     2 : [ 1.5294577746, 0.1759659286 ], 
                     3 : [ 1.6224944589, 0.1849281907 ], 
                     4 : [ 1.9784896628, 0.2709892535 ], 
                     5 : [ 1.9847544025, 0.3132914667 ], 
                     6 : [ 1.2248449618, 0.1724728495 ], 
                     7 : [ 1.2931533293, 0.1531314840 ], 
                     8 : [ 1.5226533618, 0.1899368719 ], 
                     9 : [ 1.6232355387, 0.2345162688 ], 
                    10 : [ 1.4338596989, 0.1783416582 ], 
                    11 : [ 1.3647861441, 0.1613865921 ], 
                    12 : [ 1.3093282782, 0.1383197089 ],
                   }, # Projection Period 1
                   { 1 : [ 1.3924165528, 0.1376299500 ], 
                     2 : [ 1.4934013203, 0.1664322699 ], 
                     3 : [ 1.5443552517, 0.1667586028 ], 
                     4 : [ 1.8611524982, 0.2544520424 ], 
                     5 : [ 1.8174117631, 0.2833586294 ], 
                     6 : [ 1.1877554723, 0.1632317732 ], 
                     7 : [ 1.2316783464, 0.1443249371 ], 
                     8 : [ 1.4927510435, 0.1841491616 ], 
                     9 : [ 1.5311231238, 0.2203541288 ], 
                    10 : [ 1.3466019217, 0.1644449840 ], 
                    11 : [ 1.2956584381, 0.1511169113 ], 
                    12 : [ 1.2908188107, 0.1339669991 ],
                   }, # Projection Period 2
                   { 1 : [ 1.3979044608, 0.1361445533 ], 
                     2 : [ 1.3805723862, 0.1487459213 ], 
                     3 : [ 1.5578944460, 0.1685067198 ], 
                     4 : [ 1.8329331025, 0.2462494118 ], 
                     5 : [ 1.6999394237, 0.2627005183 ], 
                     6 : [ 1.1548215200, 0.1535963506 ], 
                     7 : [ 1.2234715135, 0.1381070440 ], 
                     8 : [ 1.4555399869, 0.1719214887 ], 
                     9 : [ 1.4668902818, 0.2080845917 ], 
                    10 : [ 1.2957961910, 0.1516572834 ], 
                    11 : [ 1.2527027049, 0.1416893403 ], 
                    12 : [ 1.2547693319, 0.1260910760 ], 
                   }, # Projection Period 3
        ]
"""List of monthly parameters for negative binomial distributions for each 
month to simulate dry spell durations. Each climate projection period is 
represented by a dictionary with integer month as keys."""
DATA_WET_SPELL = [ { 1 : [ 3.4834190801, 0.6511378830 ], 
                     2 : [ 3.2969079837, 0.6448363573 ], 
                     3 : [ 3.1038991341, 0.6378926599 ], 
                     4 : [ 3.1279284202, 0.6387882982 ], 
                     5 : [ 3.4677028606, 0.6505459568 ], 
                     6 : [ 4.2927292161, 0.6744575595 ], 
                     7 : [ 4.2300533805, 0.6728506244 ], 
                     8 : [ 4.4033743230, 0.6772385755 ], 
                     9 : [ 3.4718443358, 0.6507325753 ], 
                    10 : [ 3.5962534486, 0.6236419721 ], 
                    11 : [ 3.9514761499, 0.6652886305 ], 
                    12 : [ 3.3243714013, 0.6458186259 ], 
        }, # Data Period 1
        ]
"""List of monthly parameters for negative binomial distributions for each 
month to simulate wet spell durations. Each data period is represented by
a dictionary with integer month as keys."""
PROJ_WET_SPELL = [ { 1 : [ 6.1789609637, 0.7738771128 ],
                     2 : [ 10.9379364244, 0.8481826143 ],
                     3 : [ 13.3914610126, 0.8750860929 ],
                     4 : [ 13.8854561699, 0.8603488217 ],
                     5 : [ 5.0099023927, 0.6528734944 ],
                     6 : [ 3.9046364884, 0.5694483035 ],
                     7 : [ 4.2644809506, 0.6183685499 ],
                     8 : [ 4.6540239163, 0.6436687080 ],
                     9 : [ 4.0780948670, 0.5840615975 ],
                    10 : [ 9.5023937032, 0.7927303249 ],
                    11 : [ 13.3914610126, 0.8634218554 ],
                    12 : [ 9.0485894441, 0.8293509549 ],
                   }, # Projection Period 1
                   { 1 : [ 5.3187917850, 0.7487656058 ], 
                     2 : [ 8.8536406394, 0.8206113170 ], 
                     3 : [ 10.9285313749, 0.8528720079 ], 
                     4 : [ 11.1711633326, 0.8306775036 ], 
                     5 : [ 5.1272618117, 0.6581614443 ], 
                     6 : [ 3.9461344495, 0.5716712171 ], 
                     7 : [ 4.1920169385, 0.6149560934 ], 
                     8 : [ 4.2707810928, 0.6224557724 ], 
                     9 : [ 4.0916524402, 0.5837756379 ], 
                    10 : [ 9.1590807135, 0.7878118111 ], 
                    11 : [ 10.9285313749, 0.8379182618 ], 
                    12 : [ 8.0994677645, 0.8141748590 ],
                   }, # Projection Period 2
                   { 1 : [ 5.5364401383, 0.7560202016 ], 
                     2 : [ 8.5297187405, 0.8162847323 ], 
                     3 : [ 7.9895475468, 0.8108482288 ], 
                     4 : [ 12.6242488892, 0.8485326623 ], 
                     5 : [ 5.3871946605, 0.6732914730 ], 
                     6 : [ 3.5766304453, 0.5490994325 ], 
                     7 : [ 3.8932347795, 0.5979795260 ], 
                     8 : [ 3.7992492447, 0.5935838540 ], 
                     9 : [ 3.6440893471, 0.5494845737 ], 
                    10 : [ 8.9667264439, 0.7840313282 ], 
                    11 : [ 8.5297187405, 0.8025794357 ], 
                    12 : [ 7.9324817028, 0.8120559026 ],
                   }, # Projection Period 3
        ]
"""List of monthly parameters for negative binomial distributions for each 
month to simulate wet spell durations. Each climate projection period is 
represented by a dictionary with integer month as keys."""

# For precipitation depth distributions assume that have identified four
#  regions from PRISM data. Each region has a distribution during data 
#  periods. However, when move to climate projections use the LOCA
#  grid cells to provide regionalization. This means that have NUM_LOCA_GRID
#  different regions for projection periods. During, data periods the 
#  dictionary LOCA_GRID_MAP provides mapping from LOCA grid cells to the 
#  region (of the four PRISM regions) that applies for each month of the year
DATA_PDEPTH = [ { 1 : { 1 : [ 0.5580394795, 1.3111941113, 7.9306982781 ],
                        2 : [ 0.4628641500, 1.7433974732, 8.6332042220 ],
                        3 : [ 0.5134445444, 1.5951737331, 11.2363602024 ],
                        4 : [ 0.5567870676, 1.9800648351, 12.6659495238 ],
                        5 : [ 0.4307972903, 3.2528113244, 11.4991244024 ],
                        6 : [ 0.2605061562, 3.5623741672, 10.6213743865 ],
                        7 : [ 0.3726873800, 2.2298341137, 10.3149103930 ],
                        8 : [ 0.7104320577, 4.3722807452, 15.9881922596 ],
                        9 : [ 0.5125335856, 2.9953631300, 14.6103848835 ],
                        10 : [ 0.5696411313, 3.0600591662, 18.6484124361 ],
                        11 : [ 0.7042435391, 3.4466731292, 14.2061565262 ],
                        12 : [ 0.8898938810, 2.8876380015, 18.9225699631 ],
                       },
                  2 : { 1 : [ 0.5314905250, 1.3779716320, 9.5663118855 ],
                        2 : [ 0.3165602886, 1.2336324647, 9.4573850782 ], 
                        3 : [ 0.5153693539, 2.3365384101, 13.5044247425 ], 
                        4 : [ 0.5953401593, 2.7266818166, 17.3474323908 ], 
                        5 : [ 0.2000347254, 2.1722019230, 12.4907937215 ], 
                        6 : [ 0.3117883191, 2.9792841290, 15.0477848805 ], 
                        7 : [ 0.4719853678, 3.3462926457, 13.8965266747 ], 
                        8 : [ 0.4689846057, 2.4618500255, 12.9637007465 ], 
                        9 : [ 0.3875383115, 2.5350657014, 14.1426521408 ], 
                        10 : [ 0.6028060469, 3.3954039946, 21.2829350901 ], 
                        11 : [ 0.4089391324, 1.9097757154, 13.1620844587 ], 
                        12 : [ 0.8402326533, 3.5239436903, 18.6305362359 ],
                       },
                  3 : { 1 : [ 0.4976495180, 1.1993907827, 7.7021850612 ],
                        2 : [ 0.4694544192, 1.6638973724, 9.1659040115 ],
                        3 : [ 0.5445200079, 1.5974848883, 12.2211326498 ], 
                        4 : [ 0.6565788097, 2.1907311502, 15.0325771208 ], 
                        5 : [ 0.2675380181, 2.1203330485, 10.7098270498 ], 
                        6 : [ 0.3873013186, 3.6765232817, 13.4952025784 ], 
                        7 : [ 0.3744444351, 2.1540594935, 11.5938640554 ], 
                        8 : [ 0.6202356052, 4.5941684242, 19.5742237644 ], 
                        9 : [ 0.5100892859, 3.4364634518, 18.5390004087 ], 
                        10 : [ 0.5656847525, 2.9244307572, 17.7571442772 ], 
                        11 : [ 0.6114681789, 3.6421753111, 13.1547467110 ], 
                        12 : [ 0.8576992867, 3.2828629744, 13.2908956843 ], 
                      },
                  4 : { 1 : [ 0.5416630114, 1.2814300326, 7.5108584327 ],
                        2 : [ 0.4304518470, 1.4846430964, 8.9187165647 ],
                        3 : [ 0.5471885402, 1.5914312208, 12.8592732893 ], 
                        4 : [ 0.5879179278, 2.3081166543, 14.3426567351 ], 
                        5 : [ 0.3642733310, 3.0826649201, 12.8600428277 ], 
                        6 : [ 0.9871142904, 8.0091536490, 91.1262104227 ], 
                        7 : [ 0.4825194080, 2.3906951720, 10.7333685052 ], 
                        8 : [ 0.5933780398, 4.1884176476, 15.8250341448 ], 
                        9 : [ 0.5071577287, 3.1845193432, 14.3799854263 ], 
                        10 : [ 0.5284578373, 2.9527732139, 15.7483091693 ], 
                        11 : [ 0.7369918411, 3.7964574091, 13.9779434853 ], 
                        12 : [ 0.9065567351, 2.8015203755, 18.2105260407 ], 
                       },
                }, # data period 1
            ]
REG_KEYS = sorted( DATA_PDEPTH[0].keys() )
NUM_REGIONS = len( REG_KEYS )
"""List of monthly parameters for mixed exponential distributions for each 
month and each spatial region to simulate daily precipitation depth. Each 
data period is represented by a dictionary with region id as keys. Each
region is represented with a dictionary with integer months as keys and a
list of distribution parameters as values. The distribution parameters are 0 -
alpha, 1 - mu1, 2 - mu2."""

PROJ_PDEPTH = [ { 62 : { 1 : [0.8016496579477584, 2.169027063382938, 13.17503494410332], 
                        2 : [0.7471475162085978, 2.286089571916198, 16.67006499243872], 
                        3 : [0.7483309101875715, 2.252086908191599, 14.56170482778343], 
                        4 : [0.7055117818797079, 2.954087481363327, 17.13903720752275], 
                        5 : [0.7349434027593292, 3.612503333240251, 21.38879284158734], 
                        6 : [0.7883990709069529, 4.37920672734349, 28.51331587248957], 
                        7 : [0.786168759269283, 3.605688098841112, 30.16037265803153], 
                        8 : [0.7939902111982319, 3.7129412233567, 28.312710616707], 
                        9 : [0.7410878751405082, 3.937014566570954, 32.27460788956236], 
                        10 : [0.7474904344133341, 3.426886187004902, 24.75340845708983], 
                        11 : [0.8057033334776559, 2.885473907831232, 15.42554236752872], 
                        12 : [0.8281177877655955, 2.249492013175011, 13.61489307206248] }, 
                  63 : { 1 : [0.7982062970040906, 2.11236269571345, 13.32326270447389], 
                        2 : [0.7433485285520577, 2.261197344912325, 16.63287899083775], 
                        3 : [0.7383030531485685, 2.2324810496971, 14.57575347556785], 
                        4 : [0.7008640359380465, 3.028701991903533, 17.50550071860963], 
                        5 : [0.7492574351266559, 3.812323495711262, 22.17140259974088], 
                        6 : [0.7974037852505161, 4.382526530441488, 28.75630570245019], 
                        7 : [0.8018957920305667, 3.64936442593803, 30.26879964315353], 
                        8 : [0.7948189236657193, 3.88476419569041, 28.42012090148468], 
                        9 : [0.7554532008505478, 4.093282848384187, 32.20122577589983], 
                        10 : [0.7520383942150172, 3.550744166428804, 24.78150747967945], 
                        11 : [0.8013157894590008, 2.944702350349293, 15.55391321859405], 
                        12 : [0.8282544782840326, 2.298343260014974, 13.98779427929208] }, 
                  64 : { 1 : [0.8048193040843147, 2.099622607482847, 13.71925220286028], 
                        2 : [0.7475315039695236, 2.250688642756277, 17.0965933118907], 
                        3 : [0.7302268928095538, 2.187768460674222, 15.05020247131006], 
                        4 : [0.6895665311375297, 2.944055742347456, 17.49228030238188], 
                        5 : [0.7440975921440993, 3.67472324952121, 21.92809492351869], 
                        6 : [0.8031772098048002, 4.260830197820892, 29.73360840321369], 
                        7 : [0.8059320147197829, 3.723958848258792, 31.74050582203284], 
                        8 : [0.7886921107052163, 3.937574492970316, 28.44518307771408], 
                        9 : [0.7613409528419866, 4.168301359741747, 32.28280287215186], 
                        10 : [0.7650375648015332, 3.630491034194302, 25.64858794440739], 
                        11 : [0.802593505543285, 2.935181496093052, 15.85324294666951], 
                        12 : [0.8427152673877292, 2.341519245884955, 14.62375429844087] }, 
                  76 : { 1 : [0.7943471065175488, 2.174751368126334, 13.3774380082607], 
                        2 : [0.7420921104694449, 2.295550497626025, 17.18625675425297], 
                        3 : [0.7475026809876432, 2.230835306538656, 14.74100316582842], 
                        4 : [0.7125115198237433, 2.933316229533747, 17.44843093100332], 
                        5 : [0.7448163058909024, 3.680483508483511, 21.91495483517951], 
                        6 : [0.7964241791010906, 4.307319665597902, 28.1607204144246], 
                        7 : [0.789048563165652, 3.731559975695293, 30.07254578901654], 
                        8 : [0.8008385620183042, 3.741738084126971, 28.43085742575323], 
                        9 : [0.7471871010462917, 4.021642653976496, 32.49109107781151], 
                        10 : [0.7363527040543333, 3.489485563848629, 24.78431583526255], 
                        11 : [0.7988708344905271, 2.88615432189715, 15.57132885051061], 
                        12 : [0.8237918675675137, 2.297758085846012, 13.89807510175953] }, 
                  77 : { 1 : [0.7990924560596729, 2.108105144362405, 13.25452919451619], 
                        2 : [0.745943806157526, 2.266365681784529, 17.03491357596197], 
                        3 : [0.741060039795019, 2.242859318053694, 14.58351080930772], 
                        4 : [0.7067579112959975, 3.035086618350709, 17.48834409608192], 
                        5 : [0.7509976256412944, 3.801346396010838, 22.08659893798114], 
                        6 : [0.8039283211141571, 4.262143524328756, 28.27027422138558], 
                        7 : [0.79762257784338, 3.736554023489091, 30.29193005435483], 
                        8 : [0.7983143422144213, 3.848001425951893, 28.3367730449113], 
                        9 : [0.7562148066847182, 4.16912146048435, 32.47364022381551], 
                        10 : [0.7422626893365691, 3.642982963139201, 24.9091461221175], 
                        11 : [0.7989510688879533, 2.931952789191164, 15.69762727373525], 
                        12 : [0.830869999794021, 2.296489303669894, 14.12433397222612] }, 
                  78 : { 1 : [0.7966279858825666, 2.072238337001644, 13.53587433364003], 
                        2 : [0.7428731343056368, 2.249551949886897, 17.37682039587558], 
                        3 : [0.726110483151832, 2.217182844605552, 14.71156249087588], 
                        4 : [0.6885132163477337, 3.009471827755875, 17.43302229454497], 
                        5 : [0.7483370950706667, 3.848674770559515, 22.16258655432629], 
                        6 : [0.7990810963949636, 4.253178787243963, 28.2323198013505], 
                        7 : [0.7997665964371956, 3.700314841204003, 30.4400861927955], 
                        8 : [0.7887434159830247, 3.90591589266121, 28.17577941523832], 
                        9 : [0.7595425962514415, 4.265062355616797, 32.48618136356616], 
                        10 : [0.750338263033926, 3.757924758958792, 25.57019639762166], 
                        11 : [0.7943512228241941, 2.976840836412779, 16.0214684783154], 
                        12 : [0.8313799429118892, 2.322209205714969, 14.66799054314122] }, 
                  79 : { 1 : [0.800919846432545, 2.1458329302584, 13.81564350794259], 
                        2 : [0.7307214229346116, 2.317540207429717, 17.80640500213975], 
                        3 : [0.7044839258468351, 2.22599333885223, 15.20907173594631], 
                        4 : [0.6553472015960077, 2.949175395154565, 17.27017376311082], 
                        5 : [0.7403322539659134, 3.867460545303194, 22.01587711918009], 
                        6 : [0.7921451314806713, 4.281302855399417, 28.09245210636183], 
                        7 : [0.7953823050962961, 3.737424054959563, 30.47135199231459], 
                        8 : [0.7808015585724831, 3.914945370531534, 28.01349575643902], 
                        9 : [0.7745738440587604, 4.355679495395191, 33.17361272955048], 
                        10 : [0.771497023800065, 3.93317222702989, 26.52631096604172], 
                        11 : [0.8011749405874825, 3.051074718562049, 16.09639671890112], 
                        12 : [0.8426600232679803, 2.431409998226815, 15.29562975867613] }, 
                  90 : { 1 : [0.7960169617403392, 2.155085316909357, 13.3606935896353], 
                        2 : [0.7434980416411079, 2.275683104603579, 17.30405932228491], 
                        3 : [0.7467988809973514, 2.23931708249577, 14.66342672723632], 
                        4 : [0.714782989449388, 2.961762355540274, 17.42112608554993], 
                        5 : [0.7484376374036811, 3.729073776396286, 21.9084395365744], 
                        6 : [0.7972637252257189, 4.213657968164345, 27.42618721257337], 
                        7 : [0.7835766510063716, 3.729273620873236, 29.62311703551075], 
                        8 : [0.7996055398283822, 3.796660252734717, 28.32249707526814], 
                        9 : [0.7486551478790486, 4.085560555829218, 32.52845060388857], 
                        10 : [0.7299878830592147, 3.488453308810853, 24.61520585338698], 
                        11 : [0.7956232459039968, 2.879084638981577, 15.76703899899597], 
                        12 : [0.828003606551272, 2.295691869205378, 14.13097324692783] }, 
                  91 : { 1 : [0.8011014925097236, 2.169603066678268, 13.26670269800652], 
                        2 : [0.7417429241332092, 2.366173001224836, 17.33500923936366], 
                        3 : [0.7415005901806422, 2.29404621652554, 14.71627441481876], 
                        4 : [0.7100723330433072, 3.03608093397624, 17.40100142691835], 
                        5 : [0.7481180815851479, 3.794588049235764, 21.80194473811068], 
                        6 : [0.8043572271294447, 4.273181202748787, 27.78672593721017], 
                        7 : [0.7923772874462891, 3.808204079733183, 29.96159416648795], 
                        8 : [0.7985905248012206, 3.88304043139527, 28.36017523242486], 
                        9 : [0.7585256364071248, 4.259938611910091, 33.09891284349147], 
                        10 : [0.7412504513365178, 3.673474862197361, 24.79213747514286], 
                        11 : [0.7944355341117565, 2.964491290006241, 15.58774296285804], 
                        12 : [0.8336099791002993, 2.347651824313203, 14.41251766825869] }, 
                  92 : { 1 : [0.8018750908254455, 2.183303310347669, 13.42599128097401], 
                        2 : [0.7322109214106395, 2.386658528426362, 17.61899799727025], 
                        3 : [0.7245021477645163, 2.31107182340621, 14.95844057817796], 
                        4 : [0.6873856039372505, 3.070284653796591, 17.45151941973614], 
                        5 : [0.7525871037230543, 3.894310558229054, 22.1642866127214], 
                        6 : [0.8015115309704902, 4.325754944416944, 27.92410799772352], 
                        7 : [0.7986960518872395, 3.815079240780026, 30.06135895073129], 
                        8 : [0.7951993085673447, 3.937968809498011, 28.38383680619845], 
                        9 : [0.7708084157654158, 4.376039806030473, 33.47890746367305], 
                        10 : [0.7578785057385404, 3.805521879720131, 25.47787701735435], 
                        11 : [0.7986615030926316, 3.021965265955379, 15.99906358966734], 
                        12 : [0.837758223080364, 2.406089530614151, 14.80058273300303] }, 
                  93 : { 1 : [0.7967017912167014, 2.169846746165701, 13.58890510932383], 
                        2 : [0.7268551541337093, 2.375903603094724, 17.59218826038023], 
                        3 : [0.7139379921966845, 2.296043202160402, 14.93996155530499], 
                        4 : [0.674468785052367, 3.036916503805893, 17.23834339486061], 
                        5 : [0.749795615126963, 3.918509710929562, 22.11545898490584], 
                        6 : [0.7960110817115903, 4.338624520089778, 27.94203490197387], 
                        7 : [0.7984767144588607, 3.875144218939525, 30.86031944151557], 
                        8 : [0.7892389699074968, 4.000816495934203, 28.61594458352083], 
                        9 : [0.7748057077621461, 4.453407544979427, 33.61335714598785], 
                        10 : [0.7630903880331076, 3.890531608473453, 25.9788307005001], 
                        11 : [0.7946115241291238, 3.042865074474353, 16.05275301630715], 
                        12 : [0.834369970286865, 2.422314528193419, 15.03718346431477] }, 
                  94 : { 1 : [0.7920781797457487, 2.178684377212214, 13.80235501174421], 
                        2 : [0.7275620118076187, 2.398982394851888, 17.89250109136779], 
                        3 : [0.7094798119805814, 2.303745558902107, 15.08163541829314], 
                        4 : [0.6708719196148301, 3.028776646745568, 17.36358456398587], 
                        5 : [0.7490397764873129, 3.935987914573614, 22.20655666788215], 
                        6 : [0.7915948060533139, 4.356199442016595, 28.19156048218657], 
                        7 : [0.7975208606112821, 3.857236020241093, 31.23584076060287], 
                        8 : [0.7875074163889244, 3.944407399298474, 28.59425972579859], 
                        9 : [0.7772256295057508, 4.461191617775373, 33.79183159199817], 
                        10 : [0.7656454731469556, 3.93169880332159, 26.40016401223087], 
                        11 : [0.789940390587777, 3.068048113886417, 16.1738803240356], 
                        12 : [0.8297578016231729, 2.451603787238019, 15.35434735101597] }, 
                  104 : { 1 : [0.8025243549483214, 2.210019624808577, 13.10028910721007], 
                        2 : [0.7383652312520379, 2.39086095443663, 16.99131384077955], 
                        3 : [0.7525991802625858, 2.346950321059501, 14.39767704252528], 
                        4 : [0.730666942795149, 2.938866739592531, 17.06494483838206], 
                        5 : [0.7423735435468864, 3.59750417918397, 21.10917303070243], 
                        6 : [0.7881999218978152, 4.212477329862036, 26.33096856425303], 
                        7 : [0.787478791829337, 3.827928093972138, 29.45227755153314], 
                        8 : [0.8025813632443882, 3.745450094417968, 28.27931163464081], 
                        9 : [0.7568162182405866, 4.129059242540909, 32.1998057964], 
                        10 : [0.7379254596033339, 3.460960414582134, 23.83098415759711], 
                        11 : [0.7914899249433347, 2.87032551400973, 15.33242434650063], 
                        12 : [0.8338097447621758, 2.333465238658008, 14.26440029169141] }, 
                  105 : { 1 : [0.8009936317746292, 2.216706250638157, 13.15468458874676], 
                        2 : [0.729717534565133, 2.421088470585891, 17.20315230280458], 
                        3 : [0.7403120028917394, 2.376852729110888, 14.40729731089413], 
                        4 : [0.7147385282100388, 3.026197777186542, 17.05619953811232], 
                        5 : [0.7439137741842949, 3.689051147941809, 21.06018338461578], 
                        6 : [0.7907039138977191, 4.334282881504775, 26.28953497114088], 
                        7 : [0.7944158182369957, 3.785835869687854, 28.93137535722108], 
                        8 : [0.8039791571392355, 3.93077136851707, 29.06275727212267], 
                        9 : [0.7635234387783619, 4.384327686091977, 33.12461656904204], 
                        10 : [0.7414667441136886, 3.711039612972993, 24.43690413943775], 
                        11 : [0.7905882923261986, 2.924672528833946, 15.55534138407145], 
                        12 : [0.833086011878111, 2.363381408269447, 14.63764354523055] }, 
                  106 : { 1 : [0.7986390177409856, 2.203980356753182, 13.29455354240508], 
                        2 : [0.7238220229158968, 2.407403549965152, 17.14737607275539], 
                        3 : [0.7316084977106663, 2.364411709635886, 14.34217027713876], 
                        4 : [0.7065955028065839, 3.066014716862808, 17.00926995738696], 
                        5 : [0.7490053041264632, 3.785283134474076, 21.28272767238796], 
                        6 : [0.7905409934043534, 4.179945248391798, 25.98052772103033], 
                        7 : [0.7985893946121586, 3.844790416581236, 29.40880068678518], 
                        8 : [0.8019780608048566, 4.039292948951013, 29.24272192135862], 
                        9 : [0.7668737076924524, 4.459943365328035, 33.22057385372202], 
                        10 : [0.747984203944222, 3.787351327124285, 24.77326408152074], 
                        11 : [0.7901190511284861, 2.95598077324318, 15.74658611474007], 
                        12 : [0.8306341018745118, 2.380665314024522, 14.79919516483066] }, 
                  107 : { 1 : [0.7960451951539478, 2.197800522705169, 13.52476094339062], 
                        2 : [0.7298106916677366, 2.457803552829946, 17.6920676086813], 
                        3 : [0.7257613716768032, 2.392877868931736, 14.67336316319747], 
                        4 : [0.6990003438102174, 3.129070709842382, 17.3407105133144], 
                        5 : [0.7549930060955454, 3.908900706385351, 21.89388616291808], 
                        6 : [0.7852997695960128, 4.174162719350671, 26.45435336460234], 
                        7 : [0.7979989672864799, 3.848245733119899, 29.92755777873051], 
                        8 : [0.7971845347788521, 3.968179830694941, 29.25579122473081], 
                        9 : [0.7687528600415746, 4.509643913535294, 33.48716030728978], 
                        10 : [0.7519755959260283, 3.812041166752566, 25.21727724423538], 
                        11 : [0.7887463260401528, 2.935308509659392, 15.92256851442818], 
                        12 : [0.8278153771062517, 2.379871898212547, 15.07219500072163] }, 
                  108 : { 1 : [0.7904429155088294, 2.198191059401049, 13.68141968795849], 
                        2 : [0.7239663819449957, 2.470851696043822, 17.82121947862917], 
                        3 : [0.7176420786956119, 2.387063294900583, 14.68871452625819], 
                        4 : [0.6964849060835332, 3.111583288070015, 17.46653622438403], 
                        5 : [0.7543873955882293, 3.868252144082199, 21.83164821002092], 
                        6 : [0.7794688636287582, 4.019552668713936, 25.98449867199368], 
                        7 : [0.7955670735415699, 3.85247635562992, 30.14262262696837], 
                        8 : [0.7916649547950132, 4.018767792008257, 29.28276000034528], 
                        9 : [0.7707693988112447, 4.591532903555596, 33.72962247819458], 
                        10 : [0.7518347754362906, 3.853573464437697, 25.58698329628709], 
                        11 : [0.7849828093186696, 2.914130236010546, 16.1728366746943], 
                        12 : [0.8223071347463334, 2.374200513588031, 15.33710360124331] }, 
                  120 : { 1 : [0.800700443582044, 2.240300931284287, 13.25212670832235], 
                        2 : [0.7313463410036699, 2.482298220810524, 17.39241975557999], 
                        3 : [0.7429317086025303, 2.426889850894236, 14.43010914971324], 
                        4 : [0.7259648293317554, 3.076958290301499, 17.27194547655542], 
                        5 : [0.7536652708243529, 3.798467810827534, 21.49068281909945], 
                        6 : [0.7853138095299315, 4.126765214829757, 25.63791692073135], 
                        7 : [0.7946758420989654, 3.899468861348835, 29.35477091608856], 
                        8 : [0.8002883840039257, 4.032391992710966, 29.24237687996049], 
                        9 : [0.7638552399446936, 4.315081848554263, 32.40607781335984], 
                        10 : [0.7445218752496767, 3.602205627058065, 23.9555467721387], 
                        11 : [0.7843386326155134, 2.878978465785053, 15.68197663242594], 
                        12 : [0.8304056241396455, 2.382544505679255, 14.84588121092132] }, 
                  121 : { 1 : [0.795792584707003, 2.230246159761309, 13.32485271980129], 
                        2 : [0.726024658407422, 2.4883775343462, 17.43999555536656], 
                        3 : [0.734938194558298, 2.431254648770032, 14.38930183752394], 
                        4 : [0.7227968939644462, 3.071912411557054, 17.29385290771059], 
                        5 : [0.7582182935959779, 3.813677474983376, 21.58738783839947], 
                        6 : [0.78046716780524, 3.991055964415181, 25.15921143501221], 
                        7 : [0.7982793610322524, 3.914554692167804, 29.76674336264111], 
                        8 : [0.7969866886415419, 4.094422779616734, 29.44423899817343], 
                        9 : [0.7685519590258747, 4.424800191300736, 32.83824970087325], 
                        10 : [0.747883028433878, 3.630638001054636, 24.40689490244472], 
                        11 : [0.7824736556873025, 2.84975288486792, 15.79734594757842], 
                        12 : [0.8249190559652729, 2.364558792379834, 14.97294712819465] }, 
                  122 : { 1 : [0.7917239145071278, 2.231829750723292, 13.52984666180553], 
                        2 : [0.7191377803922154, 2.485848754546304, 17.6015690260331], 
                        3 : [0.7284728392932622, 2.425624914857634, 14.49014765892622], 
                        4 : [0.7143999964119149, 3.074219478283005, 17.38788887415734], 
                        5 : [0.7535093822265033, 3.837358000269389, 21.64949273776968], 
                        6 : [0.7759792063276183, 3.984080133966216, 25.34391918094957], 
                        7 : [0.7994283524113507, 3.941451568246344, 30.25836904029697], 
                        8 : [0.7922499405734352, 4.154521573905026, 29.78191783514821], 
                        9 : [0.7702703305017825, 4.633775874037369, 33.79470093941833], 
                        10 : [0.7432923743777649, 3.767129790431121, 24.99981344218761], 
                        11 : [0.7782526584874211, 2.839369480217008, 16.11914165191446], 
                        12 : [0.8188666193628821, 2.348012485160004, 15.36521131334922] }, 
                  123 : { 1 : [0.7898430986433854, 2.233635405749273, 13.55294126113735], 
                        2 : [0.720193153027176, 2.50880087797637, 17.7827546595169], 
                        3 : [0.7293481048102516, 2.43785735205664, 14.82998058389454], 
                        4 : [0.7091781123874635, 3.028261599327537, 17.75264282212025], 
                        5 : [0.7418621464816518, 3.702250897698546, 21.36509322396946], 
                        6 : [0.7724055782568086, 3.811521654654527, 24.90974386761428], 
                        7 : [0.8009970200686668, 3.730032348263265, 29.54467474834005], 
                        8 : [0.7927631291111952, 4.112754923362855, 29.72666070269877], 
                        9 : [0.7706073057487561, 4.705504230974018, 34.11375741998847], 
                        10 : [0.7432231909347071, 3.784959384512011, 25.21794957472455], 
                        11 : [0.7770063113536324, 2.819112956156581, 16.23904006133372], 
                        12 : [0.8126601162791558, 2.354539188240144, 15.53968235440291] }, 
                  137 : { 1 : [0.8083065025585897, 2.288767882161487, 13.66995003034815], 
                        2 : [0.7392359426876702, 2.52267835725691, 17.99354532729264], 
                        3 : [0.734176799198174, 2.443555100472147, 14.49813767101611], 
                        4 : [0.7202425969273926, 3.100800799499163, 17.67442182280563], 
                        5 : [0.7700555421201896, 4.016973007659179, 22.17769179350029], 
                        6 : [0.7927859797705976, 4.047253360615877, 25.19382566061565], 
                        7 : [0.8153794221756041, 4.018053402613461, 30.46035710115164], 
                        8 : [0.7903434397656623, 4.320601030328093, 30.02476269696642], 
                        9 : [0.7661340065033512, 4.801504744769798, 33.49666278549128], 
                        10 : [0.7379530326146582, 3.777715355997668, 24.88460632492333], 
                        11 : [0.7732591631783292, 2.765235001310678, 16.33162291458246], 
                        12 : [0.8295196663908538, 2.406088711628872, 15.80462718377437] }, 
            },  # projection period 1
            { 62 : { 1 : [0.8015142693394351, 2.166870153166387, 13.31277858488242], 
                        2 : [0.7771635642889123, 2.328354764672594, 18.13531880549212], 
                        3 : [0.7562620482390178, 2.315493099537456, 15.80678709819068], 
                        4 : [0.6841144160564967, 2.9730169052102, 17.34251641527184], 
                        5 : [0.7416248782047017, 3.634630364390624, 22.19199611908756], 
                        6 : [0.788606266456376, 4.372154630379182, 27.92548253540423], 
                        7 : [0.7728702970274444, 3.598012039076159, 31.81862930571293], 
                        8 : [0.7932806020656926, 3.804590426362627, 29.85926874066707], 
                        9 : [0.744949776790136, 3.968866701800995, 33.99800803566035], 
                        10 : [0.7453319121725404, 3.398878038014283, 25.6130821089504], 
                        11 : [0.7983326588058312, 2.875198946514131, 16.40372141814399], 
                        12 : [0.8263837494204342, 2.281282553536365, 15.26667069564887] }, 
                  63 : { 1 : [0.797798200387284, 2.120772725989882, 13.26565727380241], 
                        2 : [0.7740272225331956, 2.306578654440813, 18.08517244970031], 
                        3 : [0.7479123585628005, 2.283670973570912, 15.72776973520581], 
                        4 : [0.6828620433476325, 3.016641708734776, 17.74132742105915], 
                        5 : [0.753770021002818, 3.78749013603103, 22.86442915774344], 
                        6 : [0.797113268851975, 4.345197866344593, 28.27238294988828], 
                        7 : [0.7929275752782068, 3.706498099089439, 32.04682316789643], 
                        8 : [0.7973591608438808, 4.028579119559908, 30.08750663296735], 
                        9 : [0.7549174691821576, 4.094106815507535, 33.54063361572052], 
                        10 : [0.7510620653924694, 3.511081650989414, 25.76089708043138], 
                        11 : [0.7948163752086959, 2.926371254821674, 16.62023049231942], 
                        12 : [0.8316897520891473, 2.3401846459089, 15.85401149550463] }, 
                  64 : { 1 : [0.8072232805406933, 2.091974216520931, 13.68022603236448], 
                        2 : [0.7752029789684478, 2.297386241037886, 18.5463090017878], 
                        3 : [0.735342216142434, 2.2535302022477, 15.93455803954566], 
                        4 : [0.6678977218372619, 2.917122903483682, 17.69099326722688], 
                        5 : [0.7504771588839025, 3.697392399679443, 22.72973470580385], 
                        6 : [0.8064845094704605, 4.231841058497259, 29.3472495250397], 
                        7 : [0.8059709517323247, 3.863856147413847, 34.42475506866877], 
                        8 : [0.7922589689230121, 4.090471470874085, 30.67709752049222], 
                        9 : [0.7613788661979326, 4.191282871534789, 33.61182263371894], 
                        10 : [0.7582642678341444, 3.586518782915392, 26.43793226890254], 
                        11 : [0.7983310791610353, 2.934549552939355, 17.23312045970434], 
                        12 : [0.8435371629478577, 2.392360904296037, 16.66338323510287] }, 
                  76 : { 1 : [0.7967750111844838, 2.176464963429041, 13.3612280869679], 
                        2 : [0.7706312890415404, 2.334133535315192, 18.68088223819669], 
                        3 : [0.7513810300735889, 2.251697823845258, 15.93440756063132], 
                        4 : [0.6903742180920989, 2.918967816813601, 17.60435366909769], 
                        5 : [0.7486815492893484, 3.661915508988868, 22.51612666563254], 
                        6 : [0.7959993000200329, 4.286903999740312, 27.67492911918981], 
                        7 : [0.7787434273161861, 3.778899289757284, 31.749103793428], 
                        8 : [0.7990137280877522, 3.81632343788767, 29.35950976937078], 
                        9 : [0.7481335969059503, 4.029595610729134, 34.00226536539267], 
                        10 : [0.7396365173028232, 3.441373116677417, 25.78793907757239], 
                        11 : [0.7898797659807577, 2.849581485262592, 16.54594598815864], 
                        12 : [0.8192914913559133, 2.311383785520296, 15.40090585841299] }, 
                  77 : { 1 : [0.8033152266568502, 2.115607255014428, 13.30441172225986], 
                        2 : [0.7716777518182815, 2.295886376104762, 18.33108314075533], 
                        3 : [0.742899118714604, 2.275848129036322, 15.57512678114641], 
                        4 : [0.6848932062184282, 3.003194212239355, 17.62858705657407], 
                        5 : [0.7539034216086125, 3.768988557644755, 22.62415538983363], 
                        6 : [0.803369862053845, 4.201663833957091, 27.70771067982635], 
                        7 : [0.785783588560848, 3.761264835777992, 31.79273262982695], 
                        8 : [0.7979734348562951, 3.940567232884958, 29.63880008905748], 
                        9 : [0.7553066703044281, 4.160514341177098, 33.7350224844095], 
                        10 : [0.744603496520869, 3.588740617339999, 25.87262015840259], 
                        11 : [0.7927709804267902, 2.902277737193361, 16.81334427131921], 
                        12 : [0.8286867845043949, 2.318702612202862, 15.75677594971046] }, 
                  78 : { 1 : [0.7997050690624765, 2.067704072937192, 13.53669748433528], 
                        2 : [0.7649084165400277, 2.268728682177815, 18.53340899538239], 
                        3 : [0.7284300635413569, 2.248589588215149, 15.63760463982765], 
                        4 : [0.6684623507772208, 3.003399266194126, 17.67112616709808], 
                        5 : [0.7503122991450526, 3.805398721658777, 22.60130088361516], 
                        6 : [0.799608009076353, 4.197811908863204, 27.79338966587834], 
                        7 : [0.7892885034244096, 3.741778033147625, 31.92866303526813], 
                        8 : [0.7909318446708405, 4.014102235624859, 29.88763874170047], 
                        9 : [0.7577329096041939, 4.24594380049921, 33.59152503023191], 
                        10 : [0.7484561128879124, 3.687671917040336, 26.43931553891164], 
                        11 : [0.7893052377881348, 2.976150606445983, 17.34892430416406], 
                        12 : [0.8315439491776134, 2.361841202389797, 16.50360649726936] }, 
                  79 : { 1 : [0.8033980078088411, 2.156015633915033, 13.85945996576697], 
                        2 : [0.7533425017417991, 2.355182551798273, 18.88883046224649], 
                        3 : [0.7087717579531363, 2.26807443409916, 15.93376426650254], 
                        4 : [0.6409087749693356, 2.96942360153329, 17.64817657371789], 
                        5 : [0.7388264946398688, 3.820253663542008, 22.12707526145455], 
                        6 : [0.7990090430354084, 4.270479582719364, 28.39512917847429], 
                        7 : [0.7915270359562037, 3.818839364562389, 32.37868770576421], 
                        8 : [0.7810707981181267, 3.966319787357838, 29.73224806913421], 
                        9 : [0.7726719686999383, 4.375342101178528, 33.99995035642857], 
                        10 : [0.7633988255859906, 3.812921992989591, 27.22897521536183], 
                        11 : [0.7924865129668931, 3.023088469747906, 17.43522464119394], 
                        12 : [0.8427815907340088, 2.469769334175334, 17.27491194234928] }, 
                  90 : { 1 : [0.8000167721092015, 2.14318791211679, 13.31216664046398], 
                        2 : [0.7690677916280287, 2.324413981979211, 18.71999503253297], 
                        3 : [0.7460658710841159, 2.260919662774048, 15.69862226267024], 
                        4 : [0.6921207542281484, 2.9470901968045, 17.60058777038659], 
                        5 : [0.7492732558019454, 3.707073206699545, 22.41413253022884], 
                        6 : [0.7938591214252788, 4.153725906418162, 26.69546949994165], 
                        7 : [0.7774770936276094, 3.858074782743785, 31.49399315078537], 
                        8 : [0.7983023128638006, 3.864352945540093, 29.10296708948593], 
                        9 : [0.7482836219102301, 4.070264208439249, 33.78507833119324], 
                        10 : [0.7364700924974487, 3.476184201781172, 25.75918298662909], 
                        11 : [0.7866626533606568, 2.842368919525622, 16.72958233635238], 
                        12 : [0.821163438470264, 2.316757680025526, 15.57590090683073] }, 
                  91 : { 1 : [0.8076134399548054, 2.182787235848688, 13.33399734748767], 
                        2 : [0.7682321912711095, 2.391924702020807, 18.64044530556062], 
                        3 : [0.7432137552062678, 2.333579214874465, 15.69989539733605], 
                        4 : [0.6889772010887557, 3.003579319493803, 17.63322687246677], 
                        5 : [0.7457408381443503, 3.743860948473011, 22.14159109332446], 
                        6 : [0.8017530964133073, 4.21633623741607, 27.09301453330406], 
                        7 : [0.7839064806249504, 3.888066325164368, 31.46009654478], 
                        8 : [0.7965492815412039, 3.941048358639455, 29.653395924748], 
                        9 : [0.7580160135876725, 4.251905458161431, 34.03292428672906], 
                        10 : [0.7446908421301281, 3.625139412547574, 25.89072023947261], 
                        11 : [0.785164376111959, 2.893443394969944, 16.61001891963313], 
                        12 : [0.8259677088002144, 2.327282916181283, 15.72434878933955] }, 
                  92 : { 1 : [0.8072771612587862, 2.211260254047167, 13.50588495142883], 
                        2 : [0.7572011882603799, 2.425918083789198, 18.79039691490872], 
                        3 : [0.7251236581483079, 2.344230593504169, 15.80117337098888], 
                        4 : [0.6705475198870576, 3.053078654185128, 17.74959655616612], 
                        5 : [0.7481991766770516, 3.852427330655837, 22.29112920071683], 
                        6 : [0.804570942721167, 4.285062853572393, 27.57033509787913], 
                        7 : [0.7893619071354879, 3.86269455521905, 31.51552680401465], 
                        8 : [0.794354284146118, 4.018163746012265, 29.92422082756089], 
                        9 : [0.7678060490316656, 4.367455180057161, 34.19049604671982], 
                        10 : [0.7545349044013163, 3.72304034875274, 26.41375369445096], 
                        11 : [0.7888696407632731, 2.976870048164801, 17.01742571183996], 
                        12 : [0.8327690127287897, 2.403423813846727, 16.33888443990801] }, 
                  93 : { 1 : [0.8000051238327457, 2.179002169728824, 13.6222596043499], 
                        2 : [0.7515349070564642, 2.4220166872315, 18.72533766105897], 
                        3 : [0.7139454176097071, 2.311328486534755, 15.58582993971233], 
                        4 : [0.6579571080366974, 3.030835408270147, 17.54655987186577], 
                        5 : [0.7447728586551051, 3.878016564423026, 22.11202229301203], 
                        6 : [0.8045131668534692, 4.342634263540445, 28.18826194192494], 
                        7 : [0.7900878838593578, 3.916324523978697, 32.34210776286599], 
                        8 : [0.7889267798723018, 4.042752139827557, 30.25792225769403], 
                        9 : [0.7707581666516441, 4.446397139526848, 34.23986061667448], 
                        10 : [0.7590745649795877, 3.792641943114559, 26.85206115272174], 
                        11 : [0.7884786560510071, 3.000952571540409, 17.33375209456095], 
                        12 : [0.8333875062809025, 2.44118708753666, 16.87001605253874] }, 
                  94 : { 1 : [0.7962595817070243, 2.185832433869528, 13.8502275205841], 
                        2 : [0.7483199210799516, 2.440524387525175, 18.80471466079415], 
                        3 : [0.7091033617819636, 2.306944562843963, 15.63851568333433], 
                        4 : [0.6547105746941307, 3.012641017578044, 17.73720410156642], 
                        5 : [0.7435744946835149, 3.908692147743784, 22.38359526131678], 
                        6 : [0.8034069049391407, 4.387285680239302, 28.514003364418], 
                        7 : [0.7867678316703561, 3.868503414997108, 32.28632720229565], 
                        8 : [0.7885297194428681, 3.937013784366322, 30.27429558484679], 
                        9 : [0.7700467083832466, 4.444688920983261, 33.98572933721817], 
                        10 : [0.7616534257206257, 3.821831023173017, 27.36716836919526], 
                        11 : [0.7866525486893331, 3.0412465017584, 17.73594464451151], 
                        12 : [0.8313735365150371, 2.497702958606159, 17.37182576503561] }, 
                  104 : { 1 : [0.808652052087771, 2.211888442367785, 13.1238496135575], 
                        2 : [0.7692354966047542, 2.443893804888321, 18.48196579874531], 
                        3 : [0.7499140141393426, 2.349057910418289, 15.28981445619211], 
                        4 : [0.7047801666720898, 2.892618336141563, 17.0231814241333], 
                        5 : [0.7398210591749397, 3.565335816035577, 21.57286958421616], 
                        6 : [0.7902398483901273, 4.258414904532167, 25.9990746800717], 
                        7 : [0.7880421495486282, 3.953793727788796, 31.5027442181669], 
                        8 : [0.7986051074973989, 3.81719944127008, 29.48337570096329], 
                        9 : [0.7559474474204145, 4.094685931196071, 32.95972540363511], 
                        10 : [0.7440508739556029, 3.450442666030249, 24.83819491800177], 
                        11 : [0.7808591997019781, 2.811091993719468, 16.12490027833872], 
                        12 : [0.8260210101772866, 2.310784481222947, 15.44965009038833] }, 
                  105 : { 1 : [0.8062548903854916, 2.222846083817361, 13.2544478628781], 
                        2 : [0.7564560360989117, 2.465025948336976, 18.50580067765703], 
                        3 : [0.7408646036862253, 2.374155801911017, 15.32641025180779], 
                        4 : [0.69247624415835, 2.977399899456173, 17.15912386306651], 
                        5 : [0.742175908226179, 3.653607271637953, 21.52421613594825], 
                        6 : [0.7929191280499998, 4.324568074920997, 25.86104921633319], 
                        7 : [0.7887447988940747, 3.894928024625328, 30.43632535315137], 
                        8 : [0.7995171692537729, 3.980799692188169, 30.03859094529753], 
                        9 : [0.7587426482930001, 4.359674930547313, 33.5545768743955], 
                        10 : [0.7419036688271093, 3.654148163170113, 25.1906668098485], 
                        11 : [0.7813896708945757, 2.864845187402948, 16.42968114491524], 
                        12 : [0.8265660203214809, 2.336109311779593, 15.69679127721293] }, 
                  106 : { 1 : [0.8038057166996767, 2.222688127466884, 13.38499952585265], 
                        2 : [0.7528420732721821, 2.469163204621984, 18.42746103263], 
                        3 : [0.7322387574202792, 2.380007186976318, 15.18228073118347], 
                        4 : [0.6852644010454031, 2.99618397391905, 17.11216585338942], 
                        5 : [0.7474183888301456, 3.748624661566822, 21.70393875243458], 
                        6 : [0.7943218617037251, 4.17521601519196, 25.52320991729205], 
                        7 : [0.7898311236202179, 3.927429755094339, 30.62854423661862], 
                        8 : [0.7987362524284325, 4.061027251273003, 30.3698084885171], 
                        9 : [0.7609329018409984, 4.434564696876865, 33.57542268567525], 
                        10 : [0.7460130346961619, 3.716977064222859, 25.43136543217975], 
                        11 : [0.7835008724326096, 2.891498035848695, 16.68370409423839], 
                        12 : [0.8285506955826625, 2.364665311770145, 16.16258893953358] }, 
                  107 : { 1 : [0.8013066631282227, 2.218578958907117, 13.60191662334971], 
                        2 : [0.7518096290655363, 2.505126008844941, 18.7348653172873], 
                        3 : [0.7264878186349699, 2.405049317826158, 15.43550366412887], 
                        4 : [0.6843952240719845, 3.12321038207095, 17.68405220106467], 
                        5 : [0.7492490147227528, 3.850526023288276, 21.91775816490205], 
                        6 : [0.79549584385797, 4.219825656261029, 26.50704383402606], 
                        7 : [0.7847009181801233, 3.900513871393381, 30.89661826995284], 
                        8 : [0.7945525050429071, 3.949580907066944, 30.36445389835164], 
                        9 : [0.7632390014920329, 4.519378619187575, 33.87802504109473], 
                        10 : [0.7507009101930882, 3.731017481042959, 26.01538266061762], 
                        11 : [0.7821965565366411, 2.889340513738941, 17.01244264185019], 
                        12 : [0.8267994077815507, 2.375674118741602, 16.49463520269576] }, 
                  108 : { 1 : [0.7968046176351146, 2.219156515437642, 13.85964518036797], 
                        2 : [0.7454725559607657, 2.513871244110738, 18.73292188228001], 
                        3 : [0.7188489530552907, 2.406252176686934, 15.36709816673127], 
                        4 : [0.6785181120994401, 3.07867290132007, 17.69792196438166], 
                        5 : [0.7488993207338985, 3.840367662410096, 21.95282752264283], 
                        6 : [0.7947973635247586, 4.122939114435345, 26.43349855284487], 
                        7 : [0.781316423711956, 3.869344312104259, 30.92370421978736], 
                        8 : [0.7902909169145635, 3.996347055503579, 30.47434913020496], 
                        9 : [0.7636861775536121, 4.604232586931256, 34.08477473020638], 
                        10 : [0.7505613887075184, 3.733983935084054, 26.38056254796123], 
                        11 : [0.7777687988507541, 2.865896771979865, 17.38291249225693], 
                        12 : [0.8240573849577995, 2.411844040906606, 16.94888548135197] }, 
                  120 : { 1 : [0.8061999339412895, 2.257810756018129, 13.32563167923308], 
                        2 : [0.7582799822271878, 2.529457845063015, 18.67780291215097], 
                        3 : [0.7426331654154485, 2.437955665243558, 15.23983490842402], 
                        4 : [0.7060019486041035, 3.015152591203155, 17.41609397278927], 
                        5 : [0.746116782390968, 3.720568714934509, 21.48770203080091], 
                        6 : [0.7918563116093176, 4.189654659161865, 25.5027968332205], 
                        7 : [0.7877884922314464, 3.98955023407426, 30.6431386311101], 
                        8 : [0.798268983866465, 4.047922281306787, 30.33805062071069], 
                        9 : [0.7616592047832965, 4.340089859236392, 33.07065152342606], 
                        10 : [0.744042550753425, 3.546133315926196, 24.63021190730436], 
                        11 : [0.7782472700450068, 2.829547606757543, 16.5783710905412], 
                        12 : [0.824190719520844, 2.333165543451646, 15.99055837208688] }, 
                  121 : { 1 : [0.8030531461403007, 2.245626545176087, 13.47566891139916], 
                        2 : [0.7525036601016191, 2.53646232887953, 18.62155374279527], 
                        3 : [0.7346997554869086, 2.447539714965436, 15.09803118028952], 
                        4 : [0.7035285988638474, 3.011117414885703, 17.46103741534266], 
                        5 : [0.7493886427216545, 3.732271964825487, 21.44296214554745], 
                        6 : [0.7965135028517343, 4.130305247235431, 25.68823757549318], 
                        7 : [0.7841636704433667, 3.943380417586207, 30.34585979231273], 
                        8 : [0.7944380659652389, 4.120359640814949, 30.60145985827328], 
                        9 : [0.7650988255270119, 4.462360747543096, 33.44158963313533], 
                        10 : [0.7461950801827156, 3.555814172240196, 24.99156500736504], 
                        11 : [0.7770501261604458, 2.803256214826171, 16.8269465766276], 
                        12 : [0.821064361558922, 2.339436197795051, 16.23802302227255] }, 
                  122 : { 1 : [0.796718102374421, 2.246843342056425, 13.73861642679159], 
                        2 : [0.7429348151143197, 2.530219204922469, 18.68112707655517], 
                        3 : [0.7279728695414753, 2.44033519979855, 15.15862928575196], 
                        4 : [0.6966999212407063, 3.019268907149705, 17.58626686910359], 
                        5 : [0.7460658552925605, 3.772496050228466, 21.59216562592636], 
                        6 : [0.7931445193168154, 4.125568101955568, 25.93603903626059], 
                        7 : [0.7829380867085498, 3.959680745309167, 30.80519294911851], 
                        8 : [0.7926167659483805, 4.167384765920074, 30.95574786595588], 
                        9 : [0.7619688099790457, 4.644027908378227, 33.97854579434324], 
                        10 : [0.7435738310058198, 3.682784134465005, 25.76270023553272], 
                        11 : [0.7724716566699763, 2.80376700961096, 17.21346835086893], 
                        12 : [0.8158173803089175, 2.360898137935919, 16.65102744898383] }, 
                  123 : { 1 : [0.7998474309913679, 2.257965511075925, 13.91603706146725], 
                        2 : [0.7440536222850924, 2.585896902332156, 18.90596838189133], 
                        3 : [0.7323601050140536, 2.449498412138466, 15.40907806651193], 
                        4 : [0.6916347114629617, 2.981168500177299, 17.90281577762277], 
                        5 : [0.732485539890838, 3.660953870104512, 21.22949063565664], 
                        6 : [0.7896378537986073, 3.966461508798377, 25.57402460503276], 
                        7 : [0.787863437134998, 3.771074744695771, 30.3145044779576], 
                        8 : [0.7907535064472843, 4.062147115969991, 30.61104696920145], 
                        9 : [0.7607468258038866, 4.719237874829728, 34.02418176794378], 
                        10 : [0.7415976735214873, 3.698960787693421, 26.05832790127415], 
                        11 : [0.7746271432041987, 2.815931535115087, 17.50521239625803], 
                        12 : [0.8141851877378372, 2.368251986465249, 17.02059188930595] }, 
                  137 : { 1 : [0.8171247632355431, 2.318040888847918, 14.21253889611431], 
                        2 : [0.762405509433762, 2.619359284993899, 19.14531422340252], 
                        3 : [0.7381990334596102, 2.469195483710216, 15.21220167475202], 
                        4 : [0.704084598115529, 3.080028040734885, 17.81731652097625], 
                        5 : [0.7575462198532544, 3.921313655808501, 21.8597576316746], 
                        6 : [0.805342883942438, 4.137312911843377, 25.70713136879749], 
                        7 : [0.799770660380592, 4.036678930273385, 30.8334888491203], 
                        8 : [0.79425209749898, 4.35721461786401, 31.42591647752172], 
                        9 : [0.7595615857390747, 4.827290769791735, 33.55826179599203], 
                        10 : [0.7362705048222786, 3.743795807287411, 25.55061477248347], 
                        11 : [0.7675627258334837, 2.759451159620647, 17.38368648876019], 
                        12 : [0.8288708491286445, 2.409523294312609, 17.17976467085182] }, 
                        }, # projection period 2
               { 62 : { 1 : [0.8255132850900048, 2.189404401799186, 14.90498913761504], 
                        2 : [0.774181697927868, 2.288870563621852, 18.0145854240199], 
                        3 : [0.7566652307541536, 2.243236734381873, 14.80698107553986], 
                        4 : [0.6993443917563246, 2.9553912645739, 17.35069944285147], 
                        5 : [0.7357902245927376, 3.567605359661863, 21.94438690314405], 
                        6 : [0.8023641005281699, 4.587579792468418, 32.79527165298579], 
                        7 : [0.7730598423339351, 3.506253644485491, 32.08877327025271], 
                        8 : [0.7859274119532624, 3.848660882646993, 31.61699718743825], 
                        9 : [0.7386788769109803, 4.096360150790531, 34.08469558366062], 
                        10 : [0.7459185251765718, 3.408447499884769, 27.17410600987734], 
                        11 : [0.8022227963545064, 2.82640012435491, 16.9928932586042], 
                        12 : [0.8304028464926475, 2.235877566079242, 14.40506692707249] }, 
                  63 : { 1 : [0.8214601771249348, 2.146150218126202, 14.91377839832792], 
                        2 : [0.7712242470709754, 2.26866610359864, 17.95960231184592], 
                        3 : [0.7501269481178449, 2.220874951644894, 14.93136797321645], 
                        4 : [0.6966191533042839, 3.001274550462846, 17.72105040994664], 
                        5 : [0.7453515376702996, 3.671496159295622, 22.44875376769234], 
                        6 : [0.8105020268702702, 4.578620203124807, 32.8287116771888], 
                        7 : [0.7954909217057595, 3.659766413548384, 32.83649453195302], 
                        8 : [0.7873097101954202, 3.97673630676111, 31.5100827642259], 
                        9 : [0.7508022494184645, 4.252155001376666, 34.06610233254627], 
                        10 : [0.7504188551274499, 3.519238726575273, 27.58871981702315], 
                        11 : [0.8027254337599903, 2.885988417658574, 17.24999153853593], 
                        12 : [0.833080353425344, 2.288590203505852, 14.76512326790856] }, 
                  64 : { 1 : [0.8318828996811867, 2.132384773925472, 15.29304895484609], 
                        2 : [0.7675449555167094, 2.246374808616031, 18.17975278881589], 
                        3 : [0.7461452092639005, 2.1968735869425, 15.44144315600563], 
                        4 : [0.6820903073782294, 2.904056588953928, 17.65661485116572], 
                        5 : [0.7448510256167155, 3.580431549806096, 22.38012893479108], 
                        6 : [0.8099697414211712, 4.356540549082206, 32.82329280193305], 
                        7 : [0.8079096436160332, 3.816302754970164, 35.36459320105475], 
                        8 : [0.7855075545558943, 4.067915637802257, 32.1009386081454], 
                        9 : [0.7585244041296351, 4.280073141145055, 34.34493184726768], 
                        10 : [0.7611417715202679, 3.602924948744494, 28.82251399103374], 
                        11 : [0.8063946122373422, 2.899475542268942, 17.76283697667774], 
                        12 : [0.8432422615094124, 2.303970389247976, 15.44683509444999] }, 
                  76 : { 1 : [0.8193783114497368, 2.194010386266562, 15.06392338477393], 
                        2 : [0.7692126525076746, 2.321655638820868, 18.66704652169963], 
                        3 : [0.7558764949869555, 2.200115876772545, 14.96495524938003], 
                        4 : [0.7071097970452752, 2.93930642452451, 17.59012995955489], 
                        5 : [0.7431473035016614, 3.588645659472057, 22.27292634318665], 
                        6 : [0.8092343619607612, 4.517798239614506, 32.34054610994905], 
                        7 : [0.7776782376002619, 3.688319543684655, 32.01662908542261], 
                        8 : [0.7928159283235258, 3.824016101507094, 31.27300318691591], 
                        9 : [0.7413095473372644, 4.145333346099616, 34.03305044247393], 
                        10 : [0.7373941612787239, 3.458039836862086, 27.17126703878974], 
                        11 : [0.7957831373978026, 2.814974534351173, 17.04246107189559], 
                        12 : [0.8258045467637065, 2.25447584088595, 14.66238995465235] }, 
                  77 : { 1 : [0.8264410534323203, 2.143457266174898, 14.98152787017819], 
                        2 : [0.7678330942325923, 2.26867458646887, 18.17924199409517], 
                        3 : [0.751222174502546, 2.216671415177292, 14.89455202612077], 
                        4 : [0.701319300881669, 3.012518970872062, 17.57556941128977], 
                        5 : [0.7466757460493575, 3.679399367480283, 22.30417287703628], 
                        6 : [0.8138909423099986, 4.441424267904327, 31.9076763767669], 
                        7 : [0.7884875583116817, 3.725900834169445, 32.54206753557615], 
                        8 : [0.7915751433476431, 3.921066547219175, 31.27158395799163], 
                        9 : [0.751241723003332, 4.285171821051115, 34.25799433278596], 
                        10 : [0.7417978015999018, 3.587048077440078, 27.53466858854732], 
                        11 : [0.797919927752677, 2.861942265147031, 17.21325729139631], 
                        12 : [0.8310390893897944, 2.264612201747208, 14.75590365258797] }, 
                  78 : { 1 : [0.8232982998711186, 2.108274936248841, 15.12677747102759], 
                        2 : [0.7606831178870791, 2.231680856505928, 18.30848662461852], 
                        3 : [0.7396264029067467, 2.20972024243971, 15.05074224988664], 
                        4 : [0.6849359457475167, 2.98824229745923, 17.60589181687392], 
                        5 : [0.7440072876747076, 3.69653424189048, 22.31542587283658], 
                        6 : [0.8082239860345015, 4.408454785310849, 31.59494378176624], 
                        7 : [0.794527237502324, 3.737895120767729, 33.26060492507491], 
                        8 : [0.7831790236008652, 3.983638271832553, 31.13044002296308], 
                        9 : [0.7576580784944809, 4.394527680416167, 34.65473211493083], 
                        10 : [0.7483739665282855, 3.689234328080226, 28.59856430718348], 
                        11 : [0.7954266995254466, 2.918826210329867, 17.69264015565797], 
                        12 : [0.8325429910219574, 2.300302443342395, 15.37178177212296] }, 
                  79 : { 1 : [0.8312576246421882, 2.20079727862067, 15.59196867170672], 
                        2 : [0.7474245341527407, 2.310496558499159, 18.73323250232703], 
                        3 : [0.7224696301217866, 2.241270232677003, 15.54998429513825], 
                        4 : [0.6535640653355357, 2.878836577855985, 17.50175011536729], 
                        5 : [0.7357230483399562, 3.707399723371625, 22.03505507361889], 
                        6 : [0.7993285192650148, 4.431307272274174, 31.00947752825089], 
                        7 : [0.795372747244212, 3.780528710101416, 33.63237404130514], 
                        8 : [0.7801192725630708, 4.014000336742104, 31.4982181109632], 
                        9 : [0.7717232780415694, 4.478199013871355, 35.40682377747514], 
                        10 : [0.7709907044081913, 3.870424873505571, 30.15069247740298], 
                        11 : [0.8030641371567859, 2.998885663715426, 18.00279176967454], 
                        12 : [0.840330263091005, 2.392214054848149, 15.87082965778546] }, 
                  90 : { 1 : [0.8235905519255363, 2.178594778791779, 15.12398607506825], 
                        2 : [0.7672030646890092, 2.293199392961295, 18.64147852381936], 
                        3 : [0.752502259467244, 2.194188343166523, 14.76912894642205], 
                        4 : [0.709274194002593, 2.962250782674483, 17.50385477893236], 
                        5 : [0.7433696732015591, 3.62597696944002, 22.11726114713927], 
                        6 : [0.8078194912698963, 4.398109635437084, 31.143717574701], 
                        7 : [0.7747666744043297, 3.714519275322809, 31.57447780736004], 
                        8 : [0.794212632472115, 3.886246071377219, 31.14414108249513], 
                        9 : [0.7433702335400809, 4.20557557531797, 34.24320646887033], 
                        10 : [0.732760545170355, 3.478549783839751, 26.96870735411673], 
                        11 : [0.7927323323169196, 2.816860626039366, 17.11803396415556], 
                        12 : [0.8253025458731539, 2.252691080677172, 14.79911051131585] }, 
                  91 : { 1 : [0.8292949576831788, 2.205448902679989, 15.06537702148279], 
                        2 : [0.764160788901386, 2.35705570795133, 18.46776768899204], 
                        3 : [0.7503695083721359, 2.265417797230276, 14.88074759968984], 
                        4 : [0.7082286209047357, 3.004138651661846, 17.5605304079436], 
                        5 : [0.7448670820585033, 3.699820342604526, 21.96554036887101], 
                        6 : [0.8142143314832178, 4.447087275950424, 31.44733150504731], 
                        7 : [0.7840023638175248, 3.819645057480563, 32.30282272248891], 
                        8 : [0.7910859282088322, 3.92866461094798, 31.06702177757926], 
                        9 : [0.7567678663313248, 4.413770447431944, 35.13904166717321], 
                        10 : [0.7414264601091968, 3.596759076066745, 27.46419536412616], 
                        11 : [0.7957930490892052, 2.892729652323289, 17.28330842114502], 
                        12 : [0.8292822691866304, 2.290064098790666, 14.83977618086506] }, 
                  92 : { 1 : [0.8325567916073743, 2.231305236620954, 15.20038900083332], 
                        2 : [0.7495474386810013, 2.363288358100982, 18.5333425173483], 
                        3 : [0.7333099413022216, 2.276021826481229, 15.11888254540856], 
                        4 : [0.6852362891338711, 2.97756669033426, 17.55144989216279], 
                        5 : [0.7459368375629083, 3.764723756315357, 22.10748377012975], 
                        6 : [0.8111045713470245, 4.49865973146283, 30.94715905342674], 
                        7 : [0.7909296247367055, 3.797016087489625, 32.43475804111694], 
                        8 : [0.790408260783457, 4.031079035128244, 31.43101940924209], 
                        9 : [0.7668401214529177, 4.475627229943753, 35.48249640828975], 
                        10 : [0.7567396349427585, 3.761092844788104, 28.55642167766647], 
                        11 : [0.7972968399814244, 2.930565738458463, 17.55363230047757], 
                        12 : [0.8318645910730018, 2.359358632985141, 15.18741805261133] }, 
                  93 : { 1 : [0.8277250048411744, 2.216322760953558, 15.32441397844064], 
                        2 : [0.7408579061158398, 2.352439096411, 18.38690341199927], 
                        3 : [0.7272460357314544, 2.268190837402897, 15.14541164211347], 
                        4 : [0.6727666021509485, 2.949104941700905, 17.38902475400621], 
                        5 : [0.7445727268717343, 3.78468067207859, 22.16782830481403], 
                        6 : [0.807221193858581, 4.50896503922228, 31.03977930954125], 
                        7 : [0.7974649604580855, 3.917824095514774, 33.99358890001537], 
                        8 : [0.7851977223320976, 4.053359737785431, 31.73959869304403], 
                        9 : [0.7717318687886447, 4.560576576704491, 35.92642957493268], 
                        10 : [0.764813708143858, 3.857875838487475, 29.42453971046541], 
                        11 : [0.7970644339377043, 2.985169943119766, 17.82046614340397], 
                        12 : [0.8324945699268449, 2.398376068030567, 15.6166231076258] }, 
                  94 : { 1 : [0.8226622365717698, 2.207537624950943, 15.42655832969851], 
                        2 : [0.7386160775189342, 2.371633734797462, 18.60783364867624], 
                        3 : [0.7228563796409333, 2.284606229550694, 15.25934809263356], 
                        4 : [0.6681140511799745, 2.928734728512445, 17.46292191710869], 
                        5 : [0.7433279467575895, 3.817679669735422, 22.41878988032472], 
                        6 : [0.8046518820836761, 4.515181581895873, 31.29862740984359], 
                        7 : [0.7967631504057743, 3.901177441786098, 34.40847076391753], 
                        8 : [0.787186577105838, 4.024111544475804, 31.77815588162059], 
                        9 : [0.7745300999340134, 4.586610425102351, 36.23073293221586], 
                        10 : [0.7692309473877275, 3.891233787047884, 30.18902382847284], 
                        11 : [0.7954606423682721, 3.019143419625557, 18.20353331977667], 
                        12 : [0.8320910422933604, 2.450578105814711, 16.03168222176996] }, 
                  104 : { 1 : [0.831532156056464, 2.236981500596572, 14.97109754686799], 
                        2 : [0.7621810600654175, 2.391533238267182, 18.14588537535684], 
                        3 : [0.7545418758025219, 2.267422592442055, 14.3729632334169], 
                        4 : [0.7244475406713926, 2.922610202827407, 17.07453451620925], 
                        5 : [0.7379745906710484, 3.496925934647524, 21.30747710722208], 
                        6 : [0.8034982180474803, 4.430266245194443, 30.44874324875471], 
                        7 : [0.7830802372991945, 3.834930908695027, 31.61669489738848], 
                        8 : [0.7966129123830147, 3.855316417200795, 30.89820875805562], 
                        9 : [0.7523615589711017, 4.254767398340203, 33.67343422223319], 
                        10 : [0.7437849769812576, 3.449314665212035, 26.28250890422809], 
                        11 : [0.7930714572250273, 2.813671044007171, 16.78413597354557], 
                        12 : [0.8292614381118868, 2.271605020427655, 14.78461863470362] }, 
                  105 : { 1 : [0.8311173911853195, 2.254708508239687, 15.01079251358665], 
                        2 : [0.7496910029283999, 2.422938975753909, 18.16991714318037], 
                        3 : [0.7437385658636222, 2.28613161337985, 14.39915159786734], 
                        4 : [0.706553073855079, 2.936112894809114, 16.99006488297105], 
                        5 : [0.7380111620865276, 3.566476975760328, 21.19799524327876], 
                        6 : [0.80266081142364, 4.478450313548838, 29.68753855237378], 
                        7 : [0.7897816911163177, 3.83612033903501, 31.0753858769496], 
                        8 : [0.7953895997945774, 4.00725581080155, 31.18103285376731], 
                        9 : [0.7567928799544021, 4.500329932239092, 34.52724318498562], 
                        10 : [0.7456727590291311, 3.666186066641931, 27.05071541085628], 
                        11 : [0.7918970740827281, 2.852419157626912, 16.94784755051858], 
                        12 : [0.8277070170266323, 2.301493838577005, 15.00120288496346] }, 
                  106 : { 1 : [0.8285328414876958, 2.254326072023491, 15.11478645347353], 
                        2 : [0.7426634451492965, 2.424934953917373, 18.02797693509044], 
                        3 : [0.7367307404217697, 2.292666614804262, 14.36370996095274], 
                        4 : [0.7015670189445941, 2.96798923112575, 17.03801415293221], 
                        5 : [0.7431434294918418, 3.64680393359456, 21.4707574664219], 
                        6 : [0.8016226733939663, 4.313724321431093, 28.88886987133027], 
                        7 : [0.7929789139555381, 3.899448791983363, 31.63746774463864], 
                        8 : [0.793331970399804, 4.064499935215407, 31.30617715554434], 
                        9 : [0.7617436259287564, 4.582915591884362, 34.87717329789604], 
                        10 : [0.7503881864674006, 3.732709853469284, 27.46984872021715], 
                        11 : [0.7912050959519562, 2.879922366165504, 17.08812044537888], 
                        12 : [0.8254211484597066, 2.320961993005156, 15.07428708114072] }, 
                  107 : { 1 : [0.826651310746932, 2.242750972041826, 15.298657924255], 
                        2 : [0.7421966480742229, 2.443318710981641, 18.37680749951508], 
                        3 : [0.7337407237103162, 2.331366217190203, 14.74661619948], 
                        4 : [0.6958567040273428, 3.021754025314262, 17.41916660085822], 
                        5 : [0.7470687756900322, 3.766144006012246, 21.9879375970407], 
                        6 : [0.7996042081216844, 4.340168928523703, 29.43572435171713], 
                        7 : [0.7942378192194294, 3.913524866897706, 32.71325501417499], 
                        8 : [0.7889273169590242, 3.968391222620445, 31.2095679458036], 
                        9 : [0.7628666799656917, 4.645659598684358, 35.21222567900525], 
                        10 : [0.7530851763159572, 3.781459395870515, 28.19950861899328], 
                        11 : [0.7929192511599289, 2.877120808285506, 17.50154663871261], 
                        12 : [0.827547215832513, 2.349814297831697, 15.43317630362174] }, 
                  108 : { 1 : [0.8193473280850854, 2.242492116426049, 15.31399758065321], 
                        2 : [0.7354903074383289, 2.453872160870272, 18.502331226711], 
                        3 : [0.7290744238430629, 2.334969732060953, 14.8737304712772], 
                        4 : [0.6915719127283085, 3.001019771269179, 17.52115954652452], 
                        5 : [0.7477919477285817, 3.756213293055487, 21.96351776673478], 
                        6 : [0.7951552274162721, 4.181354812502653, 28.94211158967679], 
                        7 : [0.7949121561039814, 3.939286846873979, 33.33895425021831], 
                        8 : [0.7852254797947567, 4.042898127938887, 31.36437975241996], 
                        9 : [0.7668268123557199, 4.73689427886656, 35.80472043184547], 
                        10 : [0.7541449705375208, 3.793587996488075, 28.69082646758412], 
                        11 : [0.788039025004719, 2.878760295237329, 17.83026681536714], 
                        12 : [0.824641814079654, 2.366908876159104, 15.76097713893363] }, 
                  120 : { 1 : [0.8324003361888229, 2.270642018251769, 15.13485063242274], 
                        2 : [0.7476786241956828, 2.483526686799888, 18.2181150780148], 
                        3 : [0.7447126695632655, 2.351304852970338, 14.37190816358128], 
                        4 : [0.7174318056630852, 2.966514910707544, 17.18240596787478], 
                        5 : [0.7459936652792605, 3.651613511018168, 21.56651777201366], 
                        6 : [0.7978384898230941, 4.286421523836026, 28.63288816855878], 
                        7 : [0.7909154558618164, 3.944518550523887, 31.61816382775135], 
                        8 : [0.7946159735740358, 4.084732396086002, 31.46022315688311], 
                        9 : [0.7601018216095652, 4.459422009338565, 34.11408725385405], 
                        10 : [0.7502259673826843, 3.593496721315353, 26.53305648564815], 
                        11 : [0.7902085049668538, 2.813085549252051, 17.03491676302243], 
                        12 : [0.8233923830635606, 2.304321858008241, 15.06243702298274] }, 
                  121 : { 1 : [0.8261187648998922, 2.266943118218497, 15.07295783255787], 
                        2 : [0.7416753923837652, 2.469465497903348, 18.15595849532256], 
                        3 : [0.7401645004019614, 2.353292704382747, 14.39471436555826], 
                        4 : [0.7149662415366759, 2.964353609044079, 17.2429505547863], 
                        5 : [0.7479197044673985, 3.63719113285341, 21.53439294104569], 
                        6 : [0.7972978724317724, 4.163323686290577, 28.24595163660625], 
                        7 : [0.7944115479168913, 3.950057069798409, 32.31878747530606], 
                        8 : [0.7911220556309507, 4.149239852563773, 31.53946873814428], 
                        9 : [0.7634568819497787, 4.545634002998269, 34.44673196510538], 
                        10 : [0.7509175784024218, 3.617913575544893, 27.01412250155878], 
                        11 : [0.7878097223067916, 2.794540731546465, 17.23345851604248], 
                        12 : [0.8221001970167177, 2.307919023854964, 15.27280156953973] }, 
                  122 : { 1 : [0.8191809254419897, 2.267145015076996, 15.1943637399809], 
                        2 : [0.7330006779427379, 2.46727832797936, 18.29108113281461], 
                        3 : [0.7330422486865688, 2.357659732848838, 14.49657327886209], 
                        4 : [0.7084753354614528, 2.974413716562055, 17.39090508290499], 
                        5 : [0.7448945759572704, 3.684653379386636, 21.6764360895052], 
                        6 : [0.7931638296925159, 4.158915747422073, 28.43299476919002], 
                        7 : [0.7952229026758522, 3.978590059228347, 32.99070152326777], 
                        8 : [0.7889770079380816, 4.198652805612587, 31.96932835267469], 
                        9 : [0.7637587732687334, 4.743518235900807, 35.4448300570953], 
                        10 : [0.7463593195787583, 3.714806350834724, 27.78803313896396], 
                        11 : [0.7841346481201537, 2.792569240346166, 17.66246110390477], 
                        12 : [0.8184663350090003, 2.315606595352981, 15.65131106017529] }, 
                  123 : { 1 : [0.8202091753462852, 2.279284551227284, 15.16245973828898], 
                        2 : [0.7334320300171674, 2.502441904345926, 18.52425014373127], 
                        3 : [0.7351029742054159, 2.362426640663652, 14.78576640623117], 
                        4 : [0.7007787308291654, 2.970790962820285, 17.6745784864387], 
                        5 : [0.7358619740505862, 3.592710246677035, 21.56050092042022], 
                        6 : [0.7858475873901672, 3.974908457999065, 27.58054267395101], 
                        7 : [0.7973135489112625, 3.729661685662887, 32.06237537681301], 
                        8 : [0.7923635280201773, 4.18933489141199, 32.1769077383675], 
                        9 : [0.7658422671102433, 4.855631682046386, 35.91376740934021], 
                        10 : [0.7442686805833063, 3.720411414854301, 27.99498382956719], 
                        11 : [0.7833603016659753, 2.808936542267835, 17.87941155104119], 
                        12 : [0.8152584136651254, 2.327119549446307, 15.89984078508446] }, 
                  137 : { 1 : [0.8295189653976354, 2.314494630981724, 14.97242616803921], 
                        2 : [0.7471645070210563, 2.521395359566461, 18.6411921060169], 
                        3 : [0.7382561853268874, 2.38306341992458, 14.39168639682572], 
                        4 : [0.7114682444242606, 3.057713792524124, 17.50841813291339], 
                        5 : [0.7578009572018027, 3.861488572797991, 22.14142595601064], 
                        6 : [0.8039543334869315, 4.185236466245065, 28.08438635849778], 
                        7 : [0.8088687287242592, 3.969167538582909, 32.67021276114245], 
                        8 : [0.7950766357390344, 4.444078497941653, 32.89504811104767], 
                        9 : [0.7663142626590863, 4.988204108620057, 35.60471971957632], 
                        10 : [0.7335999096728576, 3.715794664802027, 27.03392602292832], 
                        11 : [0.7792218409356169, 2.779733180217884, 17.92943555786881], 
                        12 : [0.8296739603354618, 2.335841228858982, 16.34598582924115] }, 
                  }, # projection period 3
]
"""List of projection period dictionaries for definining mixed exponential
distributions. Each projection period dictionary contains a grid id dictionary
which has grid ids as keys and dictionary of monthly distribution parameters
as values with integer month as keys. The distribution parameters are ordered
as 0 - alpha, 1 - mu1, 2 - mu2.
"""
GRID_AREA_WT = { 62 : 0.00975665681587, 
                  63 : 0.06984963803800, 
                  64 : 0.02082930230072, 
                  76 : 0.04809232194328, 
                  77 : 0.08996761256735, 
                  78 : 0.07587308637403, 
                  79 : 0.00856966746339, 
                  90 : 0.05037034481002, 
                  91 : 0.09141978145391, 
                  92 : 0.09133421001522, 
                  93 : 0.07894275139521, 
                  94 : 0.00987122962317, 
                  104 : 0.00563905995157, 
                  105 : 0.05800708699594, 
                  106 : 0.07837366767499, 
                  107 : 0.08920227204998, 
                  108 : 0.05516277301390, 
                  120 : 0.00103060109449, 
                  121 : 0.00904520193285, 
                  122 : 0.04853306134652, 
                  123 : 0.00852111547488, 
                  137 : 0.00160855766471, 
}

"""Dictionary providing area weights for each LOCA grid cell
"""

PET_MON_NORMS = { 1 : 5.6328841,
                  2 : 5.7358650,
                  3 : 5.7279756, 
                  4 : 5.6047048, 
                  5 : 5.1975405, 
                  6 : 4.6063037, 
                  7 : 4.3182625, 
                  8 : 4.4228131, 
                  9 : 5.0171359, 
                  10 : 5.3738328, 
                  11 : 5.5505123, 
                  12 : 5.6000277,
}
""" Square root of difference between mean monthly max and mean monthly min temperature
"""

MON_MAX_BY_REGION = { 1 : [ 35.7, 35.7, 35.7, 35.7 ], 
                      2 : [ 73.2, 73.2, 73.2, 73.2 ], 
                      3 : [ 102.4, 102.4, 102.4, 102.4 ],
                      4 : [ 98.3, 98.3, 98.3, 98.3 ],
                      5 : [ 103.2, 103.2, 103.2, 103.2 ],
                      6 : [ 123.4, 123.4, 123.4, 123.4 ],
                      7 : [ 73.7, 73.7, 73.7, 73.7 ],
                      8 : [ 200.7, 200.7, 200.7, 200.7 ],
                      9 : [ 130.3, 130.3, 130.3, 130.3 ],
                      10 : [ 117.2, 117.2, 117.2, 117.2 ],
                      11 : [ 75.7, 75.7, 75.7, 75.7 ],
                      12 : [ 76.7, 76.7, 76.7, 76.7 ], }
""" Monthly maximum precipitation depth by region to use to truncate the mixed exponential
distributions.
"""

MON_MAX_BY_PP = { 1 : [ 36.0, 73.0, 102.0, 98.0, 103.0, 123.0, 73.0, 200.0, 
                        130.0, 117.0, 75.0, 76.0 ],
                  2 : [ 34.0, 70.0, 98.0, 94.0, 99.0, 118.0, 71.0, 193.0, 
                        125.0, 113.0, 73.0, 74.0 ],
                  3 : [ 37.0, 75.0, 105.0, 101.0, 106.0, 127.0, 76.0, 
                        206.0, 134.0, 120.0, 78.0, 79.0 ],
}
"""Monthly maximum precipitation depth by projection period to use to truncate the 
mixed exponential distributions. Are not using regions for projection periods so use
the same maximum for every LOCA grid cell. These maximums are based on maximums
observed in the LOCA archive.
"""

MON_MAX_BY_PP_PRISM = { 1 : [ 41.0, 83.0, 117.0, 112.0, 118.0, 141.0, 84.0, 
                              229.0, 148.0, 134.0, 86.0, 87.0 ],
                  2 : [ 45.0, 92.0, 128.0, 123.0, 129.0, 155.0, 92.0, 251.0, 
                        163.0, 147.0, 95.0, 96.0 ],
                  3 : [ 49.0, 100.0, 140.0, 134.0, 141.0, 169.0, 101.0, 
                        274.0, 178.0, 160.0, 103.0, 105.0 ],
}
"""Version of MON_MAX_BY_PP to use when want to use scaling to represent site
extrem event depths. The scaled maximum represents the 100-yr, 24-hr event 
depth for the site."""

H0_MAX_BY_PP = { 1 : [ 43.0, 88.0, 124.0, 119.0, 125.0, 149.0, 89.0, 
                       243.0, 158.0, 142.0, 92.0, 93.0 ],
                 2 : [ 43.0, 88.0, 124.0, 119.0, 125.0, 149.0, 89.0, 
                       243.0, 158.0, 142.0, 92.0, 93.0 ],
                 3 : [ 43.0, 88.0, 124.0, 119.0, 125.0, 149.0, 89.0, 
                       243.0, 158.0, 142.0, 92.0, 93.0 ],
}
"""Null hypothesis pathway maximum truncation values for the final model.
Represents 100-yr, daily as maximum"""

H1_MAX_BY_PP = { 1 : [ 52.0, 107.0, 149.0, 143.0, 150.0, 180.0, 107.0, 
                       292.0, 190.0, 171.0, 110.0, 112.0 ],
                 2 : [ 52.0, 107.0, 149.0, 143.0, 150.0, 180.0, 107.0, 
                       292.0, 190.0, 171.0, 110.0, 112.0 ],
                 3 : [ 52.0, 107.0, 149.0, 143.0, 150.0, 180.0, 107.0, 
                       292.0, 190.0, 171.0, 110.0, 112.00 ],
}
"""Alternative hypothesis pathway maximum truncation values for the final model.
Represents 200-yr, daily as maximum"""

#EOF