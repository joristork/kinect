#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np
import sys


points = []
keep_running = True
capture = False # Not necessery, but defined for clearity 
fake = False

depth_np = None
rgb_np = None
cubic = []

intrinsic_matrix = None
distortion = None

def displaypoints(im, points):
    """ Display points in a given images, used for rgb and depth """
    if len(points) >= 1:
        cv.Circle(im,points[0],4,(0,255,0),-1)
        if len(points) >= 2:
            cv.Circle(im,points[1],4,(255,0,0),-1)
            cv.Line(im,points[0],points[1],(255,0,0))
        if len(points) >= 3:
            cv.Circle(im,points[2],4,(0,0,255),-1)
            cv.Line(im,points[1],points[2],(255,0,0))
        if len(points) >= 4:
            cv.Circle(im,points[3],4,(0,0,0),-1)
            cv.Line(im,points[2],points[3],(255,0,0))
            cv.Line(im,points[3],points[0],(255,0,0))
        if len(points) == 8:
            cv.Circle(im,points[4],4,(0,255,0),-1)
            cv.Circle(im,points[5],4,(255,0,0),-1)
            cv.Circle(im,points[6],4,(0,0,255),-1)
            cv.Circle(im,points[7],4,(0,0,0),-1)
            cv.Line(im,points[4],points[5],(0,0,0),2)
            cv.Line(im,points[5],points[6],(255,0,0))
            cv.Line(im,points[6],points[7],(255,0,0))
            cv.Line(im,points[7],points[4],(0,0,0),2)

            cv.Line(im,points[4],points[0],(0,0,0),2)
            cv.Line(im,points[5],points[1],(255,0,0))
            cv.Line(im,points[6],points[2],(255,0,0))
            cv.Line(im,points[7],points[3],(255,0,0))


def print_instructions(im):
    """
    This function helps the user by giving instructions. Circles are drawn in
    a square to determine which corner needs to be clicked.
    """
    global capture
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
    elif len(points) == 8:
        if capture:
            cv.PutText(im,"Use right-click to finalize the capture",(2, 20), font, (0,0,0))
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
    cv.Line(im,(12,60),(12,90),(255,0,0))
    cv.Line(im,(32,60),(32,90),(255,0,0))
    cv.Line(im,(12,90),(32,90),(255,0,0))
    cv.Line(im,(12,60),(32,60),(255,0,0))    

def display_result(depth, data, p, screentitle):
    """
    This function will add the last information to the data that is displayed
    in a screen. In the rgb window, some text is added and in both windows
    the points that are clicked are added.
    """
    global cubic
    im = None
    data_old = np.array(data)
    if depth:
        im = frame_convert.pretty_depth_cv(data_old)        
        if len(p) == 4 and len(cubic) == 0:
            make_cubicle(data)        
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
    
    key = ( cv.WaitKey(10) ) % 0x100
    if key == 27:
        raise freenect.Kill
        
def display_rgb(dev, data, timestamp):
    """
    Handler for the Kinect. This functions is responible for all data displayed 
    in the RGB window. The image that is displayed is derived from "data".
    """
    global keep_running, rgb_np, points, capture
    rgb_np = choose_data(data, rgb_np, capture, False, points, 'RGB')
    

    key = ( cv.WaitKey(10) ) % 0x100
    if key == 27:
        raise freenect.Kill


def body(*args):
    global capture, depth_np, rgb_np, points
    """
    Handler for the Freenect. This is used to kill the Kinect and to do our
    calculations
    """
    if not keep_running:
        raise freenect.Kill

def isNaN(num):
    return num != num

def make_cubicle(depth):
    """
    This function is responsible for all the calculations. For now, it adds
    points to the image so that we can see the 3 dimensional cubicle in which
    we are working. Later this function will be used to scan for values.
    """
    global points, cubic
    # Height of cubicle
    height = 200
    
    for i in xrange(4):
        cubic.append(np.array([points[i][0],points[i][1],depth[points[i][1]][points[i][0]]], dtype=float))
        if depth[points[i][1]][points[i][0]] > 2000:
            print "Point no. ", i, " is probably in a blind spot. Please start over."
    
    
    for i in xrange(4):
        cubic = cubic + [np.cross((cubic[((i + 1) % 4)] - cubic[i]),(cubic[((i + 3) % 4)] - cubic[i]))]
        cubic[i + 4] = cubic[i + 4] / np.linalg.norm(cubic[i + 4]) 
        cubic[i + 4] = (cubic[i + 4] * height) + cubic[i]
        
        if not isNaN(cubic[i + 4][0]) and not isNaN(cubic[i + 4][1]):
            points.append((int(cubic[i + 4][0]),int(cubic[i + 4][1])))         
        
    


def handle_new_capture(depth, rgb):
    """
    This function is responsible for all the calculations. For now, it adds
    points to the image so that we can see the 3 dimensional cubicle in which
    we are working. Later this function will be used to scan for values.
    """
    print "New data captured"
    global cubic, intrinsic_matrix, distortion
    
    
    if intrinsic_matrix == None or distortion == None:
       print "Can't handle the capture because the intrinsic matrix and distortion aren't set yet."

    
    objectpoints = [(0,100,0),(100,100,0),(100,100,200),(0,100,200)]
    npoints = len(objectpoints)
    imagepoints = []
    
    o_points = cv.CreateMat(npoints, 3, cv.CV_32FC1)
    i_points = cv.CreateMat(npoints, 2, cv.CV_32FC1)
    

    for i in xrange(npoints):
        o_points[i, 0] = objectpoints[i][0]
        o_points[i, 1] = objectpoints[i][0]   
        o_points[i, 2] = objectpoints[i][0]
        i_points[i, 0] = cubic[i][0]
        i_points[i, 1] = cubic[i][1]
    
    
    rvec = cv.CreateMat(1, 3, cv.CV_32FC1)
    tvec = cv.CreateMat(1, 3, cv.CV_32FC1)
    cv.FindExtrinsicCameraParams2(o_points, i_points, intrinsic_matrix, distortion, rvec, tvec, useExtrinsicGuess=0)
    
    rotation = cv.CreateMat(3, 3, cv.CV_32FC1)
    translation = cv.CreateMat(3, 3, cv.CV_32FC1)
    cv.Rodrigues2(rvec, rotation)
    cv.Rodrigues2(tvec, translation)
    
    matrix = cv.CloneMat(rotation)
    for i in xrange(3):
       print matrix[i,0],"\t\t", matrix[i,1],"\t\t", matrix[i,2]
       
    rgb_cv = frame_convert.video_cv(rgb)
    dst = cv.CloneImage(rgb_cv)
    
    rvec_rgb = cv.CreateMat(2, 3, cv.CV_32FC1)
    
    for i in xrange(2):
        rvec_rgb[i,0] = rotation[i + 1,0] 
        rvec_rgb[i,1] = rotation[i + 1,1]
        rvec_rgb[i,2] = rotation[i + 1,2]
        
        
    cv.WarpAffine(rgb_cv, dst, rvec_rgb)
    
    cv.SaveImage("original.png", rgb_cv)
    cv.SaveImage("warped.png", dst)    
    
        
    print "New points"
    


def mouseclick(event,x,y,flags,param):
    """
    Handler for a click in the HighGUI screen, used to determine the place
    of corners
    """
    global points, capture, depth_np, rgb_np, fake, cubic
    if len(points) < 4 and event == cv.CV_EVENT_LBUTTONUP:
        if len(points) == 0:
           capture = True
        if fake:
            points = [(215, 300), (495, 328), (468, 199), (299, 187)]
        else:
            if not (x,y) in points:
                points.append((x,y))
            else:
                print "Warning: two points may not be in the same place"
            
    elif len(points) >= 4 and event == cv.CV_EVENT_LBUTTONUP and capture:
        handle_new_capture(depth_np, rgb_np)
        capture = False
        
    if event == cv.CV_EVENT_RBUTTONUP:
        points = []
        capture = False
        depth_np = None
        rgb_np = None         
        cubic = []

def generate_modelpoints(i_c, argv):
    if i_c == None and not (len(sys.argv) == 4 and sys.argv[3] == '1'):
        print "Error: The intrinsic matrix hasn't been calculated yet, please do that before you continue"
        return None
        

    global intrinsic_matrix, distortion, fake
    
    if len(sys.argv) == 4 and sys.argv[3] == '1':
        try:
            intrinsic_matrix = cv.Load("Camera_matrix.xml")
            distortion = cv.Load("Distortion.xml")         
        except: 
            print "Error: The intrinsic matrix hasn't been calculated yet, please do that before you continue"
            return None
    else:
        intrinsic_matrix = i_c[0]
        distortion = i_c[1]



    print "Press esc to stop"
    cv.NamedWindow('Depth')
    cv.NamedWindow('RGB')
    cv.SetMouseCallback("RGB",mouseclick,None)
    if len(argv) > 1 and argv[1] != "0":
        rgb_im = np.load("RGB.npy")
        depth_im = np.load("Depth.npy")
        if argv[1] == "1":
            fake = True

        while(1):
            try:
                display_depth(None,depth_im,None)
                display_rgb(None,rgb_im,None)
            except freenect.Kill:
                print "\nInfo: Done gathering points"
                break
        cv.DestroyAllWindows()
    else: 
        try:
            freenect.runloop(depth=display_depth,
                         video=display_rgb,
                         body=body)
        except freenect.Kill:
                print "\nInfo: Done gathering points"
        cv.DestroyAllWindows()
    return None


if __name__ == '__main__':

    cv.NamedWindow('Depth')
    cv.NamedWindow('RGB')
    cv.SetMouseCallback("RGB",mouseclick,None)
    print "Press esc to stop"    
    
    if len(sys.argv) == 4 and sys.argv[3] == '1':
        intrinsic_matrix = cv.Load("Camera_matrix.xml")
        distortion = cv.Load("Distortion.xml")     
    
    
    if len(sys.argv) > 1 :
        rgb_im = np.load("RGB.npy")
        depth_im = np.load("Depth.npy")
        if sys.argv[1] == "1":
            fake = True
        while(1):
            try:
                display_depth(None,depth_im,None)
                display_rgb(None,rgb_im,None)
            except freenect.Kill:
                print "Exit the program"
                break
        cv.DestroyAllWindows()
    else: 
        try:
            freenect.runloop(depth=display_depth,
                         video=display_rgb,
                         body=body)
        except freenect.Kill:
            print "Exit the program"
        cv.DestroyAllWindows()
