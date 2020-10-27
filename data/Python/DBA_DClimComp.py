# -*- coding: utf-8 -*-
"""
Dolan Creek Climate Change Analysis - DB utility functions and methods

.. module:: DBA_DClimComp
    :platform: Windows
    :synopsis: Database Utilities

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Purpose:

Python Module with objects and helper functions for dealing with and populating
our database.

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
import pyodbc
import sys

# Module level globals
# database name
DB_NAME = "DCClimComp"
# database server name
SRVR_NAME = "NMARTIN10\\TLOCALDB"
# global defines for the DSN.
# need to have already defined the DSN on your system.
DSN_NAME = "DCClimComp_SQLSRVR"
# user access identification for the database.
USER_NAME = "SwRIClimComp"
USER_PWD = "xXxXxXxX"
# Use the DSN and user information to create a connection string.
# In this case using pyodbc to facilitate this connection.
DSN_STRING = "mssql+pyodbc://%s:%s@%s" % ( USER_NAME, USER_PWD, DSN_NAME )
PYODBC_CONN_STRING = "DSN=%s;UID=%s;PWD=%s" % ( DSN_NAME, USER_NAME, USER_PWD )
# pyodbc connection strings.
# Use this version if SQL Server is on a different machine from that which is
#   used to run Python scripts. Note, that the ODBC Driver 17 needs to be
#   installed for this connection string to work.
PYODBC_CONNECTION = "DRIVER={ODBC Driver 13 for SQL Server};SERVER=%s;" \
                    "DATABASE=%s;UID=%s;PWD=%s" % \
                    ( SRVR_NAME, DB_NAME, USER_NAME, USER_PWD )
# set the date time format for SQL datetimeoffset
SQL_DTO_FMT = "%Y-%m-%d %H:%M:%S +00:00"

# schema
PRISM_SCHEMA = "PRISM"
CMIP5_SCHEMA = "CMIP5"
STATS_SCHEMA = "CalcStats"
# table names
CMIP5_PTMETA = "GridPts_Meta"
CMIP5_MODMETA = "Models_Scenarios"
CMIP5_PRECIP = "Precip_Daily"
CMIP5_TMAX = "Tmax_Daily"
CMIP5_TMIN = "Tmin_Daily"
CMIP5_OBSPRE = "Observed_Precip"
CMIP5_OBSTMAX = "Observed_Tmax"
CMIP5_OBSTMIN = "Observed_Tmin"
PRISM_PTMETA = "GridPts_Meta"
PRISM_PRECIP = "Precip_Daily"
PRISM_TMAX = "Tmax_Daily"
PRISM_TMIN = "Tmin_Daily"
PRISM_TMEAN = "Tmean_Daily"
PRISM_TDMEAN = "TAveDewPt_Daily"
PRISM_VPDMAX = "VPDMax_Daily"
PRISM_VPDMIN = "VPDMin_Daily"

# field/column names
FIELDN_ID = "Id"
FIELDN_ROW = "Row"
FIELDN_COL = "Col"
FIELDN_LON = "Longitude"
FIELDN_LAT = "Lattitude"
FIELDN_X = "utm_x"
FIELDN_Y = "utm_y"
FIELDN_DSMETHOD = "DS_Method"
FIELDN_DSRES = "DS_Resolution"
FIELDN_SCIND = "Result_Ind"
FIELDN_INITC = "ICRunNum"
FIELDN_SCENID = "Scenario_ID"
FIELDN_MODCOL = "CMIP5_Model"
FIELDN_MMPK = "Model_PK"
FIELDN_GNPK = "Node_PK"
FIELDN_DT = "Datetime_UTC"
FIELDN_PVAL = "Precip_mmpd"
FIELDN_TMXVAL = "Tmax_C"
FIELDN_TMNVAL = "Tmin_C"
FIELDN_TAVEVAL = "Tmean_C"
FIELDN_GRIDIND = "Grid_Index"
FIELDN_TDPT = "DewPtT_C"
FIELDN_VPDMX = "VpdMax_hPa"
FIELDN_VPDMN = "VpdMin_hPa"
FIELDN_STRDT = "DateStr"

# miscellaneous globals
DS_LOCA = "LOCA"
DS_BCCA = "BCCA"


def returnTableSchemaList( SchemaName ):
    """Convenience function which returns the list of tables for a schema in
    the database.
    
    The DB to examine is hard coded in the globals. Schema name is passed.
    Everything text wise in SQL Server will be stored as unicode. 
    
    Args:
        SchemaName(str): the schema name to search for in regular text.
        
    Returns:
        TableList(list): list of metadata with matching schema and unique
                          table names. Return [-1] if there is an error.
                          
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME
    # locals
    TableList = list()
    # now we need to use a try block in case there are exceptions.
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        DB_MetaData_Tuple = crsr.tables()
        TableList = [ [x[1], x[2]] for x in DB_MetaData_Tuple if x[1] == SchemaName ]
         # close up the connections
        crsr.close() 
        cnxn.close()
    except:
        # catch any exceptions here
        ErrMsg = "Exception when searching database for schema %s.\n" \
                 "Stack trace: %s \n\n" % ( SchemaName, sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        TableList = [-1]
    finally:
        # clear out
        DB_MetaData_Tuple = None
        crsr = None
        cnxn = None
    # return
    return TableList

def createCMIP5DSMetaTable( ):
    """Create the point meta data table for grid points where projections 
    have been downscaled. These point locations will have weather paramters
    stored for each day.
    
    Args:
        
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_PTMETA
    global FIELDN_ID, FIELDN_ROW, FIELDN_COL, FIELDN_LON, FIELDN_LAT
    global FIELDN_X, FIELDN_Y, FIELDN_DSMETHOD, FIELDN_DSRES
    # locals
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s smallint NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s int NOT NULL, \n" \
                    "      %s int NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s nvarchar(10) NOT NULL, \n" \
                    "      %s nvarchar(24) NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                         FIELDN_ROW, FIELDN_COL, FIELDN_LON, FIELDN_LAT,
                         FIELDN_X, FIELDN_Y, FIELDN_DSMETHOD, FIELDN_DSRES )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_PTMETA,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createCMIP5ModelMetaTable( ):
    """Archive of SQL Commands and procedure for creating the Model metadata
    table for CMIP5 results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_MODMETA
    global FIELDN_ID, FIELDN_SCIND, FIELDN_INITC, FIELDN_SCENID
    global FIELDN_MODCOL
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s smallint NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s int NOT NULL, \n" \
                    "      %s int NOT NULL, \n" \
                    "      %s nvarchar(10) NOT NULL, \n" \
                    "      %s nvarchar(64) NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_MODMETA, FIELDN_ID,
                         FIELDN_SCIND, FIELDN_INITC, FIELDN_SCENID, 
                         FIELDN_MODCOL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_MODMETA,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createCMIP5PrecipTSTable( ):
    """Archive of SQL Commands and procedure for creating the precipitation
    time series table for CMIP5 results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_PRECIP
    global FIELDN_ID, FIELDN_MMPK, FIELDN_GNPK, FIELDN_DT, FIELDN_PVAL
    global CMIP5_PTMETA, CMIP5_MODMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_PRECIP, FIELDN_ID, 
                          FIELDN_MMPK, CMIP5_SCHEMA, CMIP5_MODMETA, FIELDN_ID,
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_PVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_PRECIP,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createCMIP5TMaxTSTable( ):
    """Archive of SQL Commands and procedure for creating the TMax
    time series table for CMIP5 results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_TMAX
    global FIELDN_ID, FIELDN_MMPK, FIELDN_GNPK, FIELDN_DT, FIELDN_TMXVAL
    global CMIP5_PTMETA, CMIP5_MODMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_TMAX, FIELDN_ID, 
                          FIELDN_MMPK, CMIP5_SCHEMA, CMIP5_MODMETA, FIELDN_ID,
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMXVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_TMAX,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createCMIP5TMinTSTable( ):
    """Archive of SQL Commands and procedure for creating the TMin
    time series table for CMIP5 results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_TMIN
    global FIELDN_ID, FIELDN_MMPK, FIELDN_GNPK, FIELDN_DT, FIELDN_TMNVAL
    global CMIP5_PTMETA, CMIP5_MODMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_TMIN, FIELDN_ID, 
                          FIELDN_MMPK, CMIP5_SCHEMA, CMIP5_MODMETA, FIELDN_ID,
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMNVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_TMIN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createObsPrecipTSTable( ):
    """Archive of SQL Commands and procedure for creating the observed
    precipitation time series table for CMIP5 downloads.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_OBSPRE
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_PVAL
    global CMIP5_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_OBSPRE, FIELDN_ID, 
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_PVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_OBSPRE,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createOBSTMaxTSTable( ):
    """Archive of SQL Commands and procedure for creating the observed TMax
    time series table from CMIP5 downloads.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_OBSTMAX
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TMXVAL
    global CMIP5_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_OBSTMAX, FIELDN_ID, 
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMXVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close()
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_OBSTMAX,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createOBSTMinTSTable( ):
    """Archive of SQL Commands and procedure for creating the TMin
    observed time series table from CMIP5 archives.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_OBSTMIN
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TMNVAL
    global CMIP5_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( CMIP5_SCHEMA, CMIP5_OBSTMIN, FIELDN_ID, 
                          FIELDN_GNPK, CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMNVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close()
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( CMIP5_SCHEMA, CMIP5_OBSTMIN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def processModelsFile( InFile ):
    """Process the models file that lists each file involved in the downloaded
    model results for each download directory.
    
    Args:
        InFile (str): FQDN path for the current model file
        
    Returns:
        ModsDict (dict): Dictionary with index in results as key and
                        a list, L, for the value
                        L[0] = model short name
                        L[1] = run number/initial conditions
                        L[2] = scenario label
                        
    """
    # imports
    import traceback
    # globals
    # local parameters
    NELEM = 3            # expect to split to 3 elements per line
    IDELEM = 0           # the ID position in the list from split
    ICELEM = 1           # initial condition position in list from split
    SCENELEM = 2         # the scenario position in the list from split
    # locals
    BadDict = dict()
    ModsDict = dict()
    # start
    # read the file
    with open( InFile, 'r' ) as InF:
        AllLines = InF.readlines()
    # end of with block
    if len( AllLines ) < 1:
        print("Unsuccessful read of file %s" % InFile)
        return BadDict
    # continue
    lC = 0
    for tLine in AllLines:
        stL = tLine.strip()
        if len(stL) < 1:
            continue
        mComps = stL.split(".")
        if len(mComps) != NELEM:
            print("Invalid line of %s" % tLine)
            continue
        # add our list to our return list
        try:
            icInt = int( mComps[ICELEM] )
        except:
            SEInfo = sys.exc_info()
            print(repr(traceback.format_exception(SEInfo[0], SEInfo[1],
                                          SEInfo[2])))
            return BadDict
        # populate our dictonary
        ModsDict[lC] = [ mComps[IDELEM], icInt, mComps[SCENELEM] ]
        lC += 1
    # end of for
    # return
    return ModsDict

def createPRISMMetaTable( ):
    """Create the point meta data table for grid points These point locations 
    will have weather parameters stored for each day.
    
    Args:
        
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_PTMETA
    global FIELDN_ID, FIELDN_GRIDIND, FIELDN_LON, FIELDN_LAT
    global FIELDN_X, FIELDN_Y
    # locals
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s smallint NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s int NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "      %s float NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                         FIELDN_GRIDIND, FIELDN_LON, FIELDN_LAT,
                         FIELDN_X, FIELDN_Y )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_PTMETA,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMPrecipTSTable( ):
    """Archive of SQL Commands and procedure for creating the precipitation
    time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_PRECIP
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_PVAL
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_PRECIP, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_PVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_PRECIP,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMTMaxTSTable( ):
    """Archive of SQL Commands and procedure for creating the Tmax
    time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_TMAX
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TMXVAL
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_TMAX, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMXVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_TMAX,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMTMinTSTable( ):
    """Archive of SQL Commands and procedure for creating the Tmin
    time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_TMIN
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TMNVAL
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_TMIN, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TMNVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_TMIN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMTAveTSTable( ):
    """Archive of SQL Commands and procedure for creating the Tave
    time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_TMEAN
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TAVEVAL
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_TMEAN, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TAVEVAL )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_TMEAN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMTDPtTSTable( ):
    """Archive of SQL Commands and procedure for creating the dew point temp
    time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_TDMEAN
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_TDPT
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_TDMEAN, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_TDPT )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_TDMEAN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMVpdMaxTSTable( ):
    """Archive of SQL Commands and procedure for creating the maximum vapor 
    pressure deficit time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_VPDMAX
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_VPDMX
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_VPDMAX, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_VPDMX )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_VPDMAX,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus

def createPRISMVpdMinTSTable( ):
    """Archive of SQL Commands and procedure for creating the minimum vapor 
    pressure deficit time series table for PRISM results.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, PRISM_SCHEMA, PRISM_VPDMIN
    global FIELDN_ID, FIELDN_GNPK, FIELDN_DT, FIELDN_VPDMN
    global PRISM_PTMETA
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQL_CreateCmd = "CREATE TABLE [%s].[%s]\n" \
                    "    ( %s int NOT NULL IDENTITY(1,1 ) PRIMARY KEY, \n" \
                    "      %s smallint NOT NULL \n" \
                    "          REFERENCES %s.%s(%s), \n" \
                    "      %s datetimeoffset NOT NULL, \n" \
                    "      %s real NOT NULL, \n" \
                    "    );" % ( PRISM_SCHEMA, PRISM_VPDMIN, FIELDN_ID, 
                          FIELDN_GNPK, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID,
                          FIELDN_DT, FIELDN_VPDMN )
    # then use a try block to create the table
    try:
        # connect to database and get metadata
        cnxn = pyodbc.connect( PYODBC_CONN_STRING, autocommit=True )
        crsr = cnxn.cursor()
        SQL_Command = "USE %s" % DB_NAME
        crsr.execute( SQL_Command )
        crsr.execute( SQL_CreateCmd )
        # close up the connections
        crsr.close() 
        cnxn.close()
        RetStatus = True
    except:
        # catch any exceptions here
        ErrMsg = "Exception when creating table %s.%s.\n" \
                 "Stack trace: %s \n\n" % ( PRISM_SCHEMA, PRISM_VPDMIN,
                                            sys.exc_info()[0] )
        print("%s" % ErrMsg)
        # now set the return
        RetStatus = False
    finally:
        # clear out
        crsr = None
        cnxn = None
    # return
    return RetStatus


def createSQLPRISMPre( StartDT, EndDT, PGridID ):
    """Create a SQL query string to extract precipitation time series for the
    specified date range and the specified PRISM gird cell.
    
    Args:
        StartDT (datetime): Starting date time
        EndDT (datetime): Ending date time
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    global FIELDN_DT, FIELDN_STRDT, FIELDN_PVAL, PRISM_SCHEMA, PRISM_PRECIP
    global FIELDN_GNPK, SQL_DTO_FMT
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s]\n" \
               "    WHERE ( %s = %d AND %s >= '%s' AND %s <= '%s' ) \n" \
               "    ORDER BY %s ASC;" % \
               ( FIELDN_DT, FIELDN_STRDT, FIELDN_PVAL, PRISM_SCHEMA, 
                 PRISM_PRECIP, FIELDN_GNPK, PGridID, FIELDN_DT, 
                 StartDT.strftime( SQL_DTO_FMT ), FIELDN_DT,
                 EndDT.strftime( SQL_DTO_FMT ), FIELDN_DT )
    # return
    return SQLQuery


def createSQLPRISMGrid( ):
    """Create a SQL query string for getting all of the PRISM grid cell 
    definitions.
    
    Args:
        
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    global PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID, FIELDN_GRIDIND, FIELDN_LON
    global FIELDN_LAT, FIELDN_X, FIELDN_Y
    # locals
    SQLQuery = "SELECT %s, %s, %s, %s, %s, %s FROM [%s].[%s]\n" \
               "    ORDER BY %s ASC;" % \
               ( FIELDN_ID, FIELDN_GRIDIND, FIELDN_LON, FIELDN_LAT,
                 FIELDN_X, FIELDN_Y, PRISM_SCHEMA, PRISM_PTMETA, FIELDN_ID )

    # return
    return SQLQuery


def createSQLCMIP5Grid( ):
    """Create a SQL query string for getting all of the CMIP5 grid cell 
    definitions.
    
    Args:
        
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    global CMIP5_SCHEMA, CMIP5_PTMETA, FIELDN_ID, FIELDN_ROW, FIELDN_COL
    global FIELDN_X, FIELDN_Y, FIELDN_DSMETHOD, FIELDN_DSRES
    # locals
    SQLQuery = "SELECT %s, %s, %s, %s, %s, %s, %s FROM [%s].[%s]\n" \
               "    ORDER BY %s ASC;" % \
               ( FIELDN_ID, FIELDN_ROW, FIELDN_COL, FIELDN_X, FIELDN_Y,
                 FIELDN_DSMETHOD, FIELDN_DSRES, CMIP5_SCHEMA, CMIP5_PTMETA,
                 FIELDN_ID )
    # return
    return SQLQuery


def createSQLCMIP5Model( ):
    """Create a SQL query string for getting all of the CMIP5 model 
    definitions.
    
    Args:
        None
    
    Returns:
        RetStatus (bool): True == success
    """
    # imports
    # globals
    global PYODBC_CONN_STRING, DB_NAME, CMIP5_SCHEMA, CMIP5_MODMETA
    global FIELDN_ID, FIELDN_SCIND, FIELDN_INITC, FIELDN_SCENID
    global FIELDN_MODCOL
    # locals
    # setup the create command
    SQLQuery = "SELECT %s, %s, %s, %s, %s FROM [%s].[%s]\n" \
               "    ORDER BY %s ASC;" % \
               ( FIELDN_ID, FIELDN_SCIND, FIELDN_INITC, FIELDN_SCENID, 
                 FIELDN_MODCOL, CMIP5_SCHEMA, CMIP5_MODMETA, FIELDN_ID )
    # return
    return SQLQuery


def createSQLCMIP5Pre( StartDT, EndDT, CGridID, CModID ):
    """Create a SQL query string to extract precipitation time series for the
    specified date range and the specified CMIP5 grid cell and model
    
    Args:
        StartDT (datetime): Starting date time
        EndDT (datetime): Ending date time
        CGridID (int): Primary key, ID for the grid cell to extract
        CModID (int): foreign key, ID for the model run to extract
    
    Returns:
        SQLQuery (str): the query string
    """
    # imports
    # globals
    global FIELDN_DT, FIELDN_STRDT, FIELDN_PVAL, CMIP5_SCHEMA, CMIP5_PRECIP
    global FIELDN_GNPK, FIELDN_MMPK, SQL_DTO_FMT
    # locals
    # setup the create command
    # start out by setting our command syntax
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s]\n" \
               "    WHERE ( %s = %d AND %s = %d AND %s >= '%s' AND %s <= '%s' ) \n" \
               "    ORDER BY %s ASC;" % \
               ( FIELDN_DT, FIELDN_STRDT, FIELDN_PVAL, 
                 CMIP5_SCHEMA, CMIP5_PRECIP, FIELDN_GNPK, CGridID, 
                 FIELDN_MMPK, CModID, FIELDN_DT, 
                 StartDT.strftime( SQL_DTO_FMT ), FIELDN_DT,
                 EndDT.strftime( SQL_DTO_FMT ), FIELDN_DT )
    # return
    return SQLQuery


def createSQLPRISMAllYear( PGridID, Year ):
    """Create a SQL query string to extract daily precipitation, max temp,
    average temp, min temp, and dewpoint temperature for a specified year
    and PRISM grid cell.
    
    Args:
        PGridID (int): Primary key, ID for the grid cell to extract
        Year (int): The calendar year to extract values for
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_PVAL, FIELDN_TMXVAL, FIELDN_TAVEVAL
    global FIELDN_TMNVAL, FIELDN_TDPT, PRISM_SCHEMA, PRISM_PRECIP
    global PRISM_TMAX, FIELDN_GNPK, PRISM_TMEAN, PRISM_TMIN, PRISM_TDMEAN
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(P.%s AS nvarchar(30)) AS %s, P.%s, Tx.%s, Ta.%s, Tn.%s, Dp.%s \n" \
               "  FROM [%s].[%s] AS P \n" \
               "    INNER JOIN [%s].[%s] AS Tx \n" \
               "      On ( P.%s = Tx.%s AND P.%s = Tx.%s ) \n" \
               "    INNER JOIN [%s].[%s] AS Ta \n" \
               "      On ( P.%s = Ta.%s AND P.%s = Ta.%s ) \n" \
               "    INNER JOIN [%s].[%s] AS Tn \n" \
               "      On ( P.%s = Tn.%s AND P.%s = Tn.%s ) \n" \
               "    INNER JOIN [%s].[%s] AS Dp \n" \
               "      On ( P.%s = Dp.%s AND P.%s = Dp.%s ) \n" \
               "  WHERE ( P.%s = %d AND YEAR(P.%s) = %d) \n" \
               "  ORDER BY P.%s ASC;" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_PVAL, FIELDN_TMXVAL, FIELDN_TAVEVAL, 
                 FIELDN_TMNVAL, FIELDN_TDPT, PRISM_SCHEMA, PRISM_PRECIP, 
                 PRISM_SCHEMA, PRISM_TMAX, FIELDN_DT, FIELDN_DT, FIELDN_GNPK, 
                 FIELDN_GNPK, PRISM_SCHEMA, PRISM_TMEAN, FIELDN_DT, FIELDN_DT, 
                 FIELDN_GNPK, FIELDN_GNPK, PRISM_SCHEMA, PRISM_TMIN, FIELDN_DT,
                 FIELDN_DT, FIELDN_GNPK, FIELDN_GNPK, PRISM_SCHEMA, 
                 PRISM_TDMEAN, FIELDN_DT, FIELDN_DT, FIELDN_GNPK, FIELDN_GNPK,
                 FIELDN_GNPK, PGridID, FIELDN_DT, Year, FIELDN_DT )
    # return
    return SQLQuery


def createSQLCMIPPrecipSP( PGridID ):
    """Create a SQL query string to extract daily precipitation for the study
    period for a specific grid cell. The study period is assumed to be 
    1981-2100
    
    Args:
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_PVAL, CMIP5_SCHEMA, CMIP5_PRECIP, FIELDN_MMPK
    global FIELDN_GNPK
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s, %s FROM [%s].[%s] \n" \
               "    WHERE %s = %d AND YEAR(%s) > %d \n" \
               "    ORDER BY %s, %s ASC;\n" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_MMPK, FIELDN_PVAL, CMIP5_SCHEMA,
                 CMIP5_PRECIP, FIELDN_GNPK, PGridID, FIELDN_DT, 1980, 
                 FIELDN_DT, FIELDN_MMPK )
    # return
    return SQLQuery

def createSQLPRISMTMaxSP( PGridID, SYear, EYear ):
    """Create a SQL query string to extract daily max temperature for the 
    study period for a single grid cell. The study period is specified with
    SYear and EYear
    
    Args:
        SYear (int): Starting year
        EYear (int): Ending year
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_TMXVAL, PRISM_SCHEMA, PRISM_TMAX, FIELDN_GNPK
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s] \n" \
               "    WHERE %s = %d AND YEAR(%s) >= %d AND YEAR(%s) <= %d \n" \
               "    ORDER BY %s ASC;\n" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_TMXVAL, 
                 PRISM_SCHEMA, PRISM_TMAX, FIELDN_GNPK, PGridID, FIELDN_DT, 
                 SYear, FIELDN_DT, EYear, FIELDN_DT )
    # return
    return SQLQuery

def createSQLPRISMTMinSP( PGridID, SYear, EYear ):
    """Create a SQL query string to extract daily min temperature for the 
    study period for a single grid cell. The study period is specified with
    SYear and EYear
    
    Args:
        SYear (int): Starting year
        EYear (int): Ending year
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_TMNVAL, PRISM_SCHEMA, PRISM_TMIN, FIELDN_GNPK
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s FROM [%s].[%s] \n" \
               "    WHERE %s = %d AND YEAR(%s) >= %d AND YEAR(%s) <= %d \n" \
               "    ORDER BY %s ASC;\n" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_TMNVAL, 
                 PRISM_SCHEMA, PRISM_TMIN, FIELDN_GNPK, PGridID, FIELDN_DT, 
                 SYear, FIELDN_DT, EYear, FIELDN_DT )
    # return
    return SQLQuery

def createSQLCMIPTMaxSP( PGridID ):
    """Create a SQL query string to extract daily max temperature for the 
    study period for a single grid cell. The study period is assumed to be 
    1981-2100
    
    Args:
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_TMXVAL, CMIP5_SCHEMA, CMIP5_TMAX, FIELDN_MMPK
    global FIELDN_GNPK
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s, %s FROM [%s].[%s] \n" \
               "    WHERE %s = %d AND YEAR(%s) > %d \n" \
               "    ORDER BY %s, %s ASC;\n" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_MMPK, FIELDN_TMXVAL, 
                 CMIP5_SCHEMA, CMIP5_TMAX, FIELDN_GNPK, PGridID, FIELDN_DT, 
                 1980, FIELDN_DT, FIELDN_MMPK )
    # return
    return SQLQuery


def createSQLCMIPTMinSP( PGridID ):
    """Create a SQL query string to extract daily min temperature for the 
    study period for a single grid cell. The study period is assumed to be 
    1981-2100
    
    Args:
        PGridID (int): Primary key, ID for the grid cell to extract
    
    Returns:
        SQLQuery(str): the query string
    """
    #imports
    #globals
    global FIELDN_DT, FIELDN_TMNVAL, CMIP5_SCHEMA, CMIP5_TMIN, FIELDN_MMPK
    global FIELDN_GNPK
    # locals
    # setup the command
    SQLQuery = "SELECT CAST(%s AS nvarchar(30)) AS %s, %s, %s FROM [%s].[%s] \n" \
               "    WHERE %s = %d AND YEAR(%s) > %d \n" \
               "    ORDER BY %s, %s ASC;\n" % \
               ( FIELDN_DT, FIELDN_DT, FIELDN_MMPK, FIELDN_TMNVAL, 
                 CMIP5_SCHEMA, CMIP5_TMIN, FIELDN_GNPK, PGridID, FIELDN_DT, 
                 1980, FIELDN_DT, FIELDN_MMPK )
    # return
    return SQLQuery

#EOF