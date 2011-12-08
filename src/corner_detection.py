#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np
import sys


cv.NamedWindow('Depth')
cv.NamedWindow('RGB')
points = []
keep_running = True
capture = False # Not necessery, but defined for clearity 
fake = False

depth_np = None
rgb_np = None

def displaypoints(im, points):
    """ Display points in a given images, used for rgb and depth """
    if len(points) >= 1:
        cv.Circle(im,points[0],4,(0,255,0),-1)
        if len(points) >= 2:
            cv.Circle(im,points[1],4,(255,0,0),-1)
            cv.Line(im,points[0],points[1],(0,0,0),2)
        if len(points) >= 3:
            cv.Circle(im,points[2],4,(0,0,255),-1)
            cv.Line(im,points[1],points[2],(255,0,0))
        if len(points) >= 4:
            cv.Circle(im,points[3],4,(0,0,0),-1)
            cv.Line(im,points[2],points[3],(255,0,0))
            cv.Line(im,points[3],points[0],(0,0,0),2)
        if len(points) == 8:
            cv.Circle(im,points[4],4,(0,255,0),-1)
            cv.Circle(im,points[5],4,(255,0,0),-1)
            cv.Circle(im,points[6],4,(0,0,255),-1)
            cv.Circle(im,points[7],4,(0,0,0),-1)
            cv.Line(im,points[4],points[5],(255,0,0))
            cv.Line(im,points[5],points[6],(255,0,0))
            cv.Line(im,points[6],points[7],(255,0,0))
            cv.Line(im,points[7],points[4],(255,0,0))

            cv.Line(im,points[4],points[0],(0,0,0),2)
            cv.Line(im,points[5],points[1],(255,0,0))
            cv.Line(im,points[6],points[2],(255,0,0))
            cv.Line(im,points[7],points[3],(255,0,0))


def print_instructions(im):
    """
    This function helps the user by giving instructions. Circles are drawn in
    a square to determine which corner needs to be clicked.
    """
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 1, 8)
    if len(points) == 1:
        cv.PutText(im,"Please right-click on the blue corner to begin the capture",(2, 20), font, (0,0,0))
        print_square(im)
        cv.Circle(im,(12,90),3,(0,0,0),-1)
        cv.Circle(im,(32,90),4,(255,0,0),-1)
        cv.Circle(im,(32,60),3,(0,0,0),-1)
        cv.Circle(im,(12,60),3,(0,0,0),-1)        
    elif len(points) == 2:
        cv.PutText(im,"Please right-click on the red corner to begin the capture",(2, 20), font, (0,0,0))
        print_square(im)
        cv.Circle(im,(12,90),3,(0,0,0),-1)
        cv.Circle(im,(32,90),3,(0,0,0),-1)
        cv.Circle(im,(32,60),4,(0,0,255),-1)
        cv.Circle(im,(12,60),3,(0,0,0),-1)             
        
    elif len(points) == 3:
        cv.PutText(im,"Please right-click on the black corner to begin the capture",(2, 20), font, (0,0,0))
        print_square(im)
        cv.Circle(im,(12,90),3,(0,0,0),-1)
        cv.Circle(im,(32,90),3,(0,0,0),-1)
        cv.Circle(im,(32,60),3,(0,0,0),-1)
        cv.Circle(im,(12,60),4,(0,0,0),-1)
    elif len(points) == 4:
        cv.PutText(im,"Use right-click to finalize the capture",(2, 20), font, (0,0,0))
    elif len(points) > 4:
        pass
    else:
        cv.PutText(im,"Please right-click on the green corner to begin the capture",(2, 20), font, (0,0,0))
        print_square(im) 
        cv.Circle(im,(12,90),4,(0,255,0),-1)
        cv.Circle(im,(32,60),3,(0,0,0),-1)
        cv.Circle(im,(32,90),3,(0,0,0),-1)
        cv.Circle(im,(12,60),3,(0,0,0),-1)     
    
    if len(points) <= 4:
        cv.PutText(im,"Use left-click to cancel and start a new capture",(2, 40), font, (0,0,0))    
    else:
        cv.PutText(im,"Use left-click to start a new capture",(2, 40), font, (0,0,0))     

def print_square(im):
    """
    This function makes the black square - that helps selecting corners - in
    the left corner of the rgb window 
    """ 
    cv.Line(im,(12,60),(12,90),(0,0,0))
    cv.Line(im,(32,60),(32,90),(0,0,0))
    cv.Line(im,(12,90),(32,90),(0,0,0))
    cv.Line(im,(12,60),(32,60),(0,0,0))    

def display_result(depth, data, p, screentitle):
    """
    This function will add the last information to the data that is displayed
    in a screen. In the rgb window, some text is added and in both windows
    the points that are clicked are added.
    """
    im = None
    data_old = np.array(data)
    if depth:
        im = frame_convert.pretty_depth_cv(data_old)        
    else:
        im = frame_convert.video_cv(data)
    displaypoints(im, p)
    im_cp = cv.CloneImage(im)
    if not depth:
        print_instructions(im_cp)
    
    cv.ShowImage(screentitle, im_cp)
    
    
def choose_data(data, saved, c, depth, p, screentitle):
    """
    This function is called by display_depth and display_rgb. The function
    choices which data will be displayed in the window that is specified by
    screentitle. If a capture is going on, the data will not change. The
    screen is paused.
    """
    if c:
        if saved == None:
            saved = data[:]
            # Used for working without a Kinect
            np.save(screentitle,saved)
            
        display_result(depth, saved, p, screentitle)
    else: 
        display_result(depth, data, p, screentitle)
    return saved

def display_depth(dev, data, timestamp):
    global keep_running, depth_np, points, capture
    """
    Handler for the Kinect. This functions is responible for all data displayed 
    in the "Depth" window. The image that is displayed is derived from "data".
    """        
    depth_np = choose_data(data, depth_np, capture, True, points, 'Depth')
    
    if cv.WaitKey(10) == 27:
        keep_running = False

def display_rgb(dev, data, timestamp):
    """
    Handler for the Kinect. This functions is responible for all data displayed 
    in the RGB window. The image that is displayed is derived from "data".
    """
    global keep_running, rgb_np, points, capture
    rgb_np = choose_data(data, rgb_np, capture, False, points, 'RGB')
    
    if cv.WaitKey(10) == 27:
        keep_running = False


def body(*args):
    global capture, depth_np, rgb_np, points
    """
    Handler for the Freenect. This is used to kill the Kinect and to do our
    calculations
    """
    if not keep_running:
        raise freenect.Kill
    if not capture and depth_np and rgb_np:
        print 
     
def handle_new_capture(depth, rgb):
    print "New data taken"
    global points
    points_3d = []
    for p in points:
        points_3d.append(np.array([p[0],p[1],depth[p[1]][p[0]]], dtype=float))
    green = points_3d[0]
    blue = points_3d[1]
    red = points_3d[2]
    black = points_3d[3]
    
    green_h = np.cross((blue - green),(black - green))
    green_h = green_h / np.linalg.norm(green_h)
    green_h = (green_h * 200) + green
    
    blue_h = np.cross((red - blue),(green - blue))
    blue_h = blue_h / np.linalg.norm(blue_h)    
    blue_h = (blue_h * 200) + blue

    red_h = np.cross((black - red),(blue - red))
    red_h = red_h / np.linalg.norm(red_h)    
    red_h = (red_h * 200) + red    
    
    black_h = np.cross((green - black),(red - black))
    black_h = black_h / np.linalg.norm(black_h)    
    black_h = (black_h * 200) + black    
    
    print green_h
    print blue_h
    print red_h
    print black_h
    
    points.append((int(green_h[0]),int(green_h[1])))
    points.append((int(blue_h[0]),int(blue_h[1])))
    points.append((int(red_h[0]),int(red_h[1])))
    points.append((int(black_h[0]),int(black_h[1])))
    print points



def mouseclick(event,x,y,flags,param):
    """
    Handler for a click in the HighGUI screen, used to determine the place
    of corners
    """
    global points, capture, depth_np, rgb_np, fake
    if len(points) < 4 and event == cv.CV_EVENT_LBUTTONUP:
        if len(points) == 0:
           capture = True
        if fake:
            points = [(216, 302), (490, 328), (463, 201), (302, 190)]
        else:
            points.append((x,y))
        print points
        
    elif len(points) >= 4 and len(points) < 8 and event == cv.CV_EVENT_LBUTTONUP :
        handle_new_capture(depth_np, rgb_np)
        
    if event == cv.CV_EVENT_RBUTTONUP:
        points = []
        capture = False
        depth_np = None
        rgb_np = None            

if __name__ == '__main__':
    cv.SetMouseCallback("RGB",mouseclick,None)
    if len(sys.argv) > 1:
        rgb_im = np.load("RGB.npy")
        depth_im = np.load("Depth.npy")
        if sys.argv[1] == "1":
            fake = True
        while(1):
            display_depth(None,depth_im,None)
            display_rgb(None,rgb_im,None)
    else: 
        freenect.runloop(depth=display_depth,
                         video=display_rgb,
                         body=body)
