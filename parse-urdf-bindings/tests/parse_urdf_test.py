from parse_urdf import *


def run(file_name):
    robot = URDFModel('sawyer.urdf')

    print(robot.getBodyTransform('right_l0'))
    print(robot.getJointTransform('right_j4'))
    q = robot.getJoints()
    print(q)
    q = q + 1.0
    robot.setJoints(q)
    print(robot.getJoints())

    print(robot.getOperationalPosition(10))
    print(robot.getJacobian())

    print(robot.getBodyTransform('base_link'))
    robot.setJoints([0, 1])


run('sawyer.obj')
