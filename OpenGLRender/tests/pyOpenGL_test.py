import matplotlib.pyplot as plt
from OpenGLRender.OpenGLRender.OpenGLRender import *


def run():
    height = 480
    width = 620

    render = OpenGLRender(height, width)

    triangle_data = load_quad()
    # triangle_data = load_obj()

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
    scene = pywavefront.Wavefront('sawyer.obj', create_materials=True, collect_faces=True)

    mesh0 = scene.mesh_list[2]
    verts = []
    for face in mesh0.faces:
        for ind in face:
            vert = scene.vertices[ind]
            verts.extend(vert)
            verts.extend([.8, 0, 0, 1.0])

    out = np.array(verts, dtype=np.float32)

    return out

#


run()
