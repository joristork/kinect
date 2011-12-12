#!/usr/bin/env python
import scipy as sp
import numpy as np
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 :
        try: 
            rgb_im = np.load(sys.argv[1])
            if len(sys.argv) == 3: 
                sp.misc.imsave(sys.argv[2], rgb_im)
            else:
                sp.misc.imsave(sys.argv[1][0:-3] + "png", rgb_im)
        except:
           print "Invalid arguments"
