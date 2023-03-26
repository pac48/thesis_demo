import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import pyrr
import matplotlib.pyplot as plt
from parse_obj import *

width = 720
height = 600


def load_obj():
    # scene = loadObj('sawyer.obj')
    scene = loadObj('blob.obj')
    mesh0 = scene[0]

    verts = mesh0[1]
    verts = verts.reshape((3, -1)).T
    normals = mesh0[2]
    normals = normals.reshape((3, -1)).T
    # normals = normals[:, 0:3]
    colors = 0.95*np.ones((verts.shape[0], 3), dtype=np.float32)

    out = np.hstack((verts, colors, normals))

    return out

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.VISIBLE, False)
    window = glfw.create_window(width, height, "Pyopengl Rotating Cube", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # cube = [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
    #         0.5, -0.5, 0.5, 0.0, 1.0, 0.0,
    #         0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
    #         -0.5, 0.5, 0.5, 1.0, 1.0, 1.0,
    #
    #         -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
    #         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
    #         0.5, 0.5, -0.5, 0.0, 0.0, 1.0,
    #         -0.5, 0.5, -0.5, 1.0, 1.0, 1.0]
    cube = [
        # Front face
        -0.5, -0.5, 0.5, .9, 0, 0,  # Bottom-left
        0.5, -0.5, 0.5, .9, 0, 0,  # Bottom-right
        0.5, 0.5, 0.5,  0, .9, 0,  # Top-right

        -0.5, 0.5, 0.5, 0, .9, 0, # Top-left
        -0.5, -0.5, 0.5, .9, 0, 0,  # Bottom-left
        0.5, 0.5, 0.5, 0, .9, 0,  # Top-right

        # Back face
        -0.5, -0.5, -0.5, .9, 0, 0,  # Bottom-left
        0.5, -0.5, -0.5, .9, 0, 0,  # Bottom-right
        0.5, 0.5, -0.5,  0, .9, 0, # Top-right

        -0.5, 0.5, -0.5, 0, .9, 0,  # Top-left
        -0.5, -0.5, -0.5, .9, 0, 0,  # Bottom-left
        0.5, 0.5, -0.5,  0, .9, 0, # Top-right

        # Right face
        0.5, -0.5, 0.5,  .9, 0, 0, # Bottom-front
        0.5, -0.5, -0.5, .9, 0, 0,  # Bottom-back
        0.5, 0.5, -0.5,  .9, 0, 0, # Top-back

        0.5, 0.5, 0.5, .9, 0, 0,  # Top-front
        0.5, -0.5, 0.5, .9, 0, 0,  # Bottom-front
        0.5, 0.5, -0.5, .9, 0, 0,  # Top-back

        # Left face
        -0.5, -0.5, 0.5,  .9, 0, 0, # Bottom-front
        -0.5, -0.5, -0.5, .9, 0, 0,  # Bottom-back
        -0.5, 0.5, -0.5,  .9, 0, 0, # Top-back

        -0.5, 0.5, 0.5,  .9, 0, 0, # Top-front
        -0.5, -0.5, 0.5, .9, 0, 0,  # Bottom-front
        -0.5, 0.5, -0.5,  .9, 0, 0, # Top-back

        # Top face
        -0.5, 0.5, 0.5,  .9, 0, 0, # Front-left
        0.5, 0.5, 0.5,  .9, 0, 0, # Front-right
        0.5, 0.5, -0.5,  .9, 0, 0, # Back-right

        -0.5, 0.5, -0.5,  .9, 0, 0, # Back-left
        -0.5, 0.5, 0.5, .9, 0, 0,  # Front-left
        0.5, 0.5, -0.5,  .9, 0, 0, # Back-right

        # Bottom face
        -0.5, -0.5, 0.5, .9, 0, 0,  # Front-left
        0.5, -0.5, 0.5,  .9, 0, 0, # Front-right
        0.5, -0.5, -0.5,  .9, 0, 0, # Back-right

        -0.5, -0.5, -0.5,  .9, 0, 0, # Back-left
        -0.5, -0.5, 0.5, .9, 0, 0,  # Front-left
        0.5, -0.5, -0.5, .9, 0, 0,  # Back-right
    ]

    cube = load_obj()

    # convert to 32bit float

    cube = np.array(cube, dtype=np.float32)

    VERTEX_SHADER = """

        #version 330

        in vec3 position;
        in vec3 color;
        in vec3 normal;
        out vec3 newColor;
        out vec3 newNormal;

        uniform mat4 transform; 

        void main() {

         gl_Position = transform * vec4(position, 1.0f);
         newColor = color;
         newNormal = normal;

          }


    """

    FRAGMENT_SHADER = """
        #version 330

        in vec3 newColor;
        in vec3 newNormal;
        out vec4 outColor;

        void main() {

        vec3 lightDirection = vec3(0.0, 0.0, 1.0);
        float diffuse = max(dot(newNormal, -lightDirection), 0.2);
        outColor = vec4(diffuse*newColor, 1.0f);

        }

    """

    # Compile The Program and shaders

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

    # Create Buffer object in gpu
    VBO = glGenBuffers(1)
    # Bind the buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, cube, GL_STATIC_DRAW)

    # Create EBO
    # EBO = glGenBuffers(1)
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    # glBufferData(GL_ELEMENT_ARRAY_BUFFER, 144, indices, GL_STATIC_DRAW)

    # get the position from  shader
    position = glGetAttribLocation(shader, 'position')
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 4*9, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)

    # get the color from  shader
    color = glGetAttribLocation(shader, 'color')
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 4*9, ctypes.c_void_p(4*3))
    glEnableVertexAttribArray(color)

    # get the color from  shader
    normal = glGetAttribLocation(shader, 'normal')
    normal = 2
    glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 4*9, ctypes.c_void_p(4*6))
    glEnableVertexAttribArray(normal)

    glUseProgram(shader)

    glClearColor(0.5, 0.5, 0.5, 1.0)
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # rot_x = pyrr.Matrix44.from_x_rotation(0.5 * .1)
        # rot_y = pyrr.Matrix44.from_y_rotation(0.8 * .1)
        rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
        rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

        transformLoc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, rot_x * rot_y)

        # Draw Cube

        # glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        glDrawArrays(GL_TRIANGLES, 0, cube.shape[0])

        glfw.swap_buffers(window)

        img = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        img = np.frombuffer(img, dtype=np.uint8).reshape((height, width, 3))

        plt.imshow(img)
        plt.gca().invert_yaxis()
        plt.show()
        break


    glfw.terminate()


if __name__ == "__main__":
    main()