Quick Start
===================
A sample data field is provided in the samples directory. Following examples are using that file.

Plotting smoother degree distribution
-------------------------------------
>>> from DoaProcessor import DoaProcessor
>>> d = DoaProcessor('./samples/sample.csv',4)
>>> # You can tweak value of sigma to change the smoothness
>>> d.getPeakDegree(sigma=2,group='group-1')

.. image:: images/peak-1.png

Degree distribution plot will help you in understanding the directions for each speaker. For instance, the above figure
shows that highly captured directions are around 0, 100, 180,300 degrees.


Extracting speaking time for each speaker
-------------------------------------------
In order to extract the speaking time, you need to specify the corresponding degrees for each speaker.
This knowledge can be gained from the sitting arrangement of speakers around microphone arrays. You can also learn about it by manually exploring the degree distribution.

>>> from DoaProcessor import DoaProcessor
>>> d = DoaProcessor('./samples/sample.csv',4)
>>> # manually setting directions for each user
>>> d.setDegreeForSpeaker(group='group-',[30,104,194,315])
>>> d.getSpeakingTime(plot=True,time='sec',group='group-1')

.. image:: images/spk.png


Generating social network
----------------------------
>>> from DoaProcessor import DoaProcessor
>>> d = DoaProcessor('./samples/sample.csv',4)
>>> # manually setting directions for each user
>>> d.setDegreeForSpeaker(group='group-',[30,104,194,315])
>>> d.drawNetowrk(group='group-1')

.. image:: images/net.png
