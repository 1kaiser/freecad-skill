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

    print("Importing VTK and loading Temple STL...")
    import vtk
    
    reader = vtk.vtkSTLReader()
    reader.SetFileName("/home/kaiser/projects/freecad-skill/freecad/examples/temple.stl")
    reader.Update()
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.9, 0.9, 0.95) # Clean off-white stone/marble look
    actor.GetProperty().SetAmbient(0.2)
    actor.GetProperty().SetDiffuse(0.7)
    actor.GetProperty().SetSpecular(0.15)
    
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.15, 0.17, 0.20) # Slate grey background
    
    # Position camera explicitly
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(0, 0, 140)
    camera.SetPosition(900, -900, 700)
    camera.SetViewUp(0, 0, 1)
    
    renderer.ResetCamera() # Adjust zoom automatically to fit the structure
    
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1024, 768)
    
    print("Rendering temple mesh to PNG...")
    renderWindow.Render()
    
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(renderWindow)
    w2i.Update()
    
    out_png = "/home/kaiser/projects/freecad-skill/freecad/examples/temple.png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(out_png)
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()
    print(f"Successfully rendered temple to {out_png}")
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
