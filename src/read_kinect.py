"""
#!/usr/bin/env python
import sys
sys.path.append("/usr/local/lib/python2.6/site-packages")

import freenect
import cv
#import frame_convert

cv.NamedWindow('Depth')
cv.NamedWindow('Video')
print('Press ESC in window to stop')


def get_depth():
    return freenect.sync_get_depth()[0]
    #return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])


def get_video():
    return freenect.sync_get_video()[0]
    #return frame_convert.video_cv(freenect.sync_get_video()[0])


while True:
    cv.ShowImage('Depth', get_depth())
    cv.ShowImage('Video', get_video())
    if cv.WaitKey(10) == 27:
        break
"""

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
try:
    import cv
except:
    import opencv
import numpy as np
import freenect
#import frame_convert

def main():
    """ 
    note: the get_video and get_depth functions in freenect return an image plus
    a timestamp
    
    """
    raw_input('\nLet\'s view an rgb image from the kinect:\n(Press enter)')

    i = 0
   # while 1:
##        print 'loop de loop'
##    i = i+1
##    if i%10 == 0:
    try:
        depth = freenect.sync_get_depth()[0]
##            print 'depth:', depth
        plt.imshow(np.flipud(depth), origin="bottom")
        #plt.draw()
        
##            rgb = freenect.sync_get_video()[0]
##            print 'rgb:', rgb
##            plt.subplot(1,2,2)
##            plt.imshow(np.flipud(rgb), origin="bottom")

    except:
        print '\nHum, something went wrong. Try again...'
    plt.show()

if __name__ == "__main__":
    print '\n*** Test application to read and display Kinect data ***\n'
    main()
