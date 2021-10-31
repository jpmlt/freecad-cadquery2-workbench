# This is a CadQuery script template
import cadquery as cq
# Defines the cqvar(value, descrition) function
from freecad.cadquery2workbench.cq_variables import cqvar

# Add your script code below



# Within Cadquery FreeCAD Workbench
# you need use the show_object(cq_obbject, options) to render your model
# show_object has some options :
#       name = 'Object name' the Name of the object in FreeCAD Tree View
#       group = 'Group Name' to place the object within a Group in FreeCAD
#       rgba = cadquery Color class 
#              or 'css' style String ex. '#AE80BCB0'
#              or a tuple ex. (174, 128, 188, 0.69)
#              to set the color and alpha
#          alternatively we can set color (tuple) and alpha (float) respectively
# Use the following to render your model with grey RGB and no transparency

# show_object(result, options={"rgba":(204, 204, 204, 0.0)})
