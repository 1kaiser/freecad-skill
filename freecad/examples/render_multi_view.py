import subprocess
import time
import os
import sys

xvfb_process = None
try:
    print("Starting Xvfb...")
    xvfb_path = '/home/kaiser/.conda/envs/freecad_env/x86_64-conda-linux-gnu/sysroot/usr/bin/Xvfb'
    
    # Setup environment
    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = '/home/kaiser/.conda/envs/freecad_env/lib:' + env.get('LD_LIBRARY_PATH', '')
    env['LIBGL_ALWAYS_SOFTWARE'] = '1'
    env['LIBGL_DRIVERS_PATH'] = '/usr/lib/x86_64-linux-gnu/dri'
    
    # Run Xvfb, with GLX/RENDER enabled
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
    renderer.SetBackground(0.12, 0.14, 0.16) # Deep modern slate background
    
    # Helper to load and configure actors
    def add_temple_part(filename, color, ambient=0.2, diffuse=0.7, specular=0.1, spec_power=10):
        print(f"Loading {filename}...")
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        prop = actor.GetProperty()
        prop.SetColor(*color)
        prop.SetAmbient(ambient)
        prop.SetDiffuse(diffuse)
        prop.SetSpecular(specular)
        prop.SetSpecularPower(spec_power)
        
        renderer.AddActor(actor)
        return actor

    base_dir = "/home/kaiser/projects/freecad-skill/freecad/examples"
    
    # 1. Altar: Off-white marble / limestone
    add_temple_part(f"{base_dir}/temple_altar.stl", (0.92, 0.92, 0.94), ambient=0.2, diffuse=0.75, specular=0.1, spec_power=5)
    
    # 2. Walls and Pillars: Imperial Red
    add_temple_part(f"{base_dir}/temple_walls_pillars.stl", (0.75, 0.15, 0.15), ambient=0.25, diffuse=0.7, specular=0.05, spec_power=2)
    
    # 3. Roofs: Deep cobalt blue glazed tiles
    add_temple_part(f"{base_dir}/temple_roofs.stl", (0.08, 0.22, 0.55), ambient=0.15, diffuse=0.8, specular=0.4, spec_power=30)
    
    # 4. Finial: Metallic Gold
    add_temple_part(f"{base_dir}/temple_finial.stl", (0.95, 0.75, 0.15), ambient=0.3, diffuse=0.6, specular=0.8, spec_power=50)

    # --- Lighting Setup (April Sun Path in Beijing) ---
    # In April in Beijing, noon solar elevation is ~60 degrees from South
    # Sunlight (Directional, warm white)
    sun_light = vtk.vtkLight()
    sun_light.SetPositional(0) # Directional light
    sun_light.SetPosition(0.0, -1000.0, 1732.0) # Shining from South (negative Y) at 60 deg elevation
    sun_light.SetFocalPoint(0.0, 0.0, 140.0)
    sun_light.SetColor(1.0, 0.96, 0.90) # Warm sunlight
    sun_light.SetIntensity(1.2)
    renderer.AddLight(sun_light)
    
    # Skylight (Directional fill, cool light from North)
    sky_light = vtk.vtkLight()
    sky_light.SetPositional(0) # Directional light
    sky_light.SetPosition(0.0, 1000.0, 500.0) # Soft fill from North
    sky_light.SetFocalPoint(0.0, 0.0, 140.0)
    sky_light.SetColor(0.85, 0.90, 1.0) # Soft blue sky fill
    sky_light.SetIntensity(0.35)
    renderer.AddLight(sky_light)

    # Create render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(400, 400) # Each panel will be 400x400
    
    # Setup WindowToImageFilter
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(renderWindow)
    
    camera = renderer.GetActiveCamera()
    
    # Define views: Top, Side, Front, Isometric
    views = [
        {"name": "Top", "pos": (0.0, 0.0, 1000.0), "up": (0.0, 1.0, 0.0)},
        {"name": "Side", "pos": (1000.0, 0.0, 140.0), "up": (0.0, 0.0, 1.0)},
        {"name": "Front", "pos": (0.0, -1000.0, 140.0), "up": (0.0, 0.0, 1.0)},
        {"name": "Isometric", "pos": (700.0, -700.0, 500.0), "up": (0.0, 0.0, 1.0)}
    ]
    
    rendered_images = []
    
    for v in views:
        print(f"Rendering {v['name']} View...")
        camera.SetPosition(*v["pos"])
        camera.SetFocalPoint(0.0, 0.0, 140.0)
        camera.SetViewUp(*v["up"])
        renderer.ResetCamera()
        camera.Zoom(0.85)
        
        renderWindow.Render()
        w2i.Modified() # Force filter to update its cache
        w2i.Update()
        
        img = vtk.vtkImageData()
        img.DeepCopy(w2i.GetOutput())
        rendered_images.append(img)
        
    print("Combining views horizontally...")
    # Append images horizontally along the X axis (AppendAxis = 0)
    append = vtk.vtkImageAppend()
    append.SetAppendAxis(0)
    for img in rendered_images:
        append.AddInputData(img)
    append.Update()
    
    out_preview = f"{base_dir}/temple_preview.png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(out_preview)
    writer.SetInputConnection(append.GetOutputPort())
    writer.Write()
    print(f"Successfully saved combined preview to {out_preview}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if xvfb_process is not None:
        xvfb_process.terminate()
        xvfb_process.wait()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
