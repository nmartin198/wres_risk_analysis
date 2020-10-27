#!/usr/bin/python3
"""
Main program statement for running mHSP2 as part of a weather generator
framework simulation.

This version of mHSP2 relies weather generator output that was created
previously. It then runs, the HSPF watershed water balance model using
this forcing for two pathways. In this version, the user specifies 
whether the pathways are comparing weather forcing which would be 
historical-similar weather forcing to climate change projection 
weather forcing or whether the pathways are comparing changes to
the watershed over future time given identical weather forcing.

Command line argument options

    * *modelDir* (str): path for model directory with input files
    * *startReal* (int): the starting realization
    * *numReal* (int): the number of realizations to simulate

Typical usage examples

    **HSPF climate change comparison** ::

        python C:\Repositories\WeatherGenerator\mHSP2\standaloneMain.py MF6 
                C:\\Working\\Test_Models\\WG_mHSP2 climate --start_real 1 --num_real 2

    **Comparison between basin states** ::
        
        python C:\Repositories\WeatherGenerator\mHSP2\standaloneMain.py
                C:\\Working\\Test_Models\\WG_mHSP2 basin --i 10.0 --start_real 1 --num_real 2

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
import sys
import os
import argparse
from multiprocessing import Process
# local package imports. Can use the standard import approach because are not
#   run as independent processes
import locaMain as HSP2
import dc_setup_inputs as setIn
import dc_process_outputs as procOut


#standalone execution block
# assumes that this module is executed within the same current directory
# as the input file
if __name__ == "__main__":
    # do the argument processing stuff first
    apUsage = "%(prog)s <model directory> <run type> -i <increase in impervious> " \
              "-s <starting realization #> -n <number of realizations>"
    apDesc = "Execute standalone mHSP2 with weather generator output"
    parser = argparse.ArgumentParser( usage=apUsage, description=apDesc )
    parser.add_argument( action='store', nargs=1,
                         dest='modelDir', type=str,
                         help='Model directory with input file(s)',
                         metavar="model directory" )
    parser.add_argument( action='store', choices=["climate", "basin"], type=str, 
                         nargs=1, dest='runType',
                         help='Type of mHSP2 framework comparison',
                         metavar="simulation type" )
    parser.add_argument( '-i', '--inc_imp', action='store', nargs=1, 
                         type=float, dest="incImpA",
                         help='Amount to increase impervious area (0 - 100%)',
                         metavar="impervious increment (%)", required=False )
    parser.add_argument( '-s', '--start_real', action='store', nargs=1, 
                         dest='startReal', type=int,
                         help='Realizations to start simulating',
                         metavar="Starting realization", required=True )
    parser.add_argument( '-n', '--num_real', action='store', nargs=1, 
                         dest='numReal', type=int,
                         help='Number of realizations to simulate',
                         metavar="Number of realizations", required=True )
    # parse the command line arguments received and set the simulation directory
    args = parser.parse_args()
    Sim_Dir = os.path.normpath( args.modelDir[0] )
    # check that our directory exists
    if not os.path.isdir( Sim_Dir ):
        # this is an error
        errMsg = "Model directory %s does not exist!!!" % Sim_Dir
        sys.exit( errMsg )
    # get the current directory
    CWD = os.getcwd()
    if CWD != Sim_Dir:
        os.chdir( Sim_Dir )
    # get run type
    Run_Type = args.runType[0]
    if not Run_Type in ["climate", "basin"]:
        errMsg = "Invalid run type of %s" % Run_Type
        sys.exit( errMsg )
    # check for the increment
    if args.incImpA[0] == None:
        if Run_Type == "basin":
            # this is an error
            errMsg = "An impervious increment (-i) needs to be specified " \
                     "when run type is %s." % "basin"
            sys.exit( errMsg )
        # end if
    else:
        IIncAmount = args.incImpA[0]
    # end if
    # get the realizations
    numReal = args.numReal[0]
    startReal = args.startReal[0]
    # the preliminaries are done
    print( "Simulate realizations %d through %d" % ( startReal, 
            ( startReal + numReal ) - 1) )
    # now start our realizations loop
    for iI in range( startReal, ( startReal + numReal ), 1 ):
        # outputs
        if iI % 100 == 0:
            print("Realization %d" % iI)
        # end if
        retTuple = setIn.createHDF5Inputs( Sim_Dir, iI, Run_Type )
        if len(retTuple) != 2:
            # this is an error
            errMsg = "Issue creating HDF5 input files for realization " \
                     "%d!!!" % iI
            sys.exit( errMsg )
        # end if.
        H0File = retTuple[0]
        H1File = retTuple[1]
        # now run both in separate processes
        p0 = Process( target=HSP2.salocaMain, args=(Sim_Dir, H0File, 
                      "climate", IIncAmount ) )
        p0.start()
        p1 = Process( target=HSP2.salocaMain, args=(Sim_Dir, H1File, 
                      Run_Type, IIncAmount ) )
        p1.start()
        p0.join( 35.0 * 60.0 )
        p1.join( 35.0 * 60.0 )
        p0ECode = p0.exitcode
        p1ECode = p1.exitcode
        if ( (p0ECode != 0) or (p1ECode != 0) ):
            # this means an error
            errMsg = "There was an error or issue with one of the " \
                     "pathway processes!!!"
            sys.exit( errMsg )
        # end if
        # now need to do the output comparison stuff
        procOut.procOuts( Sim_Dir, H0File, H1File, iI )
    # end realization for
    # return to the current directory
    if CWD != Sim_Dir:
        os.chdir( CWD )
    # end if
    print( "Successful termination of mHSP2" )
    # end


#EOF