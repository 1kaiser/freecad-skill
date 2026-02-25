import sys
import os

# Set up FreeCAD paths
sys.path.append("/usr/lib/freecad/lib")
sys.path.append("/usr/share/freecad/Mod")

import FreeCAD
import Part

def create_tree():
    print("Initializing FreeCAD Tree Model...")
    # Create Document
    doc = FreeCAD.newDocument("TreeModel")
    
    # 1. Create Trunk
    trunk = doc.addObject("Part::Cylinder", "Trunk")
    trunk.Radius = 5
    trunk.Height = 50
    
    # 2. Create Foliage (Spheres)
    foliage1 = doc.addObject("Part::Sphere", "Foliage1")
    foliage1.Radius = 25
    foliage1.Placement.Base = FreeCAD.Vector(0, 0, 50)
    
    foliage2 = doc.addObject("Part::Sphere", "Foliage2")
    foliage2.Radius = 15
    foliage2.Placement.Base = FreeCAD.Vector(15, 0, 40)
    
    foliage3 = doc.addObject("Part::Sphere", "Foliage3")
    foliage3.Radius = 15
    foliage3.Placement.Base = FreeCAD.Vector(-15, 0, 40)
    
    doc.recompute()
    
    # 3. Export to STEP
    output_path = "/home/kaiser/gemini_project2/tree_model.step"
    Part.export([trunk, foliage1, foliage2, foliage3], output_path)
    print(f"Tree model successfully exported to {output_path}")

    # 4. Also export to STL for 3D viewers
    output_stl = "/home/kaiser/gemini_project2/tree_model.stl"
    import Mesh
    Mesh.export([trunk, foliage1, foliage2, foliage3], output_stl)
    print(f"Tree model successfully exported to {output_stl}")

    # 5. Export to OBJ for GLB conversion
    output_obj = "/home/kaiser/gemini_project2/tree_model.obj"
    import Mesh
    Mesh.export([trunk, foliage1, foliage2, foliage3], output_obj)
    print(f"Tree model successfully exported to {output_obj}")

if __name__ == "__main__":
    create_tree()
