"""
Blender Controller - Blender 3D Automation
Uses Blender Python API for 3D operations
"""

import logging
import subprocess
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class BlenderController:
    """Control Blender 3D via Python API"""
    
    def __init__(self, blender_path: str = "/Applications/Blender.app/Contents/MacOS/Blender"):
        """
        Initialize Blender controller
        
        Args:
            blender_path: Path to Blender executable
        """
        self.blender_path = blender_path
        self.available = self._check_availability()
        
        if self.available:
            logger.info("Blender controller initialized")
        else:
            logger.warning(f"Blender not found at {blender_path}")
    
    def _check_availability(self) -> bool:
        """Check if Blender is installed"""
        return Path(self.blender_path).exists()
    
    def _run_python_script(self, script: str, background: bool = True) -> str:
        """
        Run Python script in Blender
        
        Args:
            script: Python script to execute
            background: Run in background mode
            
        Returns:
            Script output
        """
        # Save script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            cmd = [self.blender_path]
            if background:
                cmd.append('--background')
            cmd.extend(['--python', script_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Clean up temp file
            Path(script_path).unlink()
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Blender script error: {result.stderr}")
                return ""
        
        except Exception as e:
            logger.error(f"Failed to run Blender script: {e}")
            Path(script_path).unlink(missing_ok=True)
            return ""
    
    def is_available(self) -> bool:
        """Check if Blender is available"""
        return self.available
    
    def create_cube(self, output_file: str, size: float = 2.0) -> bool:
        """
        Create a cube and save to file
        
        Args:
            output_file: Output .blend file path
            size: Cube size
        """
        script = f'''
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create cube
bpy.ops.mesh.primitive_cube_add(size={size}, location=(0, 0, 0))

# Save file
bpy.ops.wm.save_as_mainfile(filepath="{output_file}")

print("Cube created and saved to {output_file}")
'''
        
        result = self._run_python_script(script)
        if result:
            logger.info(f"Created cube: {output_file}")
            return True
        return False
    
    def create_sphere(self, output_file: str, radius: float = 1.0) -> bool:
        """Create a sphere and save to file"""
        script = f'''
import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, location=(0, 0, 0))

bpy.ops.wm.save_as_mainfile(filepath="{output_file}")

print("Sphere created")
'''
        
        result = self._run_python_script(script)
        if result:
            logger.info(f"Created sphere: {output_file}")
            return True
        return False
    
    def render_image(self, blend_file: str, output_image: str, resolution_x: int = 1920, resolution_y: int = 1080) -> bool:
        """
        Render image from .blend file
        
        Args:
            blend_file: Input .blend file
            output_image: Output image path
            resolution_x: Render width
            resolution_y: Render height
        """
        script = f'''
import bpy

# Set render settings
bpy.context.scene.render.resolution_x = {resolution_x}
bpy.context.scene.render.resolution_y = {resolution_y}
bpy.context.scene.render.filepath = "{output_image}"

# Render
bpy.ops.render.render(write_still=True)

print("Render complete: {output_image}")
'''
        
        # Run with blend file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            cmd = [
                self.blender_path,
                '--background',
                blend_file,
                '--python', script_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            Path(script_path).unlink()
            
            if result.returncode == 0:
                logger.info(f"Rendered image: {output_image}")
                return True
            else:
                logger.error(f"Render failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Render error: {e}")
            Path(script_path).unlink(missing_ok=True)
            return False
    
    def add_material(self, blend_file: str, output_file: str, color: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0)) -> bool:
        """
        Add material to object
        
        Args:
            blend_file: Input .blend file
            output_file: Output .blend file
            color: RGBA color tuple
        """
        script = f'''
import bpy

# Get active object
obj = bpy.context.active_object

if obj:
    # Create material
    mat = bpy.data.materials.new(name="Material")
    mat.use_nodes = True
    
    # Set color
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = {color}
    
    # Assign material
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    # Save
    bpy.ops.wm.save_as_mainfile(filepath="{output_file}")
    print("Material added")
else:
    print("No active object")
'''
        
        # Run with blend file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            cmd = [
                self.blender_path,
                '--background',
                blend_file,
                '--python', script_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            Path(script_path).unlink()
            
            if result.returncode == 0:
                logger.info(f"Added material: {output_file}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Add material error: {e}")
            Path(script_path).unlink(missing_ok=True)
            return False
    
    def export_obj(self, blend_file: str, output_obj: str) -> bool:
        """Export to OBJ format"""
        script = f'''
import bpy

bpy.ops.export_scene.obj(filepath="{output_obj}")
print("Exported to OBJ")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            cmd = [
                self.blender_path,
                '--background',
                blend_file,
                '--python', script_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            Path(script_path).unlink()
            
            if result.returncode == 0:
                logger.info(f"Exported OBJ: {output_obj}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Export error: {e}")
            Path(script_path).unlink(missing_ok=True)
            return False


def get_blender_controller() -> BlenderController:
    """Get Blender controller instance"""
    return BlenderController()

