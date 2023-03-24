import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
import matplotlib.pyplot as plt
import glfw

WINDOW_LIBRARY = 'GLUT'  # GLFW or GLUT
TRY_FRAMEBUFFER = True
GENERATE_TEXTURE_ID_PROBLEM = False  # Follow this global variable to see the error in texture ID generation

height = 480
width = 620

# OpenGL version info
renderer = glGetString(GL_RENDERER)
version = glGetString(GL_VERSION)
print('Renderer:', renderer)  # Renderer: b'Intel Iris Pro OpenGL Engine'
print('OpenGL version supported: ', version)  # OpenGL version supported:  b'4.1 INTEL-10.12.13'

import numpy as np


def perspective_projection_matrix(fov, aspect_ratio, near_clip, far_clip):
    fovy = np.radians(fov)

    # Calculate the projection parameters
    f = 1.0 / np.tan(fovy / 2.0)
    z_range = far_clip - near_clip
    aspect = aspect_ratio

    # Construct the projection matrix
    projection_matrix = np.array([[f / aspect, 0.0, 0.0, 0.0],
                                  [0.0, f, 0.0, 0.0],
                                  [0.0, 0.0, -(far_clip + near_clip) / z_range, -2.0 * far_clip * near_clip / z_range],
                                  [0.0, 0.0, -1.0, 0.0]], dtype=np.float32)
    # projection_matrix = np.array([[1.0, 0.0, 0.0, 0.0],
    #                               [0.0, 1.0, 0.0, 0.0],
    #                               [0.0, 0.0, 1.0, 0.0],
    #                               [0.0, 0.0, -1.0, 0.0]], dtype=np.float32)

    return projection_matrix


class Camera:
    def __init__(self, fov, aspect_ratio):
        self.model_matrix = np.array([[1.0, 0.0, 0.0, 0.0],
                                      [0.0, 1.0, 0.0, 0.0],
                                      [0.0, 0.0, 1.0, 0.0],
                                      [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
        self.projection_matrix = perspective_projection_matrix(fov, aspect_ratio, 0.1, 100)


# Utility functions
def float_size(n=1):
    return sizeof(ctypes.c_float) * n


def pointer_offset(n=0):
    return ctypes.c_void_p(float_size(n))


def create_shader(vertex_shader, fragment_shader):
    vs_id = GLuint(glCreateShader(GL_VERTEX_SHADER))  # shader id for vertex shader
    glShaderSource(vs_id, [vertex_shader], None)  # Send the code of the shader
    glCompileShader(vs_id)  # compile the shader code
    status = glGetShaderiv(vs_id, GL_COMPILE_STATUS)
    if status != 1:
        print('VERTEX SHADER ERROR')
        print(glGetShaderInfoLog(vs_id).decode())

    fs_id = GLuint(glCreateShader(GL_FRAGMENT_SHADER))
    glShaderSource(fs_id, [fragment_shader], None)
    glCompileShader(fs_id)
    status = glGetShaderiv(fs_id, GL_COMPILE_STATUS)
    if status != 1:
        print('FRAGMENT SHADER ERROR')
        print(glGetShaderInfoLog(fs_id).decode())

    # Link the shaders into a single program
    program_id = GLuint(glCreateProgram())
    glAttachShader(program_id, vs_id)
    glAttachShader(program_id, fs_id)
    glLinkProgram(program_id)
    status = glGetProgramiv(program_id, GL_LINK_STATUS)
    if status != 1:
        print('status', status)
        print('SHADER PROGRAM', glGetShaderInfoLog(program_id))

    glDeleteShader(vs_id)
    glDeleteShader(fs_id)

    return program_id


def make_context():
    if not glfw.init():
        exit(1)
    # Set window hint NOT visible
    glfw.window_hint(glfw.VISIBLE, False)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(width, height, "hidden window", None, None)
    if not window:
        glfw.terminate()
        exit(1)
    # Make the window's context current
    glfw.make_context_current(window)


make_context()

# Framebuffer to render offscreen
fbo = GLuint()
glGenFramebuffers(1, fbo)
glBindFramebuffer(GL_FRAMEBUFFER, fbo)

# add a texture (not needed for now)
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

# setup vbo
vbo = GLuint()
glGenBuffers(1, vbo)
triangle_data = np.array([
    # Positions   Colors
    .5, .5, -1.0, 0, 0, 1,
    .5, -.5, -1.0, 0, 1, 0,
    -.5, -.5, -1.0, 1, 0, 0,
    -.5, -.5, -1.0, 1, 0, 0,
    -.5, .5, -1.0, 0, 1, 0,
    .5, .5, -1.0, 0, 0, 1,
], dtype=np.float32)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, triangle_data, GL_STATIC_DRAW)

# setup vao
triangle_vao = GLuint()
glGenVertexArrays(1, triangle_vao)
glBindVertexArray(triangle_vao)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, float_size(6), pointer_offset(0))  # attribute 0 = coordinates
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, float_size(6), pointer_offset(3))  # attribute 1 = colors
glEnableVertexAttribArray(0)
glEnableVertexAttribArray(1)

with open('vertex.glsl') as f:
    vertex_shader1 = f.read()
with open('fragment.glsl') as f:
    fragment_shader1 = f.read()

main_shader = create_shader(vertex_shader1, fragment_shader1)

cam = Camera(80, float(width) / height)


def draw():
    # bind buffers
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glBindVertexArray(triangle_vao)

    # clear render data
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # select shader and draw
    glUseProgram(main_shader)

    model_location = glGetUniformLocation(main_shader, "model")
    glUniformMatrix4fv(model_location, 1, GL_TRUE, cam.model_matrix)
    projection_location = glGetUniformLocation(main_shader, "projection")
    glUniformMatrix4fv(projection_location, 1, GL_TRUE, cam.projection_matrix)


    glDrawArrays(GL_TRIANGLES, 0, 6)  # render 3 vert starting at position 0

    img = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    img = np.frombuffer(img, dtype=np.uint8).reshape((height, width, 3))
    plt.imshow(img)
    plt.gca().invert_yaxis()
    plt.show()


draw()
