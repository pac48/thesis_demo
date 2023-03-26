import os.path

import numpy
import numpy as np
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GL import *
from OpenGL.GLUT import *
import glfw


class Camera:
    def __init__(self, fov, aspect_ratio):
        self.model_matrix = np.array([[1.0, 0.0, 0.0, 0.0],
                                      [0.0, 1.0, 0.0, 0.0],
                                      [0.0, 0.0, 1.0, -1.0],
                                      [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
        self.projection_matrix = self.perspective_projection_matrix(fov, aspect_ratio, 0.01, 100)

    def perspective_projection_matrix(self, fov, aspect_ratio, near_clip, far_clip):
        fovy = np.radians(fov)

        # Calculate the projection parameters
        f = 1.0 / np.tan(fovy / 2.0)
        z_range = far_clip - near_clip
        aspect = aspect_ratio

        # Construct the projection matrix0
        projection_matrix = np.array([[f / aspect, 0.0, 0.0, 0.0],
                                      [0.0, f, 0.0, 0.0],
                                      [0.0, 0.0, -(far_clip + near_clip) / z_range,
                                       -2.0 * far_clip * near_clip / z_range],
                                      [0.0, 0.0, -1.0, 0.0]], dtype=np.float32)

        # projection_matrix = np.identity(4, dtype=np.float32)

        return projection_matrix


class OpenGLRender:
    def __init__(self, height_in, width_in):
        self.height = height_in
        self.width = width_in
        self.triangle_data = []
        self.cam = Camera(80, float(width_in) / height_in)
        self.light_dir = numpy.array([0.0, 0.0, -1.0])

        self.fbo = []
        self.vbo = []
        self.vao = []
        self.window = []

        # OpenGL version info
        renderer = glGetString(GL_RENDERER)
        version = glGetString(GL_VERSION)
        print('Renderer:', renderer)  # Renderer: b'Intel Iris Pro OpenGL Engine'
        print('OpenGL version supported: ', version)  # OpenGL version supported:  b'4.1 INTEL-10.12.13'

        self.make_context()

        module_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(module_path, 'vertex.glsl')) as f:
            vertex_shader = f.read()
        with open(os.path.join(module_path, 'fragment.glsl')) as f:
            fragment_shader = f.read()

        self.main_shader = self.create_shader(vertex_shader, fragment_shader)

        # Framebuffer to render offscreen
        self.fbo = GLuint()
        glGenFramebuffers(1, self.fbo)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        # add a texture (not needed for now) TODO add textures
        self.color_texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self.color_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_texture, 0)

        # Create a depth buffer texture and bind it to the framebuffer object
        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT,
                     GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_texture, 0)



    def setupBuffers(self):
        # setup vbo
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.triangle_data, GL_STATIC_DRAW)

        # setup vao
        self.vao = GLuint()
        glGenVertexArrays(1, self.vao)
        glBindVertexArray(self.vao)

        positionAttributeLocation = glGetAttribLocation(self.main_shader, 'position')
        positionAttributeLocation = 0
        glVertexAttribPointer(positionAttributeLocation, 3, GL_FLOAT, GL_FALSE, self.float_size(10),
                              self.pointer_offset(0))
        glEnableVertexAttribArray(positionAttributeLocation)

        colorAttributeLocation = glGetAttribLocation(self.main_shader, 'color')
        colorAttributeLocation = 1
        glVertexAttribPointer(colorAttributeLocation, 4, GL_FLOAT, GL_FALSE, self.float_size(10),
                              self.pointer_offset(3))

        glEnableVertexAttribArray(colorAttributeLocation)

        normalAttributeLocation = glGetAttribLocation(self.main_shader, 'normal')
        normalAttributeLocation = 2
        glVertexAttribPointer(normalAttributeLocation, 3, GL_FLOAT, GL_FALSE, self.float_size(10),
                              self.pointer_offset(7))
        glEnableVertexAttribArray(normalAttributeLocation)

        glUseProgram(self.main_shader)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)


    def setTriangleData(self, triangle_data_in):
        assert triangle_data_in.dtype == np.float32, "Array must be of type float32"
        self.triangle_data = triangle_data_in

    # Utility functions
    def float_size(self, n=1):
        return sizeof(ctypes.c_float) * n

    def pointer_offset(self, n=0):
        return ctypes.c_void_p(self.float_size(n))

    def create_shader(self, vertex_shader, fragment_shader):

        vertex_shader = compileShader(vertex_shader, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)

        # Link the shaders into a program
        shader_program = compileProgram(vertex_shader, fragment_shader)

        return shader_program

        # vs_id = GLuint(glCreateShader(GL_VERTEX_SHADER))  # shader id for vertex shader
        # glShaderSource(vs_id, [vertex_shader], None)  # Send the code of the shader
        # glCompileShader(vs_id)  # compile the shader code
        # status = glGetShaderiv(vs_id, GL_COMPILE_STATUS)
        # if status != 1:
        #     print('VERTEX SHADER ERROR')
        #     print(glGetShaderInfoLog(vs_id).decode())
        #
        # fs_id = GLuint(glCreateShader(GL_FRAGMENT_SHADER))
        # glShaderSource(fs_id, [fragment_shader], None)
        # glCompileShader(fs_id)
        # status = glGetShaderiv(fs_id, GL_COMPILE_STATUS)
        # if status != 1:
        #     print('FRAGMENT SHADER ERROR')
        #     print(glGetShaderInfoLog(fs_id).decode())
        #
        # # Link the shaders into a single program
        # program_id = GLuint(glCreateProgram())
        # glAttachShader(program_id, vs_id)
        # glAttachShader(program_id, fs_id)
        # glLinkProgram(program_id)
        # status = glGetProgramiv(program_id, GL_LINK_STATUS)
        # if status != 1:
        #     print('status', status)
        #     print('SHADER PROGRAM', glGetShaderInfoLog(program_id))
        #
        # glDeleteShader(vs_id)
        # glDeleteShader(fs_id)
        #
        # return program_id

    def make_context(self):
        if not glfw.init():
            print("failed to create GL context")
            exit(1)
        # Set window hint NOT visible

        glfw.window_hint(glfw.VISIBLE, False)
        # glfw.window_hint(glfw.DEPTH_BITS, 24)

        # Create a windowed mode window and its OpenGL context
        # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        self.window = glfw.create_window(self.width, self.height, "hidden window", None, None)
        if not self.window:
            print("failed to create GL context")
            glfw.terminate()
            exit(1)
        # Make the window's context current
        glfw.make_context_current(self.window)



    def draw(self):
        # bind buffers

        # select shader and draw
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)




        model_location = glGetUniformLocation(self.main_shader, "model")
        glUniformMatrix4fv(model_location, 1, GL_TRUE, self.cam.model_matrix)
        projection_location = glGetUniformLocation(self.main_shader, "projection")
        glUniformMatrix4fv(projection_location, 1, GL_TRUE, self.cam.projection_matrix)

        light_dir_location = glGetUniformLocation(self.main_shader, "lightDir")
        glUniform3fv(light_dir_location, 1, self.light_dir)

        # glEnable(GL_CULL_FACE)
        # glFrontFace(GL_CW)
        # glCullFace(GL_FRONT)
        glDrawArrays(GL_TRIANGLES, 0, self.triangle_data.shape[0])

        # glCullFace(GL_BACK)
        # glDrawArrays(GL_TRIANGLES, 0, self.triangle_data.shape[0])

        # for i in range(self.triangle_data.size//(10*3)):
        #     glDrawArrays(GL_TRIANGLES, 3*i+1, 3)  # render 3 vert starting at position 0

        img = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        img = np.frombuffer(img, dtype=np.uint8).reshape((self.height, self.width, 3))

        return img
