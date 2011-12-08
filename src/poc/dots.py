from pylab import*

seed(0)

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import correlate

def create_dots(x_max, y_max, n):
    
    rand_x = randint(0, x_max, n)
    rand_y = randint(0, y_max, n)

    x_part = 10
    y_part = 10
    rand_x_part = rand_x[10:20]
    rand_y_part = rand_y[10:20]

    fig = figure(figsize=(6,6))
    ax = fig.add_axes([0,0,1,1])

    ax.scatter(rand_x, rand_y, s=1.1)
    ax.set_aspect(1)
    ax.set_xlim(-2, x_max + 2)
    ax.set_ylim(-2, y_max + 2)
    ax.set_axis_off()

    fig.canvas.draw()

    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data
        

def create_img(xcoord, ycoord, x_max, y_max, figsize=(6,6)):
    fig = figure(figsize=figsize)
    ax = fig.add_axes([0,0,1,1])

    ax.scatter(xcoord, ycoord, s=1.1)
    ax.set_aspect(1)
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_axis_off()

    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))


def get_part(dots, x, y, size=20):
    x = round(x*4.8)
    y = round(y*4.8)
    return dots[y-size/2-2:y+size/2+2, x-size/2-2:x+size/2+2]

def create_part_img(part):
    fig = figure(figsize=(6,6))
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(part, 'gray')
    ax.set_aspect(1)
    ax.set_axis_off()

def get_corr(dots, part):

    corr = correlate(dots, part, output = np.float64)
    return corr

dots = create_dots(100,100,4000)
dots = dots[:,:,0] # it is grayscale
part = get_part(dots, 22, 20, 30)
#part = part/amax(part)
create_part_img(part)


corr = get_corr(dots, part)
corr_copy = corr.copy()
for x in xrange(corr.shape[0]):
    for y in xrange(corr.shape[1]):
        if x < 30 or x > (corr.shape[0]-30) or y < 30 or y > (corr.shape[1]-30):
            corr_copy[y,x] = 0

target = unravel_index(argmax(corr_copy), corr_copy.shape)
create_part_img(corr)

fig = figure(figsize=(6,6))
ax = fig.add_axes([0,0,1,1])
ax.imshow(corr_copy, 'gray')
ax.set_aspect(1)
ax.set_axis_off()

ax.add_patch(Circle((target[1], target[0]), radius= 35 , alpha = 0.5))


show()

