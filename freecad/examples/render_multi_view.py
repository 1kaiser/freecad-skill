import argparse
import subprocess
import time
import os
import sys
import math

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Generic Multi-View 3D Plotter with Materials and Solar Lighting")
    
    # Inputs
    parser.add_argument("-i", "--inputs", nargs="+", help="Paths to input 3D model file(s) (STL, OBJ, STEP, IGES, FCSTD, BREP)")
    parser.add_argument("-c", "--colors", nargs="+", help="Colors for each input (Hex string like '#FF0000' or float RGB like '0.7,0.1,0.1')")
    parser.add_argument("-m", "--materials", nargs="+", help="Material presets for each input (marble, stone, matte, plastic, glossy, tile, gold, metal)")
    
    # Lighting & Output
    parser.add_argument("-o", "--output", default=None, help="Path to save the output combined preview image")
    parser.add_argument("-el", "--elevation", type=float, default=60.0, help="Solar elevation angle in degrees (default: 60.0)")
    parser.add_argument("-az", "--azimuth", type=float, default=180.0, help="Solar azimuth angle in degrees (default: 180.0 - South)")
    parser.add_argument("--size", type=int, default=400, help="Resolution (width & height) of each view panel (default: 400)")
    
    # Advanced parameterization
    parser.add_argument("--views", nargs="+", default=["Top", "Side", "Front", "Isometric"],
                        help="Views to render (choices: Top, Bottom, Front, Back, Side, Left, Isometric)")
    parser.add_argument("--bg-color", default="#1F242C",
                        help="Background color in hex (e.g. #1F242C) or RGB floats (e.g. 0.12,0.14,0.16)")
    parser.add_argument("--headlight", type=float, default=0.3,
                        help="Headlight intensity tracking camera view (default: 0.3)")
    parser.add_argument("--zoom", type=float, default=0.85,
                        help="Camera zoom factor, < 1.0 zooms out (default: 0.85)")
    parser.add_argument("--distance-scale", type=float, default=1.0,
                        help="Multiplier for camera distance to scale viewport bounds (default: 1.0)")
    
    return parser.parse_args()

def parse_color(color_str):
    color_str = color_str.strip()
    if color_str.startswith("#"):
        h = color_str.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    else:
        return tuple(float(x) for x in color_str.split(","))

# Material properties mapper
MATERIAL_PRESETS = {
    "marble": {"ambient": 0.2, "diffuse": 0.75, "specular": 0.1, "spec_power": 5},
    "stone": {"ambient": 0.2, "diffuse": 0.75, "specular": 0.1, "spec_power": 5},
    "matte": {"ambient": 0.25, "diffuse": 0.7, "specular": 0.05, "spec_power": 2},
    "plastic": {"ambient": 0.25, "diffuse": 0.7, "specular": 0.05, "spec_power": 2},
    "glossy": {"ambient": 0.15, "diffuse": 0.8, "specular": 0.4, "spec_power": 30},
    "tile": {"ambient": 0.15, "diffuse": 0.8, "specular": 0.4, "spec_power": 30},
    "gold": {"ambient": 0.3, "diffuse": 0.6, "specular": 0.8, "spec_power": 50},
    "metal": {"ambient": 0.3, "diffuse": 0.6, "specular": 0.8, "spec_power": 50}
}

# Standard views relative to focal point and camera distance
VIEW_CONFIGS = {
    "top": {
        "name": "Top", 
        "pos": lambda fx, fy, fz, d: (fx, fy, fz + d), 
        "up": (0.0, 1.0, 0.0)
    },
    "bottom": {
        "name": "Bottom", 
        "pos": lambda fx, fy, fz, d: (fx, fy, fz - d), 
        "up": (0.0, -1.0, 0.0)
    },
    "front": {
        "name": "Front", 
        "pos": lambda fx, fy, fz, d: (fx, fy - d, fz), 
        "up": (0.0, 0.0, 1.0)
    },
    "back": {
        "name": "Back", 
        "pos": lambda fx, fy, fz, d: (fx, fy + d, fz), 
        "up": (0.0, 0.0, 1.0)
    },
    "side": { # Right view
        "name": "Side", 
        "pos": lambda fx, fy, fz, d: (fx + d, fy, fz), 
        "up": (0.0, 0.0, 1.0)
    },
    "left": {
        "name": "Left", 
        "pos": lambda fx, fy, fz, d: (fx - d, fy, fz), 
        "up": (0.0, 0.0, 1.0)
    },
    "isometric": {
        "name": "Isometric", 
        "pos": lambda fx, fy, fz, d: (fx + d * 0.707, fy - d * 0.707, fz + d * 0.5), 
        "up": (0.0, 0.0, 1.0)
    }
}

def convert_to_stl(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.stl', '.obj']:
        return file_path, False
    
    print(f"Converting {file_path} to temporary STL via FreeCAD...")
    import tempfile
    
    # Configure path to import FreeCAD modules
    fc_paths = ['/home/kaiser/.conda/envs/freecad_env/lib', '/home/kaiser/.conda/envs/freecad_env/Ext']
    for p in fc_paths:
        if p not in sys.path:
            sys.path.append(p)
            
    import FreeCAD
    import Part
    import Mesh
    
    fd, temp_stl = tempfile.mkstemp(suffix='.stl')
    os.close(fd)
    
    try:
        if ext == '.fcstd':
            doc = FreeCAD.openDocument(file_path)
            # Find all top-level shapes
            objs = [o for o in doc.Objects if hasattr(o, "Shape") or o.isDerivedFrom("Part::Feature")]
            if not objs:
                # Fallback to all objects if none matches Part::Feature
                objs = doc.Objects
            if not objs:
                raise ValueError(f"FreeCAD document {file_path} is empty.")
            comp = doc.addObject("Part::Compound", "TempCompound")
            comp.Links = objs
            doc.recompute()
            Mesh.export([comp], temp_stl)
            FreeCAD.closeDocument(doc.Name)
        elif ext in ['.step', '.stp', '.igs', '.iges', '.brep']:
            shape = Part.read(file_path)
            doc = FreeCAD.newDocument("TempDoc")
            feature = doc.addObject("Part::Feature", "TempFeature")
            feature.Shape = shape
            doc.recompute()
            Mesh.export([feature], temp_stl)
            FreeCAD.closeDocument(doc.Name)
        else:
            raise ValueError(f"Unsupported input format: {ext}")
        print(f"Conversion successful: {temp_stl}")
        return temp_stl, True
    except Exception as e:
        if os.path.exists(temp_stl):
            os.remove(temp_stl)
        raise e

def main():
    args = parse_args()
    base_dir = "/home/kaiser/projects/freecad-skill/freecad/examples"
    temp_files = []
    
    # Setup default inputs if none are specified (Backward compatible Temple of Heaven defaults)
    if not args.inputs:
        print("No inputs specified. Using Temple of Heaven default configuration...")
        args.inputs = [
            f"{base_dir}/temple_altar.stl",
            f"{base_dir}/temple_walls_pillars.stl",
            f"{base_dir}/temple_roofs.stl",
            f"{base_dir}/temple_finial.stl"
        ]
        # Colors: Off-white, Red, Blue, Gold
        args.colors = ["#ECECEF", "#C02626", "#14388C", "#F2BF26"]
        args.materials = ["marble", "matte", "glossy", "gold"]
        if not args.output:
            args.output = f"{base_dir}/temple_preview.png"
    else:
        # If output is not specified for custom run
        if not args.output:
            args.output = "preview.png"
            
    # Resolve absolute output path
    args.output = os.path.abspath(args.output)
    
    # Convert and resolve inputs
    resolved_inputs = []
    try:
        for file_path in args.inputs:
            abs_path = os.path.abspath(file_path)
            temp_path, is_temp = convert_to_stl(abs_path)
            resolved_inputs.append((temp_path, abs_path))
            if is_temp:
                temp_files.append(temp_path)
    except Exception as e:
        print(f"Error during input resolution or format conversion: {e}")
        # Clean up already created temp files before exiting
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        sys.exit(1)
        
    # Process colors
    colors = []
    if args.colors:
        for c in args.colors:
            colors.append(parse_color(c))
    # Fill remaining colors with default light grey/stone look
    while len(colors) < len(args.inputs):
        colors.append((0.9, 0.9, 0.95))
        
    # Process materials
    materials = []
    if args.materials:
        for m in args.materials:
            m_lower = m.lower()
            materials.append(MATERIAL_PRESETS.get(m_lower, MATERIAL_PRESETS["matte"]))
    while len(materials) < len(args.inputs):
        materials.append(MATERIAL_PRESETS["matte"])

    # Parse background color
    bg_color = parse_color(args.bg_color)

    # Resolve views to render
    views_to_render = []
    for v in args.views:
        v_lower = v.lower()
        if v_lower in VIEW_CONFIGS:
            views_to_render.append(VIEW_CONFIGS[v_lower])
        else:
            print(f"Warning: Unknown view name '{v}'. Skipping.")
            
    if not views_to_render:
        print("Error: No valid views specified to render.")
        for tf in temp_files:
            if os.path.exists(tf):
                os.remove(tf)
        sys.exit(1)

    # Spawning virtual frame buffer for headless execution
    xvfb_process = None
    try:
        print("Starting Xvfb...")
        xvfb_path = '/home/kaiser/.conda/envs/freecad_env/x86_64-conda-linux-gnu/sysroot/usr/bin/Xvfb'
        
        # Setup environment
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = '/home/kaiser/.conda/envs/freecad_env/lib:' + env.get('LD_LIBRARY_PATH', '')
        env['LIBGL_ALWAYS_SOFTWARE'] = '1'
        env['LIBGL_DRIVERS_PATH'] = '/usr/lib/x86_64-linux-gnu/dri'
        
        xvfb_process = subprocess.Popen([
            xvfb_path, ':99', '-screen', '0', '1600x1200x24',
            '+extension', 'GLX', '+extension', 'RENDER', '-noreset'
        ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(2)
        
        if xvfb_process.poll() is not None:
            print(f"Xvfb failed to start. Code: {xvfb_process.returncode}")
            sys.exit(1)
            
        os.environ['DISPLAY'] = ':99'
        os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'
        os.environ['LIBGL_DRIVERS_PATH'] = '/usr/lib/x86_64-linux-gnu/dri'
        os.environ['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH']
        print("Xvfb started successfully.")

        print("Importing VTK...")
        import vtk
        
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(*bg_color)
        
        # Load all meshes and configure actors
        actors = []
        for (temp_path, original_path), color, mat in zip(resolved_inputs, colors, materials):
            print(f"Loading mesh: {original_path}...")
            
            ext = os.path.splitext(original_path)[1].lower()
            if ext == '.obj':
                reader = vtk.vtkOBJReader()
            else:
                reader = vtk.vtkSTLReader()
                
            reader.SetFileName(temp_path)
            reader.Update()
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            prop = actor.GetProperty()
            prop.SetColor(*color)
            prop.SetAmbient(mat["ambient"])
            prop.SetDiffuse(mat["diffuse"])
            prop.SetSpecular(mat["specular"])
            prop.SetSpecularPower(mat["spec_power"])
            
            renderer.AddActor(actor)
            actors.append(actor)
            
        if not actors:
            print("Error: No actors loaded.")
            sys.exit(1)
            
        # 1. Reset camera first to automatically compute scene bounds
        print("Computing scene bounding box and camera distance...")
        renderer.ResetCamera()
        camera = renderer.GetActiveCamera()
        
        # Auto-detect focal point (scene center) and bounding box scale
        f_x, f_y, f_z = camera.GetFocalPoint()
        default_pos = camera.GetPosition()
        camera_dist = math.sqrt((default_pos[0]-f_x)**2 + (default_pos[1]-f_y)**2 + (default_pos[2]-f_z)**2)
        print(f"Scene Center (Focal Point): ({f_x:.2f}, {f_y:.2f}, {f_z:.2f})")
        print(f"Auto-calculated camera distance: {camera_dist:.2f}")

        # 2. Lighting Setup based on user Solar coordinates (Elevation & Azimuth)
        # Convert angles to 3D direction vector
        el_rad = math.radians(args.elevation)
        az_rad = math.radians(args.azimuth)
        
        # Calculate primary sunlight coordinates relative to focal point
        sun_d = camera_dist * 2.0
        lx = sun_d * math.cos(el_rad) * math.sin(az_rad)
        ly = sun_d * math.cos(el_rad) * math.cos(az_rad)
        lz = sun_d * math.sin(el_rad)
        
        sun_light = vtk.vtkLight()
        sun_light.SetPositional(0) # Directional
        sun_light.SetPosition(lx + f_x, ly + f_y, lz + f_z)
        sun_light.SetFocalPoint(f_x, f_y, f_z)
        sun_light.SetColor(1.0, 0.96, 0.90) # Warm sunlight
        sun_light.SetIntensity(1.2)
        renderer.AddLight(sun_light)
        
        # Skylight (cool directional fill from opposite side)
        sky_light = vtk.vtkLight()
        sky_light.SetPositional(0)
        sky_light.SetPosition(-lx + f_x, -ly + f_y, lz + f_z)
        sky_light.SetFocalPoint(f_x, f_y, f_z)
        sky_light.SetColor(0.85, 0.90, 1.0) # Soft blue sky
        sky_light.SetIntensity(0.35)
        renderer.AddLight(sky_light)

        # Camera-aligned headlight to prevent pitch-black unlit views (e.g. Side view)
        head_light = None
        if args.headlight > 0.0:
            head_light = vtk.vtkLight()
            head_light.SetPositional(0)
            head_light.SetColor(1.0, 1.0, 1.0)
            head_light.SetIntensity(args.headlight)
            renderer.AddLight(head_light)

        # Create render window
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetOffScreenRendering(1)
        renderWindow.AddRenderer(renderer)
        renderWindow.SetSize(args.size, args.size)
        
        # Setup image filter
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(renderWindow)
        
        scaled_dist = camera_dist * args.distance_scale
        rendered_images = []
        
        for v in views_to_render:
            print(f"Rendering {v['name']} View...")
            pos = v["pos"](f_x, f_y, f_z, scaled_dist)
            camera.SetPosition(*pos)
            camera.SetFocalPoint(f_x, f_y, f_z)
            camera.SetViewUp(*v["up"])
            renderer.ResetCamera()
            
            # Apply padding (zoom out/in)
            camera.Zoom(args.zoom)
            
            # Position headlight at current camera view
            if head_light is not None:
                head_light.SetPosition(*pos)
                head_light.SetFocalPoint(f_x, f_y, f_z)
            
            renderWindow.Render()
            w2i.Modified()
            w2i.Update()
            
            img = vtk.vtkImageData()
            img.DeepCopy(w2i.GetOutput())
            rendered_images.append(img)
            
        print("Combining views horizontally...")
        append = vtk.vtkImageAppend()
        append.SetAppendAxis(0) # horizontal combine
        for img in rendered_images:
            append.AddInputData(img)
        append.Update()
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(args.output)
        writer.SetInputConnection(append.GetOutputPort())
        writer.Write()
        print(f"Successfully saved combined preview to {args.output}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up temporary STL files
        for tf in temp_files:
            try:
                if os.path.exists(tf):
                    os.remove(tf)
            except Exception as e:
                print(f"Warning: Failed to delete temporary file {tf}: {e}")
                
        if xvfb_process is not None:
            xvfb_process.terminate()
            xvfb_process.wait()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

if __name__ == "__main__":
    main()
