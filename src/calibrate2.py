import numpy as np
import cv
import freenect
import frame_convert

rgb = None
depth = None

rgb_points = []
depth_points = []

def showrgb():
    global rgb
    
    cv.ShowImage("RGB", rgb)

def showdepth():
    global depth
    
    cv.ShowImage("Depth", depth)

def addpoint(im, point, point_list):
    cv.Circle(im, point, 4, (0, 140, 0), -1)
    point_list.append(point)

def calibrate():
    global rgb, rgb_points, depth_points
    
    points = [(0, 0, 0), (282, 0, 0), (282, 200, 0), (0, 200, 0)]
    
    # 4 = len(rgb_points) = len(depth_points) = len(points)
    o_points = cv.CreateMat(4, 3, cv.CV_32FC1)
    rgb_i_points = cv.CreateMat(4, 2, cv.CV_32FC1)
    depth_i_points = cv.CreateMat(4, 2, cv.CV_32FC1)
    
    for i in range(4):
        o_points[i, 0] = points[i][0]
        o_points[i, 1] = points[i][1]
        o_points[i, 2] = points[i][2]
        
        rgb_i_points[i, 0] = rgb_points[i][0]
        rgb_i_points[i, 1] = rgb_points[i][1]
        
        depth_i_points[i, 0] = depth_points[i][0]
        depth_i_points[i, 1] = depth_points[i][1]
    
    point_counts = cv.CreateMat(1, 1, cv.CV_32SC1)
    point_counts[0, 0] = 4.0
    
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

def mouseclicked(event, x, y, flags, isrgb):
    global rgb, depth, rgb_points, depth_points
    
    if event == cv.CV_EVENT_LBUTTONUP:
        if isrgb:
            if len(rgb_points) < 4:
                addpoint(rgb, (x, y), rgb_points)
            else:
                print "Already added the chessboard's corners in the RGB image."
        else:
            if len(depth_points) < 4:
                addpoint(depth, (x, y), depth_points)
            else:
                print "Already added the corners to the depth image."
       
        if len(rgb_points) == 4 and len(depth_points) == 4:
            a, b, c, d, e, f = calibrate()
            print "rgb m: ", np.asarray(a)
            print "rgb d: ", np.asarray(b)
            print "depth m: ", np.asarray(c)
            print "depth d: ", np.asarray(d)
            print "R: ", np.asarray(e)
            print "t: ", np.asarray(f)

def keypressed(key):
    if key == 27 or key == 113: # Esc or Q
        raise freenect.Kill
    elif key == 97: # A
        print "AAAA"
    else:
        print key

def main():
    global rgb, depth
    
    cv.NamedWindow("RGB")
    cv.NamedWindow("Depth")
    cv.SetMouseCallback("RGB", mouseclicked, True)
    cv.SetMouseCallback("Depth", mouseclicked, False)
    
    rgb = frame_convert.video_cv(np.load("RGB.npy"))
    depth = frame_convert.pretty_depth_cv(np.load("Depth.npy"))
    
    while True:
        try:
            showrgb()
            showdepth()
            
            key = (cv.WaitKey(10)) % 0x100
            if key < 255:
                keypressed(key)
        except freenect.Kill:
            break

if __name__ == "__main__":
    main()

