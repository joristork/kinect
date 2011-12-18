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
# TODO: Use our own matrices instead of those found by Nicolas Burrus (see also
#       stereo_calibrate_auto.py).

"""
Rectification functions for aligning Microsoft Kinect's depth with its color
image. It uses the camera matrices which can be estimated by 
stereo_calibrate_auto.py.
"""

import cv
from math import tan

# Initialize all at None
rgb_mapx = rgb_mapy = rgb_h = depth_mapx = depth_mapy = depth_h = None


def load_rectification_matrices(homographic=False):
    """
    Load the recitfication matrices
    
    Input: optional bool homographic, when True, load the homographic matrices
    Output: none
    """
    
    global rgb_mapx, rgb_mapy, depth_mapx, depth_mapy

    rgb_mapx = cv.Load("matrices/nicolas_burrus/rgb_mapx.xml")
    rgb_mapy = cv.Load("matrices/nicolas_burrus/rgb_mapy.xml")

    depth_mapx = cv.Load("matrices/nicolas_burrus/depth_mapx.xml")
    depth_mapy = cv.Load("matrices/nicolas_burrus/depth_mapy.xml")
    
    if homographic:
        load_homographic_matrices()


def load_homographic_matrices():
    """
    Load the homographic matrices
    
    Input: none
    Output: none
    """

    global rgb_h, depth_h

    rgb_h = cv.Load("matrices/nicolas_burrus/rgb_h.xml")
    depth_h = cv.Load("matrices/nicolas_burrus/depth_h.xml")


def rectify_rgb(rgb, align=False):
    """
    Rectify the Kinect color image according to the matrices found by
    calibrating.
    
    Input: raw IplImage rgb from the Kinect
           optional bool align, when True, align the image to the depth image
    Output: either the rectified IplImage r or the rectified aligned IplImage a
    """
    global rgb_mapx, rgb_mapy, rgb_h
    
    if not rgb_mapx:
        load_rectification_matrices()
    
    r = cv.CloneImage(rgb)
    cv.Remap(rgb, r, rgb_mapx, rgb_mapy)
    
    if align:
        if not rgb_h:
            load_homographic_matrices()
        a = cv.CloneImage(r)
        cv.WarpPerspective(r, a, rgb_h)
        return a

    return r


def rectify_depth(depth, align=True):
    """
    Rectify the Kinect depth image according to the matrices found by
    calibrating.
    
    Input: raw IplImage depth from the Kinect
           optional bool align, when True, align the image to the rgb image
    Output: either the rectified IplImage r or the rectified aligned IplImage a
    """
    global depth_mapx, depth_mapy, depth_h
    
    if not depth_mapx:
        load_rectification_matrices()
    
    r = cv.CloneImage(depth)
    cv.Remap(depth, r, depth_mapx, depth_mapy)
    
    if align:
        if not depth_h:
            load_homographic_matrices()
        a = cv.CloneImage(r)
        cv.WarpPerspective(r, a, depth_h)
        return a

    return r


def depth_to_centimeters(d):
    """
    The Kinect depth sensor uses some sort of logarithmic scale. To get it on a
    linear scale, the following formula can be used. (Proposed by Dr. Stephane
    Magnenat at http://groups.google.com/group/openkinect/browse_thread/thread/
    31351846fd33c78/e98a94ac605b9f21?lnk=gst&q=stephane#e98a94ac605b9f21 .)
    
    Input: float d that contains Kinect's depth at a certain position
    Output: a float that is that same depth in meters
    """

    if d < 2047:
        return 12.36 * tan(d / 2842.5 + 1.1863)
    else:
        return -1.0


def depth_image_to_centimeters(depth):
    """
    Convert the entire RECTIFIED depth image to linear scale.
    
    Input: IplImage depth, the rectified Kinect depth image
    Output: IplImage r, the rectified depth image on linear scale
    """

    r = cv.CreateImage((depth.width, depth.height), cv.IPL_DEPTH_8U, 1)
    for y in xrange(depth.height):
        for x in xrange(depth.width):
            r[y, x] = depth_to_centimeters(depth[y, x])

    return r


def get_depth_from_rgb(x, y, depth):
    """
    Get the depth from a position in the RECTIFIED color image. Exactly one of
    these two images should be aligned to the other.
    
    Input: int x, the x coordinate from the rectified color image
           int y, the y coordinate from the rectified color image
           IplImage depth, the RECTIFIED depth image
    Output: a float that represents the depth in meters at the wanted position
    
    Note: If you need to know the depth in meters for all positions, use
    depth_image_to_meters() instead. The depth of the location (x, y) in the
    color image will then be the value of the location (x, y) in the corrected
    depth image (result of depth_image_to_meters).
    """

    return depth_to_meters(depth[y, x])

