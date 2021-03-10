# wres_risk_analysis

This repository provides a collection of Python modules and Jupyter
Notebooks for implementing ["Watershed-Scale, Probabilistic Risk Assessment of Water Resources Impacts from Climate Change"](https://doi.org/10.3390/w13010040) and ["Risk Assessment of Future Climate and Land Use/Land Cover Change Impacts on Water Resources"](https://doi.org/10.3390/hydrology8010038) for a specific study site in west-central Texas.

   

## About the Project

This project is a scientific study of future impacts to water resources
and is not a code-based project. The study does present a framework 
for analysis of water resources risks from systemic changes. A site-specific 
application of this framework was implemented as part of the study to examine
two future systemic changes: 1) climate change and 2) land use and land cover
change.

The source code for this custom implementation is included 
as part of this project. GitHub is used to provide open access
to custom simulation and processing code that was used in the study. 
There is not a 'release' or software 'product' associated with this
project.

   

## What is in the Project?

There are four top level sub-directories within the project structure.

1. [**Data**](https://github.com/nmartin198/wres_risk_analysis/tree/main/data) : Holds 
   Python scripts and a T-SQL script for processing 
   and formatting the data sets used in this study. The data sets
   used in this study are all publicly available at the links below.
   * [PRISM historical climate data](https://prism.oregonstate.edu/explorer/)
   * [Downscaled CMIP3 and CMIP5 Climate and Hydrology Projection](https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/)

2. [**Jupter Notebooks**](https://github.com/nmartin198/wres_risk_analysis/tree/main/jupyter_notebooks): 
   Provides copies of Jupyter Notebooks used for data processing and 
   analysis and for simulation results processing and analysis.

   * The file sizes for these notebooks tends to be large so you may
     need to reload multiple times or just copy it to a local location.

3. [**Model Inputs**](https://github.com/nmartin198/wres_risk_analysis/tree/main/model_inputs): 
   Holds a copy of the input file for the mHSP2 model used in the study. 
   All other model inputs are included in the source code files.

4. [**src**](https://github.com/nmartin198/wres_risk_analysis/tree/main/src): Python 
   source code for the framework.

   

## Authors

* Nick Martin <img src="ORCIDiD_iconvector.svg" alt="ORCID" width="16" height="16" /><a href="https://orcid.org/0000-0002-6432-7390">https://orcid.org/0000-0002-6432-7390</a>
   - nmartin@swri.org
   - nick.martin@stanfordalumni.org

   

## License

This project is licensed under the GNU General Public License v.3.0 - see the [LICENSE](LICENSE) file for details.

   

## Acknowledgments

This work was funded by [Southwest Research Institute](https://www.swri.org/groundwater-and-surface-water-analysis-and-modeling) internal research and 
development grant 15-R8937.
