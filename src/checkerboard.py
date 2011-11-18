#!/usr/bin/env python
import freenect
import matplotlib.pyplot as mp
import signal
import frame_convert
import scipy
from cv import fromarray,FindChessboardCorners, DrawChessboardCorners


mp.ion()
image_rgb = None
image_depth = None
keep_running = True
width_checker = 6
height_checker = 9



def display_depth(dev, data, timestamp):
    global image_depth
    data = frame_convert.pretty_depth(data)
    mp.gray()
    mp.figure(1)
    if image_depth:
        image_depth.set_data(data)
    else:
        image_depth = mp.imshow(data, interpolation='nearest', animated=True)
    mp.draw()


def display_rgb(dev, data, timestamp):
    global image_rgb
    mp.figure(2)
    if image_rgb:
        corners = FindChessboardCorners(data, (6,9))
        for co in corners[1]:
            #line_coords = find_line(corners[1])
            #for co in line_coords:
            #    data = set_dot(co[0],co[1],data)
            
            data = set_dot(co[0], co[1], data)
        image_rgb.set_data(data)
    else:
        image_rgb = mp.imshow(data, interpolation='nearest', animated=True)
    mp.draw()
    
def set_dot(x,y, im):
    width = len(im[0])
    height = len(im)
    for i in xrange(15):
        if (y - 7 + i) > 0 and (y + 7 + i) < height:
            im[y - 7 + i][x] = [255,0,0]
        if (x - 7 + i) > 0 and (x + 7 + i) < width:
            im[y][x - 7 + i] = [255,0,0]
            
    return im
    
def find_line(corners):
    global width_checker
    global height_checker
    number_corners = len(corners)
    result = []    
    p0 = (0,0)
    p1 = (corners[0][0],corners[0][1])
    p2 = (corners[0][0],corners[0][1]) 
    p3 = (0,0)     
    for cor in corners:
        if cor[0] > p0[0] and cor[1] > p0[1]:
            p0 = (cor[0], cor[1])
        if cor[0] < p0[0] and cor[1] < p0[1]:
            p1 = (cor[0], cor[1])

        if cor[0] < p2[0]:
            
            p2 = (cor[0], cor[1])
            
        if cor[0] > p3[0]:
            p3 = (cor[0], cor[1])
        
        
        
        result = [p0,p1,p2,p3]
 
    
    

    return result
    
    
    
    

def body(*args):
    if not keep_running:
        raise freenect.Kill


def handler(signum, frame):
    global keep_running
    keep_running = False


print('Press Ctrl-C in terminal to stop')
signal.signal(signal.SIGINT, handler)
freenect.runloop(depth=display_depth,
                 video=display_rgb,
                 body=body)
