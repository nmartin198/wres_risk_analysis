# src: Framework Scripts and Simulation Modules

This directory contains all of the simulation code used to implement the 
framework. There are three independent but related categories in this folder.

1. **wg_tm**: Full framework implementation with monthly water balance model
   * Provides synthetic weather output for each realization.
   * Provides monthly water balance output for each realization.

2. **mHSP2**: Daily time step, continuous simulation water balance model.
   * Requires synthetic weather generator output for each realization from
     **wg_tm**
   * Provides daily water balance output for each realization.

3. **Post Processing**: provides modules and scripts for processing
   realization-based outputs to probabilistic outputs.

