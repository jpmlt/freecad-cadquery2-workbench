import cadquery as cq

# X axis line length 20.0
path = cq.Workplane("XZ").moveTo(-10, 0).lineTo(10, 0)

# Sweep a circle from diameter 2.0 to diameter 1.0 to diameter 2.0 along X axis length 10.0 + 10.0
defaultSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .circle(2.0)
    .workplane(offset=10.0)     # Note offset is relative to latest workplane so here we are at pos=0
    .circle(1.0)
    .workplane(offset=10.0)
    .circle(2.0)
    .sweep(path, multisection=True)
)

# We can sweep through different shapes
recttocircletorectSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .rect(2.0, 2.0)
    .workplane(offset=8.0)
    .circle(1.0)
    .workplane(offset=4.0)
    .circle(1.0)
    .workplane(offset=8.0)
    .rect(2.0, 2.0)
    .sweep(path, multisection=True)
)

circletorecttocircleSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .circle(1.0)
    .workplane(offset=7.0)
    .rect(2.0, 2.0)
    .workplane(offset=6.0)
    .rect(2.0, 2.0)
    .workplane(offset=7.0)
    .circle(1.0)
    .sweep(path, multisection=True)
)


# Placement of the Shape is important otherwise could produce unexpected shape
# In below case circle is set on worplane with offset=0 however path start at pos -10
circletorectNotOk = (
    cq.Workplane("YZ")
    .circle(1.0)
    .workplane(offset=10.0)
    .rect(2.0, 2.0)
    .sweep(path, multisection=True)
)

# Placement of the Shape is important otherwise could produce unexpected shape
# Setting worplane with offset=-10 render what we want
circletorectOK = (
    cq.Workplane("YZ")
    .workplane(offset=-10.0)
    .circle(1.0)
    .workplane(offset=20.0)
    .rect(2.0, 2.0)
    .sweep(path, multisection=True)
)

# Switch to an arc for the path : line l=5.0 then half circle r=4.0 then line l=5.0
path = (
    cq.Workplane("XZ")
    .moveTo(-5, 4)
    .lineTo(0, 4)
    .threePointArc((4, 0), (0, -4))
    .lineTo(-5, -4)
)

# Placement of different shapes should follow the path
# cylinder r=1.5 along first line
# then sweep along arc from r=1.5 to r=1.0
# then cylinder r=1.0 along last line
arcSweep = (
    cq.Workplane("YZ")
    .workplane(offset=-5)
    .moveTo(0, 4)
    .circle(1.5)
    .workplane(offset=5, centerOption="CenterOfMass")
    .circle(1.5)
    .moveTo(0, -8)
    .circle(1.0)
    .workplane(offset=-5, centerOption="CenterOfMass")
    .circle(1.0)
    .sweep(path, multisection=True)
)


# Translate the resulting solids so that they do not overlap and display them left to right
show_object(defaultSweep, name='Default')
show_object(circletorecttocircleSweep.translate((0, 5, 0)), name='Circle to Rect to Circle')
show_object(recttocircletorectSweep.translate((0, 10, 0)), name='Rect to Circle to Rect')
show_object(circletorectNotOk.translate((0, 15, 0)), name='Circle to Rect Wrong Def')
show_object(circletorectOK.translate((0, 20, 0)), name='Circle to Rect Right Def')
show_object(arcSweep.translate((0, -5, 0)), name='Arc')
