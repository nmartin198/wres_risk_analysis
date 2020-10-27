# Data Sets and the Project Database

Two weather parameter data sets are used in this study.

1. [PRISM historical climate data](https://prism.oregonstate.edu/explorer/)

2. [Downscaled CMIP3 and CMIP5 Climate and Hydrology Projection](https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/)

These data sets are publicly available and are not reproduced in this
repository.

However, a custom SQLServer database was created to facilitate processing 
and analysis of these data sets. The Python scripts and T-SQL command 
snippets in this folder structure provide for creation of the database
and interal tables and for querying the database for processing and 
analysis.

* **Python**: A collection of Python scrips for populating database tables 
  and for querying the database for analysis of the component data sets.

* **T SQL**: A text file containing various T-SQL syntax commands for 
  database and table creation and for query syntax optimization.


