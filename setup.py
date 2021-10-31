from setuptools import setup
import os
# from freecad.cadquery2workbench.version import __version__
# name: this is the name of the distribution.
# Packages using the same name here cannot be installed together

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "cadquery2workbench", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.cadquery2workbench',
      version=str(__version__),
      packages=['freecad',
                'freecad.cadquery2workbench'],
      maintainer="JPMLT",
      maintainer_email="jpm.gth@netc.fr",
      url="https://github.com/...",
      description="CadQuery v2 FreeCAD Workbench",
      install_requires=['cadquery'], # https://github.com/CadQuery/cadquery
      include_package_data=True)
