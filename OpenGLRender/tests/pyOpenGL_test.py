import matplotlib.pyplot as plt
from OpenGLRender.render import *
import numpy as np
from parse_obj import *
from parse_urdf import *


def run():
    height = 480 * 4
    width = 620 * 4

    render = OpenGLRender(height, width)

    # triangle_data = load_cube()
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
        .5, .5, 0.0, 0, 0, 1, 1, 0, 0, 1.0,
        .5, -.5, 0.0, 0, 1, 0, 1, 0, 0, 1.0,
        -.5, -.5, 0.0, 1, 0, 0, 1, 0, 0, 1.0,
        -.5, -.5, 0.0, 1, 0, 0, 1, 0, 0, 1.0,
        -.5, .5, 0.0, 0, 1, 0, 1, 0, 0, 1.0,
        .5, .5, 0.0, 0, 0, 1, 1, 0, 0, 1.0,
    ], dtype=np.float32)


def load_cube():
    cube = [
        # Front face
        -0.5, -0.5, 0.5,
        0.5, -0.5, 0.5,
        0.5, 0.5, 0.5,

        -0.5, 0.5, 0.5,
        -0.5, -0.5, 0.5,
        0.5, 0.5, 0.5,

        # Back face
        -0.5, -0.5, -0.5,
        0.5, -0.5, -0.5,
        0.5, 0.5, -0.5,

        -0.5, 0.5, -0.5,
        -0.5, -0.5, -0.5,
        0.5, 0.5, -0.5,

        # Right face
        0.5, -0.5, 0.5,
        0.5, -0.5, -0.5,
        0.5, 0.5, -0.5,

        0.5, 0.5, 0.5,
        0.5, -0.5, 0.5,
        0.5, 0.5, -0.5,

        # Left face
        -0.5, -0.5, 0.5,
        -0.5, -0.5, -0.5,
        -0.5, 0.5, -0.5,

        -0.5, 0.5, 0.5,
        -0.5, -0.5, 0.5,
        -0.5, 0.5, -0.5,

        # Top face
        -0.5, 0.5, 0.5,
        0.5, 0.5, 0.5,
        0.5, 0.5, -0.5,

        -0.5, 0.5, -0.5,
        -0.5, 0.5, 0.5,
        0.5, 0.5, -0.5,

        # Bottom face
        -0.5, -0.5, 0.5,
        0.5, -0.5, 0.5,
        0.5, -0.5, -0.5,

        -0.5, -0.5, -0.5,
        -0.5, -0.5, 0.5,
        0.5, -0.5, -0.5,
    ]
    vertices = .5 * np.array(cube, dtype=np.float32)
    vertices = vertices.reshape((-1, 3))
    colors = 0.95 * np.ones((vertices.shape[0], 4), dtype=np.float32)

    normals = vertices * 0 + 1

    out = np.hstack((vertices, colors, normals))

    return out


def load_obj():
    scene = loadObj('sawyer.obj')

    mesh0 = scene['right_l0']

    verts = mesh0[1]
    verts = verts.reshape((3, -1)).T
    normals = mesh0[2]
    normals = normals.reshape((3, -1)).T
    # normals = normals[:, 0:3]
    colors = 0.95 * np.ones((verts.shape[0], 4), dtype=np.float32)

    out = np.hstack((verts, colors, normals))

    return out


run()
