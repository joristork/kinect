#!/usr/bin/env python
#
# Image Processing - Final project - Kinect
#
# Group Kinect 1:
# - J. Stork
# - L. Swartsenburg
# - S. van Veen
# - B. Weelinck
# - J. van der Woning
# - J. Zuiddam
#
# Author: J. van der Woning
# Date: December 12, 2011
#
# TODO: The matrices found by StereoCalibrate seem to be incorrect. Therefore,
#       this file is only useful for finding the homographic matrices (since
#       rectify.py uses Nicolas Burrus' matrices instead of those found here,
#       this DOES work).

"""
Perform automatic stereo calibration of the Microsoft Kinect based on
checkerboard recognition.

The user takes a number of shots from the Kinect camera. In these shots, the
corners of a checkerboard are located and stored. When enough shots have been
taken, all interesting camera matrices are calculated and stored in the matrices
folder.

Usage:
The program can be invoked by calling one of:
- ./stereo_calibrate_auto
- ./stereo_calibrate_auto [shots]
- ./stereo_calibrate_auto [cb_width cb_height]
- ./stereo_calibrate_auto [shots] [cb_width cb_height]
Where [cb_width cb_height] is the pair of the width and height of the
checkerboard. When shots is negative, present screenshots are used instead of
the Kinect camera.

Example:
./stereo_calibrate_auto 5 9 6
This call tells us the checkerboard's size is 9x6 and we need to take 5 shots.
"""

import numpy as np
import cv, cv2
import freenect
import frame_convert
import sys
from rectify import *

# Indicates if the Kinect output is used (fake = False) or not (fake = True)
fake = False

# The current image
rgb = None

# The number of shots to take
shots = 5

# The number of shots that has currently been taken
taken = 0

# The shots of which the checkerboard corners have been found
rgb_shots = []
depth_shots = []

# The currently found checkerboard corners
rgb_points = []
depth_points = []

# Some state indicators
keep_running = True
using_depth = False
calibrating = False
waiting = False
found = False
stop = False

# The (width, height) tuple of the checkerboard
cb_dim = (9, 6)

# The note on top of the screen
note = "Please cover the IR source and press any key to start calibration."


def showrgb():
    """
    Show the current image with the current note.
    
    Input: none
    Output: none
    """

    global rgb
    
    shownote(rgb)
    cv.ShowImage("Calibrate", rgb)


def shownote(im):
    """
    Show the note at the top of the given image.
    
    Input: IplImage im, the image on top of which the note should be shown
    Output: none
    """

    global note
    
    if len(note) == 0:
        return
    
    w, h = cv.GetSize(im)
    cv.Rectangle(im, (0, 0), (w, 30), (255, 255, 255), cv.CV_FILLED)
    
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 1, 8)
    
    cv.PutText(im, note, (2, 20), font, (0, 0, 0))


def handle_rgb(dev, data, timestamp):
    """
    Handler for the images from the Kinect. It initiates the finding of the
    chessboard corners.
    
    Input: DevPtr dev, the Kinect object
           np.array data, the image from the Kinect
           int timestamp, the time at which this image was received
    Output: none
    """

    global keep_running, rgb, using_depth, rgb_points, depth_points, shots
    global taken, calibrating, waiting, note, stop, fake
    
    if keep_running:
        if using_depth and not fake:
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
    """
    Find the chessboard corners in the current image.
    
    Input: none
    Output: none
    """

    global cb_dim, rgb, using_depth, taken, depth_points, rgb_points, shots
    global waiting, note, found, rgb_shots, depth_shots

    image_size = cv.GetSize(rgb)
    
    # Convert image to greyscale so that the checkerboard is easier to find
    grey_image = cv.CreateImage(image_size, cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(rgb, grey_image, cv.CV_BGR2GRAY)
    found, points = cv.FindChessboardCorners(grey_image, cb_dim)
    
    if found:
        # Get a more precise location of the checkerboard corners
        points = cv.FindCornerSubPix(grey_image, points, (11, 11), (-1, -1), 
            (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))
        
        if using_depth:
            depth_points = depth_points + points
            taken = taken + 1
            shot = cv.CloneImage(rgb)
            depth_shots = depth_shots + [shot]
            note = "Took %d/%d depth shots. Press any key to continue." % (
                    int(taken / 2), shots)
        else:
            rgb_points = rgb_points + points
            taken = taken + 1
            shot = cv.CloneImage(rgb)
            rgb_shots = rgb_shots + [shot]
            note = "Took %d/%d RGB shots. Press any key to continue." % (
                    int(taken / 2) + 1, shots)
        
        cv.DrawChessboardCorners(rgb, cb_dim, points, found)
        waiting = True


def calibrate():
    """
    Perform stereo calibration of the two cameras of the Kinect. The calibration
    is based on checkerboardrecognition, which has te be performed before
    calling this function.
    
    Input: none
    Output: CvMat rgb_matrix, the camera matrix of the rgb camera
            CvMat rgb_distortion, the distortion vector of the rgb camera
            CvMat depth_matrix, the camera matrix of the depth camera
            CvMat depth_distortion, the distortion vector of the depth camera
            CvMat R, the rotation matrix between the rgb and depth camera
            CvMat T, the translation vector betrween the rgb and depth camera
    """
    
    global rgb, rgb_points, depth_points, shots, cb_dim

    number_of_points = cb_dim[0] * cb_dim[1]
    
    point_counts = cv.CreateMat(shots, 1, cv.CV_32SC1)
    for i in range(shots):
        point_counts[i, 0] = number_of_points
    
    o_points = cv.CreateMat(number_of_points * shots, 3, cv.CV_64FC1)
    rgb_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    depth_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    
    # Convert the found checkerboard corners to the right format
    j = -1
    for i in range(number_of_points * shots):
        if i % cb_dim[0] == 0: 
            j = (j + 1)
        
        # Give the original checkerboard locations
        o_points[i, 0] = i % cb_dim[0]
        o_points[i, 1] = j % cb_dim[1]
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
    
    rvecs = cv.CreateMat(shots, 3, cv.CV_64FC1)
    tvecs = cv.CreateMat(shots, 3, cv.CV_64FC1)

    cv.CalibrateCamera2(o_points, rgb_i_points, point_counts, image_size, 
        rgb_matrix, rgb_distortion, rvecs, tvecs)
    cv.CalibrateCamera2(o_points, depth_i_points, point_counts, image_size, 
        depth_matrix, depth_distortion, rvecs, tvecs)
    
    R = cv.CreateMat(3, 3, cv.CV_64FC1)
    T = cv.CreateMat(3, 1, cv.CV_64FC1)

    cv.StereoCalibrate(o_points, rgb_i_points, depth_i_points, point_counts,
        rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, image_size,
        R, T)
    
    return rgb_matrix, rgb_distortion, depth_matrix, depth_distortion, R, T


def getrectifymap(cm1, d1, cm2, d2, R, t):
    """
    Get the mappings that rectify both the rgb and the depth image.
    
    Input:  CvMat cm1, the camera matrix of the rgb camera
            CvMat d1, the distortion vector of the rgb camera
            CvMat cm2, the camera matrix of the depth camera
            CvMat d2, the distortion vector of the depth camera
            CvMat R, the rotation matrix between the rgb and depth camera
            CvMat t, the translation vector betrween the rgb and depth camera
    Output: CvMat rgb_mapx, the mapping of the x coordinates of the rgb image
            to their rectified base
            CvMat rgb_mapy, the same for its y coordinates
            CvMat depth_mapx, the same for the depth image's x coordinates
            CvMat depth_mapy, the same for its y coordinates
    """
    
    global rgb
    
    R1 = cv.CreateMat(3, 3, cv.CV_64FC1)
    R2 = cv.CreateMat(3, 3, cv.CV_64FC1)
    P1 = cv.CreateMat(3, 4, cv.CV_64FC1)
    P2 = cv.CreateMat(3, 4, cv.CV_64FC1)
    
    cv.StereoRectify(cm1, cm2, d1, d2, cv.GetSize(rgb), R, t, R1, R2, P1, P2)
    
    rgb_mapx = cv.CreateMat(rgb.height, rgb.width, cv.CV_16SC2)
    rgb_mapy = cv.CreateMat(rgb.height, rgb.width, cv.CV_16UC1)
    depth_mapx = cv.CreateMat(rgb.height, rgb.width, cv.CV_16SC2)
    depth_mapy = cv.CreateMat(rgb.height, rgb.width, cv.CV_16UC1)
    
    cv.InitUndistortRectifyMap(cm1, d1, R1, P1, rgb_mapx, rgb_mapy)
    cv.InitUndistortRectifyMap(cm2, d2, R2, P2, depth_mapx, depth_mapy)
    
    return rgb_mapx, rgb_mapy, depth_mapx, depth_mapy


def keypressed(key):
    """
    Handler for when a key is pressed.
    
    Input: int key, the key that has been pressed
    Output: none
    """
    
    global stop
    
    # Stop when Esc or Q is pressed
    if key == 27 or key == 113:
        stop = True


def body(*args):
    """
    Main loop of the freenect library.
    """

    global keep_running
    
    if not keep_running:
        raise freenect.Kill


def findhomography():
    """
    Find the homography matrices from the rectified rgb image to the rectified
    depth image and the other way around. This is done using checkerboard
    recognition in the rectified versions of the earlier taken shots.
    
    Input: none
    Output: CvMat rgb_H, the homography matrix that transforms the rectified rgb
            image to the base of the rectified depth image.
            CvMat depth_H, the same for the depth image to the rgb base.
    """
    
    global rgb_shots, depth_shots, cb_dim, rgb
    
    image_size = cv.GetSize(rgb)
    shots = len(rgb_shots)
    number_of_points = cb_dim[0] * cb_dim[1]
    
    rrgb_points = []
    rdepth_points = []
    
    # Load the rectification matrices in the rectify module
    load_rectification_matrices()
    
    # Find the checkerboard corners in all shots
    for i in range(shots):
        # Don't align the rectified images yet
        rrgb = rectify_rgb(rgb_shots[i], False)
        rdepth = rectify_depth(depth_shots[i], False)
        
        gray = cv.CreateImage(image_size, cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(rrgb, gray, cv.CV_BGR2GRAY)
        found, rgb_points = cv.FindChessboardCorners(gray, cb_dim)
        
        # When unable to find the checkerboard corners, skip this shot
        if not found:
            shots = shots - 1
            continue

        cv.CvtColor(rdepth, gray, cv.CV_BGR2GRAY)
        found, depth_points = cv.FindChessboardCorners(gray, cb_dim)
        
        # When unable to find the checkerboard corners, skip this shot
        if not found:
            shots = shots - 1
            continue

        rgb_points = cv.FindCornerSubPix(gray, rgb_points, (11, 11), (-1, -1), (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))
        rrgb_points = rrgb_points + rgb_points
        
        depth_points = cv.FindCornerSubPix(gray, depth_points, (11, 11), (-1, -1), (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))
        rdepth_points = rdepth_points + depth_points
    
    # When no shots were useful for finding checkerboard corners, fail.
    if shots < 1:
        return None, None
    
    rrgb_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    rdepth_i_points = cv.CreateMat(number_of_points * shots, 2, cv.CV_64FC1)
    
    # Convert the found checkerboard corners to the right format
    for i in range(number_of_points * shots):
        rrgb_i_points[i, 0] = rrgb_points[i][0]
        rrgb_i_points[i, 1] = rrgb_points[i][1]
        
        rdepth_i_points[i, 0] = rdepth_points[i][0]
        rdepth_i_points[i, 1] = rdepth_points[i][1]

    # Find the homography matrices
    rgb_H = cv.CreateMat(3, 3, cv.CV_64FC1)
    depth_H = cv.CreateMat(3, 3, cv.CV_64FC1)
    cv.FindHomography(rrgb_i_points, rdepth_i_points, rgb_H, cv.CV_RANSAC)
    cv.FindHomography(rdepth_i_points, rrgb_i_points, depth_H, cv.CV_RANSAC)
    
    return rgb_H, depth_H


def waitforkey(key=-1):
    """
    Wait until a key is pressed.
    
    Input: optional int key. When key is set, program execution is halted until
           that specific key is pressed.
    Output: none
    """
    
    while True:
        k = cv.WaitKey(10)
        if (key == -1 and k >= 0 and k < 255) or (key >= 0 and k == key):
            break


def main(argv=[]):
    """
    Main program. Processes user input, instructs the user to take camera shots,
    processes the shots, finds camera matrices, rectify maps and homography
    matrices and finally tells the user whether all this has been completed
    successful or not.
    
    Input: optional list command-line arguments of one of the following forms:
           - [filename, shots]
           - [filename, cb_width, cb_height]
           - [filename, shots, cb_width, cb_height]
           Where cb_width and _height are the width and height of the
           checkerboard. When shots is negative, present screenshots are used
           instead of the Kinect camera.
    Output: none
    """

    global cb_dim, shots, fake, stop, taken, keep_running, using_depth
    global calibrating, found, note, rgb
    
    # Process command line arguments
    if len(argv) == 3:
        cb_dim = (int(argv[1]), int(argv[2]))
    elif len(argv) > 1:
        v = int(argv[1])
        if v < 0:
            shots = 1
            fake = True
        else:
            shots = v
    
    if len(argv) > 3:
        cb_dim = (int(argv[2]), int(argv[3]))


    cv.NamedWindow("Calibrate")

    print('Press Esc or Q in window to stop')
    
    # Enter the shot taking loop
    while not stop and taken < (2 * shots):
        keep_running = True
        using_depth = False
        calibrating = False
        found = False
        
        # Either use a stored image or the Kinect camera (color image)
        if fake:
            while keep_running:
                im = cv2.imread("Example_RGB.png")
                corr = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                handle_rgb(None, corr, None)
        else:
            freenect.runloop(depth=None,
                             video=handle_rgb,
                             body=body)

        # When no shot was taken or the user wants to quit, stop the program
        if stop or taken == 0:
            return

        keep_running = True
        using_depth = True
        found = False

        # Either use a stored image or the Kinect camera (IR image)
        if fake:
            while keep_running:
                im = cv2.imread("Example_IR.png")
                corr = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                handle_rgb(None, corr, None)
        else:
            freenect.runloop(depth=None,
                             video=handle_rgb,
                             body=body,
                             vmode=freenect.VIDEO_IR_8BIT)

        if stop:
            return
        
        note = "Please move the checkerboard. Press any key to continue."


    note = "Calculating the camera matrices..."
    # Checkerboard recognition was succesful, we're slightly happy
    rgb = cv.LoadImage("img/neutral.png")
    showrgb()
    
    rgb_cm, rgb_d, depth_cm, depth_d, R, t = calibrate()
    
    rgb_mapx, rgb_mapy, depth_mapx, depth_mapy = getrectifymap(rgb_cm, rgb_d,
        depth_cm, depth_d, R, t)
        
    # Save all found matrices
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
    
    note = "Found the camera matrices. Press any key to continue."
    showrgb()
    
    # Wait for any key
    waitforkey()

    note = "Calculating the homography matrices..."
    showrgb()
    
    rgb_H, depth_H = findhomography()
    
    if not rgb_H:
        note = "Could not find the Homography matrices. Press any key to exit."
        # Finding the homography matrices failed, we're sad
        rgb = cv.LoadImage("img/fail.png")
        
        showrgb()
        waitforkey()
        
        print "Done"
    else:
        note = "Found the homography matrices. Press any key to exit."
        # Finding the homography matrices was successful we're happy
        rgb = cv.LoadImage("img/success.png")

        showrgb()
        
        waitforkey()
        
        cv.Save("matrices/rgb_h.xml", rgb_H)
        cv.Save("matrices/depth_h.xml", depth_H)
        
        print "Done"


if __name__ == "__main__":
    main(sys.argv)

