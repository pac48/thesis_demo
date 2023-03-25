from setuptools import setup, Extension

# Define the extension module
extension_mod = Extension('ParseObj',
                          sources=['ParseObj/parse_obj.cpp'],
                          include_dirs=['/usr/local/include'],
                          # libraries=['mylibrary'],
                          library_dirs=['/usr/local/lib']
                          )

# Define the package and the extension module
setup(name='ParseObj',
      version='0.1',
      description='Python package to parse obj',
      packages=['ParseObj'],
      ext_modules=[extension_mod])