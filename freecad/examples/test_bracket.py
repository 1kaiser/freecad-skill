import os
import FreeCAD
import Part
import Mesh

doc = FreeCAD.newDocument("Bracket")

# Base plate
base = doc.addObject("Part::Box", "Base")
base.Length = 50.0
base.Width = 30.0
base.Height = 5.0

# Cylinder hole
hole = doc.addObject("Part::Cylinder", "Hole")
hole.Radius = 4.0
hole.Height = 10.0
hole.Placement.Base = FreeCAD.Vector(25.0, 15.0, -2.0) # Center of base plate

doc.recompute()

# Cut hole from base
cut = doc.addObject("Part::Cut", "BracketWithHole")
cut.Base = base
cut.Tool = hole

doc.recompute()

# Save STEP and STL
out_step = "/home/kaiser/projects/freecad-skill/freecad/examples/bracket.step"
out_stl = "/home/kaiser/projects/freecad-skill/freecad/examples/bracket.stl"

Part.export([cut], out_step)
print(f"Exported STEP to {out_step}")

# Use Mesh module to export STL
Mesh.export([cut], out_stl)
print(f"Exported STL to {out_stl}")
