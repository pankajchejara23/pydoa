Loading DoA data with `PyDoA`
==========================

By default, `whampy` can load the DR1 Full sky release of WHAM data from the fits file release.
This can be done with a provided local copy of the file::

	>>> from pydoa import DoaProcessor
	>>> # Load data file
	>>> survey = DoaProcessor('file-name.csv')
