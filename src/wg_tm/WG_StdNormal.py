# -*- coding: utf-8 -*-
"""
.. module:: WG_StdNormal
   :platform: Windows, Linux
   :synopsis: Classes and logic to handle the white noise error term

.. moduleauthor:: Nick Martin <nick.martin@stanfordalumni.org>

Work with the white noise error term used in calculation of other weather parameters.
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
from scipy import stats as scstats
from WG_PrecipDepth import CreateDistError


class StdNormal(object):
    """Standard normal distribution object for use in the Weather 
    Generator. Standard normals are used in other weather parameter error
    terms."""
    
    def __init__(self, loc=0.0, scale=1.0, name="Custom standard normal" ):
        """Override of default initialization method"""
        super().__init__()
        # do some checks and assign our properties
        if not isinstance( loc, (int, float) ):
            ErrorMsg = "loc must be a number!!!"
            raise CreateDistError( ErrorMsg )
        if not isinstance( scale, (int, float ) ):
            ErrorMsg = "scale must be a number!!!"
            raise CreateDistError( ErrorMsg )
        self.name = name
        self.stnorm = scstats.norm( loc=loc, scale=scale )
    
    def ranval1( self, rstate):
        """Use the random state sampler to return a value back from distribuiton
        
        Args:
            rstate (np.random_state): the random state for the sampler
            
        Returns:
            numd (int): the sampled number of days for the spell length
            
        """
        numda = self.stnorm.rvs( size=1, random_state=rstate )
        numd = numda[0]
        return numd
    
    def ranArray( self, asize, rstate ):
        """Sample asize values and put them in an array
        
        Args:
            asize (int) = size of the return array
            rstate (np.random_state): the random state for the sampler
            
        Returns:
            numda (np.array): the corresponding array of spell lengths
            
        """
        numda = self.stnorm.rvs( size=asize, random_state=rstate )
        return numda


class ErrorTSampler(object):
    """An error term probability sampler. Use this to track the random
    state and produce reproduceable sampling sequences. This uses the numpy
    random.uniform distribution to draw the random numbers.
    """
    
    def __init__( self, seed=None ):
        """Default initialization method
        
        Kwargs:
            seed (int): default is none but sets the seed for the object

        """
        super().__init__()
        self.ranstate = np.random.RandomState(seed=seed)
    
    def getSingleVal( self, ):
        """Produce a single value from the random sampler from a uniform
        distribution between [0.0 - 1.0]
        """
        return self.ranstate.uniform(low=0.0, high=1.0)
    
    def getSampleArray( self, N ):
        """Produce a sample of random numbers between 0.0 and 1.0 of size N.
        
        Will return a numpy array
        """
        return self.ranstate.uniform(low=0.0, high=1.0, size=N)

#EOF