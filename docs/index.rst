PyDoA Documentation
========================

The PyDoA package provides functionality of processing and visualizing DoA data.
It provides the following main features:

-The ability to map degrees to speakers
-The ability to extract speaking time for each speaker
-The ability to generate window-wise speaking time
-The ability to generate interaction network
_The ability to generate a web-based dashboard for visualizing the DoA data in an interactive manner.

Quick Start
-----------

Here is a simple script demonstrating the PyDoA:

    >>> from pydoa import DoAProcessor
    >>> # Load the Survey
    >>> doa = DoAProcessor('speak.csv')

    >>> # Visualize distrbution of degrees
    >>> doa.generateDistribution()



Getting started
^^^^^^^^^^^^^^^

.. toctree::
  :maxdepth: 1

  installing.rst
  loading_data.rst
