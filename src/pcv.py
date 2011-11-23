
from visual import *
import freenect

MAX_DEPTH=2047
scene = display()

def point_array(depth):
    for y, line in enumerate(depth):
        for x, z in enumerate(line):
            if y % 2 and x % 2 and z < MAX_DEPTH:
                    yield (x, 480 - y, 2047 - z)

pts = None

def capture():
    global pts
    old_pts = pts
    depth = freenect.sync_get_depth()[0]
    pts = points(pos=list(point_array(depth)))
    if old_pts:
        old_pts.visible = False

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

