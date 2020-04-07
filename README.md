# PyDoA
##### A Python Package for Processing and Visualizing DoA (Direction of Arrival) data from Group Discussion
PyDoA is a python package aiming at simplifying processing the DoA (Direction of Arrival) data captured from microphone arrays. DoA data contains direction of sound arrival which in the case of circular array varies from 0 to 360 degrees.

### Installation

You can install PyDoA using pip::

<pre> pip install pydoa </pre>

To install the latest developer version of PyDoA you can type::
<pre>
    git clone https://github.com/pankajchejara23/pydoa.git
    cd pydoa
    python setup.py install
</pre>

You may need to add the ``--user`` option to the last line `if you do not
have root access <https://docs.python.org/2/install/#alternate-installation-the-user-scheme>`_.
You can also install the latest developer version in a single line with pip::
<pre>
    pip install git+https://github.com/pankajchejara23/pydoa.git
</pre>
### Dependencies
 * requests
 * pandas
 * networkx
 * scipy
 * dash
 * numpy
 * matplotlib
 * dash-bootstrap-components
 * dash-cytoscape




### Full Documentation
 https://pydoa.readthedocs.io

### License
MIT License

Copyright (c) 2020 Pankaj Chejara

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
