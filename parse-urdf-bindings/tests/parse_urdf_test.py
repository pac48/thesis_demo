from parse_urdf import *


def run(file_name):
    # out = loadModel(file_name)
    out = URDFModel('sawyer.urdf')

    print(out.getBodyTransform('base_link'))

#


run('sawyer.obj')
