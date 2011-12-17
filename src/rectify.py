import cv
from math import tan

rgb_mapx = cv.Load("matrices/nicolas_burrus/rgb_mapx.xml")
rgb_mapy = cv.Load("matrices/nicolas_burrus/rgb_mapy.xml")
depth_mapx = cv.Load("matrices/nicolas_burrus/depth_mapx.xml")
depth_mapy = cv.Load("matrices/nicolas_burrus/depth_mapy.xml")

def rectify_rgb(rgb):
    """
    Rectify the Kinect color image according to the matrices found by
    calibrating.
    
    Input: raw IplImage rgb from the Kinect
    Output: rectified IplImage r
    """
    
    r = cv.CloneImage(rgb)
    cv.Remap(rgb, r, rgb_mapx, rgb_mapy)
    return r

def rectify_depth(depth):
    """
    Rectify the Kinect depth image according to the matrices found by
    calibrating.
    
    Input: raw IplImage depth from the Kinect
    Output: rectified IplImage r
    """
    r = cv.CloneImage(depth)
    cv.Remap(depth, r, depth_mapx, depth_mapy)
    return r

def depth_to_meters(d):
    """
    The Kinect depth sensor uses some sort of logarithmic scale. To get it on a
    linear scale, the following formula can be used. (Proposed by Dr. Stephane
    Magnenat at http://groups.google.com/group/openkinect/browse_thread/thread/
    31351846fd33c78/e98a94ac605b9f21?lnk=gst&q=stephane#e98a94ac605b9f21 .)
    
    Input: float d that contains Kinect's depth at a certain position
    Output: a float that is that same depth in meters
    """

    if d < 2047:
        return 0.1236 * tan(d / 2842.5 + 1.1863)
    else:
        return -1.0

def depth_image_to_meters(depth):
    """
    Convert the entire RECTIFIED depth image to linear scale.
    
    Input: IplImage depth, the rectified Kinect depth image
    Output: IplImage r, the rectified depth image on linear scale
    """

    r = cv.CreateImage((depth.width, depth.height), cv.IPL_DEPTH_8U, 1)
    for y in xrange(depth.height):
        for x in xrange(depth.width):
            r[y, x] = 100 * depth_to_meters(depth[y, x])

    return r

def get_depth_from_rgb(x, y, depth):
    """
    Get the depth from a position in the RECTIFIED color image.
    
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

