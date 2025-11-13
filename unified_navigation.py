"""
Unified Navigation Module
Combines: Focus Navigation + Flythrough + Virtual Endoscopy
"""

import vtk
import numpy as np
from PyQt5.QtCore import QTimer
try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ========== FOCUS NAVIGATION ==========

class FocusNavigationManager:
    """Manages focus navigation by controlling part visibility and transparency"""
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.actors = {}
        self.current_focus = None
        self.transparency = 0.3
        self.original_opacities = {}
    
    def set_actors(self, actors):
        self.actors = actors
        self.original_opacities.clear()
        for part_name, actor in self.actors.items():
            opacity = actor.GetProperty().GetOpacity()
            self.original_opacities[part_name] = opacity
    
    def focus_on_part(self, part_name, transparency=0.3):
        self.transparency = transparency
        self.current_focus = part_name
        
        if part_name == 'None' or part_name not in self.actors:
            self.clear_focus()
            return
        
        for name, actor in self.actors.items():
            if name == part_name:
                actor.GetProperty().SetOpacity(1.0)
            else:
                actor.GetProperty().SetOpacity(1.0 - transparency)
    
    def clear_focus(self):
        self.current_focus = None
        for part_name, actor in self.actors.items():
            if part_name in self.original_opacities:
                actor.GetProperty().SetOpacity(self.original_opacities[part_name])
            else:
                actor.GetProperty().SetOpacity(1.0)
    
    def set_transparency(self, transparency):
        self.transparency = transparency
        if self.current_focus and self.current_focus in self.actors:
            self.focus_on_part(self.current_focus, transparency)
    
    def get_current_focus(self):
        return self.current_focus
    
    def toggle_part_focus(self, part_name):
        if self.current_focus == part_name:
            self.clear_focus()
        else:
            self.focus_on_part(part_name, self.transparency)


# ========== FLYTHROUGH MANAGER ==========

class FlythroughManager:
    """Manages fly-through camera navigation with manual point selection"""
    
    def __init__(self, renderer, organ_type):
        self.renderer = renderer
        self.organ_type = organ_type
        self.flythrough_timer = None
        self.flythrough_path = []
        self.flythrough_index = 0
        self.speed = 1.0
        
        # Manual path creation
        self.manual_points = []
        self.point_sphere_actors = []
        self.path_line_actor = None
        self.is_picking_mode = False
        self.picker = None
        self.picker_observer = None
        
        self.setup_picker()
    
    def setup_picker(self):
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.005)
    
    def enable_picking_mode(self, interactor):
        self.is_picking_mode = True
        if self.picker_observer:
            interactor.RemoveObserver(self.picker_observer)
        self.picker_observer = interactor.AddObserver("LeftButtonPressEvent", self.on_pick_point)
        return True
    
    def disable_picking_mode(self, interactor):
        self.is_picking_mode = False
        if self.picker_observer:
            interactor.RemoveObserver(self.picker_observer)
            self.picker_observer = None
    
    def on_pick_point(self, obj, event):
        if not self.is_picking_mode:
            return
        
        click_pos = obj.GetEventPosition()
        self.picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        picked_pos = self.picker.GetPickPosition()
        
        if self.picker.GetCellId() >= 0:
            self.add_manual_point(picked_pos)
            print(f"✓ Point {len(self.manual_points)} picked at: {picked_pos}")
    
    def add_manual_point(self, position):
        self.manual_points.append(position)
        
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(2.0)
        sphere.SetThetaResolution(16)
        sphere.SetPhiResolution(16)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 1.0)
        actor.GetProperty().SetOpacity(0.8)
        
        self.renderer.AddActor(actor)
        self.point_sphere_actors.append(actor)
        self.update_path_line()
        
        render_window = self.renderer.GetRenderWindow()
        if render_window:
            render_window.Render()
    
    def update_path_line(self):
        if self.path_line_actor:
            self.renderer.RemoveActor(self.path_line_actor)
            self.path_line_actor = None
        
        if len(self.manual_points) < 2:
            return
        
        points = vtk.vtkPoints()
        for pos in self.manual_points:
            points.InsertNextPoint(pos)
        
        lines = vtk.vtkCellArray()
        for i in range(len(self.manual_points) - 1):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i + 1)
            lines.InsertNextCell(line)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        
        tube = vtk.vtkTubeFilter()
        tube.SetInputData(polydata)
        tube.SetRadius(0.5)
        tube.SetNumberOfSides(12)
        tube.Update()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        self.path_line_actor = vtk.vtkActor()
        self.path_line_actor.SetMapper(mapper)
        self.path_line_actor.GetProperty().SetColor(0.0, 1.0, 1.0)
        self.path_line_actor.GetProperty().SetOpacity(0.6)
        
        self.renderer.AddActor(self.path_line_actor)
    
    def clear_manual_points(self):
        for actor in self.point_sphere_actors:
            self.renderer.RemoveActor(actor)
        self.point_sphere_actors.clear()
        
        if self.path_line_actor:
            self.renderer.RemoveActor(self.path_line_actor)
            self.path_line_actor = None
        
        self.manual_points.clear()
        print("Manual path cleared")
        
        render_window = self.renderer.GetRenderWindow()
        if render_window:
            render_window.Render()
    
    def generate_smooth_path_from_manual_points(self, points_per_segment=20):
        if len(self.manual_points) < 2:
            return []
        
        smooth_path = []
        for i in range(len(self.manual_points) - 1):
            p1 = np.array(self.manual_points[i])
            p2 = np.array(self.manual_points[i + 1])
            
            for j in range(points_per_segment):
                t = j / points_per_segment
                interp_point = p1 * (1 - t) + p2 * t
                
                if i < len(self.manual_points) - 2:
                    look_point = np.array(self.manual_points[i + 1])
                else:
                    direction = p2 - p1
                    look_point = interp_point + direction * 0.5
                
                smooth_path.append({
                    'position': tuple(interp_point),
                    'focal_point': tuple(look_point)
                })
        
        smooth_path.append({
            'position': self.manual_points[-1],
            'focal_point': self.manual_points[-1]
        })
        
        return smooth_path
    
    def start_manual_flythrough(self, speed=1.0):
        if len(self.manual_points) < 2:
            print("Need at least 2 points for fly-through")
            return False
        
        self.flythrough_path = self.generate_smooth_path_from_manual_points()
        self.flythrough_index = 0
        self.speed = speed
        
        if not self.flythrough_path:
            return False
        
        self.flythrough_timer = QTimer()
        self.flythrough_timer.timeout.connect(self.update_flythrough)
        interval = int(50 / speed)
        self.flythrough_timer.start(interval)
        
        print(f"Starting manual fly-through with {len(self.flythrough_path)} path points")
        return True
    
    def start_flythrough(self, path_type=None, speed=1.0):
        self.stop_flythrough()
        self.speed = speed
        self.flythrough_path = self.create_flythrough_path(path_type)
        self.flythrough_index = 0
        
        if not self.flythrough_path:
            return False
        
        self.flythrough_timer = QTimer()
        self.flythrough_timer.timeout.connect(self.update_flythrough)
        interval = int(50 / speed)
        self.flythrough_timer.start(interval)
        return True
    
    def create_flythrough_path(self, path_type):
        if self.organ_type == 'heart':
            return self.create_heart_flythrough(path_type)
        elif self.organ_type == 'brain':
            return self.create_brain_flythrough(path_type)
        elif self.organ_type == 'muscles':
            return self.create_muscle_flythrough(path_type)
        elif self.organ_type == 'teeth':
            return self.create_dental_flythrough(path_type)
        return []
    
    def create_heart_flythrough(self, path_type):
        path = []
        for i in range(100):
            t = i / 100.0
            x = -1.5 - t * 0.8 * np.sin(t * np.pi)
            y = -1.0 + t * 7.0
            z = t * 1.5 * np.cos(t * np.pi * 0.5)
            
            if i < 99:
                t_next = (i + 1) / 100.0
                look_x = -1.5 - t_next * 0.8 * np.sin(t_next * np.pi)
                look_y = -1.0 + t_next * 7.0
                look_z = t_next * 1.5 * np.cos(t_next * np.pi * 0.5)
            else:
                look_x, look_y, look_z = x, y + 1, z
            
            path.append({
                'position': (x, y, z),
                'focal_point': (look_x, look_y, look_z)
            })
        return path
    
    def create_brain_flythrough(self, path_type):
        path = []
        for i in range(120):
            t = i / 120.0
            angle = t * np.pi * 2
            radius = 5.0 + np.sin(t * np.pi * 3) * 0.5
            x = radius * np.cos(angle)
            y = 1 + np.sin(t * np.pi * 2) * 2
            z = radius * np.sin(angle)
            path.append({'position': (x, y, z), 'focal_point': (0, 1, 0)})
        return path
    
    def create_muscle_flythrough(self, path_type):
        path = []
        for i in range(80):
            t = i / 80.0
            x = -3 + t * 6
            y = 4 - t * 6
            z = np.sin(t * np.pi * 2) * 2
            if i < 79:
                t_next = (i + 1) / 80.0
                look_x = -3 + t_next * 6
                look_y = 4 - t_next * 6
                look_z = np.sin(t_next * np.pi * 2) * 2
            else:
                look_x, look_y, look_z = x + 1, y - 1, z
            path.append({'position': (x, y, z), 'focal_point': (look_x, look_y, look_z)})
        return path
    
    def create_dental_flythrough(self, path_type):
        path = []
        for i in range(100):
            t = i / 100.0
            angle = t * np.pi * 2
            radius = 4.0
            x = radius * np.cos(angle)
            y = 0.5 + np.sin(t * np.pi * 4) * 0.5
            z = radius * np.sin(angle)
            look_angle = angle + np.pi / 8
            look_x = 2.5 * np.cos(look_angle)
            look_y = 0
            look_z = 2.5 * np.sin(look_angle)
            path.append({'position': (x, y, z), 'focal_point': (look_x, look_y, look_z)})
        return path
    
    def update_flythrough(self):
        if self.flythrough_index >= len(self.flythrough_path):
            self.stop_flythrough()
            return
        
        point = self.flythrough_path[self.flythrough_index]
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(point['position'])
        camera.SetFocalPoint(point['focal_point'])
        camera.SetViewUp(0, 1, 0)
        self.renderer.ResetCameraClippingRange()
        self.flythrough_index += 1
    
    def stop_flythrough(self):
        if self.flythrough_timer:
            self.flythrough_timer.stop()
            self.flythrough_timer = None
        self.flythrough_index = 0
        self.flythrough_path = []
    
    def is_running(self):
        return self.flythrough_timer is not None
    
    def set_speed(self, speed):
        self.speed = speed
        if self.flythrough_timer and self.flythrough_timer.isActive():
            interval = int(50 / speed)
            self.flythrough_timer.setInterval(interval)
    
    def get_manual_point_count(self):
        return len(self.manual_points)
    
    def has_manual_path(self):
        return len(self.manual_points) >= 2


# ========== VIRTUAL ENDOSCOPY ==========

class VirtualEndoscopyManager:
    """Virtual endoscopy with automatic centerline extraction"""
    
    def __init__(self, renderer, model_loader):
        self.renderer = renderer
        self.model_loader = model_loader
        self.flythrough_timer = None
        self.camera_path = []
        self.current_index = 0
        self.speed = 1.0
        self.is_active = False
        self.path_actors = []
    
    def extract_centerline_from_segmentation(self, label_value):
        if self.model_loader.segmentation_data is None:
            return None
        
        mask = (self.model_loader.segmentation_data == label_value).astype(np.uint8)
        if mask.sum() < 100:
            return None
        
        if not SCIPY_AVAILABLE:
            return None
        
        try:
            distance = ndimage.distance_transform_edt(mask)
            from scipy.ndimage import maximum_filter
            local_max = (distance == maximum_filter(distance, size=5))
            coords = np.argwhere(local_max & (distance > 1))
            
            if len(coords) < 10:
                return None
            
            sorted_coords = self.sort_points_into_path(coords)
            return sorted_coords
        except Exception as e:
            print(f"Centerline extraction failed: {e}")
            return None
    
    def sort_points_into_path(self, points):
        if len(points) < 2:
            return points
        
        path = [points[0]]
        remaining = list(points[1:])
        
        while remaining:
            current = path[-1]
            distances = [np.linalg.norm(current - p) for p in remaining]
            nearest_idx = np.argmin(distances)
            path.append(remaining[nearest_idx])
            remaining.pop(nearest_idx)
            if distances[nearest_idx] > 20:
                break
        
        return np.array(path)
    
    def start_automatic_flythrough(self, speed=1.0, show_path=True):
        target_label = self.auto_detect_tubular_structure()
        if target_label is None:
            return False
        
        centerline = self.extract_centerline_from_segmentation(target_label)
        if centerline is None:
            return False
        
        self.camera_path = self.create_camera_path_from_centerline(centerline)
        if not self.camera_path:
            return False
        
        return self.start_flythrough(speed, show_path)
    
    def auto_detect_tubular_structure(self):
        if self.model_loader.segmentation_data is None:
            return None
        
        labels = self.model_loader.get_unique_labels()
        if len(labels) == 0:
            return None
        
        best_label = None
        max_extent = 0
        
        for label in labels:
            mask = (self.model_loader.segmentation_data == label)
            z_coords = np.where(mask)[0]
            if len(z_coords) > 0:
                z_extent = z_coords.max() - z_coords.min()
                if z_extent > max_extent:
                    max_extent = z_extent
                    best_label = label
        
        return best_label
    
    def create_camera_path_from_centerline(self, centerline_points):
        if centerline_points is None or len(centerline_points) < 10:
            return []
        
        smoothed = self.smooth_path(centerline_points, window=7)
        
        if self.model_loader.ct_image:
            spacing = self.model_loader.ct_image.GetSpacing()
            origin = self.model_loader.ct_image.GetOrigin()
        else:
            spacing = (1.0, 1.0, 1.0)
            origin = (0.0, 0.0, 0.0)
        
        camera_path = []
        for i in range(len(smoothed) - 5):
            pos = smoothed[i]
            pos_world = (
                pos[0] * spacing[0] + origin[0],
                pos[1] * spacing[1] + origin[1],
                pos[2] * spacing[2] + origin[2]
            )
            look_ahead_idx = min(i + 5, len(smoothed) - 1)
            focal = smoothed[look_ahead_idx]
            focal_world = (
                focal[0] * spacing[0] + origin[0],
                focal[1] * spacing[1] + origin[1],
                focal[2] * spacing[2] + origin[2]
            )
            camera_path.append({'position': pos_world, 'focal_point': focal_world})
        
        return camera_path
    
    def smooth_path(self, points, window=5):
        if len(points) < window:
            return points
        smoothed = np.copy(points).astype(float)
        for i in range(len(points)):
            start = max(0, i - window // 2)
            end = min(len(points), i + window // 2 + 1)
            smoothed[i] = np.mean(points[start:end], axis=0)
        return smoothed
    
    def start_flythrough(self, speed=1.0, show_path=True):
        if not self.camera_path:
            return False
        
        self.current_index = 0
        self.speed = speed
        self.is_active = True
        
        self.flythrough_timer = QTimer()
        self.flythrough_timer.timeout.connect(self.update_camera)
        interval = int(50 / speed)
        self.flythrough_timer.start(interval)
        return True
    
    def update_camera(self):
        if self.current_index >= len(self.camera_path):
            self.current_index = 0
        
        point_data = self.camera_path[self.current_index]
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(point_data['position'])
        camera.SetFocalPoint(point_data['focal_point'])
        
        view_dir = np.array(point_data['focal_point']) - np.array(point_data['position'])
        view_dir = view_dir / np.linalg.norm(view_dir)
        ref_up = np.array([0, 0, 1])
        if abs(np.dot(view_dir, ref_up)) > 0.99:
            ref_up = np.array([0, 1, 0])
        right = np.cross(view_dir, ref_up)
        right = right / np.linalg.norm(right)
        up = np.cross(right, view_dir)
        camera.SetViewUp(up)
        self.renderer.ResetCameraClippingRange()
        self.current_index += 1
    
    def stop_flythrough(self):
        if self.flythrough_timer:
            self.flythrough_timer.stop()
            self.flythrough_timer = None
        self.current_index = 0
        self.camera_path = []
        self.is_active = False
    
    def is_running(self):
        return self.is_active
    
    def set_speed(self, speed):
        self.speed = speed
        if self.flythrough_timer and self.flythrough_timer.isActive():
            interval = int(50 / speed)
            self.flythrough_timer.setInterval(interval)