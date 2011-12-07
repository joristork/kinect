#!/usr/bin/env python
import freenect
import cv
import frame_convert


cv.NamedWindow('Depth')
cv.NamedWindow('RGB')
points = []
keep_running = True


def display_depth(dev, data, timestamp):
    global keep_running
    cv.ShowImage('Depth', frame_convert.pretty_depth_cv(data))
    if cv.WaitKey(10) == 27:
        keep_running = False


def display_rgb(dev, data, timestamp):
    global keep_running, points
    im = frame_convert.video_cv(data)
    if len(points) >= 1:
        cv.Circle(im,points[0],4,(0,255,0),-1)
        if len(points) >= 2:
            cv.Circle(im,points[1],4,(255,0,0),-1)
            cv.Line(im,points[0],points[1],(255,0,0))
        if len(points) >= 3:
            cv.Circle(im,points[2],4,(0,0,255),-1)
            cv.Line(im,points[1],points[2],(255,0,0))
        if len(points) == 4:
            cv.Circle(im,points[3],4,(0,0,0),-1)
            cv.Line(im,points[2],points[3],(255,0,0))
            cv.Line(im,points[3],points[0],(255,0,0))
            
    cv.ShowImage('RGB', im)
    
    # This creates a IPL image: print type(frame_convert.video_cv(data))
    
    
    
    if cv.WaitKey(10) == 27:
        keep_running = False


def body(*args):
    if not keep_running:
        raise freenect.Kill

def mouseclick(event,x,y,flags,param):
    global points
    if len(points) < 4 and event == cv.CV_EVENT_LBUTTONUP:
        points.append((x,y))
        print points
    if event == cv.CV_EVENT_RBUTTONUP:
        points = []


print('Press ESC in window to stop')
cv.SetMouseCallback("RGB",mouseclick,None)


freenect.runloop(depth=display_depth,
                 video=display_rgb,
                 body=body)
