-- Collection of T-SQL snippets for creation of MS SqlServer DB and
-- maintenance of table design. Also has several testing snippets 
-- for query optimization.
-- Author: Nick Martin <nick.martin@stanfordalumni.org>


-- Copyright 2020 Nick Martin
-- 
-- This file is part of a collection of scripts and modules in the GitHub
-- repository https://github.com/nmartin198/wres_risk_analysis, hereafter
-- `wres_risk_analysis`.
-- 
-- wres_risk_analysis is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
-- 
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.


-- Create the new database.
--   SQL Server Express has a maximimum size of 10 GB
--   Set the log file to have a maximum of half of that.
USE master;
GO
CREATE DATABASE DCClimComp
ON 
( NAME = DCClimComp_dat,
    FILENAME = 'C:\MSSQL_DB\MSSQL14.TLOCALDB\MSSQL\DATA\DCClimCompdat.mdf',
    SIZE = 153600MB,
    MAXSIZE = 163840MB,
    FILEGROWTH = 5120MB )
LOG ON
( NAME = DCClimComp_log,
    FILENAME = 'C:\MSSQL_DB\MSSQL14.TLOCALDB\MSSQL\DATA\DCClimComplog.ldf',
    SIZE = 2048MB,
    MAXSIZE = 10240MB,
    FILEGROWTH = 1024MB ) ;
GO

-- Next give our default user the permissions that we need.
--		Make sure that this is mixed access.
CREATE LOGIN SwRIClimComp WITH PASSWORD = 'xXxXxXxXxX', 
		DEFAULT_DATABASE = DCClimComp, DEFAULT_LANGUAGE = English, CHECK_POLICY = OFF;
GO

-- Next make our new account a database user
USE [DCClimComp];
GO
CREATE USER [SwRIClimComp] FOR LOGIN [SwRIClimComp];
GO

-- Assign the permissions that we want.
USE [DCClimComp];
GO
ALTER ROLE db_owner ADD MEMBER SwRIClimComp;
GO

-- Now have the database. Set up some default Schemas, functions, and tables.
-- PRISM schema is for the PRISM historical data
USE [DCClimComp];
GO
CREATE SCHEMA PRISM;
GO

-- CMIP5 schema is for the CMIP5 Model Output
USE [DCClimComp];
GO
CREATE SCHEMA CMIP5;
GO

-- CalcStats schema is for calculated tables
USE [DCClimComp];
GO
CREATE SCHEMA CalcStats;
GO

-- Find and delete rows if needed
USE [DCClimComp];
GO

DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
-- SELECT @StartDate AS 'Datetimeoffset';
SELECT * FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK = 34
	ORDER BY Datetime_UTC ASC;

-- DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
DECLARE @StartDate as datetimeoffset(7) = '2069-01-01 00:00:00 +00:00';
-- SELECT @StartDate AS 'Datetimeoffset';
SELECT * FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK = 33
	ORDER BY Datetime_UTC ASC;

DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
DELETE FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK = 34;
GO

DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
DELETE FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK = 33;
GO

DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
-- SELECT @StartDate AS 'Datetimeoffset';
SELECT * FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK > 32
	ORDER BY Datetime_UTC ASC;

DECLARE @StartDate as datetimeoffset(7) = '2071-01-01 00:00:00 +00:00';
DELETE FROM CMIP5.Precip_Daily
	WHERE Datetime_UTC >= @StartDate AND Model_PK > 32;
GO

SELECT Datetime_UTC, Precip_mmpd FROM [PRISM].[Precip_Daily]
    WHERE ( Node_PK = 1 AND Datetime_UTC >= '1981-01-01 00:00:00 +00:00' AND Datetime_UTC <= '2010-12-31 00:00:00 +00:00' ) 
    ORDER BY Datetime_UTC ASC;


SELECT Datetime_UTC,Precip_mmpd FROM [PRISM].[Precip_Daily]
	WHERE ( Node_PK = 1 AND YEAR(Datetime_UTC) = 1981)
	ORDER BY Datetime_UTC ASC;

SELECT P.Datetime_UTC, P.Precip_mmpd, Tx.Tmax_C, Ta.Tmean_C, Tn.Tmin_C, Dp.DewPtT_C
	FROM [PRISM].[Precip_Daily] AS P
		INNER JOIN [PRISM].[Tmax_Daily] AS Tx
			On ( P.Datetime_UTC = Tx.Datetime_UTC AND P.Node_PK = Tx.Node_PK )
		INNER JOIN [PRISM].[Tmean_Daily] AS Ta
			On ( P.Datetime_UTC = Ta.Datetime_UTC AND P.Node_PK = Ta.Node_PK )
		INNER JOIN [PRISM].[Tmin_Daily] AS Tn
			On ( P.Datetime_UTC = Tn.Datetime_UTC AND P.Node_PK = Tn.Node_PK )
		INNER JOIN [PRISM].[TAveDewPt_Daily] AS Dp
			On ( P.Datetime_UTC = Dp.Datetime_UTC AND P.Node_PK = Dp.Node_PK )
	WHERE ( P.Node_PK = 1 AND YEAR(P.Datetime_UTC) = 1981)
	ORDER BY P.Datetime_UTC ASC;

-- 10 minutes
SELECT P.Datetime_UTC, P.Precip_mmpd, Tx.Tmax_C, Tn.Tmin_C 
	FROM [CMIP5].[Precip_Daily] AS P
		INNER JOIN [CMIP5].[Tmax_Daily] AS Tx
			on ( P.Datetime_UTC = Tx.Datetime_UTC AND P.Node_PK = Tx.Node_PK AND P.Model_PK = Tx.Model_PK )
		INNER JOIN [CMIP5].[Tmin_Daily] AS Tn
			on ( P.Datetime_UTC = Tn.Datetime_UTC AND P.Node_PK = Tn.Node_PK AND P.Model_PK = Tn.Model_PK )
	WHERE ( P.Node_PK = 2 AND P.Model_PK = 5 AND YEAR(P.Datetime_UTC) = 1981)
	ORDER BY P.Datetime_UTC ASC;


SELECT Datetime_UTC, Precip_mmpd FROM [CMIP5].[Precip_Daily]
	WHERE ( Node_PK = 2 AND Model_PK = 5 AND YEAR(Datetime_UTC) = 1981)
	ORDER BY Datetime_UTC ASC;

SELECT Datetime_UTC, Model_PK, Precip_mmpd FROM [CMIP5].[Precip_Daily]
	WHERE Node_PK = 2 AND YEAR(Datetime_UTC) > 1980
	ORDER BY Datetime_UTC, Model_PK ASC;

