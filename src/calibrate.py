import exceptions
import cv
import numpy as np
import time

enable_capture = False
captured_points = []
clicks = 0
quit = False
current_points = []
accept = False

def get_intrinsic_matrix(argv):
    """Note that we ensure ``choice'' is not interpreted as a string"""
    global enable_capture, quit, current_points, captured_points, accept
    enable_capture = False
    captured_points = []
    clicks = 0
    quit = False
    current_points = []
    accept = False    
    
    camera = -1
    if len(argv) > 2:
        try:
            camera = int(argv[2])
        except exceptions.ValueError:
            print "\nError: A invalid argument has been passed. The second argument is ignored\n"    
    cam = cv.CaptureFromCAM(camera);
    if cv.QueryFrame(cam) == None:
        print "\nError: You selected a invalid camera, return to main menu\n"
        return None    
    
    cb_dim = get_cb_dimensions()

    
    
    if cb_dim == None:
       return None



    cv.NamedWindow('Calibrate')
    cv.SetMouseCallback("Calibrate",mouseclick,None)
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 1, 8)

    
    while True:
        image = cv.QueryFrame(cam)
        image_size = cv.GetSize(image)
        
        
        grey_image = cv.CreateImage(image_size, cv.IPL_DEPTH_8U, 1 ) 
        cv.CvtColor(image,grey_image,cv.CV_BGR2GRAY)
        found, points = cv.FindChessboardCorners(grey_image, cb_dim, cv.CV_CALIB_CB_ADAPTIVE_THRESH)
        
        
        if found:
            points = cv.FindCornerSubPix(grey_image, points, (11,11), (-1,-1), (cv.CV_TERMCRIT_EPS+cv.CV_TERMCRIT_ITER,30,0.1)) 	
            cv.DrawChessboardCorners(image, cb_dim, points, found)
            cv.PutText(image,"Use left-click to capture points",(2, 40), font, (0,0,0))  
            current_points = points
            enable_capture = True
        else:
            enable_capture = False
            
            
        if quit:
            break
            
            
        cv.PutText(image,"Click twice on the right mousebutton to finalize the capture.",(2, 20), font, (0,0,0))            
        cv.ShowImage("Calibrate", image)

        key = ( cv.WaitKey(1) ) % 0x100
        if key == 27:
            break
    
    cv.DestroyWindow("Calibrate")
    
    if len(captured_points) > 0:
        number_of_points = cb_dim[0]*cb_dim[1]
       
        
        shots = len(captured_points) / number_of_points
        pointcounts = cv.CreateMat(shots, 1, cv.CV_32SC1)
        for i in xrange(shots):
            pointcounts[i,0] = number_of_points

        camera_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
        distortion = cv.CreateMat(5, 1, cv.CV_32FC1)
        rvecs = cv.CreateMat(shots, 3, cv.CV_32FC1)
        tvecs = cv.CreateMat(shots, 3, cv.CV_32FC1)
        
        cv.Set2D(camera_matrix,0,0,1.0)
        cv.Set2D(camera_matrix,1,1,1.0)
        
        
        o_points = cv.CreateMat(number_of_points * shots, 3, cv.CV_32FC1)
        i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_32FC1)
        j = -1
        for i in xrange(number_of_points * shots):
            if i % cb_dim[1] == 0: 
                j = (j + 1)
            o_points[i, 0] = j % cb_dim[0]
            o_points[i, 1] = i % cb_dim[1]
            
            o_points[i, 2] = 0.0
            i_points[i, 0] = captured_points[i][0]
            i_points[i, 1] = captured_points[i][1]

        print "Calculating intrinsic matrix....."
        cv.CalibrateCamera2(o_points, i_points, pointcounts, image_size, camera_matrix, distortion, rvecs, tvecs) 
        print "Done"
        
        

        cv.NamedWindow( "Undistort" )
        cv.SetMouseCallback("Undistort",mouseclick_dist,None)


        print "Show the resulting camera image. Left click to accept."
        while(1):
            image=cv.QueryFrame(cam)
            t = cv.CloneImage(image) 
            cv.Undistort2(image, t, camera_matrix, distortion)
            cv.ShowImage("Undistort", t)
            c = cv.WaitKey(33)
            if accept:
                break
            elif c==1048603:		# enter esc key to exit
                break
                
                
        cv.DestroyAllWindows() 
        print "\nInfo: Intrinsic matrix and distortion coefficients have been set."
        
        if len(argv) == 4 and argv[3] == "2":
            cv.Save("Camera_matrix.xml",camera_matrix)
            cv.Save("Distortion.xml",distortion)
        
        for i in xrange(shots):
          print tvecs[i,0], tvecs[i,1], tvecs[i,2]
        
        
        
        return camera_matrix, distortion
    else:
        print "\nInfo: No points have been set and so we didn't find an intrinsic matrix."
        return None

def mouseclick_dist(event,x,y,flags,param):
    global accept
    if event == cv.CV_EVENT_LBUTTONUP:
        accept = True
    
    
def mouseclick(event,x,y,flags,param):
    global enable_capture, captured_points, clicks, quit, current_points
    if event == cv.CV_EVENT_LBUTTONUP:
        clicks = 0
        if enable_capture:
            print "Added new points"
            captured_points = captured_points + current_points
    if event == cv.CV_EVENT_RBUTTONUP:
        if clicks == 0:
            clicks = 1
        else:
            quit = True

    
def get_cb_dimensions():
    CB_width = 0
    CB_width = raw_input('\nChessboard width:\n>> ')
    CB_height = 0
    CB_height = raw_input('\nChessboard height:\n>> ')
    
    try:
        CB_width = int(CB_width)
        CB_height = int(CB_height) 
        return (CB_width, CB_height)       
    except exceptions.ValueError:
        print "You gave invalid values for the dimensions. Please press enter to try again or press 'x' and enter to go back to the main menu."
        inp = raw_input(">> ")
        while(inp != "x" and inp != ""):
            inp = raw_input(">> ")
        if inp == "":
            return get_cb_dimensions()
    return None
    
def set_camera(argv):
    camera = raw_input('\nCamera index:\n>> ')
    
    try:
        c = int(camera)
        if len(argv) == 1:
            argv = argv + ["0",camera]
        elif len(argv) == 2:
            argv = argv + [camera]
        elif len(argv) > 2:
            argv[2] = camera
        return argv
    except exceptions.ValueError:
        print "You entered an invalid value. Please press enter to try again or press 'x' and enter to go back to the main menu."
        inp = raw_input(">> ")
        while(inp != "x" and inp != ""):
            inp = raw_input(">> ")
        if inp == "":
            return set_camera(argv)
    return None       
    
if __name__ == '__main__':
    matrix, distortion =  get_intrinsic_matrix()
    for i in xrange(3):
       print matrix[i,0],"\t\t", matrix[i,1],"\t\t", matrix[i,2]
