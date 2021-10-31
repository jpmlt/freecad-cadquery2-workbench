from cadquery import *

w = 10
d = 10
h = 10

part1 = Workplane().box(2*w,2*d,h)
part2 = Workplane().box(w,d,2*h)
part3 = Workplane().box(w,d,3*h)

assy1 = (
    Assembly(part1, name='part1', loc=Location(Vector(-w,0,h/2), Vector(1, 0, 0), 45))
    .add(part2, name='part2', loc=Location(Vector(1.5*w,-.5*d,h/2), Vector(1, 0, 0), -45), color=Color(0,0,1,0.5))
    .add(part3, name='part3', loc=Location(Vector(-.5*w,-.5*d,2*h)), color=Color("red"))
)

# Displays the result of this script
show_object(assy1, group='Assy1')


part2_1 = Workplane().box(2*w,2*d,h)
part2_2 = Workplane().box(w,d,2*h)
part2_3 = Workplane().box(w,d,3*h)

part2_1.faces('>Z').edges('<X').vertices('<Y').tag('pt1')
part2_1.faces('>X').edges('<Z').vertices('<Y').tag('pt2')
part2_3.faces('<Z').edges('<X').vertices('<Y').tag('pt1')
part2_2.faces('<X').edges('<Z').vertices('<Y').tag('pt2')

assy2 = (
    Assembly(part2_1, name='part2_1', loc=Location(Vector(-w,3*d,h/2)))         # ,loc=Location(Vector(-w,3*d,h/2), Vector(1, 0, 0), 45)
    .add(part2_2, name='part2_2',color=Color(0,0,1,0.5))
    .add(part2_3, name='part2_3',color=Color("red"))
    .constrain('part2_1@faces@>Z','part2_3@faces@<Z','Axis')
    .constrain('part2_1@faces@>Z','part2_2@faces@<Z','Axis')
    .constrain('part2_1@faces@>Y','part2_3@faces@<Y','Axis')
    .constrain('part2_1@faces@>Y','part2_2@faces@<Y','Axis')
    .constrain('part2_1?pt1','part2_3?pt1','Point')
    .constrain('part2_1?pt2','part2_2?pt2','Point')
    .solve()
)

# Displays the result of this script
show_object(assy2, group='Assy2')

