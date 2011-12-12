#!/usr/bin/env python
import create_model as cm
import calibrate as calib
import sys
import cv


"""
This module combines all functions. It can be called with:

./Kinect 
./Kinect.py 0       
    Use the Kinect for making a 3d model
    
./Kinect.py 1
    The program starts using a static images for making a 3d model, so that 
    you can work without a Kinect. You don't have to select all the points in the
    image either, they are preset. If you do want to specify the points 
    yourself, pass any argument BUT 0 and 1. 

./Kinect.py * 
    The program starts using a static image for making a 3d model, so that 
    we can work without a Kinect. 
    
./Kinect.py * A
    The value of A specifies the index of the camera that is to be used for
    calibration. If -1 is passed, the program chooses itself. If two camera's
    are attached (e.g. a camera in your laptop and the Kinect) they likely have 
    the indexes 0 and 1.
    
./Kinect * A 1
    The programs has a module that calculates the intrinsic camera matrix. This
    has to be done once for a camera, so instead of doing it over all the time
    you load the intrinsic camera matrix from a xml file if the 3rd argument
    is "1". 
    
./Kinect * A 2
    If a new camera is used, you have to determine the new camera matrix. This
    can be done each time, but it is more convenient to store the new matrix
    in a xml file so that it can be loaded next time you execute the program
    (by setting the 3rd argument to "1"). You can set the program in "save" mode
    by setting the 3rd argument to "2". 

"""

def menu(argv):
    """ The main menu. ``fails''= number of invalid choices """
    fails = 0
    i_c = None
    points = None    
    
    def prompt(fails, i_c, points, argv):
        """Note that we ensure ``choice'' is not interpreted as a string"""
        cv.NamedWindow("test")
        cv.DestroyAllWindows()
        print '\n --- MAIN MENU ---'
        print '\n [1] Calibrate the camera'
        print '\n [2] Start making a 3d model'
        print '\n [3] Select another camera'        
        print '\n [4] Exit'        
        choice = 0
        choice = raw_input('\nChoose one:\n>> ')
        router(choice, fails, i_c, points, argv)

    def router(choice, fails, i_c, points, argv):
        """ Executes the desired choice, if it is valid """
        if choice == '1':
            print "\nStart to calibrate the camera\n" 
            i_c = calib.get_intrinsic_matrix(argv)
            prompt(0,i_c, points, argv)
        elif choice == '2':
            print "Start generating modelpoints\n"
            points = cm.generate_modelpoints(i_c, argv)
            prompt(0,i_c, points, argv)
        elif choice == '3':
            print "\nPlease enter the index of the camera you want to use."
            argv = calib.set_camera(argv)
            prompt(0,i_c, points, argv)            
            
        elif choice == '4':
            print '\nGoodbye!\n'
            sys.exit(0)
        else:
            tryagain(fails, choice, i_c, points, argv)

    def tryagain(fails, choice, i_c, points, argv):
        """ Gives the user three chances to enter a valid choice """
        fails += 1
        if (fails > 2):
            print '\nToo many wrong choices. Exiting...\n'
            sys.exit(0)
        print '\nSorry, ``'+choice+'\'\' is not a valid choice. Try again.'
        prompt(fails, i_c, points, argv)
    prompt(fails, i_c, points, argv)

 

if __name__ == '__main__':
    menu(sys.argv)
