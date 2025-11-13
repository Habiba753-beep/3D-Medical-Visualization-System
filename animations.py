"""
Enhanced Animation Manager Module - UPGRADED
Implements realistic blood flow with glowing particles, color gradients, and heartbeat deformation
"""

import vtk
import numpy as np
from PyQt5.QtCore import QTimer


class AnimationManager:
    """Manages animations with realistic particle flow and organ deformation"""
    
    def __init__(self, renderer, organ_type):
        """Initialize animation manager"""
        self.renderer = renderer
        self.organ_type = organ_type
        self.actors = {}
        
        # Animation timers
        self.flow_timer = None
        self.electrical_timer = None
        self.contraction_timer = None
        
        # ========== ENHANCED BLOOD FLOW PARAMETERS ==========
        self.flow_particles = []
        self.flow_path_points = []
        self.particle_speed = 2.0
        
        # Blood appearance configuration
        self.NUM_PARTICLES = 50  # Number of blood particles (reduced for visibility)
        self.PARTICLE_RADIUS = 1.5  # Size of each drop (MUCH LARGER)
        self.TUBE_RADIUS = 2.0  # Width of blood stream tube (MUCH LARGER)
        self.USE_GLOW = True  # Enable glow effect 
        # Heartbeat pulse parameters
        self.heartbeat_phase = 0.0
        self.heartbeat_frequency = 1.2  # seconds per beat
        self.base_speed = 2.0
        
        # ========== HEART DEFORMATION ==========
        self.deformation_phase = 0
        self.deformation_parts = []
        self.original_scales = {}
        self.original_positions = {}  # Store original positions
        
        # Electrical animation
        self.electrical_particles = []
        self.electrical_index = 0
    
    def set_manual_flow_path(self, path_points):
        """
        Set a custom path for blood flow particles.
        This allows integration with the manual point-picking system.
        
        Args:
            path_points: List of (x, y, z) tuples defining the flow path
        """
        if len(path_points) >= 2:
            self.flow_path_points = path_points
            print(f"âœ“ Custom flow path set with {len(path_points)} points")
            return True
        else:
            print("âœ— Need at least 2 points for flow path")
            return False
    
        
    def set_actors(self, actors):
        """Set organ actors"""
        self.actors = actors
        
        # Store original scales AND positions for deformation reset
        self.original_scales.clear()
        self.original_positions.clear()
        for part_name, actor in self.actors.items():
            scale = actor.GetScale()
            position = actor.GetPosition()
            self.original_scales[part_name] = scale
            self.original_positions[part_name] = position
    
    # ========== ENHANCED BLOOD FLOW WITH GLOWING PARTICLES ==========
    
    def set_manual_flow_path(self, path_points):
        """
        Set a custom path for blood flow particles.
        This allows integration with the manual point-picking system.
        
        Args:
            path_points: List of (x, y, z) tuples defining the flow path
        """
        if len(path_points) >= 2:
            self.flow_path_points = path_points
            print(f"âœ“ Custom flow path set with {len(path_points)} points")
            return True
        else:
            print("âœ— Need at least 2 points for flow path")
            return False
    
    def start_flow_animation(self, flow_type=None, speed=5, use_manual_path=False):
        """
        Start blood flow animation with optional manual path support.
        
        Args:
            flow_type: Type of flow (e.g., "Blood Flow - Aorta")
            speed: Animation speed (1-10)
            use_manual_path: If True, use manually picked path points
        """
        self.stop_flow_animation()
        
        # Map speed (1-10) to actual particle speed
        self.base_speed = speed * 0.4  # Scale factor
        self.particle_speed = self.base_speed
        
        
        # Determine flow path
        # Determine flow path
        if use_manual_path and len(self.flow_path_points) >= 2:
            print(f"Using manual flow path with {len(self.flow_path_points)} points")
            path_points = self.flow_path_points
        else:
            # Create automatic path based on organ and flow type
            path_points = self.create_flow_path(flow_type)

        if not path_points or len(path_points) < 2:
            print("Failed to create flow path")
            return False
        self.create_entry_exit_markers(path_points)
        
        
        # Create glowing blood particles along the path
        self.create_glowing_blood_particles(path_points)
        
        # Create blood stream tube (optional visualization of the vessel)
        self.create_blood_vessel_tube(path_points)
        
        # Start deformation for heart (SIZE CHANGE, NOT POSITION CHANGE)
        if self.organ_type == 'heart':
            self.setup_heart_deformation()
        
        # Reset heartbeat phase
        self.heartbeat_phase = 0.0
        
        # Start animation timer
        self.flow_timer = QTimer()
        self.flow_timer.timeout.connect(self.update_flow_animation)
        interval = 30  # ~33 FPS for smooth animation
        self.flow_timer.start(interval)
        
        return True
    
    def create_entry_exit_markers(self, path_points):
        """
        Create visible markers at entry and exit points of the blood flow path.
        
        Args:
            path_points: List of (x, y, z) coordinates defining the path
        """
        # Entry point marker (GREEN sphere)
        entry_point = path_points[0]
        entry_sphere = vtk.vtkSphereSource()
        entry_sphere.SetCenter(entry_point)
        entry_sphere.SetRadius(2.5)  # Large and visible
        entry_sphere.SetThetaResolution(32)
        entry_sphere.SetPhiResolution(32)
        
        entry_mapper = vtk.vtkPolyDataMapper()
        entry_mapper.SetInputConnection(entry_sphere.GetOutputPort())
        
        entry_actor = vtk.vtkActor()
        entry_actor.SetMapper(entry_mapper)
        entry_actor.GetProperty().SetColor(0.0, 1.0, 0.0)  # Bright green
        entry_actor.GetProperty().SetOpacity(0.8)
        
        self.renderer.AddActor(entry_actor)
        
        # Store for cleanup
        if not hasattr(self, 'entry_exit_markers'):
            self.entry_exit_markers = []
        self.entry_exit_markers.append(entry_actor)
        
        # Exit point marker (RED sphere)
        exit_point = path_points[-1]
        exit_sphere = vtk.vtkSphereSource()
        exit_sphere.SetCenter(exit_point)
        exit_sphere.SetRadius(2.5)  # Large and visible
        exit_sphere.SetThetaResolution(32)
        exit_sphere.SetPhiResolution(32)
        
        exit_mapper = vtk.vtkPolyDataMapper()
        exit_mapper.SetInputConnection(exit_sphere.GetOutputPort())
        
        exit_actor = vtk.vtkActor()
        exit_actor.SetMapper(exit_mapper)
        exit_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Bright red
        exit_actor.GetProperty().SetOpacity(0.8)
        
        self.renderer.AddActor(exit_actor)
        self.entry_exit_markers.append(exit_actor)
        
        print(f"âœ“ Created entry (green) and exit (red) markers")
        print(f"  Entry: {entry_point}")
        print(f"  Exit: {exit_point}")
   
    def create_glowing_blood_particles(self, path_points):
        """
        Create realistic glowing blood particles with trails and color gradients.
        
        Args:
            path_points: List of (x, y, z) coordinates defining the path
        """
        self.flow_particles = []
        
        # Distribute particles evenly along path
        for i in range(self.NUM_PARTICLES):
            # Create sphere for blood drop (LARGER and SMOOTHER)
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(self.PARTICLE_RADIUS)
            sphere.SetThetaResolution(32)  # More detail
            sphere.SetPhiResolution(32)  # More detail
            # Create mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            # Create actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # Calculate initial position along path (evenly distributed)
            initial_progress = i / self.NUM_PARTICLES
            
            if i == 0:
                path_length = len(path_points)
                idx = int(initial_progress * (path_length - 1))
                pos = path_points[idx]
                print(f"  First particle at: {pos} (progress: {initial_progress})")
            
            # Set initial color based on position (gradient along path)
            color = self.get_blood_color(initial_progress)
            actor.GetProperty().SetColor(color)
            
            # Enable glow/shine effect (ENHANCED VISIBILITY)
            if self.USE_GLOW:
                actor.GetProperty().SetSpecular(0.9)  # Very high shine
                actor.GetProperty().SetSpecularPower(100)  # Sharp highlight
                actor.GetProperty().SetOpacity(1.0)  # FULLY OPAQUE for visibility
            else:
                actor.GetProperty().SetSpecular(0.5)
                actor.GetProperty().SetSpecularPower(30)
                actor.GetProperty().SetOpacity(1.0)  # FULLY OPAQUE
            
            # Add slight randomness to speed for realism
            speed_variation = np.random.uniform(0.85, 1.15)
            
            # Store particle data
            particle_data = {
                'actor': actor,
                'path': path_points,
                'progress': initial_progress,  # 0.0 to 1.0 along path
                'speed_factor': speed_variation,
                'trail_actors': []  # For motion trails
            }
            
            self.flow_particles.append(particle_data)
            self.renderer.AddActor(actor)
        
        print(f"âœ“ Created {self.NUM_PARTICLES} glowing blood particles")
    
    def get_blood_color(self, progress):
        """
        Get blood color based on progress along path.
        Creates gradient: Deep Crimson â†’ Red â†’ Orange â†’ Yellow
        
        Args:
            progress: 0.0 to 1.0 representing position along path
        
        Returns:
            (r, g, b) tuple
        """
        # Color stops along gradient
        # 0.0: Deep Crimson (dark red)
        # 0.4: Bright Red
        # 0.7: Orange-Red
        # 1.0: Yellow-Orange (oxygenated)
        
        if progress < 0.4:
            # Deep crimson â†’ Bright red
            t = progress / 0.4
            r = 0.6 + (0.4 * t)  # 0.6 â†’ 1.0
            g = 0.0 + (0.1 * t)  # 0.0 â†’ 0.1
            b = 0.0 + (0.1 * t)  # 0.0 â†’ 0.1
        elif progress < 0.7:
            # Bright red â†’ Orange
            t = (progress - 0.4) / 0.3
            r = 1.0  # Keep red high
            g = 0.1 + (0.4 * t)  # 0.1 â†’ 0.5
            b = 0.1 * (1 - t)  # 0.1 â†’ 0.0
        else:
            # Orange â†’ Yellow (oxygenated blood)
            t = (progress - 0.7) / 0.3
            r = 1.0  # Keep red high
            g = 0.5 + (0.4 * t)  # 0.5 â†’ 0.9
            b = 0.0 + (0.2 * t)  # 0.0 â†’ 0.2
        
        return (r, g, b)
    
    def create_blood_vessel_tube(self, path_points):
        """
        Create a semi-transparent tube representing the blood vessel.
        
        Args:
            path_points: List of (x, y, z) coordinates
        """
        # Create points
        points = vtk.vtkPoints()
        for point in path_points:
            points.InsertNextPoint(point)
        
        # Create polyline
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(path_points))
        for i in range(len(path_points)):
            polyline.GetPointIds().SetId(i, i)
        
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polyline)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        # Create tube
        tube = vtk.vtkTubeFilter()
        tube.SetInputData(polydata)
        tube.SetRadius(self.TUBE_RADIUS)
        tube.SetNumberOfSides(20)
        tube.CappingOn()
        tube.Update()
        
        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        # Create actor
        vessel_actor = vtk.vtkActor()
        vessel_actor.SetMapper(mapper)
        vessel_actor.GetProperty().SetColor(0.4, 0.05, 0.05)  # Dark red vessel
        vessel_actor.GetProperty().SetOpacity(0.15)  # Very transparent
        
        self.renderer.AddActor(vessel_actor)
        
        # Store for cleanup
        if not hasattr(self, 'vessel_actors'):
            self.vessel_actors = []
        self.vessel_actors.append(vessel_actor)
    
    def update_flow_animation(self):
        """
        Update particle positions with heartbeat pulse and color gradient.
        """
        # ADD THIS DEBUG LINE:
        # Uncomment to debug particle positions
        if len(self.flow_particles) > 0 and hasattr(self, 'debug_counter'):
            if self.debug_counter % 30 == 0:  # Print every 30 frames
                p = self.flow_particles[0]
                pos = p['actor'].GetPosition()
                print(f"Particle 0 at: {pos}, progress: {p['progress']:.2f}")
            self.debug_counter += 1
        else:
            self.debug_counter = 0
        
        # Update heartbeat pulse (affects speed)
        self.heartbeat_phase += 0.05  # Increment phase
        
        # Calculate pulse factor using sine wave
        # Creates "ba-bump" effect every ~1.2 seconds
        pulse = 1.0 + 0.3 * np.sin(self.heartbeat_phase * np.pi / (self.heartbeat_frequency * 60))
        current_speed = self.base_speed * pulse
        
        # Update blood particles
        for particle in self.flow_particles:
            path = particle['path']
            if not path:
                continue
            
            # Calculate movement speed
            speed = current_speed * particle['speed_factor'] * 0.01
            
            # Update progress along path (0.0 to 1.0)
            particle['progress'] += speed
            
            # Loop back to start when reaching end
            if particle['progress'] >= 1.0:
                particle['progress'] = particle['progress'] % 1.0
            
            # Calculate position with smooth interpolation
            path_length = len(path)
            float_index = particle['progress'] * (path_length - 1)
            idx = int(float_index)
            next_idx = (idx + 1) % path_length
            fraction = float_index - idx
            
            # Interpolate position
            current_pos = np.array(path[idx])
            next_pos = np.array(path[next_idx])
            interpolated_pos = current_pos * (1 - fraction) + next_pos * fraction
            
            # Add slight random jitter for realism (small wobble)
            jitter = np.random.normal(0, 0.02, 3)
            final_pos = interpolated_pos + jitter
            
            # Update particle position
            particle['actor'].SetPosition(tuple(final_pos))
            
            # Update color based on progress
            color = self.get_blood_color(particle['progress'])
            particle['actor'].GetProperty().SetColor(color)
        
        # Update heart deformation (SIZE CHANGE ONLY)
        if self.organ_type == 'heart' and self.deformation_parts:
            self.update_heart_deformation()
    
    # ========== PATH CREATION METHODS (UNCHANGED) ==========
    
    def create_flow_path(self, flow_type):
        """
        Create automatic flow path based on organ type.
        Falls back to this if no manual path is set.
        """
        if self.organ_type == 'heart':
            return self.create_heart_flow_path(flow_type)
        elif self.organ_type == 'brain':
            return self.create_brain_flow_path(flow_type)
        elif self.organ_type == 'muscles':
            return self.create_muscle_flow_path(flow_type)
        elif self.organ_type == 'teeth':
            return self.create_dental_flow_path(flow_type)
        return []
    
    def create_heart_flow_path(self, flow_type):
        """Create heart-specific flow paths"""
        points = []
        
        if flow_type and 'Aorta' in flow_type:
            # Aorta flow path (ascending then descending)
            for i in range(80):
                t = i / 80.0
                x = -1.5 - t * 0.8 * np.sin(t * np.pi)
                y = -1.0 + t * 7.0
                z = t * 1.8 * np.cos(t * np.pi * 0.5)
                points.append((x, y, z))
        
        elif flow_type and 'Pulmonary' in flow_type:
            for i in range(60):
                t = i / 60.0
                x = 1.5 + t * 0.5
                y = 1.0 + t * 4.0
                z = np.cos(t * np.pi) * 0.4
                points.append((x, y, z))
        
        elif flow_type and 'Coronary' in flow_type:
            for i in range(70):
                t = i / 70.0
                angle = t * 2 * np.pi
                x = -1.5 + 2.5 * np.cos(angle)
                y = -1.0 + 2.5 * np.sin(angle)
                z = t * 0.8
                points.append((x, y, z))
        
        else:
            # Default circular flow
            for i in range(60):
                t = i / 60.0
                angle = t * 2 * np.pi
                x = 2.5 * np.cos(angle)
                y = 2.5 * np.sin(angle)
                z = np.sin(t * np.pi * 2) * 0.5
                points.append((x, y, z))
        
        return points
    
    def create_brain_flow_path(self, flow_type):
        """Create brain cerebral artery flow"""
        points = []
        for i in range(70):
            t = i / 70.0
            angle = t * np.pi
            x = 3.5 * np.cos(angle)
            y = 1 + t * 2.5
            z = 3.5 * np.sin(angle)
            points.append((x, y, z))
        return points
    
    def create_muscle_flow_path(self, flow_type):
        """Create muscle tissue perfusion flow"""
        points = []
        for i in range(60):
            t = i / 60.0
            x = -2 + t * 4.5
            y = 2 - t * 4.5
            z = np.sin(t * np.pi * 3) * 0.3
            points.append((x, y, z))
        return points
    
    def create_dental_flow_path(self, flow_type):
        """Create dental pulp blood flow"""
        points = []
        for i in range(50):
            t = i / 50.0
            angle = t * np.pi * 2
            x = 2.8 * np.cos(angle)
            y = 0.2
            z = 2.8 * np.sin(angle)
            points.append((x, y, z))
        return points
    
    # ========== HEART DEFORMATION (SIZE-BASED, NOT MOVEMENT) ==========
    
    def setup_heart_deformation(self):
        """Identify heart parts that should deform (pump)"""
        self.deformation_parts = []
        
        # Keywords for parts that should pump
        pump_keywords = [
            'ventricle', 'atrium', 'chamber',
            'left_ventricle', 'right_ventricle',
            'left_atrium', 'right_atrium',
            'lv', 'rv', 'la', 'ra'
        ]
        
        for part_name, actor in self.actors.items():
            part_lower = part_name.lower().replace(' ', '_')
            
            # Check if this part should pump
            for keyword in pump_keywords:
                if keyword in part_lower:
                    self.deformation_parts.append({
                        'name': part_name,
                        'actor': actor,
                        'base_scale': self.original_scales.get(part_name, (1, 1, 1)),
                        'base_position': self.original_positions.get(part_name, (0, 0, 0)),
                        'amplitude': 0.15 if 'ventricle' in part_lower else 0.10
                    })
                    break
        
        print(f"âœ“ Heart deformation enabled for {len(self.deformation_parts)} parts")
        self.deformation_phase = 0
    
    def update_heart_deformation(self):
        """
        Update heart pumping deformation - SIZE CHANGE ONLY.
        The position stays fixed; only the scale changes to simulate contraction/expansion.
        """
        # Increment phase (heartbeat cycle)
        self.deformation_phase += 0.08  # ~75 BPM at 30ms timer
        
        # Calculate scale factor using sine wave
        # Systole (contraction): scale < 1.0
        # Diastole (relaxation): scale > 1.0
        scale_multiplier = 1.0 + 0.12 * np.sin(self.deformation_phase)
        
        # Apply deformation to each heart part
        for part_data in self.deformation_parts:
            actor = part_data['actor']
            base_scale = part_data['base_scale']
            base_position = part_data['base_position']
            amplitude = part_data['amplitude']
            
            # Calculate new scale (pulsating SIZE)
            new_scale = (
                base_scale[0] * (1.0 + amplitude * (scale_multiplier - 1.0)),
                base_scale[1] * (1.0 + amplitude * (scale_multiplier - 1.0)),
                base_scale[2] * (1.0 + amplitude * (scale_multiplier - 1.0))
            )
            
            # Apply scale change
            actor.SetScale(new_scale)
            
            # CRITICAL: Keep position fixed (don't move the heart parts)
            actor.SetPosition(base_position)
    
    def stop_flow_animation(self):
        """Stop flow animation and reset deformation"""
        if self.flow_timer:
            self.flow_timer.stop()
            self.flow_timer = None
        
        # Remove particles
        for particle in self.flow_particles:
            self.renderer.RemoveActor(particle['actor'])
        self.flow_particles = []
        
        # Remove vessel tubes
        if hasattr(self, 'vessel_actors'):
            for actor in self.vessel_actors:
                self.renderer.RemoveActor(actor)
            self.vessel_actors = []
        if hasattr(self, 'entry_exit_markers'):
            for actor in self.entry_exit_markers:
                self.renderer.RemoveActor(actor)
            self.entry_exit_markers = []
        
        
        # Reset heart deformation
        self.reset_deformation()
        
        self.deformation_phase = 0
        self.heartbeat_phase = 0.0
    
    def reset_deformation(self):
        """Reset all actors to original scales AND positions"""
        for part_name, actor in self.actors.items():
            if part_name in self.original_scales:
                actor.SetScale(self.original_scales[part_name])
            if part_name in self.original_positions:
                actor.SetPosition(self.original_positions[part_name])
    
    # ========== ELECTRICAL SIGNAL ANIMATION (UNCHANGED) ==========
    
    def start_electrical_animation(self, speed=5):
        """Start electrical signal animation"""
        self.stop_electrical_animation()
        
        self.create_electrical_particles()
        
        self.electrical_timer = QTimer()
        self.electrical_timer.timeout.connect(self.update_electrical_animation)
        interval = max(20, int(100 / speed))
        self.electrical_timer.start(interval)
        
        return True
    
    def create_electrical_particles(self):
        """Create particles for electrical signal"""
        self.electrical_particles = []
        
        path_points = self.create_electrical_path()
        
        num_particles = 8
        for i in range(num_particles):
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(0.3)
            sphere.SetThetaResolution(16)
            sphere.SetPhiResolution(16)
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1.0, 1.0, 0.0)  # Yellow
            actor.GetProperty().SetOpacity(0.9)
            
            self.electrical_particles.append({
                'actor': actor,
                'path': path_points,
                'index': int(i * len(path_points) / num_particles)
            })
            
            self.renderer.AddActor(actor)
    
    def create_electrical_path(self):
        """Create electrical conduction path"""
        points = []
        
        if self.organ_type == 'heart':
            for i in range(50):
                t = i / 50.0
                x = 0
                y = 1.5 - t * 3.5
                z = np.sin(t * np.pi) * 0.4
                points.append((x, y, z))
        
        elif self.organ_type == 'brain':
            for i in range(60):
                t = i / 60.0
                x = -2 + t * 4
                y = 1 + np.sin(t * np.pi * 2) * 0.6
                z = np.cos(t * np.pi) * 0.4
                points.append((x, y, z))
        
        else:
            for i in range(40):
                t = i / 40.0
                x = -1 + t * 2
                y = t * 2
                z = 0
                points.append((x, y, z))
        
        return points
    
    def update_electrical_animation(self):
        """Update electrical signal positions"""
        for particle in self.electrical_particles:
            path = particle['path']
            if not path:
                continue
            
            particle['index'] = (particle['index'] + 1) % len(path)
            position = path[particle['index']]
            particle['actor'].SetPosition(position)
    
    def stop_electrical_animation(self):
        """Stop electrical signal animation"""
        if self.electrical_timer:
            self.electrical_timer.stop()
            self.electrical_timer = None
        
        for particle in self.electrical_particles:
            self.renderer.RemoveActor(particle['actor'])
        self.electrical_particles = []
        self.electrical_index = 0
    
    # ========== CONTRACTION ANIMATION (LEGACY) ==========
    
    def start_contraction_animation(self):
        """Start standalone contraction animation (without flow)"""
        self.stop_contraction_animation()
        
        self.setup_heart_deformation()
        
        self.contraction_timer = QTimer()
        self.contraction_timer.timeout.connect(self.update_contraction_only)
        self.contraction_timer.start(50)
        
        self.deformation_phase = 0
        return True
    
    def update_contraction_only(self):
        """Update only contraction (no particles)"""
        if self.deformation_parts:
            self.update_heart_deformation()
    
    def stop_contraction_animation(self):
        """Stop contraction animation"""
        if self.contraction_timer:
            self.contraction_timer.stop()
            self.contraction_timer = None
        
        self.reset_deformation()
        self.deformation_phase = 0
    
    # ========== UTILITY METHODS ==========
    
    def is_flow_running(self):
        """Check if flow animation is running"""
        return self.flow_timer is not None
    
    def is_electrical_running(self):
        """Check if electrical animation is running"""
        return self.electrical_timer is not None
    
    def is_contraction_running(self):
        """Check if contraction animation is running"""
        return self.contraction_timer is not None
    
    def stop_all_animations(self):
        """Stop all animations"""
        self.stop_flow_animation()
        self.stop_electrical_animation()
        self.stop_contraction_animation()