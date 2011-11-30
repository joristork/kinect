
from pylab import *
from visual import *
import freenect

MAX_DEPTH=2047
scene = display()

# I have left this code here for documentative purposes
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

def point_array_numpy(depth):
    """
    NumPy version of point array, that allows for speed improvements.
    """

    return reshape(dstack([cached_3d_grid, 2047 - depth]), (-1, 3))

pts = None

def capture():
    global pts
    old_pts = pts
    depth = freenect.sync_get_depth()[0]
    print "Converting..."
    #pos_list = list(point_array(depth))
    pos_list = point_array_numpy(depth)
    print "Generating object..."
    pts = points(pos=pos_list)
    if old_pts:
        old_pts.visible = False
    print "Captured..."

capture()

while True:
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
        elif s == 'c':
            capture()

