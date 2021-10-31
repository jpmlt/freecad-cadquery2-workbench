import cadquery as cq
# Defines the cqvar(value, descrition) function
from freecad.cadquery2workbench.cq_variables import cqvar
import math as m

# These can be modified rather than hardcoding values for each dimension.
size = cqvar(10, 'Cube Size')       # set variable value and his description
thickness = 1.25                    # Another way to setup a variable and his description
describe_parameter(thickness,'Walls Thickness')

# Only Constant (Integer or Float) are on the CadQuery Variables Editor
# radius as a function will not be shown
radius = (size/2-thickness)*m.sqrt(2)

# Create a 3D Hollow Cube block based on the dimension variables above
cq_hollow_cube = cq.Workplane('XY').box(size, size, size). \
	faces(">X").workplane(). \
	rect(size-2*thickness, size-2*thickness).cutThruAll(). \
	faces(">Y").workplane().center(size/2, 0). \
	rect(size-2*thickness, size-2*thickness).cutThruAll(). \
	faces(">Z").workplane().center(0,-size/2). \
	rect(size-2*thickness, size-2*thickness).cutThruAll()
# show it
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
show_object(cq_hollow_cube, name='hollow_cube',
                            rgba='#6860A080',
                            group='Cube')

# Use debug to higlight a specific part or face or any valid cq object
# Debug object are rendered with a color Red and a transparency alpha=0.6
dbg = cq_hollow_cube.faces(">Z") 
# show it
debug(dbg, name='Faces >Z', group='Cube')

# Create a 3D Sphere based on the dimension variables above
cq_sphere = cq.Workplane('XY').sphere(radius)
# show it
# options of show_object can be passed either as a list of options or as a dict
show_object(cq_sphere, options=dict(name='sphere',
                                    rgba=cq.Color('whitesmoke'),
                                    group='Sphere'))
