---
name: freecad
description: Procedural 3D modeling, CAD automation, and engineering analysis using FreeCAD. Use for creating CAD parts, exporting STEP/STL/GLB files, and performing geometric computations.
---

# FreeCAD Automation Skill

Use this skill to generate 3D geometry and perform engineering workflows using the FreeCAD Python API.

## Core Workflow

1.  **Write a Python Script**: Use the `Part`, `Mesh`, `Draft`, and `importOBJ` modules.
2.  **Ensure Path Compatibility**: Always add `/usr/lib/freecad/lib` and `/usr/share/freecad/Mod` to `sys.path`.
3.  **Headless Execution**:
    - Use `freecadcmd -c script.py` for purely geometric tasks.
    - Use `xvfb-run -a freecad script.py` if GUI modules or offscreen rendering are required.
4.  **Export & Convert**:
    - **STEP**: `Part.export([objs], "file.step")`
    - **STL**: `Mesh.export([objs], "file.stl")`
    - **GLB**: Export to OBJ via `Mesh.export`, then convert using `obj2gltf -i file.obj -o file.glb --binary`.

## Python API Patterns

### Document Setup
```python
import FreeCAD, Part
doc = FreeCAD.newDocument("MyPart")
```

### Creating Primitives
```python
box = doc.addObject("Part::Box", "MyBox")
box.Length, box.Width, box.Height = 10, 10, 10
doc.recompute()
```

### Transformations
```python
box.Placement.Base = FreeCAD.Vector(x, y, z)
box.Placement.Rotation = FreeCAD.Rotation(axis, angle)
```

## Critical Constraints
- **Absolute Paths**: Always use absolute paths for export to avoid directory confusion in `freecadcmd`.
- **Recompute**: Always call `doc.recompute()` after modifying properties.
- **Unit System**: Default is mm.
- **Orientation**: FreeCAD is **Z-up**. For web/GLB viewers, apply a -90 deg X-axis rotation to convert to **Y-up**.

## Dependencies
- **freecad**: `sudo apt install freecad`
- **xvfb**: `sudo apt install xvfb` (for headless GUI)
- **obj2gltf**: `npm install -g obj2gltf` (for GLB export)
