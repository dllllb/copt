# OSMNX installation
Benchmark solution uses osmnx library which can couse some problems with depenedcies version. To install libraries use the following command:
```conda config --prepend channels conda-forge
conda create -n ox --strict-channel-priority osmnx```
All other libraries should be install in this new ox enviroment.