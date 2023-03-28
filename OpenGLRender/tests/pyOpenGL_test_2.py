import matplotlib.pyplot as plt
from OpenGLRender.render import *
import numpy as np
from parse_obj import *
from parse_urdf import *


def run():
    height = 480 * 4
    width = 620 * 4

    render = OpenGLRender(height, width)
    #
    # render.cam.model_matrix = np.identity(4, np.float32)

    triangle_data = load_robot()

    render.setTriangleData(triangle_data)
    render.setupBuffers()

    img = render.draw()

    plt.imshow(img)
    plt.gca().invert_yaxis()
    plt.show()


def load_robot():
    scene = loadObj('sawyer.obj')

    robot = URDFModel('sawyer.urdf')
    q = robot.getJoints()
    robot.setJoints(q + 6*(np.random.random(q.shape)-.5) )

    outAll = []
    for name, mesh in scene.items():
        trans = robot.getBodyTransform(name)

        verts = mesh[1]
        verts = verts.reshape((3, -1))
        verts = (trans[0:3, 0:3] @ verts) + trans[0:3, 3:4]

        normals = mesh[2]
        normals = normals.reshape((3, -1))
        normals = trans[0:3, 0:3] @ normals

        colors = 0.95 * np.ones((4, verts.shape[1]), dtype=np.float32)

        out = np.vstack((verts, colors, normals))
        outAll.append(out)

    return np.hstack(outAll).T


run()
