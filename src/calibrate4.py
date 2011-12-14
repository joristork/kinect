import numpy as np
import cv
import freenect
import frame_convert

rgb = None

rgb_points = None
depth_points = None

keep_running = True
points_set = False
using_depth = False

def showrgb():
    global rgb
    
    cv.ShowImage("Calibrate", rgb)

def calibrate():
    global rgb, rgb_points, depth_points

    cb_dim = (9, 6)
    number_of_points = cb_dim[0]*cb_dim[1]
    
    point_counts = cv.CreateMat(1, 1, cv.CV_32SC1)
    point_counts[0, 0] = number_of_points
    
    o_points = cv.CreateMat(number_of_points, 3, cv.CV_32FC1)
    rgb_i_points = cv.CreateMat(number_of_points, 2, cv.CV_32FC1)
    depth_i_points = cv.CreateMat(number_of_points, 2, cv.CV_32FC1)
    
    j = -1
    for i in range(number_of_points):
        if i % cb_dim[1] == 0: 
            j = (j + 1)
        o_points[i, 0] = j % cb_dim[0]
        o_points[i, 1] = i % cb_dim[1]
        o_points[i, 2] = 0.0
        
        rgb_i_points[i, 0] = rgb_points[i][0]
        rgb_i_points[i, 1] = rgb_points[i][1]
        
        depth_i_points[i, 0] = depth_points[i][0]
        depth_i_points[i, 1] = depth_points[i][1]
    
    rgb_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
    rgb_distortion = cv.CreateMat(5, 1, cv.CV_32FC1)
    
    depth_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
    depth_distortion = cv.CreateMat(5, 1, cv.CV_32FC1)
    
    image_size = cv.GetSize(rgb)
    
    R = cv.CreateMat(3, 3, cv.CV_32FC1)
    T = cv.CreateMat(3, 1, cv.CV_32FC1)

    cv.StereoCalibrate(o_points, rgb_i_points, depth_i_points, point_counts,
        rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, image_size,
        R, T, flags=0)
    
    return rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, R, T

def mouseclicked(event, x, y, flags, arg):
    global rgb, rgb_points, depth_points, keep_running, using_depth, points_set
    
    """
    if event == cv.CV_EVENT_LBUTTONUP:
        keep_running = False
        if using_depth:
            if len(depth_points) < 4:
                addpoint(rgb, (x, y), depth_points)
            else:
                print "Already added the corners to the depth image."
        else:
            if len(rgb_points) < 4:
                addpoint(rgb, (x, y), rgb_points)
            else:
                print "Already added the chessboard's corners in the RGB image."
       
        if len(rgb_points) == 4 and len(depth_points) == 4:
            a, b, c, d, e, f = calibrate()
            print "rgb m: ", np.asarray(a)
            print "rgb d: ", np.asarray(b)
            print "depth m: ", np.asarray(c)
            print "depth d: ", np.asarray(d)
            print "R: ", np.asarray(e)
            print "t: ", np.asarray(f)
            
            points_set = True
            
            showrgb()
            cv.WaitKey(0)
        elif len(rgb_points) == 4 and not using_depth:
            points_set = True
            
            showrgb()
            cv.WaitKey(0)
"""

def keypressed(key):
    if key == 27 or key == 113: # Esc or Q
        raise freenect.Kill

def display_rgb(dev, data, timestamp):
    global keep_running, rgb, using_depth, rgb_points, depth_points
    
    if keep_running:
        if using_depth:
            cvdata = frame_convert.video_cv(data[:160,:213])
            resized = cv.CreateImage((640, 480), cv.IPL_DEPTH_8U, 3)
            cv.Resize(cvdata, resized)
            rgb = resized
        else:
            rgb = frame_convert.video_cv(data)
        
        showrgb()

    
    cb_dim = (9,6)
    image_size = cv.GetSize(rgb)
    
    grey_image = cv.CreateImage(image_size, cv.IPL_DEPTH_8U, 1 ) 
    cv.CvtColor(rgb, grey_image, cv.CV_BGR2GRAY)
    found, points = cv.FindChessboardCorners(grey_image, cb_dim)
        
    if found:
        points = cv.FindCornerSubPix(grey_image, points, (11, 11), (-1, -1), (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1)) 	
        cv.DrawChessboardCorners(rgb, cb_dim, points, found)
        if using_depth:
            depth_points = points
        else:
            rgb_points = points
        keep_running = False

    if cv.WaitKey(10) == 27:
        keep_running = False


def body(*args):
    global keep_running
    
    if not keep_running:
        raise freenect.Kill


def main():
    global rgb, keep_running, points_set, using_depth
    
    cv.NamedWindow("Calibrate")
    cv.SetMouseCallback("Calibrate", mouseclicked, None)

    print('Press ESC in window to stop')
    freenect.runloop(depth=None,
                     video=display_rgb,
                     body=body)

    showrgb()
    cv.WaitKey(0)

    keep_running = True
    using_depth = True
    print('Press ESC in window to stop')
    freenect.runloop(depth=None,
                     video=display_rgb,
                     body=body,
                     vmode=freenect.VIDEO_IR_8BIT)

    a, b, c, d, e, f = calibrate()
    print "rgb m: ", np.asarray(a)
    print "rgb d: ", np.asarray(b)
    print "depth m: ", np.asarray(c)
    print "depth d: ", np.asarray(d)
    print "R: ", np.asarray(e)
    print "t: ", np.asarray(f)
    
    showrgb()
    cv.WaitKey(0)

if __name__ == "__main__":
    main()

