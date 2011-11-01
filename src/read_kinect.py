#!/usr/bin/env python
"""
:synopsis:  Kinect project for part 2 of Beeldbewerken course, BSc
            Informatica, University of Amsterdam. Depends on the OpenKinect's
            python wrappers, obtainable via git:
            https://github.com/OpenKinect/libfreenect.git

.. moduleauthor:: Joris Stork <joris@wintermute.eu>

"""

__author__ = "Joris Stork"

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv
import numpy as np
import freenect

def main():
    raw_input('\nLet\'s view an rgb image from the kinect:\n(Press enter)')
    try:
        depth, rgb = freenect.sync_get_depth(), freenect.sync_get_video()
        plt.subplot(1,1,1)
        plt.imshow(np.flipud(rgb))
        plt.show()
    except:
        print '\nHum, something went wrong. Try again...'
        main()


if __name__ == "__main__":
    print '\n*** Test application to read and display Kinect data ***\n'
    main()
