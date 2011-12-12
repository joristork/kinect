#!/usr/bin/env python
import create_model as cm
import calibrate as calib
import sys
import cv

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
