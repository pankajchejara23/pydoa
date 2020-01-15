====================================
Documenation for DoaProcessor class
====================================

DoA data file contains the direction of sound detected by the microphone array. This class provides functions to process DoA (Direction of Arrival) datafile.

Loading data file
-----------------
The data file should contain data in the following format::

   group-label,timestamp,direction

A snapshot of the data file is shown in the below image

>>> from pydoa import DoaProcessor
>>> # Specify name of data file and number of speakers
>>> doa = DoaProcessor('file.csv',4)
