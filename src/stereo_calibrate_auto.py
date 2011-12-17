import numpy as np
import cv
import freenect
import frame_convert
import sys

rgb = None

rgb_points = None
depth_points = None

keep_running = True
points_set = False
using_depth = False
calibrating = False
waiting = False
found = False
stop = False

cb_dim = (9, 6)
shots = 5
taken = 0

note = "Press any key to start calibration."

def showrgb():
    global rgb
    
    shownote(rgb)
    cv.ShowImage("Calibrate", rgb)

def shownote(im):
    global note
    
    if len(note) == 0:
        return
    
    w, h = cv.GetSize(im)
    cv.Rectangle(im, (0, 0), (w, 30), (255, 255, 255), cv.CV_FILLED)
    
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 1, 8)
    
    cv.PutText(im, note, (2, 20), font, (0, 0, 0))


def handle_rgb(dev, data, timestamp):
    global keep_running, rgb, using_depth, rgb_points, depth_points, shots
    global taken, calibrating, waiting, note
    
    if keep_running:
        if using_depth:
            cvdata = frame_convert.video_cv(data[:160,:213])
            resized = cv.CreateImage((640, 480), cv.IPL_DEPTH_8U, 3)
            cv.Resize(cvdata, resized)
            rgb = resized
        else:
            rgb = frame_convert.video_cv(data)
        
        if not calibrating:
            showrgb()

    if found and not waiting:
        keep_running = False
    elif calibrating and not waiting:
        findchessboardcorners()
        
        showrgb()

    key = cv.WaitKey(10)
    if key >= 0 and key < 255:
        keypressed(key)
        if stop:
            keep_running = False
        elif not calibrating:
            calibrating = True
            note = "Looking for inner chessboard corners..."
        else:
            waiting = False
            note = "Looking for inner chessboard corners..."

def findchessboardcorners():
    global cb_dim, rgb, using_depth, taken, depth_points, rgb_points, shots
    global waiting, note, found

    image_size = cv.GetSize(rgb)
    
    grey_image = cv.CreateImage(image_size, cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(rgb, grey_image, cv.CV_BGR2GRAY)
    found, points = cv.FindChessboardCorners(grey_image, cb_dim)
    
    if found:
        points = cv.FindCornerSubPix(grey_image, points, (11, 11), (-1, -1), 
            (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1)) 	
        
        #cv.DrawChessboardCorners(rgb, cb_dim, points, found)
        
        if using_depth:
            if taken > 1:
                depth_points = depth_points + points
            else:
                depth_points = points
            taken = taken + 1
            note = "Took %d/%d depth shots. Press any key to continue." % (int(taken / 2), shots)
        else:
            if taken > 0:
                rgb_points = rgb_points + points
            else:
                rgb_points = points
            taken = taken + 1
            note = "Took %d/%d RGB shots. Press any key to continue." % (int(taken / 2) + 1, shots)
        
        waiting = True

def calibrate():
    global rgb, rgb_points, depth_points, shots, cb_dim

    number_of_points = cb_dim[0] * cb_dim[1]
    
    point_counts = cv.CreateMat(shots, 1, cv.CV_32SC1)
    for i in range(shots):
        point_counts[i, 0] = number_of_points
    
    o_points = cv.CreateMat(number_of_points * shots, 3, cv.CV_64FC1)
    rgb_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    depth_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    
    j = -1
    for i in range(number_of_points * shots):
        if i % cb_dim[1] == 0: 
            j = (j + 1)
        o_points[i, 0] = j % cb_dim[0]
        o_points[i, 1] = i % cb_dim[1]
        o_points[i, 2] = 0.0
        
        rgb_i_points[i, 0] = rgb_points[i][0]
        rgb_i_points[i, 1] = rgb_points[i][1]
        
        depth_i_points[i, 0] = depth_points[i][0]
        depth_i_points[i, 1] = depth_points[i][1]
    
    rgb_matrix = cv.CreateMat(3, 3, cv.CV_64FC1)
    rgb_distortion = cv.CreateMat(5, 1, cv.CV_64FC1)
    
    depth_matrix = cv.CreateMat(3, 3, cv.CV_64FC1)
    depth_distortion = cv.CreateMat(5, 1, cv.CV_64FC1)
    
    image_size = cv.GetSize(rgb)
    
    R = cv.CreateMat(3, 3, cv.CV_64FC1)
    T = cv.CreateMat(3, 1, cv.CV_64FC1)

    cv.StereoCalibrate(o_points, rgb_i_points, depth_i_points, point_counts,
        rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, image_size,
        R, T, flags=0)
    
    return rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, R, T

def getrectifymap(cm1, d1, cm2, d2, R, t):
    global rgb
    
    R1 = cv.CreateMat(3, 3, cv.CV_64FC1)
    R2 = cv.CreateMat(3, 3, cv.CV_64FC1)
    P1 = cv.CreateMat(3, 4, cv.CV_64FC1)
    P2 = cv.CreateMat(3, 4, cv.CV_64FC1)
    
    # Huge error in OpenCV! All matrices MUST be 64 bit single-channel floating point
    cv.StereoRectify(cm1, cm2, d1, d2, cv.GetSize(rgb), R, t, R1, R2, P1, P2) #alpha=0
    
    rgb_mapx = cv.CreateMat(rgb.height, rgb.width, cv.CV_16SC2)
    rgb_mapy = cv.CreateMat(rgb.height, rgb.width, cv.CV_16UC1)
    depth_mapx = cv.CreateMat(rgb.height, rgb.width, cv.CV_16SC2)
    depth_mapy = cv.CreateMat(rgb.height, rgb.width, cv.CV_16UC1)
    
    cv.InitUndistortRectifyMap(cm1, d1, R1, P1[:, :3], rgb_mapx, rgb_mapy)
    cv.InitUndistortRectifyMap(cm2, d2, R2, P2[:, :3], depth_mapx, depth_mapy)
    
    return rgb_mapx, rgb_mapy, depth_mapx, depth_mapy

def keypressed(key):
    global stop
    
    if key == 27 or key == 113: # Esc or Q
        stop = True

def body(*args):
    global keep_running
    
    if not keep_running:
        raise freenect.Kill


def main(argv=[]):
    global rgb, keep_running, points_set, using_depth, shots, taken, stop, note
    global calibrating, found
    
    if len(argv) > 1:
        shots = int(argv[1])
    
    cv.NamedWindow("Calibrate")

    print('Press Esc or Q in window to stop')
    
    while not stop and taken < (2 * shots):
        keep_running = True
        using_depth = False
        calibrating = False
        found = False
        freenect.runloop(depth=None,
                         video=handle_rgb,
                         body=body)
        if stop:
            return

        keep_running = True
        using_depth = True
        found = False
        freenect.runloop(depth=None,
                         video=handle_rgb,
                         body=body,
                         vmode=freenect.VIDEO_IR_8BIT)

        if stop:
            return
        
        note = "Please move the checkerboard. Press any key to continue."


    note = "Calculating the camera matrices..."
    showrgb()
    
    rgb_cm, rgb_d, depth_cm, depth_d, R, t = calibrate()
    rgb_mapx, rgb_mapy, depth_mapx, depth_mapy = getrectifymap(rgb_cm, rgb_d, depth_cm, depth_d, R, t)
    
    cv.Save("matrices/rgb_cm.xml", rgb_cm)
    cv.Save("matrices/rgb_d.xml", rgb_d)
    cv.Save("matrices/depth_cm.xml", depth_cm)
    cv.Save("matrices/depth_d.xml", depth_d)
    cv.Save("matrices/Rotation.xml", R)
    cv.Save("matrices/translation.xml", t)
    
    cv.Save("matrices/rgb_mapx.xml", rgb_mapx)
    cv.Save("matrices/rgb_mapy.xml", rgb_mapy)
    cv.Save("matrices/depth_mapx.xml", depth_mapx)
    cv.Save("matrices/depth_mapy.xml", depth_mapy)
    
    note = "Found the camera matrices. Press any key to exit."
    showrgb()
    cv.WaitKey(0)

if __name__ == "__main__":
    main(sys.argv)

