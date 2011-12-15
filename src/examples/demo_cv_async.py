#!/usr/bin/env python
import freenect
import cv
import frame_convert

cv.NamedWindow('Depth')
cv.NamedWindow('RGB')
keep_running = True


def display_depth(dev, data, timestamp):
    global keep_running
    #cv.ShowImage('Depth', frame_convert.pretty_depth_cv(data))
    if cv.WaitKey(10) == 27:
        keep_running = False


def display_rgb(dev, data, timestamp):
    global keep_running
    cvdata = frame_convert.video_cv(data[:160,:213])
    resized = cv.CreateImage((640, 480), cv.IPL_DEPTH_8U, 3)
    cv.Resize(cvdata, resized)
    grey = cv.CreateImage((640, 480), cv.IPL_DEPTH_8U, 1) 
    cv.CvtColor(resized, grey, cv.CV_BGR2GRAY)
    cv.ShowImage('RGB', resized)
    cv.ShowImage('Depth', grey)
    if cv.WaitKey(10) == 27:
        keep_running = False


def body(*args):
    if not keep_running:
        raise freenect.Kill


print('Press ESC in window to stop')
freenect.runloop(depth=display_depth,
                 video=display_rgb,
                 body=body,
                 vmode=freenect.VIDEO_IR_8BIT)
