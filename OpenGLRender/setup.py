from setuptools import setup, find_packages

setup(
    name='OpenGLRender',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.2',
        'matplotlib>=3.7.1',
        'glfw>=2.5.7',
        'PyOpenGL>=3.1.6',
    ],
    author='Paul Gesel',
    author_email='paulgesel@gmail.com',
    description='Small library to render objects off screen with OpenGL.',
    license='MIT',
    keywords='OpenGL',
    url='https://github.com/pac48/thesis_demo',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
)