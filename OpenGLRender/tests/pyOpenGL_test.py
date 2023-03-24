import matplotlib.pyplot as plt
from OpenGLRender.OpenGLRender.OpenGLRender import *

height = 480
width = 620

render = OpenGLRender(height, width)
triangle_data = np.array([
    # Positions   Colors
    .5, .5, -1.0, 0, 0, 1,
    .5, -.5, -1.0, 0, 1, 0,
    -.5, -.5, -1.0, 1, 0, 0,
    -.5, -.5, -1.0, 1, 0, 0,
    -.5, .5, -1.0, 0, 1, 0,
    .5, .5, -1.0, 0, 0, 1,
], dtype=np.float32)
render.setTriangleData(triangle_data)
render.setupBuffers()
img = render.draw()

plt.imshow(img)
plt.gca().invert_yaxis()
plt.show()
