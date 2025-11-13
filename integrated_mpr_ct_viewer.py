"""
Integrated Professional MPR CT Viewer with Curved MPR
Combines VTK 3D visualization with MPR slice viewing
"""

import vtk
import numpy as np
import SimpleITK as sitk
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QSlider, QLabel, QGroupBox, 
                             QComboBox, QMessageBox, QSplitter, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class IntegratedMPRViewer(QWidget):
    """Professional MPR viewer integrated with VTK"""
    
    def __init__(self, renderer, model_loader, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.model_loader = model_loader
        
        # MPR Data
        self.itk_image = None
        self.scan_array = None
        self.ct_dimensions = None
        self.ct_spacing = None
        self.ct_origin = None
        
        # Crosshair positions
        self.crosshair_x = 0
        self.crosshair_y = 0
        self.crosshair_z = 0
        
        # Window/Level settings
        self.axial_L = 40.0
        self.axial_W = 400.0
        self.coronal_L = 40.0
        self.coronal_W = 400.0
        self.sagittal_L = 40.0
        self.sagittal_W = 400.0
        
        # Curved MPR
        self.curved_mpr_points = []  # User-drawn curve points
        self.curved_mpr_actors = []
        self.is_drawing_curve = False
        self.curved_mpr_slices = []
        
        # Cine mode
        self.is_playing_z = False
        self.is_playing_y = False
        self.is_playing_x = False
        self.cine_timer = QTimer(self)
        self.cine_timer.timeout.connect(self.next_slice)
        
        self.block_updates = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the MPR viewer UI"""
        main_layout = QVBoxLayout(self)
        
        # Top controls
        controls_layout = self.create_controls()
        main_layout.addLayout(controls_layout)
        
        # MPR Views (2x2 grid)
        views_layout = QGridLayout()
        
        # Axial view (top-left)
        self.axial_fig, self.axial_ax = plt.subplots(figsize=(4, 4))
        self.axial_canvas = FigureCanvas(self.axial_fig)
        axial_panel = self.create_view_panel('axial', self.axial_ax, 
                                             self.axial_canvas, "Axial (Z)")
        views_layout.addWidget(axial_panel, 0, 0)
        
        # Coronal view (top-right)
        self.coronal_fig, self.coronal_ax = plt.subplots(figsize=(4, 4))
        self.coronal_canvas = FigureCanvas(self.coronal_fig)
        coronal_panel = self.create_view_panel('coronal', self.coronal_ax,
                                               self.coronal_canvas, "Coronal (Y)")
        views_layout.addWidget(coronal_panel, 0, 1)
        
        # Sagittal view (bottom-left)
        self.sagittal_fig, self.sagittal_ax = plt.subplots(figsize=(4, 4))
        self.sagittal_canvas = FigureCanvas(self.sagittal_fig)
        sagittal_panel = self.create_view_panel('sagittal', self.sagittal_ax,
                                                self.sagittal_canvas, "Sagittal (X)")
        views_layout.addWidget(sagittal_panel, 1, 0)
        
        # Curved MPR view (bottom-right)
        self.curved_fig, self.curved_ax = plt.subplots(figsize=(4, 4))
        self.curved_canvas = FigureCanvas(self.curved_fig)
        curved_panel = self.create_curved_mpr_panel()
        views_layout.addWidget(curved_panel, 1, 1)
        
        main_layout.addLayout(views_layout)
    
    def create_controls(self):
        """Create control panel"""
        layout = QHBoxLayout()
        
        # Slice navigation group
        nav_group = QGroupBox("Slice Navigation")
        nav_layout = QGridLayout()
        
        # Z slider (Axial)
        nav_layout.addWidget(QLabel("Z (Axial):"), 0, 0)
        self.axial_slider = QSlider(Qt.Horizontal)
        self.axial_slider.setRange(0, 0)
        self.axial_slider.valueChanged.connect(lambda: self.update_crosshair('z'))
        nav_layout.addWidget(self.axial_slider, 0, 1)
        self.axial_label = QLabel("0")
        nav_layout.addWidget(self.axial_label, 0, 2)
        
        # Y slider (Coronal)
        nav_layout.addWidget(QLabel("Y (Coronal):"), 1, 0)
        self.coronal_slider = QSlider(Qt.Horizontal)
        self.coronal_slider.setRange(0, 0)
        self.coronal_slider.valueChanged.connect(lambda: self.update_crosshair('y'))
        nav_layout.addWidget(self.coronal_slider, 1, 1)
        self.coronal_label = QLabel("0")
        nav_layout.addWidget(self.coronal_label, 1, 2)
        
        # X slider (Sagittal)
        nav_layout.addWidget(QLabel("X (Sagittal):"), 2, 0)
        self.sagittal_slider = QSlider(Qt.Horizontal)
        self.sagittal_slider.setRange(0, 0)
        self.sagittal_slider.valueChanged.connect(lambda: self.update_crosshair('x'))
        nav_layout.addWidget(self.sagittal_slider, 2, 1)
        self.sagittal_label = QLabel("0")
        nav_layout.addWidget(self.sagittal_label, 2, 2)
        
        nav_group.setLayout(nav_layout)
        layout.addWidget(nav_group)
        
        # Cine controls
        cine_group = QGroupBox("Cine (Animation)")
        cine_layout = QHBoxLayout()
        
        self.play_z_btn = QPushButton("â–¶ Z")
        self.play_z_btn.clicked.connect(lambda: self.toggle_cine('z'))
        cine_layout.addWidget(self.play_z_btn)
        
        self.play_y_btn = QPushButton("â–¶ Y")
        self.play_y_btn.clicked.connect(lambda: self.toggle_cine('y'))
        cine_layout.addWidget(self.play_y_btn)
        
        self.play_x_btn = QPushButton("â–¶ X")
        self.play_x_btn.clicked.connect(lambda: self.toggle_cine('x'))
        cine_layout.addWidget(self.play_x_btn)
        
        cine_group.setLayout(cine_layout)
        layout.addWidget(cine_group)
        
        # Curved MPR controls
        curved_group = QGroupBox("Curved MPR")
        curved_layout = QHBoxLayout()
        
        self.draw_curve_btn = QPushButton("ðŸ–Šï¸ Draw Curve")
        self.draw_curve_btn.setCheckable(True)
        self.draw_curve_btn.clicked.connect(self.toggle_curve_drawing)
        curved_layout.addWidget(self.draw_curve_btn)
        
        self.clear_curve_btn = QPushButton("ðŸ—‘ï¸ Clear Curve")
        self.clear_curve_btn.clicked.connect(self.clear_curve)
        curved_layout.addWidget(self.clear_curve_btn)
        
        self.generate_mpr_btn = QPushButton("ðŸ“Š Generate MPR")
        self.generate_mpr_btn.clicked.connect(self.generate_curved_mpr)
        curved_layout.addWidget(self.generate_mpr_btn)
        
        curved_group.setLayout(curved_layout)
        layout.addWidget(curved_group)
        
        layout.addStretch()
        return layout
    
    def create_view_panel(self, view_name, ax, canvas, title):
        """Create a view panel with window/level controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title_label)
        
        # Canvas
        canvas.setCursor(QCursor(Qt.CrossCursor))
        canvas.mpl_connect('button_press_event', 
                          lambda event: self.handle_mouse_click(event, view_name))
        layout.addWidget(canvas)
        
        # Window/Level controls
        wl_layout = QHBoxLayout()
        
        wl_layout.addWidget(QLabel("L:"))
        level_slider = QSlider(Qt.Horizontal)
        level_slider.setRange(-1000, 3000)
        level_slider.setValue(40)
        level_slider.valueChanged.connect(lambda: self.update_window_level(view_name))
        setattr(self, f'{view_name}_level_slider', level_slider)
        wl_layout.addWidget(level_slider)
        
        level_label = QLabel("40")
        setattr(self, f'{view_name}_level_label', level_label)
        wl_layout.addWidget(level_label)
        
        wl_layout.addWidget(QLabel("W:"))
        width_slider = QSlider(Qt.Horizontal)
        width_slider.setRange(1, 2000)
        width_slider.setValue(400)
        width_slider.valueChanged.connect(lambda: self.update_window_level(view_name))
        setattr(self, f'{view_name}_width_slider', width_slider)
        wl_layout.addWidget(width_slider)
        
        width_label = QLabel("400")
        setattr(self, f'{view_name}_width_label', width_label)
        wl_layout.addWidget(width_label)
        
        layout.addLayout(wl_layout)
        return panel
    
    def create_curved_mpr_panel(self):
        """Create curved MPR panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title_label = QLabel("Curved MPR")
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title_label)
        
        self.curved_canvas.setCursor(QCursor(Qt.CrossCursor))
        layout.addWidget(self.curved_canvas)
        
        # Info label
        self.curved_info_label = QLabel("Draw curve on any view, then generate MPR")
        self.curved_info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.curved_info_label)
        
        return panel
    
    def load_ct_from_model_loader(self):
        """Load CT data from the main model loader"""
        if not self.model_loader.ct_image:
            QMessageBox.warning(self, "No CT Data", 
                              "Please load a CT scan first in the main window.")
            return False
        
        try:
            # Get CT image from model loader
            self.itk_image = self.model_loader.ct_image
            self.scan_array = sitk.GetArrayFromImage(self.itk_image)
            
            # Get dimensions and spacing
            self.ct_dimensions = self.scan_array.shape  # (Z, Y, X)
            self.ct_spacing = self.itk_image.GetSpacing()
            self.ct_origin = self.itk_image.GetOrigin()
            
            print(f"MPR Viewer - CT loaded: {self.ct_dimensions}")
            
            # Initialize view
            self.initialize_view()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CT: {e}")
            return False
    
    def initialize_view(self):
        """Initialize view after loading CT"""
        if self.scan_array is None:
            return
        
        self.block_updates = True
        
        D, H, W = self.scan_array.shape
        
        # Set slider ranges
        self.axial_slider.setRange(0, D - 1)
        self.axial_slider.setValue(D // 2)
        
        self.coronal_slider.setRange(0, H - 1)
        self.coronal_slider.setValue(H // 2)
        
        self.sagittal_slider.setRange(0, W - 1)
        self.sagittal_slider.setValue(W // 2)
        
        # Set initial crosshair
        self.crosshair_z = D // 2
        self.crosshair_y = H // 2
        self.crosshair_x = W // 2
        
        # Set default window/level for CT
        self.axial_L = 40.0
        self.axial_W = 400.0
        self.coronal_L = 40.0
        self.coronal_W = 400.0
        self.sagittal_L = 40.0
        self.sagittal_W = 400.0
        
        # Update sliders
        for view in ['axial', 'coronal', 'sagittal']:
            getattr(self, f'{view}_level_slider').setValue(40)
            getattr(self, f'{view}_width_slider').setValue(400)
        
        self.block_updates = False
        self.update_all_views()
    
    def update_crosshair(self, axis):
        """Update crosshair position from slider"""
        if self.scan_array is None or self.block_updates:
            return
        
        if axis == 'z':
            self.crosshair_z = self.axial_slider.value()
            self.axial_label.setText(str(self.crosshair_z))
        elif axis == 'y':
            self.crosshair_y = self.coronal_slider.value()
            self.coronal_label.setText(str(self.crosshair_y))
        elif axis == 'x':
            self.crosshair_x = self.sagittal_slider.value()
            self.sagittal_label.setText(str(self.crosshair_x))
        
        self.update_all_views()
    
    def update_window_level(self, view_name):
        """Update window/level for a view"""
        if self.scan_array is None or self.block_updates:
            return
        
        level = getattr(self, f'{view_name}_level_slider').value()
        width = getattr(self, f'{view_name}_width_slider').value()
        
        setattr(self, f'{view_name}_L', float(level))
        setattr(self, f'{view_name}_W', float(width))
        
        getattr(self, f'{view_name}_level_label').setText(str(level))
        getattr(self, f'{view_name}_width_label').setText(str(width))
        
        self.update_all_views()
    
    def handle_mouse_click(self, event, view_type):
        """Handle mouse clicks on MPR views"""
        if self.scan_array is None or event.xdata is None or event.ydata is None:
            return
        
        x_data = int(round(event.xdata))
        y_data = int(round(event.ydata))
        D, H, W = self.scan_array.shape
        
        # If drawing curve, add point
        if self.is_drawing_curve:
            self.add_curve_point(event, view_type)
            return
        
        # Otherwise, update crosshair
        self.block_updates = True
        
        if view_type == 'axial':
            # Click on axial view (Z slice)
            if 0 <= x_data < W and 0 <= y_data < H:
                self.crosshair_x = x_data
                self.crosshair_y = y_data
                self.sagittal_slider.setValue(self.crosshair_x)
                self.coronal_slider.setValue(self.crosshair_y)
        
        elif view_type == 'coronal':
            # Click on coronal view (Y slice)
            if 0 <= x_data < W and 0 <= y_data < D:
                self.crosshair_x = x_data
                self.crosshair_z = y_data
                self.sagittal_slider.setValue(self.crosshair_x)
                self.axial_slider.setValue(self.crosshair_z)
        
        elif view_type == 'sagittal':
            # Click on sagittal view (X slice)
            if 0 <= x_data < H and 0 <= y_data < D:
                self.crosshair_y = x_data
                self.crosshair_z = y_data
                self.coronal_slider.setValue(self.crosshair_y)
                self.axial_slider.setValue(self.crosshair_z)
        
        self.block_updates = False
        self.update_all_views()
    
    def update_all_views(self):
        """Update all MPR views"""
        if self.scan_array is None or self.block_updates:
            return
        
        # Get slices
        axial_slice = self.scan_array[self.crosshair_z, :, :]
        coronal_slice = self.scan_array[:, self.crosshair_y, :]
        sagittal_slice = self.scan_array[:, :, self.crosshair_x]
        
        # Plot each view
        self.plot_slice(self.axial_ax, self.axial_canvas, axial_slice, 
                       'axial', self.axial_L, self.axial_W)
        
        self.plot_slice(self.coronal_ax, self.coronal_canvas, coronal_slice,
                       'coronal', self.coronal_L, self.coronal_W)
        
        self.plot_slice(self.sagittal_ax, self.sagittal_canvas, sagittal_slice,
                       'sagittal', self.sagittal_L, self.sagittal_W)
    
    def plot_slice(self, ax, canvas, slice_data, view_type, level, width):
        """Plot a single slice with crosshair"""
        ax.clear()
        
        # Window/Level
        vmin = level - (width / 2.0)
        vmax = level + (width / 2.0)
        
        # Display slice
        ax.imshow(slice_data, cmap='gray', origin='lower',
                 vmin=vmin, vmax=vmax, interpolation='bilinear', aspect='equal')
        
        # Draw crosshair
        H, W = slice_data.shape
        
        if view_type == 'axial':
            ax.axvline(x=self.crosshair_x, color='yellow', linewidth=1, alpha=0.7)
            ax.axhline(y=self.crosshair_y, color='yellow', linewidth=1, alpha=0.7)
        elif view_type == 'coronal':
            ax.axvline(x=self.crosshair_x, color='yellow', linewidth=1, alpha=0.7)
            ax.axhline(y=self.crosshair_z, color='yellow', linewidth=1, alpha=0.7)
        elif view_type == 'sagittal':
            ax.axvline(x=self.crosshair_y, color='yellow', linewidth=1, alpha=0.7)
            ax.axhline(y=self.crosshair_z, color='yellow', linewidth=1, alpha=0.7)
        
        # Draw curve points if any
        if self.curved_mpr_points:
            self.draw_curve_on_view(ax, view_type)
        
        ax.axis('off')
        canvas.draw_idle()
    
    # ========== CURVED MPR FUNCTIONALITY ==========
    
    def toggle_curve_drawing(self):
        """Toggle curve drawing mode"""
        self.is_drawing_curve = self.draw_curve_btn.isChecked()
        
        if self.is_drawing_curve:
            self.curved_mpr_points = []
            self.curved_info_label.setText("Click on any view to draw curve points")
            self.curved_info_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.curved_info_label.setText(f"Curve has {len(self.curved_mpr_points)} points")
            self.curved_info_label.setStyleSheet("color: blue;")
    
    def add_curve_point(self, event, view_type):
        """Add a point to the curved MPR path"""
        if event.xdata is None or event.ydata is None:
            return
        
        x_data = int(round(event.xdata))
        y_data = int(round(event.ydata))
        D, H, W = self.scan_array.shape
        
        # Convert 2D click to 3D point based on view
        if view_type == 'axial':
            # Axial view: use current Z
            if 0 <= x_data < W and 0 <= y_data < H:
                point_3d = (x_data, y_data, self.crosshair_z)
        
        elif view_type == 'coronal':
            # Coronal view: use current Y
            if 0 <= x_data < W and 0 <= y_data < D:
                point_3d = (x_data, self.crosshair_y, y_data)
        
        elif view_type == 'sagittal':
            # Sagittal view: use current X
            if 0 <= x_data < H and 0 <= y_data < D:
                point_3d = (self.crosshair_x, x_data, y_data)
        else:
            return
        
        self.curved_mpr_points.append(point_3d)
        self.curved_info_label.setText(f"Points: {len(self.curved_mpr_points)} - Click more or uncheck to finish")
        
        # Update views to show points
        self.update_all_views()
    
    def draw_curve_on_view(self, ax, view_type):
        """Draw curve points on a view"""
        if not self.curved_mpr_points:
            return
        
        # Extract coordinates based on view
        points_2d = []
        for px, py, pz in self.curved_mpr_points:
            if view_type == 'axial':
                points_2d.append((px, py))
            elif view_type == 'coronal':
                points_2d.append((px, pz))
            elif view_type == 'sagittal':
                points_2d.append((py, pz))
        
        if len(points_2d) > 1:
            xs, ys = zip(*points_2d)
            ax.plot(xs, ys, 'r-', linewidth=2, alpha=0.8)
            ax.plot(xs, ys, 'ro', markersize=5)
    
    def clear_curve(self):
        """Clear the curved MPR curve"""
        self.curved_mpr_points = []
        self.curved_mpr_slices = []
        self.is_drawing_curve = False
        self.draw_curve_btn.setChecked(False)
        
        # Clear 3D curve visualization
        for actor in self.curved_mpr_actors:
            self.renderer.RemoveActor(actor)
        self.curved_mpr_actors = []
        
        self.curved_info_label.setText("Curve cleared. Draw new curve.")
        self.curved_info_label.setStyleSheet("color: gray; font-style: italic;")
        
        # Clear curved MPR view
        self.curved_ax.clear()
        self.curved_ax.axis('off')
        self.curved_ax.text(0.5, 0.5, 'Draw curve and generate MPR',
                           ha='center', va='center', 
                           transform=self.curved_ax.transAxes,
                           fontsize=14, color='gray')
        self.curved_canvas.draw_idle()
        
        self.update_all_views()
    
    def generate_curved_mpr(self):
        """Generate curved MPR from drawn curve"""
        if len(self.curved_mpr_points) < 2:
            QMessageBox.warning(self, "Need More Points",
                              "Please draw a curve with at least 2 points")
            return
        
        try:
            # Interpolate curve to get smooth path
            curve_points = self.interpolate_curve(self.curved_mpr_points)
            
            # Extract perpendicular slices along curve
            mpr_slices = self.extract_perpendicular_slices(curve_points)
            
            if not mpr_slices:
                QMessageBox.warning(self, "MPR Failed", 
                                  "Could not extract slices along curve")
                return
            
            # Display curved MPR
            self.display_curved_mpr(mpr_slices)
            
            # Visualize curve in 3D
            self.visualize_curve_in_3d(curve_points)
            
            self.curved_info_label.setText(f"âœ“ MPR generated with {len(mpr_slices)} slices")
            self.curved_info_label.setStyleSheet("color: green; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate MPR: {e}")
            import traceback
            traceback.print_exc()

    def interpolate_curve(self, points, num_samples=200):
        """Interpolate curve points using spline for smooth path"""
        if len(points) < 2:
            return points
        
        # Convert to numpy array
        points_array = np.array(points)
        
        # Calculate cumulative arc length
        distances = np.sqrt(np.sum(np.diff(points_array, axis=0)**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(distances)])
        total_length = cumulative_distances[-1]
        # Ensure we have enough samples for smooth MPR
        if total_length > 0:
            # Adaptive sampling: more points for longer curves
            num_samples = min(300, max(200, int(total_length * 2)))
        else:
            num_samples = 200
        
        # Create evenly spaced samples along the curve
        sample_distances = np.linspace(0, total_length, num_samples)
        
        # Interpolate each coordinate
        interpolated = []
        for i in range(3):  # x, y, z
            interp_coord = np.interp(sample_distances, cumulative_distances, points_array[:, i])
            interpolated.append(interp_coord)
        
        # Combine into points list
        result = [(interpolated[0][i], interpolated[1][i], interpolated[2][i]) 
                for i in range(num_samples)]
        
        return result

    def extract_perpendicular_slices(self, curve_points, slice_thickness=2):
        """Extract perpendicular slices along the curve using proper resampling"""
        slices = []
        D, H, W = self.scan_array.shape
        slice_height = 80  # Height of perpendicular slice (vertical in final image)
        
        # Process every point or use adaptive step for very long curves
        step = max(1, len(curve_points) // 400)
        
        for i in range(0, len(curve_points) - 1, step):
            try:
                # Current point and calculate tangent
                p1 = np.array(curve_points[max(0, i-1)])
                p2 = np.array(curve_points[min(len(curve_points)-1, i+1)])
                
                center = np.array(curve_points[i])
                
                # Tangent vector (direction of curve)
                tangent = p2 - p1
                tangent_length = np.linalg.norm(tangent)
                
                if tangent_length < 0.01:
                    continue
                
                tangent = tangent / tangent_length
                
                # Create orthonormal basis for the slice plane
                # Choose an arbitrary vector not parallel to tangent
                if abs(tangent[2]) < 0.9:
                    arbitrary = np.array([0, 0, 1])
                else:
                    arbitrary = np.array([0, 1, 0])
                
                # First perpendicular vector (normal 1)
                normal1 = np.cross(tangent, arbitrary)
                normal1 = normal1 / np.linalg.norm(normal1)
                
                # Second perpendicular vector (normal 2) - completes orthonormal basis
                normal2 = np.cross(tangent, normal1)
                normal2 = normal2 / np.linalg.norm(normal2)
                
                # Extract ONE column of perpendicular slice (1D profile)
                # This will become one vertical line in the final curved MPR
                slice_column = np.zeros(slice_height)
                
                # Sample points along the perpendicular direction (normal2)
                for row in range(slice_height):
                    # Offset from center along perpendicular direction
                    offset = (row - slice_height/2) * 1.0
                    
                    # 3D position in volume
                    pos = center + offset * normal2
                    
                    # Get intensity using trilinear interpolation
                    intensity = self.trilinear_interpolation(pos[0], pos[1], pos[2])
                    slice_column[row] = intensity
                
                slices.append(slice_column)
                
            except Exception as e:
                continue
        
        return slices



    def trilinear_interpolation(self, x, y, z):
        """Perform trilinear interpolation for smooth sampling"""
        D, H, W = self.scan_array.shape
        
        # Clamp coordinates to volume bounds
        x = np.clip(x, 0, W - 1.001)
        y = np.clip(y, 0, H - 1.001)
        z = np.clip(z, 0, D - 1.001)
        
        # Get integer parts
        x0, y0, z0 = int(np.floor(x)), int(np.floor(y)), int(np.floor(z))
        x1, y1, z1 = min(x0 + 1, W - 1), min(y0 + 1, H - 1), min(z0 + 1, D - 1)
        
        # Get fractional parts
        xd = x - x0
        yd = y - y0
        zd = z - z0
        
        # Get values at 8 corners of the cube
        c000 = self.scan_array[z0, y0, x0]
        c001 = self.scan_array[z0, y0, x1]
        c010 = self.scan_array[z0, y1, x0]
        c011 = self.scan_array[z0, y1, x1]
        c100 = self.scan_array[z1, y0, x0]
        c101 = self.scan_array[z1, y0, x1]
        c110 = self.scan_array[z1, y1, x0]
        c111 = self.scan_array[z1, y1, x1]
        
        # Interpolate along x
        c00 = c000 * (1 - xd) + c001 * xd
        c01 = c010 * (1 - xd) + c011 * xd
        c10 = c100 * (1 - xd) + c101 * xd
        c11 = c110 * (1 - xd) + c111 * xd
        
        # Interpolate along y
        c0 = c00 * (1 - yd) + c01 * yd
        c1 = c10 * (1 - yd) + c11 * yd
        
        # Interpolate along z
        c = c0 * (1 - zd) + c1 * zd
        
        return c

    def display_curved_mpr(self, slices):
        """Display curved MPR as straightened view - each slice is a vertical column"""
        if not slices:
            return
        
        # Stack slices horizontally - each slice becomes a vertical column
        # This creates the proper curved MPR visualization
        mpr_image = np.column_stack(slices)
        
        # Apply slight smoothing to reduce artifacts
        try:
            from scipy.ndimage import gaussian_filter
            if len(slices) > 5:
                mpr_image = gaussian_filter(mpr_image, sigma=0.5)
        except ImportError:
            pass  # Skip smoothing if scipy not available
        
        # Display with proper aspect ratio
        self.curved_ax.clear()
        self.curved_ax.imshow(mpr_image, cmap='gray', aspect='auto',
                            vmin=self.axial_L - self.axial_W/2,
                            vmax=self.axial_L + self.axial_W/2,
                            interpolation='bilinear')
        self.curved_ax.set_title(f"Curved MPR ({len(slices)} positions)")
        self.curved_ax.set_xlabel("Position along curve")
        self.curved_ax.set_ylabel("Perpendicular distance")
        self.curved_canvas.draw_idle()
        
        # Store for later use
        self.curved_mpr_slices = slices


    def visualize_curve_in_3d(self, curve_points):
        """Visualize the curve path in 3D VTK view"""
        # Clear previous curve actors
        for actor in self.curved_mpr_actors:
            self.renderer.RemoveActor(actor)
        self.curved_mpr_actors = []
        
        if len(curve_points) < 2:
            return
        
        # Create VTK points
        points = vtk.vtkPoints()
        for x, y, z in curve_points:
            # Convert voxel coordinates to world coordinates
            if self.ct_spacing and self.ct_origin:
                wx = x * self.ct_spacing[0] + self.ct_origin[0]
                wy = y * self.ct_spacing[1] + self.ct_origin[1]
                wz = z * self.ct_spacing[2] + self.ct_origin[2]
                points.InsertNextPoint(wx, wy, wz)
            else:
                points.InsertNextPoint(x, y, z)
        
        # Create polyline
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(curve_points))
        for i in range(len(curve_points)):
            polyline.GetPointIds().SetId(i, i)
        
        # Create cell array
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polyline)
        
        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        # Create tube filter for better visibility
        tube = vtk.vtkTubeFilter()
        tube.SetInputData(polydata)
        tube.SetRadius(1.0)
        tube.SetNumberOfSides(12)
        tube.CappingOn()
        tube.Update()
        
        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 1.0, 0.0)  # Yellow
        actor.GetProperty().SetOpacity(0.8)
        
        self.renderer.AddActor(actor)
        self.curved_mpr_actors.append(actor)
        
        # Add spheres at curve points
        for x, y, z in curve_points[::10]:  # Every 10th point
            sphere = vtk.vtkSphereSource()
            
            if self.ct_spacing and self.ct_origin:
                wx = x * self.ct_spacing[0] + self.ct_origin[0]
                wy = y * self.ct_spacing[1] + self.ct_origin[1]
                wz = z * self.ct_spacing[2] + self.ct_origin[2]
                sphere.SetCenter(wx, wy, wz)
            else:
                sphere.SetCenter(x, y, z)
            
            sphere.SetRadius(3.0)
            sphere.Update()
            
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere.GetOutputPort())
            
            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)
            sphere_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red
            
            self.renderer.AddActor(sphere_actor)
            self.curved_mpr_actors.append(sphere_actor)
    
    # ========== CINE MODE ==========
    
    def toggle_cine(self, axis):
        """Toggle cine loop for an axis"""
        if self.scan_array is None:
            QMessageBox.warning(self, "No Data", "Load CT scan first")
            return
        
        if axis == 'z':
            self.is_playing_z = not self.is_playing_z
            self.play_z_btn.setText("â¸ Z" if self.is_playing_z else "â–¶ Z")
        elif axis == 'y':
            self.is_playing_y = not self.is_playing_y
            self.play_y_btn.setText("â¸ Y" if self.is_playing_y else "â–¶ Y")
        elif axis == 'x':
            self.is_playing_x = not self.is_playing_x
            self.play_x_btn.setText("â¸ X" if self.is_playing_x else "â–¶ X")
        
        # Start/stop timer
        if self.is_playing_z or self.is_playing_y or self.is_playing_x:
            if not self.cine_timer.isActive():
                self.cine_timer.start(50)  # 20 FPS
        else:
            self.cine_timer.stop()
    
    def next_slice(self):
        """Advance to next slice in cine loop"""
        if self.scan_array is None:
            return
        
        if self.is_playing_z:
            val = self.axial_slider.value()
            max_val = self.axial_slider.maximum()
            self.axial_slider.setValue(0 if val >= max_val else val + 1)
        
        if self.is_playing_y:
            val = self.coronal_slider.value()
            max_val = self.coronal_slider.maximum()
            self.coronal_slider.setValue(0 if val >= max_val else val + 1)
        
        if self.is_playing_x:
            val = self.sagittal_slider.value()
            max_val = self.sagittal_slider.maximum()
            self.sagittal_slider.setValue(0 if val >= max_val else val + 1)
    
    def clear(self):
        """Clear all data"""
        self.scan_array = None
        self.itk_image = None
        self.curved_mpr_points = []
        self.curved_mpr_slices = []
        
        # Clear 3D curve
        for actor in self.curved_mpr_actors:
            self.renderer.RemoveActor(actor)
        self.curved_mpr_actors = []
        
        # Stop cine
        if self.cine_timer.isActive():
            self.cine_timer.stop()
        
        # Clear views
        for ax, canvas in [(self.axial_ax, self.axial_canvas),
                          (self.coronal_ax, self.coronal_canvas),
                          (self.sagittal_ax, self.sagittal_canvas),
                          (self.curved_ax, self.curved_canvas)]:
            ax.clear()
            ax.axis('off')
            canvas.draw_idle()