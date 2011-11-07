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
import frame_convert

def main():
    """ 
    note: the get_video and get_depth functions in freenect return an image plus
    a timestamp
    
    """
    raw_input('\nLet\'s view an rgb image from the kinect:\n(Press enter)')
    while 1:
        print 'loop de loop'
        try:
            print 'checkpoint 1'
            depth = freenect.sync_get_depth()[0]
            print 'checkpoint 5'
            plt.subplot(1,2,2)
            print 'checkpoint 6'
            plt.imshow(np.flipud(depth))
            print 'checkpoint 7'
            
            rgb = freenect.sync_get_video()[0]
            print 'checkpoint 2'
            plt.subplot(1,1,1)
            print 'checkpoint 3'
            plt.imshow(np.flipud(rgb))
            print 'checkpoint 4'


            plt.show()
            print 'checkpoint 8'

        except:
            print '\nHum, something went wrong. Try again...'
            main()


if __name__ == "__main__":
    print '\n*** Test application to read and display Kinect data ***\n'
    main()
