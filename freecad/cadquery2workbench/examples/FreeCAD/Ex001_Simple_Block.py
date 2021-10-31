import cadquery as cq
# Defines the cqvar(value, descrition) function to setup variables
from freecad.cadquery2workbench.cq_variables import cqvar

# These can be modified rather than hardcoding values for each dimension.
length = cqvar(80.0, "Length of the block")
height = cqvar(60.0, "Height of the block")
thickness = cqvar(10.0, "Thickness of the block")

# Create a 3D block based on the dimension variables above.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
# positive Z direction is "up", and the negative Z direction is "down".
result = cq.Workplane("XY").box(length, height, thickness)

# Within Cadquery FreeCAD Workbench
# you need use the following to render your model
# show_object(result)  # Render the result of this script
# show_object has some options :
#       name = 'Object name' the Name of the object in FreeCAD Tree View
#       group = 'Group Name' to place the object within a Group in FreeCAD
#       rgba = cadquery Color class 
#              or 'css' style String ex. '#AE80BCB0'
#              or a tuple ex. (174, 128, 188, 0.69)
#              to set the color and alpha
#          alternatively we can set color (tuple) and alpha (float) respectively
show_object(result, name='Box', group='Box Group', rgba='#AE80BCB0')
