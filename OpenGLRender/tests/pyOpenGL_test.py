import matplotlib.pyplot as plt
from OpenGLRender.render import *
import numpy as np
from parse_obj import *


def run():
    height = 480
    width = 620

    render = OpenGLRender(height, width)

    # triangle_data = load_quad()
    triangle_data = load_obj()

    render.setTriangleData(triangle_data)
    render.setupBuffers()

    img = render.draw()

    plt.imshow(img)
    plt.gca().invert_yaxis()
    plt.show()


def load_quad():
    return np.array([
        # Positions   Colors    normals
        .5, .5, 0.0,      0, 0, 1, 1,      0, 0, 1.0,
        .5, -.5, 0.0,      0, 1, 0, 1,      0, 0, 1.0,
        -.5, -.5, 0.0,      1, 0, 0, 1,      0, 0, 1.0,
        -.5, -.5, 0.0,      1, 0, 0, 1,      0, 0, 1.0,
        -.5, .5, 0.0,      0, 1, 0, 1,      0, 0, 1.0,
        .5, .5, 0.0,      0, 0, 1, 1,      0, 0, 1.0,
    ], dtype=np.float32)


def load_obj():
    scene = loadObj('sawyer.obj')
    mesh0 = scene[9]

    verts = mesh0[1]
    verts = verts.reshape((3, -1)).T
    normals = mesh0[2]
    normals = normals.reshape((3, -1)).T
    colors = np.ones((verts.shape[0], 4), dtype=np.float32)

    out = np.hstack((verts, colors, normals))

    return out

run()
