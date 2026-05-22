import os
import sys
import math

# Ensure FreeCAD paths
sys.path.extend(['/home/kaiser/.conda/envs/freecad_env/lib', '/home/kaiser/.conda/envs/freecad_env/Ext'])
import FreeCAD
import Part
import Mesh

def main():
    print("Initializing FreeCAD document for Temple of Heaven...")
    doc = FreeCAD.newDocument("TempleOfHeaven")

    # Helper function to create cylinders
    def add_cylinder(name, radius, height, x=0.0, y=0.0, z=0.0):
        cyl = doc.addObject("Part::Cylinder", name)
        cyl.Radius = float(radius)
        cyl.Height = float(height)
        cyl.Placement.Base = FreeCAD.Vector(float(x), float(y), float(z))
        doc.recompute()
        return cyl

    # Helper function to create cones
    def add_cone(name, base_radius, top_radius, height, x=0.0, y=0.0, z=0.0):
        cone = doc.addObject("Part::Cone", name)
        cone.Radius1 = float(base_radius)
        cone.Radius2 = float(top_radius)
        cone.Height = float(height)
        cone.Placement.Base = FreeCAD.Vector(float(x), float(y), float(z))
        doc.recompute()
        return cone

    # Helper function to create spheres
    def add_sphere(name, radius, x=0.0, y=0.0, z=0.0):
        sphere = doc.addObject("Part::Sphere", name)
        sphere.Radius = float(radius)
        sphere.Placement.Base = FreeCAD.Vector(float(x), float(y), float(z))
        doc.recompute()
        return sphere

    parts = []

    # --- 1. Three-Tiered Altar Platform (Base) ---
    # Tier 1 (Bottom): 68m diameter, 2m height (scaled to mm/10: 340 radius, 20 height)
    t1 = add_cylinder("Altar_Tier_1", 340.0, 20.0, 0, 0, 0)
    parts.append(t1)

    # Tier 2 (Middle): 52m diameter, 2m height (scaled to 260 radius, 20 height)
    t2 = add_cylinder("Altar_Tier_2", 260.0, 20.0, 0, 0, 20.0)
    parts.append(t2)

    # Tier 3 (Top): 36m diameter, 2m height (scaled to 180 radius, 20 height)
    t3 = add_cylinder("Altar_Tier_3", 180.0, 20.0, 0, 0, 40.0)
    parts.append(t3)

    # --- 2. The Main Hall Chamber ---
    # Circular Hall sitting on Tier 3 (Z=60). Height of wall = 120. Outer radius = 160.
    hall_outer = add_cylinder("Hall_Outer", 160.0, 120.0, 0, 0, 60.0)
    # Make it hollow by cutting inner cylinder (Radius = 150)
    hall_inner = add_cylinder("Hall_Inner", 150.0, 120.0, 0, 0, 60.0)
    doc.recompute()

    cut_hall = doc.addObject("Part::Cut", "Hall_Wall")
    cut_hall.Base = hall_outer
    cut_hall.Tool = hall_inner
    doc.recompute()
    parts.append(cut_hall)

    # Add door arches (4 cutouts at 0, 90, 180, 270 degrees)
    for i in range(4):
        angle = math.radians(i * 90)
        x = 160.0 * math.cos(angle)
        y = 160.0 * math.sin(angle)
        box = doc.addObject("Part::Box", f"Door_{i}")
        box.Length = 30.0
        box.Width = 30.0
        box.Height = 70.0
        box.Placement.Base = FreeCAD.Vector(x - 15.0, y - 15.0, 60.0)
        doc.recompute()
        
        cut_with_door = doc.addObject("Part::Cut", f"Hall_Wall_Door_{i}")
        cut_with_door.Base = parts[-1]
        cut_with_door.Tool = box
        doc.recompute()
        parts[-1] = cut_with_door

    # --- 3. The Pillars (Columns) ---
    # Inner Pillars: 4 columns, radius 6, height 192 (representing 4 seasons)
    for i in range(4):
        angle = math.radians(i * 90 + 45) # place in corners
        x = 50.0 * math.cos(angle)
        y = 50.0 * math.sin(angle)
        p = add_cylinder(f"Inner_Pillar_{i}", 6.0, 192.0, x, y, 60.0)
        parts.append(p)

    # Middle Pillars: 12 columns, radius 5, height 140 (representing 12 months)
    for i in range(12):
        angle = math.radians(i * 30)
        x = 100.0 * math.cos(angle)
        y = 100.0 * math.sin(angle)
        p = add_cylinder(f"Middle_Pillar_{i}", 5.0, 140.0, x, y, 60.0)
        parts.append(p)

    # Outer Pillars: 12 columns, radius 4, height 90 (representing 12 shichen)
    for i in range(12):
        angle = math.radians(i * 30 + 15)
        x = 145.0 * math.cos(angle)
        y = 145.0 * math.sin(angle)
        p = add_cylinder(f"Outer_Pillar_{i}", 4.0, 90.0, x, y, 60.0)
        parts.append(p)

    # --- 4. Triple-Eaved Roof ---
    # Bottom roof eave: Sits at Z = 140. Height = 20. Radii = 175 -> 150
    roof_bottom = add_cone("Roof_Bottom", 175.0, 150.0, 20.0, 0, 0, 140.0)
    parts.append(roof_bottom)

    # Middle roof eave: Sits at Z = 190. Height = 20. Radii = 135 -> 110
    roof_middle = add_cone("Roof_Middle", 135.0, 110.0, 20.0, 0, 0, 190.0)
    parts.append(roof_middle)

    # Top roof cone: Sits at Z = 240. Height = 40. Radii = 95 -> 0.1
    roof_top = add_cone("Roof_Top", 95.0, 0.1, 40.0, 0, 0, 240.0)
    parts.append(roof_top)

    # Finial (Gilded sphere) at the apex: Z = 280, Radius = 12
    finial = add_sphere("Finial", 12.0, 0, 0, 280.0)
    parts.append(finial)

    # --- 5. Combine and Export ---
    comp = doc.addObject("Part::Compound", "TempleOfHeavenModel")
    comp.Links = parts
    doc.recompute()

    # Save document
    doc_path = "/home/kaiser/projects/freecad-skill/freecad/examples/temple.fcstd"
    doc.saveAs(doc_path)
    print(f"Saved FreeCAD document to {doc_path}")

    # Export STEP
    out_step = "/home/kaiser/projects/freecad-skill/freecad/examples/temple.step"
    Part.export([comp], out_step)
    print(f"Exported STEP to {out_step}")

    # Export STL
    out_stl = "/home/kaiser/projects/freecad-skill/freecad/examples/temple.stl"
    Mesh.export([comp], out_stl)
    print(f"Exported STL to {out_stl}")

    # Export individual material groups for rendering
    # 1. Altar
    altar_comp = doc.addObject("Part::Compound", "AltarGroup")
    altar_comp.Links = parts[0:3]
    doc.recompute()
    out_altar = "/home/kaiser/projects/freecad-skill/freecad/examples/temple_altar.stl"
    Mesh.export([altar_comp], out_altar)
    print(f"Exported Altar STL to {out_altar}")

    # 2. Walls and Pillars
    wp_comp = doc.addObject("Part::Compound", "WallsPillarsGroup")
    wp_comp.Links = parts[3:32]
    doc.recompute()
    out_wp = "/home/kaiser/projects/freecad-skill/freecad/examples/temple_walls_pillars.stl"
    Mesh.export([wp_comp], out_wp)
    print(f"Exported Walls/Pillars STL to {out_wp}")

    # 3. Roofs
    roofs_comp = doc.addObject("Part::Compound", "RoofsGroup")
    roofs_comp.Links = parts[32:35]
    doc.recompute()
    out_roofs = "/home/kaiser/projects/freecad-skill/freecad/examples/temple_roofs.stl"
    Mesh.export([roofs_comp], out_roofs)
    print(f"Exported Roofs STL to {out_roofs}")

    # 4. Finial
    finial_comp = doc.addObject("Part::Compound", "FinialGroup")
    finial_comp.Links = [parts[35]]
    doc.recompute()
    out_finial = "/home/kaiser/projects/freecad-skill/freecad/examples/temple_finial.stl"
    Mesh.export([finial_comp], out_finial)
    print(f"Exported Finial STL to {out_finial}")

if __name__ == "__main__":
    main()

