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
        xvfb_path, ':99', '-screen', '0', '1024x768x24',
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

    print("Importing VTK and loading STL...")
    import vtk
    
    reader = vtk.vtkSTLReader()
    reader.SetFileName("/home/kaiser/projects/freecad-skill/freecad/examples/bracket.stl")
    reader.Update()
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.15, 0.17, 0.20) # Modern slate grey background
    
    # Position camera
    camera = renderer.GetActiveCamera()
    renderer.ResetCamera()
    camera.Azimuth(35)
    camera.Elevation(30)
    
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(800, 600)
    
    print("Rendering mesh to PNG...")
    renderWindow.Render()
    
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(renderWindow)
    w2i.Update()
    
    out_png = "/home/kaiser/projects/freecad-skill/freecad/examples/bracket.png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(out_png)
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()
    print(f"Successfully rendered image to {out_png}")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if xvfb_process is not None:
        xvfb_process.terminate()
        xvfb_process.wait()
    # Bypasses X11 cleanup connection warnings/crashes
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
