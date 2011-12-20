
from pylab import *
from visual import *
import freenect
import time

cached_data = False
MAX_DEPTH=2047
scene = display()

# NOTE: I have left this code here for documentative purposes
# We will be removing this in the future
def point_array(depth):
    for y, line in enumerate(depth):
        for x, z in enumerate(line):
            if y % 2 and x % 2 and z < MAX_DEPTH:
                    yield (x, 480 - y, 2047 - z)

def generate_3d_grid():
    """
    This function yields a NumPy array of shape (480, 640, 2) that can be
    dstack'ed on a depth array returned by the freenect library. This can then
    in turn be passed in flattened form to numeric to render a point cloud.
    """

    width = dstack([reshape(arange(640), (1, -1, 1)), reshape(ones((640,)), (1, -1, 1))])
    height = dstack([reshape(ones((480,)), (-1, 1, 1)), reshape(arange(479, -1, -1), (-1, 1, 1))])
    return width * height

# This caches most of the array generation required
# as this data will remain static throughout the program.
# A nice memory/speed tradeoff
cached_3d_grid = generate_3d_grid()

def generate_filter_grid():
    f = 4

    width = dstack([reshape(ones((640/f,)), (1, -1, 1)),
                    reshape(arange(0, 640, f), (1, -1, 1))])

    height = dstack([reshape(arange(0, 480, f), (-1, 1, 1)),
                     reshape(ones((480/f,)), (-1, 1, 1))])

    return array((width * height).reshape((-1, 2)), dtype=int)
    

cached_filter_grid = generate_filter_grid()

def point_array_numpy(depth):
    """
    NumPy version of point array, that allows for speed improvements.
    """
    start_time = time.time()

    # Mirror the Z-axis and transform 3D grid to depth image.
    depth_image = dstack([cached_3d_grid, MAX_DEPTH - depth])

    # Shrink data set by a factor of 4 and convert to list of 3D-vectors.
    point_list = depth_image[cached_filter_grid[:,0], cached_filter_grid[:,1]]

    print "Filtering..."
    f = point_list[:,2] != 0
    point_list = point_list[f]

    print 'elapsed: %.3f sec' % (time.time() - start_time)

    return point_list

pts = None

def capture(cached_data=False):
    global pts
    old_pts = pts

    if cached_data:
        depth = np.load('kinect1.npy')
    else:
        depth = freenect.sync_get_depth()[0]

    print "Converting..."
    #pos_list = list(point_array(depth))
    pos_list = point_array_numpy(depth)

    print "Generating object..."

    pts = points(pos=pos_list)

    # Restore old position.
    if old_pts:
        pts.x = old_pts.x
        pts.y = old_pts.y
        pts.z = old_pts.z

        old_pts.visible = False

    print "Captured..."

capture(cached_data=cached_data)

while True:
    rate(60)
    if scene.kb.keys: # is there an event waiting to be processed?
        s = scene.kb.getkey() # obtain keyboard information
        #if len(s) == 1:
        #    prose.text += s # append new character
        #elif (s == 'backspace' or s == 'delete') and len(prose.text) > 0:
        #    prose.text = prose.text[:-1] # erase one letter
        #elif s == 'shift+delete':
        #    prose.text = '' # erase all the text
        if s == 'h':
            pts.x -= 20
        elif s == 'j':
            pts.y -= 20
        elif s == 'k':
            pts.y += 20
        elif s == 'l':
            pts.x += 20
        elif s == '[':
            pts.z -= 20
        elif s == ']':
            pts.z += 20
        elif s == 'c':
            capture(cached_data=cached_data)
