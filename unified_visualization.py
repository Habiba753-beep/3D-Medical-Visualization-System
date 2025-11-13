"""
Unified Visualization Module
Combines: Clipping Planes + Curved MPR + CT Viewer
"""

import vtk
import numpy as np
# After line 7 (after "import numpy as np")
try:
    from vtkmodules.util import numpy_support
    NUMPY_SUPPORT_AVAILABLE = True
except ImportError:
    NUMPY_SUPPORT_AVAILABLE = False
    print("Warning: VTK numpy support not available")

# ========== CLIPPING MANAGER ==========

class ClippingManager:
    """Manages 3 independent, orthogonal clipping planes"""
    
    def __init__(self):
        self.actors = {}
        self.scene_bounds = [0] * 6
        
        self.plane_x = vtk.vtkPlane()
        self.plane_x.SetNormal(1, 0, 0)
        
        self.plane_y = vtk.vtkPlane()
        self.plane_y.SetNormal(0, 1, 0)
        
        self.plane_z = vtk.vtkPlane()
        self.plane_z.SetNormal(0, 0, 1)
        
        self.enabled_x = False
        self.enabled_y = False
        self.enabled_z = False
        
        self.update_plane_origins(50, 50, 50)
    
    def set_actors(self, actors):
        self.actors = actors
    
    def set_scene_bounds(self, bounds):
        if bounds:
            self.scene_bounds = bounds
            print(f"[ClippingManager] Scene bounds set: {bounds}")
            self.update_plane_origins(50, 50, 50)
    
    def update_plane_state(self, axis, enabled, position_percent):
        if axis == 'x':
            self.enabled_x = enabled
            self.update_plane_origin('x', position_percent)
        elif axis == 'y':
            self.enabled_y = enabled
            self.update_plane_origin('y', position_percent)
        elif axis == 'z':
            self.enabled_z = enabled
            self.update_plane_origin('z', position_percent)
        
        self.apply_clipping()
    
    def update_plane_origins(self, x_percent, y_percent, z_percent):
        self.update_plane_origin('x', x_percent)
        self.update_plane_origin('y', y_percent)
        self.update_plane_origin('z', z_percent)
    
    def update_plane_origin(self, axis, position_percent):
        percent = position_percent / 100.0
        
        x_min, x_max = self.scene_bounds[0], self.scene_bounds[1]
        y_min, y_max = self.scene_bounds[2], self.scene_bounds[3]
        z_min, z_max = self.scene_bounds[4], self.scene_bounds[5]
        
        if x_max == x_min: x_max = x_min + 1.0
        if y_max == y_min: y_max = y_min + 1.0
        if z_max == z_min: z_max = z_min + 1.0
        
        if axis == 'x':
            origin_x = x_min + (x_max - x_min) * percent
            self.plane_x.SetOrigin(origin_x, 0, 0)
        elif axis == 'y':
            origin_y = y_min + (y_max - y_min) * percent
            self.plane_y.SetOrigin(0, origin_y, 0)
        elif axis == 'z':
            origin_z = z_min + (z_max - z_min) * percent
            self.plane_z.SetOrigin(0, 0, origin_z)
    
    def apply_clipping(self):
        if not self.actors:
            return
        
        for actor in self.actors.values():
            mapper = actor.GetMapper()
            mapper.RemoveAllClippingPlanes()
            
            if self.enabled_x:
                mapper.AddClippingPlane(self.plane_x)
            if self.enabled_y:
                mapper.AddClippingPlane(self.plane_y)
            if self.enabled_z:
                mapper.AddClippingPlane(self.plane_z)
    
    def remove_all_clipping(self):
        for actor in self.actors.values():
            mapper = actor.GetMapper()
            mapper.RemoveAllClippingPlanes()

# ========== INTERACTIVE MPR MANAGER (NEW!) ==========

class InteractiveMPRManager:
    """Manages 3 interactive MPR planes using vtkImagePlaneWidget"""
    
    def __init__(self):
        """Initialize MPR plane manager"""
        self.planeWidgetX = None  # Sagittal
        self.planeWidgetY = None  # Coronal
        self.planeWidgetZ = None  # Axial
        self.interactor = None
        self.ct_image = None
        
        # Plane states
        self.enabled_x = False
        self.enabled_y = False
        self.enabled_z = False
    
    def set_interactor(self, interactor):
        """Set the VTK interactor (required for plane widgets)"""
        self.interactor = interactor
        print(f"[MPRManager] Interactor set: {self.interactor is not None}")
    
    def set_ct_image(self, ct_image):
        """Set CT image data for the planes"""
        # Clear any old planes first
        self.remove_all_planes()
        
        self.ct_image = ct_image
        
        if ct_image and self.interactor:
            print("[MPRManager] Creating plane widgets...")
            self.create_plane_widgets()
        else:
            print(f"[MPRManager] Cannot create planes - CT: {ct_image is not None}, Interactor: {self.interactor is not None}")
    
    def create_plane_widgets(self):
        """Create the three interactive image plane widgets with PROPER texture setup"""
        if not self.ct_image or not self.interactor:
            print("[MPRManager] Cannot create planes: missing CT image or interactor")
            return
        
        bounds = self.ct_image.GetBounds()
        center = self.ct_image.GetCenter()
        scalar_range = self.ct_image.GetScalarRange()
        
        print(f"[MPRManager] Creating plane widgets")
        print(f"  Center: {center}")
        print(f"  Bounds: {bounds}")
        print(f"  Scalar Range: {scalar_range}")
        
        # ✅ OPTIMAL window/level for CT
        window = 1500
        level = -500
        
        # --- X PLANE (Sagittal) ---
        self.planeWidgetX = vtk.vtkImagePlaneWidget()
        self.planeWidgetX.SetInteractor(self.interactor)
        self.planeWidgetX.SetInputData(self.ct_image)
        self.planeWidgetX.SetPlaneOrientationToXAxes()
        self.planeWidgetX.SetSlicePosition(center[0])
        
        # ✅ CRITICAL: These settings make the texture visible
        self.planeWidgetX.DisplayTextOn()
        self.planeWidgetX.SetWindowLevel(window, level)
        self.planeWidgetX.SetResliceInterpolateToLinear()
        self.planeWidgetX.TextureInterpolateOn()
        self.planeWidgetX.SetUseContinuousCursor(False)
        self.planeWidgetX.SetMarginSizeX(0.0)
        self.planeWidgetX.SetMarginSizeY(0.0)
        
        # ✅ CRITICAL: Force the plane to render as a textured surface
        self.planeWidgetX.GetPlaneProperty().SetOpacity(1.0)
        self.planeWidgetX.GetTexturePlaneProperty().SetOpacity(1.0)
        
        # ✅ MUST call On() first to initialize internal structures
        self.planeWidgetX.On()
        # Then disable interaction until user enables it
        self.planeWidgetX.SetEnabled(False)
        
        # --- Y PLANE (Coronal) ---
        self.planeWidgetY = vtk.vtkImagePlaneWidget()
        self.planeWidgetY.SetInteractor(self.interactor)
        self.planeWidgetY.SetInputData(self.ct_image)
        self.planeWidgetY.SetPlaneOrientationToYAxes()
        self.planeWidgetY.SetSlicePosition(center[1])
        
        self.planeWidgetY.DisplayTextOn()
        self.planeWidgetY.SetWindowLevel(window, level)
        self.planeWidgetY.SetResliceInterpolateToLinear()
        self.planeWidgetY.TextureInterpolateOn()
        self.planeWidgetY.SetUseContinuousCursor(False)
        self.planeWidgetY.SetMarginSizeX(0.0)
        self.planeWidgetY.SetMarginSizeY(0.0)
        
        self.planeWidgetY.GetPlaneProperty().SetOpacity(1.0)
        self.planeWidgetY.GetTexturePlaneProperty().SetOpacity(1.0)
        
        self.planeWidgetY.On()
        self.planeWidgetY.SetEnabled(False)
        
        # --- Z PLANE (Axial) ---
        self.planeWidgetZ = vtk.vtkImagePlaneWidget()
        self.planeWidgetZ.SetInteractor(self.interactor)
        self.planeWidgetZ.SetInputData(self.ct_image)
        self.planeWidgetZ.SetPlaneOrientationToZAxes()
        self.planeWidgetZ.SetSlicePosition(center[2])
        
        self.planeWidgetZ.DisplayTextOn()
        self.planeWidgetZ.SetWindowLevel(window, level)
        self.planeWidgetZ.SetResliceInterpolateToLinear()
        self.planeWidgetZ.TextureInterpolateOn()
        self.planeWidgetZ.SetUseContinuousCursor(False)
        self.planeWidgetZ.SetMarginSizeX(0.0)
        self.planeWidgetZ.SetMarginSizeY(0.0)
        
        self.planeWidgetZ.GetPlaneProperty().SetOpacity(1.0)
        self.planeWidgetZ.GetTexturePlaneProperty().SetOpacity(1.0)
        
        self.planeWidgetZ.On()
        self.planeWidgetZ.SetEnabled(False)
        
        print("[MPRManager] ✅ Plane widgets created with texture mapping")
    
    def update_plane_state(self, axis, enabled, position_percent):
        """Update plane visibility and position"""
        if not self.ct_image:
            return
        
        bounds = self.ct_image.GetBounds()
        
        if axis == 'x' and self.planeWidgetX:
            self.enabled_x = enabled
            x_min, x_max = bounds[0], bounds[1]
            position = x_min + (x_max - x_min) * (position_percent / 100.0)
            self.planeWidgetX.SetSlicePosition(position)
            self.planeWidgetX.SetEnabled(enabled)
            
            # ✅ Ensure texture stays visible when enabled
            if enabled:
                self.planeWidgetX.GetTexturePlaneProperty().SetOpacity(1.0)
        
        elif axis == 'y' and self.planeWidgetY:
            self.enabled_y = enabled
            y_min, y_max = bounds[2], bounds[3]
            position = y_min + (y_max - y_min) * (position_percent / 100.0)
            self.planeWidgetY.SetSlicePosition(position)
            self.planeWidgetY.SetEnabled(enabled)
            
            if enabled:
                self.planeWidgetY.GetTexturePlaneProperty().SetOpacity(1.0)
        
        elif axis == 'z' and self.planeWidgetZ:
            self.enabled_z = enabled
            z_min, z_max = bounds[4], bounds[5]
            position = z_min + (z_max - z_min) * (position_percent / 100.0)
            self.planeWidgetZ.SetSlicePosition(position)
            self.planeWidgetZ.SetEnabled(enabled)
            
            if enabled:
                self.planeWidgetZ.GetTexturePlaneProperty().SetOpacity(1.0)
    
    def set_window_level(self, window, level):
        """Set window/level for all planes"""
        if self.planeWidgetX:
            self.planeWidgetX.SetWindowLevel(window, level)
        if self.planeWidgetY:
            self.planeWidgetY.SetWindowLevel(window, level)
        if self.planeWidgetZ:
            self.planeWidgetZ.SetWindowLevel(window, level)
    
    def remove_all_planes(self):
        """Disable and remove all planes"""
        if self.planeWidgetX:
            self.planeWidgetX.SetEnabled(False)
            self.planeWidgetX.Off()
            self.planeWidgetX = None
        if self.planeWidgetY:
            self.planeWidgetY.SetEnabled(False)
            self.planeWidgetY.Off()
            self.planeWidgetY = None
        if self.planeWidgetZ:
            self.planeWidgetZ.SetEnabled(False)
            self.planeWidgetZ.Off()
            self.planeWidgetZ = None
        
        self.enabled_x = self.enabled_y = self.enabled_z = False


# ========== CURVED MPR MANAGER ==========

class CurvedMPRManager:
    """Manages curved multi-planar reconstruction visualization"""
    
    def __init__(self, renderer, organ_type):
        self.renderer = renderer
        self.organ_type = organ_type
        self.mpr_actors = []
    
    def clear(self):
        for actor in self.mpr_actors:
            self.renderer.RemoveActor(actor)
        self.mpr_actors.clear()
    
    def show_mpr(self, path_type):
        self.clear()
        points = self.create_path(path_type)
        
        if points and points.GetNumberOfPoints() > 1:
            self.create_mpr_tube(points)
            return True
        return False
    
    def create_path(self, path_type):
        if self.organ_type == 'heart':
            return self.create_heart_path(path_type)
        elif self.organ_type == 'brain':
            return self.create_brain_path(path_type)
        elif self.organ_type == 'muscles':
            return self.create_muscle_path(path_type)
        elif self.organ_type == 'teeth':
            return self.create_dental_path(path_type)
        return None
    
    def create_heart_path(self, path_type):
        points = vtk.vtkPoints()
        
        if "Coronary" in path_type:
            for i in range(50):
                t = i / 50.0
                angle = t * 2 * np.pi
                x = -1.5 + 2.0 * np.cos(angle)
                y = -1.0 + 2.0 * np.sin(angle)
                z = t * 0.5
                points.InsertNextPoint(x, y, z)
        elif "Aorta" in path_type:
            for i in range(60):
                t = i / 60.0
                x = -1.5 - t * 0.5
                y = -1.0 + t * 6.0
                z = np.sin(t * np.pi) * 0.3
                points.InsertNextPoint(x, y, z)
        elif "Pulmonary" in path_type:
            for i in range(50):
                t = i / 50.0
                x = 1.5 + t * 0.3
                y = 1.0 + t * 4.0
                z = np.cos(t * np.pi) * 0.3
                points.InsertNextPoint(x, y, z)
        
        return points
    
    def create_brain_path(self, path_type):
        points = vtk.vtkPoints()
        
        if "Cerebral" in path_type or "Arteries" in path_type:
            for i in range(60):
                t = i / 60.0
                angle = t * np.pi
                x = 3 * np.cos(angle)
                y = 1 + t * 2
                z = 3 * np.sin(angle)
                points.InsertNextPoint(x, y, z)
        elif "Ventricular" in path_type:
            for i in range(40):
                t = i / 40.0
                x = -1 + t * 2
                y = 1 - t * 0.5
                z = 0
                points.InsertNextPoint(x, y, z)
        elif "White Matter" in path_type or "Tracts" in path_type:
            for i in range(50):
                t = i / 50.0
                x = -2 + t * 4
                y = 1 + np.sin(t * np.pi) * 0.5
                z = np.cos(t * np.pi * 2) * 0.3
                points.InsertNextPoint(x, y, z)
        
        return points
    
    def create_muscle_path(self, path_type):
        points = vtk.vtkPoints()
        
        if "Fiber" in path_type:
            for i in range(50):
                t = i / 50.0
                x = -2 + t * 0.2
                y = 2 - t * 4
                z = np.sin(t * np.pi * 3) * 0.2
                points.InsertNextPoint(x, y, z)
        elif "Tendon" in path_type:
            for i in range(30):
                t = i / 30.0
                x = -2
                y = -2 - t * 2
                z = t * 0.5
                points.InsertNextPoint(x, y, z)
        elif "Fascia" in path_type:
            for i in range(40):
                t = i / 40.0
                angle = t * np.pi * 2
                x = 2 * np.cos(angle)
                y = t * 3
                z = 2 * np.sin(angle)
                points.InsertNextPoint(x, y, z)
        
        return points
    
    def create_dental_path(self, path_type):
        points = vtk.vtkPoints()
        
        if "Root Canal" in path_type:
            for i in range(30):
                t = i / 30.0
                x = 2
                y = 1 - t * 3
                z = 2
                points.InsertNextPoint(x, y, z)
        elif "Alveolar" in path_type or "Bone" in path_type:
            for i in range(50):
                t = i / 50.0
                angle = t * np.pi
                x = 3 * np.cos(angle)
                y = -1
                z = 3 * np.sin(angle)
                points.InsertNextPoint(x, y, z)
        elif "Periodontal" in path_type:
            for i in range(40):
                t = i / 40.0
                angle = t * np.pi * 2
                x = 2.5 * np.cos(angle)
                y = 0
                z = 2.5 * np.sin(angle)
                points.InsertNextPoint(x, y, z)
        
        return points
    
    def create_mpr_tube(self, points):
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(points.GetNumberOfPoints())
        for i in range(points.GetNumberOfPoints()):
            polyline.GetPointIds().SetId(i, i)
        
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polyline)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        tube = vtk.vtkTubeFilter()
        tube.SetInputData(polydata)
        tube.SetRadius(0.15)
        tube.SetNumberOfSides(12)
        tube.CappingOn()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        actor.GetProperty().SetOpacity(0.7)
        
        self.mpr_actors.append(actor)
        self.renderer.AddActor(actor)


# ========== CT VIEWER ==========

class CTViewer:
    """Manages CT volume visualization with 3 orthogonal planes"""
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.ct_image = None
        
        self.axial_actor = None
        self.coronal_actor = None
        self.sagittal_actor = None
        
        self.axial_position = 0.5
        self.coronal_position = 0.5
        self.sagittal_position = 0.5
        
        self.axial_visible = True
        self.coronal_visible = True
        self.sagittal_visible = True
        
        self.dimensions = None
        self.spacing = None
        self.origin = None
    
    def set_ct_image(self, vtk_image):
        self.ct_image = vtk_image
        self.dimensions = vtk_image.GetDimensions()
        self.spacing = vtk_image.GetSpacing()
        self.origin = vtk_image.GetOrigin()
        
        print(f"CT Image loaded:")
        print(f"  Dimensions: {self.dimensions}")
        print(f"  Spacing: {self.spacing}")
        print(f"  Origin: {self.origin}")
        
        self.create_planes()
    
    def create_planes(self):
        if self.ct_image is None:
            return
        
        self.clear_planes()
        
        self.axial_actor = self.create_image_plane('axial', self.axial_position)
        self.coronal_actor = self.create_image_plane('coronal', self.coronal_position)
        self.sagittal_actor = self.create_image_plane('sagittal', self.sagittal_position)
        
        if self.axial_actor:
            self.axial_actor.SetVisibility(self.axial_visible)
        if self.coronal_actor:
            self.coronal_actor.SetVisibility(self.coronal_visible)
        if self.sagittal_actor:
            self.sagittal_actor.SetVisibility(self.sagittal_visible)
    
    def create_image_plane(self, plane_type, position):
        if self.ct_image is None:
            return None
        
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(self.ct_image)
        reslice.SetOutputDimensionality(2)
        
        if plane_type == 'axial':
            slice_idx = int(position * (self.dimensions[2] - 1))
            reslice.SetResliceAxesOrigin(
                self.origin[0] + self.dimensions[0] * self.spacing[0] / 2,
                self.origin[1] + self.dimensions[1] * self.spacing[1] / 2,
                self.origin[2] + slice_idx * self.spacing[2]
            )
            reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)
        elif plane_type == 'coronal':
            slice_idx = int(position * (self.dimensions[1] - 1))
            reslice.SetResliceAxesOrigin(
                self.origin[0] + self.dimensions[0] * self.spacing[0] / 2,
                self.origin[1] + slice_idx * self.spacing[1],
                self.origin[2] + self.dimensions[2] * self.spacing[2] / 2
            )
            reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
        elif plane_type == 'sagittal':
            slice_idx = int(position * (self.dimensions[0] - 1))
            reslice.SetResliceAxesOrigin(
                self.origin[0] + slice_idx * self.spacing[0],
                self.origin[1] + self.dimensions[1] * self.spacing[1] / 2,
                self.origin[2] + self.dimensions[2] * self.spacing[2] / 2
            )
            reslice.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
        
        reslice.Update()
        
        color_map = vtk.vtkImageMapToColors()
        color_map.SetInputConnection(reslice.GetOutputPort())
        
        lut = vtk.vtkLookupTable()
        lut.SetRange(-1000, 3000)
        lut.SetValueRange(0.0, 1.0)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetRampToLinear()
        lut.Build()
        
        color_map.SetLookupTable(lut)
        color_map.Update()
        
        mapper = vtk.vtkImageMapper()
        mapper.SetInputConnection(color_map.GetOutputPort())
        mapper.SetColorWindow(2000)
        mapper.SetColorLevel(500)
        
        actor = vtk.vtkActor2D()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        
        return actor
    
    def update_axial_position(self, position):
        self.axial_position = np.clip(position, 0.0, 1.0)
        if self.axial_actor:
            self.renderer.RemoveActor(self.axial_actor)
        self.axial_actor = self.create_image_plane('axial', self.axial_position)
        if self.axial_actor:
            self.axial_actor.SetVisibility(self.axial_visible)
    
    def update_coronal_position(self, position):
        self.coronal_position = np.clip(position, 0.0, 1.0)
        if self.coronal_actor:
            self.renderer.RemoveActor(self.coronal_actor)
        self.coronal_actor = self.create_image_plane('coronal', self.coronal_position)
        if self.coronal_actor:
            self.coronal_actor.SetVisibility(self.coronal_visible)
    
    def update_sagittal_position(self, position):
        self.sagittal_position = np.clip(position, 0.0, 1.0)
        if self.sagittal_actor:
            self.renderer.RemoveActor(self.sagittal_actor)
        self.sagittal_actor = self.create_image_plane('sagittal', self.sagittal_position)
        if self.sagittal_actor:
            self.sagittal_actor.SetVisibility(self.sagittal_visible)
    
    def set_axial_visibility(self, visible):
        self.axial_visible = visible
        if self.axial_actor:
            self.axial_actor.SetVisibility(visible)
    
    def set_coronal_visibility(self, visible):
        self.coronal_visible = visible
        if self.coronal_actor:
            self.coronal_actor.SetVisibility(visible)
    
    def set_sagittal_visibility(self, visible):
        self.sagittal_visible = visible
        if self.sagittal_actor:
            self.sagittal_actor.SetVisibility(visible)
    
    def clear_planes(self):
        if self.axial_actor:
            self.renderer.RemoveActor(self.axial_actor)
            self.axial_actor = None
        if self.coronal_actor:
            self.renderer.RemoveActor(self.coronal_actor)
            self.coronal_actor = None
        if self.sagittal_actor:
            self.renderer.RemoveActor(self.sagittal_actor)
            self.sagittal_actor = None
    
    def clear(self):
        self.clear_planes()
        self.ct_image = None
        self.dimensions = None
        self.spacing = None
        self.origin = None