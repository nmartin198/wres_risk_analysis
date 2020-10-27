# -*- coding: utf-8 -*-
"""
.. module:: WG_PrecipDepth
   :platform: Windows, Linux
   :synopsis: Contains logic for determining and selecting the precipitation depth for a day

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Uses a custom implementation of a mied exponential distribution
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
import numpy as np
from WG_Inputs import MON_MAX_BY_REGION, LOCA_GRID_MAP, MON_MAX_BY_PP
from WG_Inputs import MON_MAX_BY_PP_PRISM, H0_MAX_BY_PP, H1_MAX_BY_PP

# parameters
MAX_REC_24HR_PRECIP = 1825.0
"""Maximum recorded 24 hour precipitation depth in mm. This is from Reunion
Island on Jan. 7-8 1966 during Tropical Storm Denise. This could be used as 
the upper boundary for PDFs and CDFs"""
MAX_ATLAS14_24HR_PRECIP = 510.0
"""1000-yr, 24-hr depth from NOAA Atlas 14 in mm. Can also be used for upper
boundary for PDFs and CDFs."""
ATLAS14__350YR_24HR_PRECIP = 372.0
"""Average of 200-yr and 500-yr, 24-hr depth from NOAA Atlas 14 in mm. Can 
also be used for upper boundary for PDFs and CDFs."""
ATLAS14_150YR_24HR_PRECIP = 300.0
"""Average of 200-yr and 100-yr, 24-hr depth from NOAA Atlas 14 in mm. Can 
also be used for upper boundary for PDFs and CDFs."""
WD_THRESH = 0.2
"""Wet dry threshold as used in this study in millimeters. It provides the
minimum possible precipitation and so bounds our PDFs and CDFs"""



class CreateDistError(Exception):
    """Custom exception error for when something happens with a distribution
    """
    def __init__(self, arg):
        self.args = arg


class MixedExp(object):
    """Mixed exponential distribution object for use in the Weather 
    Generator"""
    
    def __init__( self, alpha, mu1, mu2, gridId, mon, SelOpt, cPeriod=1,
                  name="Custom mixed exponential" ):
        """Override of default initialization method. The maximum truncation value
        is determined separately for data period distributions as compared to 
        projection period distributions. 
        
        Args:
            alpha (float): mixing or proportionality coefficient
            mu1 (float): mean for exponential one
            mu2 (float): mean for exponential two
            gridId (int): grid index for this distribution
            mon (int): month index from 1-12
            SelOpt (int): Option for selecting the trunctation 1 = PRISM, 2 = LOCA
            cPeriod (int): projection period for distribution; only used if IsDP == false
            name (str): name for this distribution

        """
        super().__init__()
        # do some checks and assign our properties
        if not isinstance( alpha, (int, float)):
            ErrorMsg = "Alpha must be an int or a float!!!"
            raise CreateDistError( ErrorMsg )
        if (alpha <= 0.0) or (alpha >= 1.0):
            ErrorMsg = "Alpha weight must be between 0.0 and 1.0 for a mixed " \
                       "distribution"
            raise CreateDistError( ErrorMsg )
        self.alpha = float( alpha )
        if not isinstance( mu1, (int, float)):
            ErrorMsg = "Mean part 1 must be an int or a float!!!"
            raise CreateDistError( ErrorMsg )
        if ( mu1 <= 0.0 ) or (mu1 >= 500.0 ):
            ErrorMsg = "Mean part 1 must be between 0.0 and 500.0 for a " \
                       "mixed exponential distribution"
            raise CreateDistError( ErrorMsg )
        self.mu1 = float( mu1 )
        if not isinstance( mu2, (int, float)):
            ErrorMsg = "Mean part 2 must be an int or a float!!!"
            raise CreateDistError( ErrorMsg )
        if ( mu2 <= 0.0 ) or (mu2 >= 500.0 ):
            ErrorMsg = "Mean part 2 must be between 0.0 and 500.0 for a " \
                       "mixed exponential distribution"
            raise CreateDistError( ErrorMsg )
        self.mu2 = float( mu2 )
        # now assign the name
        self.name = str( name )
        # we want to set some of our other properties now
        self._stats()
        # now create the CDF to use in calculations. We need to find our 
        # max for truncation purposes
        if ( SelOpt <= 1 ):
            cRegionID = LOCA_GRID_MAP[gridId][mon]
            cMaxDepth = MON_MAX_BY_REGION[mon][cRegionID-1]
        elif ( SelOpt == 2 ):
            cMaxDepth = MON_MAX_BY_PP[cPeriod][(mon - 1)]
        elif ( SelOpt == 3 ):
            cMaxDepth = MON_MAX_BY_PP_PRISM[cPeriod][(mon - 1)]
        elif ( SelOpt == 4 ):
            cMaxDepth = H0_MAX_BY_PP[cPeriod][(mon - 1)]
        else:
            cMaxDepth = H1_MAX_BY_PP[cPeriod][(mon - 1)]
        # end if
        self.calcCDF( MaxDepth=cMaxDepth )
    
    def _stats(self, ):
        """Convenience function to calculate some statistics, using the 
        defining parameters
        """
        self.rate1 = 1.0 / self.mu1
        self.rate2 = 1.0 / self.mu2
        self.var1 = 1.0 / (self.rate1**2.0)
        self.var2 = 1.0 / (self.rate2**2.0)
        self.mean = (self.alpha * self.mu1) + ( ( 1.0 - self.alpha) * self.mu2 )
        self.var = ( ( self.alpha * self.mu1**2.0) + ( ( 1.0 - self.alpha ) *
                      self.mu2**2.0 ) + ( self.alpha * ( 1.0 - self.alpha ) *
                      ( self.mu1 - self.mu2)**2.0 ) )
    
    def _pdf(self, x):
        """Internal method for calculating the probability density for any
        particular X value. X could also be a numpy array.
        
        Args:
            x (float or np.float): value to calculate the pdf for
            
        Returns:
            fpd_x (float or np.float): probability density for x
        """
        fpd_x = ( ( ( self.alpha / self.mu1 ) * 
                    np.exp( ( ( -1.0 * x ) / self.mu1 ), dtype=np.float64 ) )
                    + ( ( ( 1.0 - self.alpha ) / self.mu2 ) * 
                         np.exp( ( ( -1.0 * x ) / self.mu2 ), dtype=np.float64 ) ) )
        # now return 
        return fpd_x
    
    def calcCDF( self, MaxDepth=ATLAS14_150YR_24HR_PRECIP ):
        """Calculate the cumulative distribution function CDF.
        Use the set boundaries to bound this calculation.

        KWargs:
            MaxDepth (float): maximum truncation depth for distribution
        """
        AllXs = [ 1.0 * x for x in range(1, int(MaxDepth), 1) ]
        AllXs.insert( 0, WD_THRESH )
        AllXs.append( MaxDepth )
        NumX = len( AllXs )
        npAllXs = np.array( AllXs, dtype=np.float64 )
        ExtendedPMF = np.zeros( NumX, dtype=np.float64 )
        ExtendedPMF[1:] = self._pdf( npAllXs[1:] )
        InterPs = np.array( [round(0.01 * x, 2) for x in range(101)],
                            dtype=np.float64 )
        cumPMFpre = np.cumsum( ExtendedPMF, dtype=np.float64 )
        MaxPMF = cumPMFpre.max()
        CutOffInd = np.argmax( cumPMFpre == MaxPMF )
        truncPMF = cumPMFpre[:(CutOffInd + 1)]
        scalePMF = truncPMF / MaxPMF
        TotInds = len( InterPs )
        ValuePs = np.interp( InterPs, scalePMF, npAllXs[:(CutOffInd + 1)] )
        self.cdf = np.zeros( (2, TotInds), dtype=np.float64 )
        self.cdf[0,:] = ValuePs
        self.cdf[1,:] = InterPs
    
    def ranval1( self, val ):
        """With the specified val between 0.0 and 1.0, which is essentially
        a probability, return the corresponding value from the cdf.
        
        Args:
            val (float): between [0.0 and 1.0]
            
        Returns:
            pdep (float): the corresponding depth from the distribution
            
        """
        pdep = np.interp( val, self.cdf[1,:], self.cdf[0,:] )
        return pdep
    
    def ranArray( self, arr ):
        """With the specified array of values between 0.0 and 1.0, which is 
        essentially probabilities, return the corresponding value from the cdf.
        
        Args:
            arr (np.array): floats between [0.0 and 1.0]
            
        Returns:
            pdep (np.array): the corresponding depth from the distribution
            
        """
        pdep = np.interp( arr, self.cdf[1,:], self.cdf[0,:] )
        return pdep


class PrecipSampler(object):
    """A precipitation depth probability sampler. 
    
    Use this to track the random
    state and produce reproduceable sampling sequences. This uses the numpy
    random.uniform distribution to draw the random numbers.
    """
    
    def __init__( self, pd_sample_seed=None ):
        """Default initialization method
        
        KWargs:
            pd_sample_seed (int): the seed to use for the sampler

        """
        super().__init__()
        self.ranstate = np.random.RandomState(seed=pd_sample_seed)
    
    def getSingleVal( self, ):
        """Produce a single value from the random sampler from a uniform
        distribution between [0.0 - 1.0]
        """
        return self.ranstate.uniform(low=0.0, high=1.0)
    
    def getSampleArray( self, N ):
        """Produce a sample of random numbers between 0.0 and 1.0 of size N.
        Will return a numpy array"""
        return self.ranstate.uniform(low=0.0, high=1.0, size=N)


#EOF