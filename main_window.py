"""
Professional Main Window with Integrated MPR Viewer - FIXED
Enhanced GUI with neon accents, scrolling, and integrated MPR tab
"""

import vtk
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QSlider, QCheckBox,
                             QGroupBox, QTabWidget, QSplitter, QScrollArea,
                             QFileDialog, QButtonGroup, QRadioButton, QMessageBox,
                             QProgressDialog, QFrame, QListWidget, QAbstractItemView,
                             QGridLayout) # <--- 1. إضافة QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from model_loader import ModelLoader
from unified_navigation import FocusNavigationManager, FlythroughManager, VirtualEndoscopyManager
from unified_visualization import ClippingManager, CurvedMPRManager
from visualization.integrated_mpr_ct_viewer import IntegratedMPRViewer
# After line 23 (after other imports from visualization)
from unified_visualization import ClippingManager, CurvedMPRManager, InteractiveMPRManager
from navigation.animations import AnimationManager
from config import (ORGAN_CONFIGS, BACKGROUND_COLOR, get_color_for_part, get_color_for_label,
                    get_color_for_part_hsv, get_color_for_part_pure_hsv, generate_hsv_colors,
                    print_hsv_color_map)


def set_button_style(self, button, style='primary'):
    """Set button style dynamically"""
    style_map = {
        'primary': 'primaryButton',
        'secondary': 'secondaryButton',
        'accent': 'accentButton',
        'danger': 'dangerButton',
        'success': 'successButton'
    }
    button.setObjectName(style_map.get(style, 'primaryButton'))
    button.setStyle(button.style())  # Force refresh

class MedicalVisualizationWindow(QMainWindow):
    """Professional main window with integrated MPR viewer"""
    
    def __init__(self):
        super().__init__()
      
        

        self.setWindowTitle("3D Medical Visualization System - Professional Edition")
            # ✅ ADD THIS DEBUG STYLESHEET FIRST (before theme)

        
        self.virtual_endoscopy = None
        # Initialize VTK components
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(*BACKGROUND_COLOR)
        
        # Initialize managers
        self.model_loader = ModelLoader()
        self.clipping_manager = None
        # After line 54
        self.mpr_manager = None  # New: Interactive MPR planes manager
        self.current_clipping_mode = 'simple'  # 'simple' or 'mpr'
        self.mpr_manager = None
        self.mpr_viewer = None
        self.focus_manager = None
        self.animation_manager = None
        self.flythrough_manager = None
        
        # Initialize UI attributes
        self.mpr_placeholder = None
        
        # Current state
        self.current_organ = None
        self.current_data_mode = None
        self.actors = {}
        self.mappers = {}
        self.part_checkboxes = {}
        
        # Setup UI
        self.setup_ui()
        
        # Apply professional theme
        self.apply_professional_theme()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
    
        # ✅ FIX: Left panel with FIXED width (no stretch)
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, stretch=0)  # stretch=0 = fixed size

        # ✅ Right viewer panel takes ALL remaining space
        right_panel = self.create_viewer_panel()
        main_layout.addWidget(right_panel, stretch=1)  # stretch=1 = fills space
    def create_control_panel(self):
        """Create left control panel with scrolling"""
        panel = QWidget()
        panel.setObjectName("controlPanel")
        
        # ✅ FIX: Use FIXED width to prevent horizontal scrolling
        panel.setFixedWidth(670)  # Fixed at 420px - no stretching!

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Title bar
        title_bar = self.create_title_bar()
        panel_layout.addWidget(title_bar)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # ✅ FIX: Disable horizontal scrollbar completely
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setObjectName("controlScroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # ✅ FIX: Add horizontal margins to prevent text overflow
        scroll_layout.setContentsMargins(15, 20, 15, 20)  # Left and right margins
        scroll_layout.setSpacing(18)
        
        # Add data loading group
        data_group = self.create_data_loading_group()
        scroll_layout.addWidget(data_group)
        
        # Add tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        
        viz_tab = self.create_visualization_tab()
        self.tabs.addTab(viz_tab, "🎨 Visualization")
        
        nav_tab = self.create_navigation_tab()
        self.tabs.addTab(nav_tab, "🧭 Navigation")
        
        anim_tab = self.create_animations_tab()
        self.tabs.addTab(anim_tab, "▶️ Animations")
        
        scroll_layout.addWidget(self.tabs)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        panel_layout.addWidget(scroll)
        
        # Status bar
        status_bar = self.create_status_bar()
        panel_layout.addWidget(status_bar)
        
        return panel
    
    def create_title_bar(self):
        """Create enhanced title bar with gradient"""
        title_widget = QFrame()
        title_widget.setObjectName("titleBar")
        title_widget.setFixedHeight(80)  # ✅ Reduced from 90px
        
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(15, 10, 15, 10)  # ✅ Reduced margins
        title_layout.setSpacing(3)  # ✅ Reduced from 5px
        
        # ✅ Shorter title that fits
        title = QLabel("🏥 Medical Visualization")
        title.setObjectName("mainTitle")
        title.setWordWrap(True)  # ✅ Allow wrapping if needed
        title_layout.addWidget(title)
        
        # ✅ Shorter subtitle
        subtitle = QLabel("3D Analysis System")  # ✅ Shortened
        subtitle.setObjectName("subtitle")
        title_layout.addWidget(subtitle)
        
        return title_widget
    
    def create_status_bar(self):
        """Create fixed status bar"""
        status_widget = QFrame()
        status_widget.setObjectName("statusBar")
        status_widget.setFixedHeight(60)
        
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.status_label = QLabel("Ready to load data")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        return status_widget
    def create_data_loading_group(self):
        """Create data loading group"""
        data_group = QGroupBox("📊 Data Loading")
        data_group.setObjectName("dataGroup")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(12)
        
        # ✅ FIX: Enable word wrapping for long labels
        organ_label = QLabel("🏥 Anatomical System:")
        organ_label.setObjectName("sectionLabel")
        organ_label.setWordWrap(True)  # ← Add this
        data_layout.addWidget(organ_label)
        
        self.organ_selector = QComboBox()
        self.organ_selector.setObjectName("organSelector")
        self.organ_selector.addItem("Select System")
        for organ_key, config in ORGAN_CONFIGS.items():
            self.organ_selector.addItem(config['name'], organ_key)
        data_layout.addWidget(self.organ_selector)
        
        mode_label = QLabel("📊 Data Type:")
        mode_label.setObjectName("sectionLabel")
        mode_label.setWordWrap(True)  # ← Add this
        data_layout.addWidget(mode_label)
        
        # Radio buttons
        self.mode_button_group = QButtonGroup()
        
        # ✅ FIX: Shorten text to fit width
        self.obj_mode_radio = QRadioButton("3D Models (OBJ/STL)")  # Shortened
        self.obj_mode_radio.setChecked(True)
        self.obj_mode_radio.setObjectName("modeRadio")
        self.mode_button_group.addButton(self.obj_mode_radio)
        data_layout.addWidget(self.obj_mode_radio)
        
        self.ct_mode_radio = QRadioButton("CT Scan (NIfTI)")
        self.ct_mode_radio.setObjectName("modeRadio")
        self.mode_button_group.addButton(self.ct_mode_radio)
        data_layout.addWidget(self.ct_mode_radio)
        
        # Buttons with shorter text
        self.load_obj_btn = QPushButton("📂 Load OBJ")  # Shortened
        self.load_obj_btn.setObjectName("successButton")
        self.load_obj_btn.clicked.connect(self.load_obj_folder_dialog)
        data_layout.addWidget(self.load_obj_btn)
        
        self.load_ct_btn = QPushButton("📂 Load CT ")  # Shortened
        self.load_ct_btn.setObjectName("successButton")
        self.load_ct_btn.clicked.connect(self.load_ct_dialog)
        data_layout.addWidget(self.load_ct_btn)
        
        self.load_seg_btn = QPushButton("📂 Load Segmentation")  # Shortened
        self.load_seg_btn.setObjectName("accentButton")
        self.load_seg_btn.clicked.connect(self.load_segmentation_dialog)
        self.load_seg_btn.setEnabled(False)
        data_layout.addWidget(self.load_seg_btn)
        
        self.load_seg_folder_btn = QPushButton("📂 Load Seg Folder")  # Shortened
        self.load_seg_folder_btn.setObjectName("accentButton")
        self.load_seg_folder_btn.clicked.connect(self.load_segmentation_folder_dialog)
        self.load_seg_folder_btn.setEnabled(False)
        data_layout.addWidget(self.load_seg_folder_btn)
        
        self.create_from_seg_btn = QPushButton("🔨 Create 3D")  # Shortened
        self.create_from_seg_btn.setObjectName("primaryButton")
        self.create_from_seg_btn.clicked.connect(self.create_models_from_segmentation)
        self.create_from_seg_btn.setEnabled(False)
        data_layout.addWidget(self.create_from_seg_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Scene")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.clicked.connect(self.clear_scene)
        data_layout.addWidget(self.clear_btn)
        
        data_group.setLayout(data_layout)
        return data_group
    
    def create_visualization_tab(self):
        """Create visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        surface_group = QGroupBox("🎨 Surface Rendering")
        surface_layout = QVBoxLayout()
        
        self.surface_checkbox = QCheckBox("Enable Surface Rendering")
        self.surface_checkbox.setChecked(True)
        self.surface_checkbox.stateChanged.connect(self.toggle_surface_rendering)
        surface_layout.addWidget(self.surface_checkbox)
        
        # --- (بداية التعديل) ---
        # 1. تم نقل "Parts Visibility Control" ليكون *داخل*
        #    "Surface Rendering"
        
        visibility_group = QGroupBox("Parts Visibility Control (Render)")
        visibility_layout = QVBoxLayout()

        visibility_instructions = QLabel("All parts are shown by default. Use Ctrl/Shift to de-select parts to hide them.")
        visibility_instructions.setStyleSheet("color: #888888; font-style: italic; font-size: 8pt;")
        visibility_layout.addWidget(visibility_instructions)

        self.visibility_list_widget = QListWidget()
        self.visibility_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.visibility_list_widget.setStyleSheet("""
            QListWidget { 
                background-color: #1a1a1a; 
                border: 1px solid #333; 
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078d4  ; /* مختار = ظاهر */
                color: #0a0a0a;
            }
            QListWidget::item {
                background-color: #333; /* غير مختار = مخفي */
                color: #888;
                border-bottom: 1px solid #222;
            }
        """)
        self.visibility_list_widget.itemSelectionChanged.connect(self.apply_visibility_logic)
        visibility_layout.addWidget(self.visibility_list_widget)

        visibility_buttons = QHBoxLayout()
        self.show_all_btn = QPushButton("Show All")
        self.show_all_btn.clicked.connect(self.show_all_parts)
        visibility_buttons.addWidget(self.show_all_btn)

        self.hide_all_btn = QPushButton("Hide All")
        self.hide_all_btn.clicked.connect(self.hide_all_parts)
        visibility_buttons.addWidget(self.hide_all_btn)
        visibility_layout.addLayout(visibility_buttons)
        
        visibility_group.setLayout(visibility_layout)
        # 2. تمت إضافة الجروب إلى "surface_layout" (التابع للجروب الأب)
        surface_layout.addWidget(visibility_group)
        # --- (نهاية التعديل) ---

        surface_group.setLayout(surface_layout)
        layout.addWidget(surface_group)
      # REPLACE the entire clipping_group section with this:

        # ========== CLIPPING MODE SELECTOR ==========
        clipping_mode_group = QGroupBox("✂️ Clipping Mode")
        mode_layout = QVBoxLayout()

        self.clipping_mode_buttons = QButtonGroup()

        self.simple_clip_radio = QRadioButton("Simple Clipping (Cut 3D Models)")
        self.simple_clip_radio.setChecked(True)
        self.simple_clip_radio.toggled.connect(self.switch_clipping_mode)
        self.clipping_mode_buttons.addButton(self.simple_clip_radio)
        mode_layout.addWidget(self.simple_clip_radio)

        self.mpr_clip_radio = QRadioButton("Interactive MPR Planes (CT Slices)")
        self.mpr_clip_radio.toggled.connect(self.switch_clipping_mode)
        self.clipping_mode_buttons.addButton(self.mpr_clip_radio)
        mode_layout.addWidget(self.mpr_clip_radio)

        clipping_mode_group.setLayout(mode_layout)
        layout.addWidget(clipping_mode_group)

        # ========== SIMPLE CLIPPING CONTROLS ==========
        self.simple_clipping_group = QGroupBox("🔪Simple Clipping Planes")
        simple_layout = QGridLayout()
        simple_layout.setSpacing(10)

        # Create 3 CheckBoxes
        self.clip_x_check = QCheckBox("Enable X-Axis")
        self.clip_y_check = QCheckBox("Enable Y-Axis")
        self.clip_z_check = QCheckBox("Enable Z-Axis")

        # Create 3 Sliders
        
        self.clip_x_slider = QSlider(Qt.Horizontal)
        self.clip_x_slider.setToolTip("Adjust X-axis clipping position")
        self.clip_y_slider = QSlider(Qt.Horizontal)
        self.clip_y_slider.setToolTip("Adjust Y-axis clipping position")
        self.clip_z_slider = QSlider(Qt.Horizontal)
        self.clip_z_slider.setToolTip("Adjust Z-axis clipping position")
        # Create 3 Labels
        self.clip_x_label = QLabel("50%")
        self.clip_y_label = QLabel("50%")
        self.clip_z_label = QLabel("50%")

        # Add controls to grid
        simple_layout.addWidget(self.clip_x_check, 0, 0)
        simple_layout.addWidget(self.clip_x_slider, 0, 1)
        simple_layout.addWidget(self.clip_x_label, 0, 2)

        simple_layout.addWidget(self.clip_y_check, 1, 0)
        simple_layout.addWidget(self.clip_y_slider, 1, 1)
        simple_layout.addWidget(self.clip_y_label, 1, 2)

        simple_layout.addWidget(self.clip_z_check, 2, 0)
        simple_layout.addWidget(self.clip_z_slider, 2, 1)
        simple_layout.addWidget(self.clip_z_label, 2, 2)

        # Connect signals
        for slider, label, axis in [
            (self.clip_x_slider, self.clip_x_label, 'x'),
            (self.clip_y_slider, self.clip_y_label, 'y'),
            (self.clip_z_slider, self.clip_z_label, 'z')
        ]:
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(50)
            slider.sliderMoved.connect(lambda value, lbl=label, ax=axis: 
                                        self.update_simple_clipping(ax, 'slider', value, lbl))
            slider.sliderReleased.connect(self.render_clipping_update)

        for check, axis in [
            (self.clip_x_check, 'x'),
            (self.clip_y_check, 'y'),
            (self.clip_z_check, 'z')
        ]:
            check.stateChanged.connect(lambda state, ax=axis: 
                                        self.update_simple_clipping(ax, 'check', state))

        self.simple_clipping_group.setLayout(simple_layout)
        layout.addWidget(self.simple_clipping_group)

        # ========== MPR CLIPPING CONTROLS ==========
        self.mpr_clipping_group = QGroupBox("🖼️Interactive MPR Planes (CT)")
        mpr_layout = QGridLayout()
        mpr_layout.setSpacing(10)

        # Info label
        mpr_info = QLabel("💡 Requires CT scan loaded. Shows actual CT slices.")
        mpr_info.setWordWrap(True)
        mpr_info.setStyleSheet("color: #00ff88; font-style: italic;")
        mpr_layout.addWidget(mpr_info, 0, 0, 1, 3)

        # Create 3 CheckBoxes for MPR
        self.mpr_x_check = QCheckBox("Show Sagittal (X)")
        self.mpr_y_check = QCheckBox("Show Coronal (Y)")
        self.mpr_z_check = QCheckBox("Show Axial (Z)")

        # Create 3 Sliders for MPR
        self.mpr_x_slider = QSlider(Qt.Horizontal)
        self.mpr_y_slider = QSlider(Qt.Horizontal)
        self.mpr_z_slider = QSlider(Qt.Horizontal)

        # Create 3 Labels for MPR
        self.mpr_x_label = QLabel("50%")
        self.mpr_y_label = QLabel("50%")
        self.mpr_z_label = QLabel("50%")

        # Add controls to grid
        mpr_layout.addWidget(self.mpr_x_check, 1, 0)
        mpr_layout.addWidget(self.mpr_x_slider, 1, 1)
        mpr_layout.addWidget(self.mpr_x_label, 1, 2)

        mpr_layout.addWidget(self.mpr_y_check, 2, 0)
        mpr_layout.addWidget(self.mpr_y_slider, 2, 1)
        mpr_layout.addWidget(self.mpr_y_label, 2, 2)

        mpr_layout.addWidget(self.mpr_z_check, 3, 0)
        mpr_layout.addWidget(self.mpr_z_slider, 3, 1)
        mpr_layout.addWidget(self.mpr_z_label, 3, 2)

        # Connect signals
        for slider, label, axis in [
            (self.mpr_x_slider, self.mpr_x_label, 'x'),
            (self.mpr_y_slider, self.mpr_y_label, 'y'),
            (self.mpr_z_slider, self.mpr_z_label, 'z')
        ]:
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(50)
            slider.sliderMoved.connect(lambda value, lbl=label, ax=axis: 
                                        self.update_mpr_clipping(ax, 'slider', value, lbl))
            slider.sliderReleased.connect(self.render_clipping_update)

        for check, axis in [
            (self.mpr_x_check, 'x'),
            (self.mpr_y_check, 'y'),
            (self.mpr_z_check, 'z')
        ]:
            check.stateChanged.connect(lambda state, ax=axis: 
                                        self.update_mpr_clipping(ax, 'check', state))

        self.mpr_clipping_group.setLayout(mpr_layout)
        layout.addWidget(self.mpr_clipping_group)

        # Initially hide MPR group
        self.mpr_clipping_group.setVisible(False)
        # --- (بداية الحذف) ---
        # 3. تم حذف الجروب من مكانه القديم (لم نعد نحتاجه هنا)
        visibility_group = QGroupBox("👁️Parts Visibility Control")
        # ... (كل الكود من 326 إلى 374 تم حذفه) ...
        layout.addWidget(visibility_group)
        # --- (نهاية الحذف) ---
        
        layout.addStretch()
        return tab
    
    
   
        
    
    
    def create_navigation_tab(self):
        """Create navigation tab with manual fly-through"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Focus Navigation Group (MODIFIED FOR MULTI-SELECT OPACITY)
        focus_group = QGroupBox("🎯Manual Opacity Control")
        focus_layout = QVBoxLayout()
        
        focus_part_label = QLabel("Select Parts to make Transparent:")
        focus_layout.addWidget(focus_part_label)

        # --- (BEGIN ADDED WIDGETS) ---
        self.opacity_list_widget = QListWidget()
        self.opacity_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # (استعارة الـ style من قائمة الإظهار لتوحيد الشكل)
        self.opacity_list_widget.setStyleSheet("""
            QListWidget { 
                background-color: #1a1a1a; 
                border: 1px solid #333; 
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078d4; /* مختار = سيصبح شفاف */
                color: #0a0a0a;
            }
            QListWidget::item {
                background-color: #333; /* غير مختار = سيظل واضح */
                color: #888;
                border-bottom: 1px solid #222;
            }
        """)
        # ربط التغيير في الاختيار بالدالة المنطقية
        self.opacity_list_widget.itemSelectionChanged.connect(self.apply_opacity_logic)
        focus_layout.addWidget(self.opacity_list_widget)

        self.selected_parts_label = QLabel("Selected: None")
        self.selected_parts_label.setWordWrap(True)
        self.selected_parts_label.setStyleSheet("color: #888; font-style: italic; min-height: 20px;")
        focus_layout.addWidget(self.selected_parts_label)

        self.clear_opacity_btn = QPushButton("Clear Selection")
        self.clear_opacity_btn.clicked.connect(self.clear_opacity_selection)
        focus_layout.addWidget(self.clear_opacity_btn)
        # --- (END ADDED WIDGETS) ---

        transparency_label = QLabel("Selected Part Opacity:") # (تم تعديل النص)
        focus_layout.addWidget(transparency_label)
        
        transparency_layout = QHBoxLayout()
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(70)
        # (تم تعديل الدالة المستدعاة)
        self.transparency_slider.valueChanged.connect(self.update_selection_opacity)
        transparency_layout.addWidget(self.transparency_slider)
        
        self.transparency_value_label = QLabel("70%")
        self.transparency_value_label.setMinimumWidth(50)
        transparency_layout.addWidget(self.transparency_value_label)
        focus_layout.addLayout(transparency_layout)
        
        focus_group.setLayout(focus_layout)
        layout.addWidget(focus_group)
        
        # Manual Fly-through Group (NEW!)
        manual_fly_group = QGroupBox("✈️ Manual Fly-through (Point Selection)")
        manual_fly_layout = QVBoxLayout()
        
        # Instructions
        instruction_label = QLabel(
            "Click on 3D model to pick camera path points.\n"
            "Points will be connected in order."
        )
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("color: #00ff88; font-style: italic; padding: 5px;")
        manual_fly_layout.addWidget(instruction_label)
        
        # Point picking controls
        pick_controls = QHBoxLayout()
        
        self.start_picking_btn = QPushButton("🖱️ Start Picking Points")
        self.start_picking_btn.setCheckable(True)
        self.start_picking_btn.clicked.connect(self.toggle_point_picking)
        pick_controls.addWidget(self.start_picking_btn)
        
        self.clear_points_btn = QPushButton("🗑️ Clear Points")
        self.clear_points_btn.clicked.connect(self.clear_manual_points)
        pick_controls.addWidget(self.clear_points_btn)
        
        manual_fly_layout.addLayout(pick_controls)
        
        # Point count label
        self.point_count_label = QLabel("Points selected: 0")
        self.point_count_label.setStyleSheet("font-weight: bold; color: #00aaff;")
        manual_fly_layout.addWidget(self.point_count_label)
        
        # Manual fly-through buttons
        manual_fly_buttons = QHBoxLayout()
        
        self.manual_flythrough_btn = QPushButton("▶️ Start Manual Fly-through")
        self.manual_flythrough_btn.clicked.connect(self.start_manual_flythrough)
        self.manual_flythrough_btn.setEnabled(False)
        manual_fly_buttons.addWidget(self.manual_flythrough_btn)
        
        self.stop_manual_flythrough_btn = QPushButton("⏹️ Stop")
        self.stop_manual_flythrough_btn.clicked.connect(self.stop_flythrough)
        self.stop_manual_flythrough_btn.setEnabled(False)
        manual_fly_buttons.addWidget(self.stop_manual_flythrough_btn)
        
        manual_fly_layout.addLayout(manual_fly_buttons)
        
        manual_fly_group.setLayout(manual_fly_layout)
        layout.addWidget(manual_fly_group)
        
        # Automatic Fly-through Group
        flythrough_group = QGroupBox("🚁 Automatic Fly-through")
        flythrough_layout = QVBoxLayout()
        
        speed_label = QLabel("Speed:")
        flythrough_layout.addWidget(speed_label)
        
        speed_slider_layout = QHBoxLayout()
        self.flythrough_speed = QSlider(Qt.Horizontal)
        self.flythrough_speed.setMinimum(1)
        self.flythrough_speed.setMaximum(10)
        self.flythrough_speed.setValue(3)
        self.flythrough_speed.valueChanged.connect(self.update_flythrough_speed)
        speed_slider_layout.addWidget(self.flythrough_speed)
        
        self.flythrough_speed_label = QLabel("3")
        self.flythrough_speed_label.setMinimumWidth(50)
        speed_slider_layout.addWidget(self.flythrough_speed_label)
        flythrough_layout.addLayout(speed_slider_layout)
        
        flythrough_buttons = QHBoxLayout()
        self.flythrough_btn = QPushButton("▶️ Start Auto Fly-through")
        self.flythrough_btn.clicked.connect(self.start_flythrough)
        flythrough_buttons.addWidget(self.flythrough_btn)
        
        self.stop_flythrough_btn = QPushButton("⏹️ Stop")
        self.stop_flythrough_btn.clicked.connect(self.stop_flythrough)
        self.stop_flythrough_btn.setEnabled(False)
        flythrough_buttons.addWidget(self.stop_flythrough_btn)
        flythrough_layout.addLayout(flythrough_buttons)
        
        flythrough_group.setLayout(flythrough_layout)
        layout.addWidget(flythrough_group)
        
        # Camera Control Group
        reset_group = QGroupBox("📷 Camera Control")
        reset_layout = QVBoxLayout()
        
        self.reset_camera_btn = QPushButton("🔄 Reset Camera View")
        self.reset_camera_btn.clicked.connect(self.reset_camera)
        reset_layout.addWidget(self.reset_camera_btn)
        
        reset_group.setLayout(reset_layout)
        layout.addWidget(reset_group)
        
        layout.addStretch()
        return tab
    
  
    
    def create_animations_tab(self):
        """Create animations tab with manual path integration"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # ========== BLOOD FLOW GROUP ==========
        flow_group = QGroupBox("💉 Blood Flow Animation")
        flow_layout = QVBoxLayout()
        
        # Flow mode selection
        flow_mode_label = QLabel("Flow Mode:")
        flow_layout.addWidget(flow_mode_label)

        self.flow_mode_group = QButtonGroup()

        self.auto_flow_radio = QRadioButton("Automatic Path (Predefined)")
        self.auto_flow_radio.setChecked(True)
        self.flow_mode_group.addButton(self.auto_flow_radio)
        flow_layout.addWidget(self.auto_flow_radio)

        self.manual_flow_radio = QRadioButton("Manual Path (Use Picked Points)")
        self.flow_mode_group.addButton(self.manual_flow_radio)
        flow_layout.addWidget(self.manual_flow_radio)

        # Instructions for manual mode
        manual_flow_info = QLabel(
            "💡 Tip: Go to Navigation tab → Pick points on model → "
            "Return here and select 'Manual Path'"
        )
        manual_flow_info.setWordWrap(True)
        manual_flow_info.setStyleSheet("color: #00ff88; font-style: italic; padding: 5px;")
        flow_layout.addWidget(manual_flow_info)
        
        # Flow type selector (for automatic mode)
        flow_type_label = QLabel("Flow Type (Automatic):")
        flow_layout.addWidget(flow_type_label)
        
        self.flow_type = QComboBox()
        self.flow_type.addItem("Select Flow Type")
        flow_layout.addWidget(self.flow_type)
        
        # Instructions for manual mode
        manual_flow_info = QLabel(
            "💡 Tip: Go to Navigation tab → Pick points on model → "
            "Return here and select 'Manual Path'"
        )
        manual_flow_info.setWordWrap(True)
        manual_flow_info.setStyleSheet("color: #00ff88; font-style: italic; padding: 5px;")
        flow_layout.addWidget(manual_flow_info)
        
        # Speed control
        flow_speed_label = QLabel("Animation Speed:")
        flow_layout.addWidget(flow_speed_label)
        
        flow_speed_layout = QHBoxLayout()
        self.flow_speed = QSlider(Qt.Horizontal)
        self.flow_speed.setMinimum(1)
        self.flow_speed.setMaximum(10)
        self.flow_speed.setValue(5)
        self.flow_speed.valueChanged.connect(lambda v: self.flow_speed_value_label.setText(str(v)))
        flow_speed_layout.addWidget(self.flow_speed)
        
        self.flow_speed_value_label = QLabel("5")
        self.flow_speed_value_label.setMinimumWidth(50)
        flow_speed_layout.addWidget(self.flow_speed_value_label)
        flow_layout.addLayout(flow_speed_layout)
        
        # Flow control buttons
        flow_buttons = QHBoxLayout()
        self.start_flow_btn = QPushButton("▶️ Start Blood Flow")
        self.start_flow_btn.clicked.connect(self.start_flow_animation)
        flow_buttons.addWidget(self.start_flow_btn)
        
        self.stop_flow_btn = QPushButton("⏹️ Stop")
        self.stop_flow_btn.clicked.connect(self.stop_flow_animation)
        self.stop_flow_btn.setEnabled(False)
        flow_buttons.addWidget(self.stop_flow_btn)
        flow_layout.addLayout(flow_buttons)
        
        flow_group.setLayout(flow_layout)
        layout.addWidget(flow_group)
        
        # ========== ELECTRICAL SIGNAL GROUP ==========
        electrical_group = QGroupBox("⚡ Electrical Signal Animation")
        electrical_layout = QVBoxLayout()
        
        electrical_speed_label = QLabel("Speed:")
        electrical_layout.addWidget(electrical_speed_label)
        
        electrical_speed_layout = QHBoxLayout()
        self.electrical_speed = QSlider(Qt.Horizontal)
        self.electrical_speed.setMinimum(1)
        self.electrical_speed.setMaximum(10)
        self.electrical_speed.setValue(5)
        self.electrical_speed.valueChanged.connect(lambda v: self.electrical_speed_label.setText(str(v)))
        electrical_speed_layout.addWidget(self.electrical_speed)
        
        self.electrical_speed_label = QLabel("5")
        self.electrical_speed_label.setMinimumWidth(50)
        electrical_speed_layout.addWidget(self.electrical_speed_label)
        electrical_layout.addLayout(electrical_speed_layout)
        
        electrical_buttons = QHBoxLayout()
        self.start_electrical_btn = QPushButton("⚡ Start Signals")
        self.start_electrical_btn.clicked.connect(self.start_electrical_animation)
        electrical_buttons.addWidget(self.start_electrical_btn)
        
        self.stop_electrical_btn = QPushButton("⏹️ Stop")
        self.stop_electrical_btn.clicked.connect(self.stop_electrical_animation)
        self.stop_electrical_btn.setEnabled(False)
        electrical_buttons.addWidget(self.stop_electrical_btn)
        electrical_layout.addLayout(electrical_buttons)
        
        electrical_group.setLayout(electrical_layout)
        layout.addWidget(electrical_group)
        
        # ========== CONTRACTION GROUP ==========
        contraction_group = QGroupBox("💗 Heart Contraction")
        contraction_layout = QVBoxLayout()
        
        contraction_info = QLabel(
            "Note: Heart deformation is automatically included with Blood Flow.\n"
            "Use this for standalone contraction without particles."
        )
        contraction_info.setWordWrap(True)
        contraction_info.setStyleSheet("color: #888888; font-style: italic;")
        contraction_layout.addWidget(contraction_info)
        
        contraction_buttons = QHBoxLayout()
        self.contraction_btn = QPushButton("💗 Start Contraction")
        self.contraction_btn.clicked.connect(self.start_contraction)
        contraction_buttons.addWidget(self.contraction_btn)
        
        self.stop_contraction_btn = QPushButton("⏹️ Stop")
        self.stop_contraction_btn.clicked.connect(self.stop_contraction)
        self.stop_contraction_btn.setEnabled(False)
        contraction_buttons.addWidget(self.stop_contraction_btn)
        contraction_layout.addLayout(contraction_buttons)
        
        contraction_group.setLayout(contraction_layout)
        layout.addWidget(contraction_group)
        
        layout.addStretch()
        return tab
    
    # <!-- (تم الحذف) دالة "create_parts_tab" لم نعد بحاجتها -->

    def start_virtual_endoscopy(self):
        """Start automatic virtual endoscopy"""
        if not self.virtual_endoscopy:
            self.virtual_endoscopy = VirtualEndoscopyManager(self.renderer, self.model_loader)
        
        speed = self.flythrough_speed.value()
        show_path = self.show_flythrough_path.isChecked()
        mode = self.flythrough_mode.currentText()
        
        success = False
        
        if "Auto-detect" in mode:
            # Automatic detection
            success = self.virtual_endoscopy.start_automatic_flythrough(speed, show_path)
        else:
            # Manual selection
            structure = self.flythrough_structure.currentText()
            if structure and structure != "(Load segmentation first)":
                success = self.virtual_endoscopy.start_flythrough_for_structure(
                    structure, speed, show_path
                )
        
        if success:
            self.flythrough_btn.setEnabled(False)
            self.stop_flythrough_btn.setEnabled(True)
            self.update_status("Virtual endoscopy started")
            self.start_render_timer()
        else:
            self.update_status("Failed to start virtual endoscopy - need CT segmentation", error=True)
            QMessageBox.warning(self, "Cannot Start", 
                            "Virtual endoscopy requires:\n\n"
                            "1. Load CT scan\n"
                            "2. Load segmentation (file or folder)\n"
                            "3. Create 3D models from segmentation\n\n"
                            "The system will automatically find tubular structures.")

    def stop_virtual_endoscopy(self):
        """Stop virtual endoscopy"""
        if self.virtual_endoscopy:
            self.virtual_endoscopy.stop_flythrough()
        
        self.flythrough_btn.setEnabled(True)
        self.stop_flythrough_btn.setEnabled(False)
        self.update_status("Virtual endoscopy stopped")
        self.stop_render_timer()

    def update_flythrough_speed(self, value):
        """Update flythrough speed"""
        self.flythrough_speed_label.setText(str(value))
        if self.virtual_endoscopy and self.virtual_endoscopy.is_running():
            self.virtual_endoscopy.set_speed(value)

    
    def create_viewer_panel(self):
        """Create right viewer panel with tabs"""
        panel = QWidget()
        panel.setObjectName("viewerPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.viewer_tabs = QTabWidget()
        self.viewer_tabs.setObjectName("viewerTabs")
        
        view_3d_widget = self.create_3d_view()
        self.viewer_tabs.addTab(view_3d_widget, "3D View")
        
        self.mpr_tab_widget = QWidget()
        mpr_tab_layout = QVBoxLayout(self.mpr_tab_widget)
        mpr_tab_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mpr_placeholder = QLabel("Load CT scan to enable MPR viewer")
        self.mpr_placeholder.setAlignment(Qt.AlignCenter)
        self.mpr_placeholder.setStyleSheet("color: #666666; font-size: 14pt;")
        mpr_tab_layout.addWidget(self.mpr_placeholder)
        
        self.viewer_tabs.addTab(self.mpr_tab_widget, "MPR View")
        self.viewer_tabs.setTabEnabled(1, False)
        
        layout.addWidget(self.viewer_tabs)
        
        return panel
    
    def create_3d_view(self):
        """Create 3D VTK view widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.vtk_widget = QVTKRenderWindowInteractor(widget)
        layout.addWidget(self.vtk_widget)
        
        render_window = self.vtk_widget.GetRenderWindow()
        render_window.AddRenderer(self.renderer)
        
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)
        
        
        return widget
    
    # File Loading Methods
    def load_obj_folder_dialog(self):
        """Load OBJ folder"""
        organ_index = self.organ_selector.currentIndex()
        if organ_index == 0:
            QMessageBox.warning(self, "No System Selected",
                              "Please select an anatomical system first!")
            return
        
        organ_key = self.organ_selector.itemData(organ_index)
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with OBJ/STL Files")
        
        if not folder:
            return
        
        progress = QProgressDialog("Loading OBJ files...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            self.clear_scene()
            self.current_organ = organ_key
            self.current_data_mode = 'obj'
            
            models = self.model_loader.load_obj_folder(folder, organ_key)
            progress.close()
            
            if models and len(models) > 0:
                self.create_actors_from_models(models, organ_key)
                self.initialize_managers()
                self.reset_camera()
                self.update_status(f"Loaded {len(models)} OBJ models successfully")
                QMessageBox.information(self, "Success",
                                      f"Successfully loaded {len(models)} 3D models!")
            else:
                self.update_status("No valid OBJ/STL files found", error=True)
        except Exception as e:
            progress.close()
            self.update_status(f"Error: {str(e)}", error=True)
    
    def load_ct_dialog(self):
        """Load CT scan and enable MPR viewer"""
        organ_index = self.organ_selector.currentIndex()
        if organ_index == 0:
            QMessageBox.warning(self, "No System Selected",
                              "Please select an anatomical system first!")
            return
        
        organ_key = self.organ_selector.itemData(organ_index)
        file, _ = QFileDialog.getOpenFileName(self, "Select CT NIfTI File", "",
                                             "NIfTI Files (*.nii *.nii.gz)")
        
        if not file:
            return
        
        progress = QProgressDialog("Loading CT scan...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            self.clear_scene()
            self.current_organ = organ_key
            self.current_data_mode = 'ct'
            
            ct_image = self.model_loader.load_ct_nifti(file, organ_key)
            progress.close()
            
            if ct_image:
                self.load_seg_btn.setEnabled(True)
                self.load_seg_folder_btn.setEnabled(True)
                self.enable_mpr_viewer() 
                self.reset_camera()
                self.vtk_widget.GetRenderWindow().Render()
                self.update_status("CT scan loaded successfully")
                QMessageBox.information(self, "Success",
                                      "CT scan loaded! Switch to MPR View tab to explore slices.")
            else:
                self.update_status("Failed to load CT", error=True)
        except Exception as e:
            progress.close()
            self.update_status(f"Error: {str(e)}", error=True)
    
    def load_segmentation_dialog(self):
        """Load segmentation from single file"""
        if self.current_data_mode != 'ct':
            QMessageBox.warning(self, "No CT Loaded", "Please load a CT scan first!")
            return
        
        file, _ = QFileDialog.getOpenFileName(self, "Select Segmentation NIfTI File", "",
                                             "NIfTI Files (*.nii *.nii.gz)")
        if not file:
            return
        
        progress = QProgressDialog("Loading segmentation...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            seg_data = self.model_loader.load_segmentation_nifti(file, self.current_organ)
            progress.close()
            
            if seg_data is not None:
                self.create_from_seg_btn.setEnabled(True)
                unique_labels = len(self.model_loader.get_unique_labels())
                self.update_status(f"Segmentation loaded ({unique_labels} regions)")
                QMessageBox.information(self, "Success",
                                      f"Segmentation loaded!\nFound {unique_labels} regions.")
            else:
                self.update_status("Failed to load segmentation", error=True)
        except Exception as e:
            progress.close()
            self.update_status(f"Error: {str(e)}", error=True)
    
    def load_segmentation_folder_dialog(self):
        """Load segmentation from folder with multiple files"""
        if self.current_data_mode != 'ct':
            QMessageBox.warning(self, "No CT Loaded", "Please load a CT scan first!")
            return
        
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Segmentation Files")
        if not folder:
            return
        
        progress = QProgressDialog("Loading segmentation folder...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            seg_data = self.model_loader.load_segmentation_folder(folder, self.current_organ)
            progress.close()
            
            if seg_data is not None:
                self.create_from_seg_btn.setEnabled(True)
                unique_labels = len(self.model_loader.get_unique_labels())
                self.update_status(f"Segmentation folder loaded ({unique_labels} regions)")
                QMessageBox.information(self, "Success",
                                      f"Segmentation folder loaded!\nFound {unique_labels} regions from multiple files.")
            else:
                self.update_status("Failed to load segmentation folder", error=True)
        except Exception as e:
            progress.close()
            self.update_status(f"Error: {str(e)}", error=True)

    def update_flythrough_structure_list(self):
        """Update available structures for manual fly-through"""
        self.flythrough_structure.clear()
        
        if self.model_loader.segmentation_files:
            # --- (سبت الكود ده زي ما هو) ---
            for label_id, info in self.model_loader.segmentation_files.items():
                filename = info['filename']
                # Remove extension
                name = filename.replace('.nii.gz', '').replace('.nii', '')
                self.flythrough_structure.addItem(name)
            self.flythrough_structure.setEnabled(True)
        else:
            self.flythrough_structure.addItem("(No structures available)")
            self.flythrough_structure.setEnabled(False)
    
    def create_models_from_segmentation(self):
        """Create 3D from segmentation"""
        if self.current_data_mode != 'ct':
            QMessageBox.warning(self, "Wrong Mode", "CT mode required!")
            return
        
        if not self.model_loader.has_segmentation():
            QMessageBox.warning(self, "No Segmentation", "Load segmentation first!")
            return
        
        num_labels = len(self.model_loader.get_unique_labels())
        progress = QProgressDialog("Creating 3D models...", "Cancel", 0, num_labels, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        models = None # عرفت المتغير بره
        try:
            models = self.model_loader.create_models_from_segmentation(
                self.current_organ,
                progress_callback=lambda i: progress.setValue(i)
            )
            progress.close()
            
        except Exception as e:
            progress.close()
            self.update_status(f"Error: {str(e)}", error=True)
            return # اخرج لو حصل إيرور

        if models and len(models) > 0:
            self.create_actors_from_models(models, self.current_organ)
            self.initialize_managers()
            self.reset_camera()
            # After self.reset_camera() in load_ct_dialog
            # ADD this:
            if self.current_clipping_mode == 'mpr':
                self.setup_mpr_planes()
                        
            # ENABLE VIRTUAL ENDOSCOPY
            self.flythrough_btn.setEnabled(True)
           # self.update_flythrough_structure_list()#
            
            self.update_status(f"Created {len(models)} 3D models")
            QMessageBox.information(self, "Success", f"Created {len(models)} 3D models!")
        else:
            self.update_status("Failed to create models", error=True)
    
    def enable_mpr_viewer(self):
        """Enable and initialize MPR viewer in tab"""
        if not self.model_loader.ct_image:
            return
        
        if self.mpr_placeholder:
            self.mpr_placeholder.setParent(None)
            self.mpr_placeholder = None
        
        if not self.mpr_viewer:
            mpr_layout = self.mpr_tab_widget.layout()
            self.mpr_viewer = IntegratedMPRViewer(self.renderer, self.model_loader, self.mpr_tab_widget)
            
            if self.mpr_viewer.load_ct_from_model_loader():
                
                # إضافة السكرول لتاب الـ MPR
                mpr_scroll_area = QScrollArea()
                mpr_scroll_area.setWidgetResizable(True)
                mpr_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                mpr_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                mpr_scroll_area.setObjectName("mprScroll") # عشان الـ Theme
                
                mpr_scroll_area.setWidget(self.mpr_viewer)
                mpr_layout.addWidget(mpr_scroll_area)
                
                self.viewer_tabs.setTabEnabled(1, True)
                self.viewer_tabs.setCurrentIndex(1)
            else:
                self.update_status("Failed to initialize MPR viewer", error=True)
 
    
    def create_actors_from_models(self, models, organ_key):
        """
        Create VTK actors with anatomically appropriate colors
        Matches part names to anatomical structures for realistic coloring
        
        !!! FIX: Disables specular light to show true anatomical colors.
        """
        print(f"\n{'='*70}")
        print(f"Creating Actors with ANATOMICAL Coloring for: {organ_key}")
        print(f"{'='*70}")
        
        for part_name, polydata in models.items():
            # Create mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polydata)
            
            # Create actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # Get anatomically appropriate color
            color = get_color_for_part(organ_key, part_name)
            
            # Print color assignment for debugging
            rgb_display = tuple(int(c * 255) for c in color)
            print(f"  🎨 {part_name:35s} -> RGB{rgb_display}")
            
            # Apply color and properties
            actor.GetProperty().SetColor(color)
            
            # 💡 التعديل النهائي لضمان ظهور اللون التشريحي بوضوح:
            # 1. زيادة قوة الانتشار (Diffuse) لتعكس اللون الأساسي بقوة.
            actor.GetProperty().SetDiffuse(1.0)
            # 2. إزالة اللمعان (Specular) الذي يسبب توحيد الألوان تحت الإضاءة.
            actor.GetProperty().SetSpecular(0.0) 
            actor.GetProperty().SetSpecularPower(0)
            
            actor.GetProperty().SetOpacity(1.0)
            
            # Add to renderer
            self.renderer.AddActor(actor)
            self.actors[part_name] = actor
            self.mappers[part_name] = mapper
        
        print(f"{'='*70}")
        print(f"✓ Created {len(models)} actors with anatomical coloring")
        print(f"{'='*70}\n")
        
        # Update UI
        self.vtk_widget.GetRenderWindow().Render()
        
        self.renderer.ResetCamera()
        

    def get_scene_bounds(self):
        """Calculates the combined bounds of all actors in the scene."""
        if not self.actors:
            return [0, 0, 0, 0, 0, 0]
        
        # (تم الإصلاح 1) استخدام "vtkBoundingBox" الصحيح
        all_bounds = vtk.vtkBoundingBox()
        
        for actor in self.actors.values():
            actor_bounds = actor.GetBounds()
            if actor_bounds:
                # (تم الإصلاح 2) "AddBounds" تأخذ "Tuple" واحد، وليس 6 أرقام.
                # (لذلك قمنا بحذف النجمة "*")
                all_bounds.AddBounds(actor_bounds) 
                
        # (تم الإصلاح 3) هذا هو الخطأ الحقيقي الثاني:
        # "GetBounds" لا "ترجع" قائمة، بل "تملأ" قائمة أنت تمررها لها.
        
        # 1. ننشئ مصفوفة (list) فارغة
        bounds_array = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # 2. نتأكد أن الحدود صالحة قبل ما نطلبها
        if all_bounds.IsValid():
            # 3. نمرر المصفوفة ليتم ملؤها
            all_bounds.GetBounds(bounds_array) 
            print(f"[Main Window] Calculated Scene Bounds: {bounds_array}")
            return bounds_array # نرجع المصفوفة الممتلئة
        else:
             print("[Main Window] Warning: Could not calculate valid scene bounds.")
             # إرجاع قيمة افتراضية كبيرة كاحتياط
             return [-100, 100, -100, 100, -100, 100]
    # <!-- (نهاية التعديل) -->

    def initialize_managers(self):
        """Initialize all managers"""
        self.clipping_manager = ClippingManager()
        self.clipping_manager.set_actors(self.actors)
        
        # Calculate scene bounds
        scene_bounds = self.get_scene_bounds()
        self.clipping_manager.set_scene_bounds(scene_bounds)
        
        self.focus_manager = FocusNavigationManager(self.renderer)
        self.focus_manager.set_actors(self.actors)
        
        self.animation_manager = AnimationManager(self.renderer, self.current_organ)
        self.animation_manager.set_actors(self.actors)
        
        # Initialize virtual endoscopy (which includes flythrough)
        self.virtual_endoscopy = VirtualEndoscopyManager(self.renderer, self.model_loader)
        
        # Initialize the manual flythrough manager using FlythroughManager
        from unified_navigation import FlythroughManager
        self.flythrough_manager = FlythroughManager(self.renderer, self.current_organ)
        
        self.update_animation_types()
        self.populate_part_lists()
    
    # Visualization Methods
    def toggle_surface_rendering(self, state):
        enabled = (state == 2)
        for actor in self.actors.values():
            actor.SetVisibility(enabled)
        self.vtk_widget.GetRenderWindow().Render()
    
    # <!-- (بداية الحذف) -->
    # <!-- تم حذف الدوال القديمة الخاصة بالـ Clipping -->
    # def toggle_clipping(self, state):
    # ...
    # def change_clipping_axis(self, index):
    # ...
    # def update_clipping(self, value):
    # ...
    # <!-- (نهاية الحذف) -->

    # <!-- (بداية الإضافة) الدالة الموحدة الجديدة للـ Clipping -->
    def update_clipping_state(self, axis, sender_type, value, label=None):
        """
        Slot function called by any of the 6 clipping controls (3 checks, 3 sliders).
        Updates the ClippingManager without rendering.
        """
        if not self.clipping_manager:
            return
        
        # 1. تحديد الحالة (Enabled/Disabled)
        if axis == 'x':
            is_enabled = self.clip_x_check.isChecked()
            current_pos = self.clip_x_slider.value()
        elif axis == 'y':
            is_enabled = self.clip_y_check.isChecked()
            current_pos = self.clip_y_slider.value()
        elif axis == 'z':
            is_enabled = self.clip_z_check.isChecked()
            current_pos = self.clip_z_slider.value()

        # 2. تحديد الموضع (Position)
        if sender_type == 'slider':
            position = value
            if label:
                label.setText(f"{position}%") # تحديث النسبة (0-100)
        else: # sender_type == 'check'
            position = current_pos
            is_enabled = (value == 2) # (2 == Qt.Checked)
        
        # 3. إرسال الأمر الموحد إلى الـ Manager
        self.clipping_manager.update_plane_state(axis, is_enabled, position)
        
        # 4. تحديث الـ Render (فقط عند تحريك الـ Slider)
        if sender_type == 'slider':
            self.vtk_widget.GetRenderWindow().Render()

    def render_clipping_update(self):
        """Called when slider is released to ensure final render."""
        self.vtk_widget.GetRenderWindow().Render()
    
    def switch_clipping_mode(self):
        """Switch between simple clipping and MPR planes"""
        if self.simple_clip_radio.isChecked():
            self.current_clipping_mode = 'simple'
            self.simple_clipping_group.setVisible(True)
            self.mpr_clipping_group.setVisible(False)
            
            # Disable MPR planes if active
            if self.mpr_manager:
                self.mpr_manager.remove_all_planes()
            
            self.update_status("Switched to Simple Clipping mode")
        else:
            self.current_clipping_mode = 'mpr'
            self.simple_clipping_group.setVisible(False)
            self.mpr_clipping_group.setVisible(True)
            
            # Disable simple clipping if active
            if self.clipping_manager:
                self.clipping_manager.remove_all_clipping()
            
            # Check if CT is loaded
            if not self.model_loader.ct_image:
                QMessageBox.warning(self, "No CT Loaded",
                                "Interactive MPR Planes require a CT scan.\n\n"
                                "Please load a CT scan first!")
                self.simple_clip_radio.setChecked(True)  # Revert
                return
            
            # Setup MPR if not already done
            if not self.mpr_manager:
                self.setup_mpr_planes()
            
            self.update_status("Switched to Interactive MPR Planes mode")
        
        self.vtk_widget.GetRenderWindow().Render()

    def update_simple_clipping(self, axis, sender_type, value, label=None):
        """Update simple clipping planes"""
        if not self.clipping_manager:
            return
        
        # Get state
        if axis == 'x':
            is_enabled = self.clip_x_check.isChecked()
            current_pos = self.clip_x_slider.value()
        elif axis == 'y':
            is_enabled = self.clip_y_check.isChecked()
            current_pos = self.clip_y_slider.value()
        elif axis == 'z':
            is_enabled = self.clip_z_check.isChecked()
            current_pos = self.clip_z_slider.value()
        else:
            return
        
        # Determine position
        if sender_type == 'slider':
            position = value
            if label:
                label.setText(f"{position}%")
        else:  # check
            position = current_pos
            is_enabled = (value == 2)
        
        # Update manager
        self.clipping_manager.update_plane_state(axis, is_enabled, position)
        
        if sender_type == 'slider':
            self.vtk_widget.GetRenderWindow().Render()

    def update_mpr_clipping(self, axis, sender_type, value, label=None):
        """Update MPR plane widgets"""
        if not self.mpr_manager:
            return
        
        # Get state
        if axis == 'x':
            is_enabled = self.mpr_x_check.isChecked()
            current_pos = self.mpr_x_slider.value()
        elif axis == 'y':
            is_enabled = self.mpr_y_check.isChecked()
            current_pos = self.mpr_y_slider.value()
        elif axis == 'z':
            is_enabled = self.mpr_z_check.isChecked()
            current_pos = self.mpr_z_slider.value()
        else:
            return
        
        # Determine position
        if sender_type == 'slider':
            position = value
            if label:
                label.setText(f"{position}%")
        else:  # check
            position = current_pos
            is_enabled = (value == 2)
        
        # Update manager
        print(f"[Main] Updating MPR {axis} plane: enabled={is_enabled}, position={position}%")
        self.mpr_manager.update_plane_state(axis, is_enabled, position)
        
        # Force render
        self.interactor.Render()
        self.vtk_widget.GetRenderWindow().Render()
        
        # Update status
        plane_name = {'x': 'Sagittal', 'y': 'Coronal', 'z': 'Axial'}[axis]
        status = "enabled" if is_enabled else "disabled"
        self.update_status(f"MPR {plane_name} plane {status} at {position}%")

    def setup_mpr_planes(self):
        """Setup MPR planes after CT is loaded"""
        if not self.model_loader.ct_image:
            print("[Main] No CT image available for MPR planes")
            return
        
        # Get VTK image data
        ct_vtk_image = self.model_loader.get_ct_volume_actor()
        
        if ct_vtk_image is None:
            print("[Main] Failed to get VTK image data")
            return
        
        # Initialize MPR manager
        if not self.mpr_manager:
            from unified_visualization import InteractiveMPRManager
            self.mpr_manager = InteractiveMPRManager()
        
        # Pass interactor and CT data
        self.mpr_manager.set_interactor(self.interactor)
        self.mpr_manager.set_ct_image(ct_vtk_image)
        
        print("[Main] MPR planes initialized successfully")
        
        # Reset camera to focus on CT volume
        bounds = ct_vtk_image.GetBounds()
        self.renderer.ResetCamera(bounds)
        
        # Position camera at 45-degree angle
        camera = self.renderer.GetActiveCamera()
        center = ct_vtk_image.GetCenter()
        
        max_dimension = max(
            bounds[1] - bounds[0],
            bounds[3] - bounds[2],
            bounds[5] - bounds[4]
        )
        
        distance = max_dimension * 2.0
        camera.SetPosition(
            center[0] + distance,
            center[1] + distance,
            center[2] + distance
        )
        camera.SetFocalPoint(center[0], center[1], center[2])
        camera.SetViewUp(0, 0, 1)
        
        self.renderer.ResetCameraClippingRange()
        self.vtk_widget.GetRenderWindow().Render()    
        
        
    # <!-- (نهاية الإضافة) -->

    # -----------------------------------------------------------------
    # --- التعديل: تطبيق المنطق العكسي للشفافية ---
    # -----------------------------------------------------------------
    
    def apply_opacity_logic(self):
        """
        Applies opacity to *selected* items, leaving others at 100%.
        This is the new "reversed" logic requested by the user.
        """
        if not self.actors:
            return

        try:
            # 1. Get all selected part names from the list
            selected_items = self.opacity_list_widget.selectedItems()
            selected_part_names = {item.text() for item in selected_items} # Use a set for faster lookup
            
            # 2. Get the opacity value from the slider
            selected_opacity = self.transparency_slider.value() / 100.0
            
            # 3. Check if any items are selected
            if selected_part_names:
                # --- (المنطق الجديد: إذا كان هناك اختيار) ---
                
                # Loop through ALL actors
                for part_name, actor in self.actors.items():
                    if part_name in selected_part_names:
                        # هذا الملف تم اختياره -> طبق عليه شفافية الـ Slider
                        actor.GetProperty().SetOpacity(selected_opacity)
                    else:
                        # هذا الملف لم يتم اختياره -> اجعله واضحاً
                        actor.GetProperty().SetOpacity(1.0)
                
                # 5. Update labels
                parts_text = ", ".join(selected_part_names)
                self.selected_parts_label.setText(f"Selected: {parts_text}")
                self.update_status(f"Opacity {selected_opacity*100}% applied to {len(selected_part_names)} parts")

            else:
                # --- (المنطق الجديد: إذا لم يكن هناك اختيار) ---
                
                # Loop through ALL actors and reset them to 100%
                for actor in self.actors.values():
                    actor.GetProperty().SetOpacity(1.0)
                
                # 5b. Update labels
                self.selected_parts_label.setText("Selected: None (All Visible)")
                self.update_status("Opacity reset. All parts visible.")

            # 6. Render the result
            self.vtk_widget.GetRenderWindow().Render()
            
        except Exception as e:
            # أي خطأ آخر
            print(f"!!!!!!!!!! خطأ غير متوقع في 'apply_opacity_logic' !!!!!!!!!!!")
            print(f"الخطأ: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"Error: {e}", error=True)


    def clear_opacity_selection(self):
        """Clears the selection in the QListWidget."""
        # <!-- (تم التعديل) التأكد من أننا نمسح القائمة الصحيحة -->
        self.opacity_list_widget.clearSelection()
    
    def update_selection_opacity(self, value):
        """Updates the opacity value label and applies the logic in real-time."""
        # 1. تحديث قيمة النسبة المئوية
        self.transparency_value_label.setText(f"{value}%")
        # 2. استدعاء الدالة الرئيسية لتطبيق القيمة فوراً على المجسمات
        self.apply_opacity_logic()
    
    # --- (نهاية التعديلات على دوال الـ Focus/Opacity) ---
    
    # --- (بداية الإضافة: المهمة رقم 2) ---
    # --- دوال التحكم في الإظهار (Visibility) ---
    
    def apply_visibility_logic(self):
        """
        Applies visibility based on the visibility_list_widget.
        Selected items = Visible. Deselected items = Hidden.
        """
        if not self.actors:
            return

        # 1. Get all selected part names from the visibility list
        selected_items = self.visibility_list_widget.selectedItems()
        selected_part_names = {item.text() for item in selected_items} # Use a set for faster lookup
        
        # 2. Loop through ALL actors
        for part_name, actor in self.actors.items():
            if part_name in selected_part_names:
                # This part IS selected -> Show it
                actor.SetVisibility(True)
            else:
                # This part is NOT selected -> Hide it
                actor.SetVisibility(False)
        
        self.vtk_widget.GetRenderWindow().Render()

    def show_all_parts(self):
        """Selects all items in the visibility list, making all parts visible."""
        # Stop listening to signals temporarily
        try:
            self.visibility_list_widget.itemSelectionChanged.disconnect(self.apply_visibility_logic)
        except TypeError:
            pass # (إصلاح الـ Crash) تجاهل الخطأ إذا لم يكن متصلاً
        
        self.visibility_list_widget.selectAll()
        
        # Reconnect signals
        self.visibility_list_widget.itemSelectionChanged.connect(self.apply_visibility_logic)
        
        # Apply the logic manually once
        self.apply_visibility_logic()
        self.update_status("All parts are visible")

    def hide_all_parts(self):
        """Deselects all items in the visibility list, hiding all parts."""
        # Stop listening to signals temporarily
        try:
            self.visibility_list_widget.itemSelectionChanged.disconnect(self.apply_visibility_logic)
        except TypeError:
            pass # (إصلاح الـ Crash) تجاهل الخطأ إذا لم يكن متصلاً
        
        self.visibility_list_widget.clearSelection()
        
        # Reconnect signals
        self.visibility_list_widget.itemSelectionChanged.connect(self.apply_visibility_logic)
        
        # Apply the logic manually once
        self.apply_visibility_logic()
        self.update_status("All parts are hidden")
        
    # --- (نهاية الإضافة: المهمة رقم 2) ---

    def start_flythrough(self):
        if not self.flythrough_manager:
            return
        
        speed = self.flythrough_speed.value()
        path_type = self.flythrough_path_selector.currentText()
        show_path = self.show_path_checkbox.isChecked()
        
        success = self.flythrough_manager.start_flythrough(
            path_type, 
            speed, 
            show_path=show_path
        )
        
        if success:
            self.flythrough_btn.setEnabled(False)
            self.stop_flythrough_btn.setEnabled(True)
            self.update_status(f"Fly-through started: {path_type}")
            self.start_render_timer()
        else:
            self.update_status("Failed to create fly-through path", error=True)
    

    def stop_flythrough(self):
        """Stop any active fly-through"""
        if self.flythrough_manager:
            self.flythrough_manager.stop_flythrough()
        
        # Reset button states
        self.flythrough_btn.setEnabled(True)
        self.stop_flythrough_btn.setEnabled(False)
        self.manual_flythrough_btn.setEnabled(self.flythrough_manager and 
                                            self.flythrough_manager.has_manual_path())
        self.stop_manual_flythrough_btn.setEnabled(False)
        
        self.update_status("Fly-through stopped")
        self.stop_render_timer()
    # Animation Methods
    # ========== ANIMATION METHODS (UPDATED) ==========
    def start_flow_animation(self):
        """Start blood flow animation with optional manual path"""
        if not self.animation_manager:
            QMessageBox.warning(self, "No Data", 
                            "Please load 3D models first!")
            return
        
        # Determine mode
        use_manual_path = self.manual_flow_radio.isChecked()
        
        if use_manual_path:
            # Check if manual points exist
            if not self.flythrough_manager or not self.flythrough_manager.has_manual_path():
                QMessageBox.warning(self, "No Manual Path",
                                "Please pick points first:\n\n"
                                "1. Go to Navigation tab\n"
                                "2. Click 'Start Picking Points'\n"
                                "3. Click on 3D model to place points\n"
                                "4. Return here and start flow animation")
                return
            
            # Transfer manual points to animation manager
            manual_points = self.flythrough_manager.manual_points
            success = self.animation_manager.set_manual_flow_path(manual_points)
            
            if not success:
                QMessageBox.warning(self, "Path Error", 
                                "Failed to set manual flow path")
                return
            
            # Start flow with manual path
            speed = self.flow_speed.value()
            success = self.animation_manager.start_flow_animation(
                flow_type=None, 
                speed=speed, 
                use_manual_path=True
            )
            
            if success:
                self.start_flow_btn.setEnabled(False)
                self.stop_flow_btn.setEnabled(True)
                self.update_status("Blood flow started (Manual Path)")
                self.start_render_timer()
                self.renderer.ResetCamera()
                self.vtk_widget.GetRenderWindow().Render()
        else:
            # Automatic mode
            flow_type = self.flow_type.currentText()
            if flow_type == "Select Flow Type":
                self.update_status("Please select a flow type", error=True)
                return
            
            speed = self.flow_speed.value()
            success = self.animation_manager.start_flow_animation(
                flow_type, 
                speed, 
                use_manual_path=False
            )
            
            if success:
                self.start_flow_btn.setEnabled(False)
                self.stop_flow_btn.setEnabled(True)
                self.update_status(f"Blood flow started: {flow_type}")
                self.start_render_timer()
            
    def stop_flow_animation(self):
        """Stop blood flow animation"""
        if self.animation_manager:
            self.animation_manager.stop_flow_animation()
        
        self.start_flow_btn.setEnabled(True)
        self.stop_flow_btn.setEnabled(False)
        self.update_status("Blood flow stopped")
        
        # Check if any other animations are still running
        self.stop_render_timer()
        
        # Force render to show stopped state
        self.vtk_widget.GetRenderWindow().Render()

    def start_electrical_animation(self):
        """Start electrical signal animation"""
        if not self.animation_manager:
            return
        
        speed = self.electrical_speed.value()
        success = self.animation_manager.start_electrical_animation(speed)
        
        if success:
            self.start_electrical_btn.setEnabled(False)
            self.stop_electrical_btn.setEnabled(True)
            self.update_status("Electrical signal animation started")
            self.start_render_timer()

    def stop_electrical_animation(self):
        """Stop electrical signal animation"""
        if self.animation_manager:
            self.animation_manager.stop_electrical_animation()
        
        self.start_electrical_btn.setEnabled(True)
        self.stop_electrical_btn.setEnabled(False)
        self.update_status("Electrical signal animation stopped")
        self.stop_render_timer()

    def start_contraction(self):
        """Start standalone contraction animation"""
        if not self.animation_manager:
            return
        
        success = self.animation_manager.start_contraction_animation()
        
        if success:
            self.contraction_btn.setEnabled(False)
            self.stop_contraction_btn.setEnabled(True)
            self.update_status("Heart contraction animation started")
            self.start_render_timer()

    def stop_contraction(self):
        """Stop contraction animation"""
        if self.animation_manager:
            self.animation_manager.stop_contraction_animation()
        
        self.contraction_btn.setEnabled(True)
        self.stop_contraction_btn.setEnabled(False)
        self.update_status("Contraction animation stopped")
        self.stop_render_timer()
    # Parts Management
    
    # <!-- (تم الحذف) كل الدوال القديمة الخاصة بـ Parts Control -->
    # apply_visibility_logic
    # show_all_parts
    # hide_all_parts
    
    def update_animation_types(self):
        self.flow_type.clear()
        self.flow_type.addItem("Select Flow Type")
        if self.current_organ in ORGAN_CONFIGS:
            animations = ORGAN_CONFIGS[self.current_organ]['animations']
            flow_animations = [a for a in animations if 'Flow' in a]
            self.flow_type.addItems(flow_animations)
    
    # <!-- (تم التعديل) اسم الدالة ومحتواها -->
    def populate_part_lists(self):
        """Populates BOTH the opacity and visibility lists."""
        
        all_parts = sorted(list(self.actors.keys()))

        # 1. Populate Opacity List (in Navigation tab)
        if hasattr(self, 'opacity_list_widget'):
            try:
                self.opacity_list_widget.itemSelectionChanged.disconnect(self.apply_opacity_logic)
            except TypeError:
                pass
            
            self.opacity_list_widget.clear()
            self.opacity_list_widget.addItems(all_parts)
            self.opacity_list_widget.itemSelectionChanged.connect(self.apply_opacity_logic)
        
        # 2. Populate Visibility List (in Visualization tab)
        if hasattr(self, 'visibility_list_widget'):
            try:
                self.visibility_list_widget.itemSelectionChanged.disconnect(self.apply_visibility_logic)
            except TypeError:
                pass
                
            self.visibility_list_widget.clear()
            self.visibility_list_widget.addItems(all_parts)
            self.visibility_list_widget.selectAll()
            self.visibility_list_widget.itemSelectionChanged.connect(self.apply_visibility_logic)
        
       
   
 
    

# Scene Management
    def clear_scene(self):
        """Clear all actors and reset the scene"""
        # Remove all actors from renderer
        for actor in self.actors.values():
            self.renderer.RemoveActor(actor)
        
        # Clear dictionaries
        self.actors.clear()
        self.mappers.clear()
        
        # Stop all animations
        if self.animation_manager:
            self.animation_manager.stop_all_animations()
        
        # Stop virtual endoscopy
        if self.virtual_endoscopy:
            self.virtual_endoscopy.stop_flythrough()
        
        # Clear model loader data
        self.model_loader.clear()
        
        # Disable buttons that require data
        self.load_seg_btn.setEnabled(False)
        self.load_seg_folder_btn.setEnabled(False)
        self.create_from_seg_btn.setEnabled(False)
        self.flythrough_btn.setEnabled(False)
        
        
        # Clear MPR viewer if it exists
        if self.mpr_viewer:
            # 💡 FIX: Manually remove all widgets from the MPR tab layout
            mpr_layout = self.mpr_tab_widget.layout()
            self._clear_layout(mpr_layout) # استخدام الدالة الجديدة للمسح
            
            self.mpr_viewer.clear()
            self.mpr_viewer = None
            
        # Disable MPR tab and switch to 3D view
        self.viewer_tabs.setTabEnabled(1, False)
        self.viewer_tabs.setCurrentIndex(0)
        
        # Restore MPR placeholder
        if not self.mpr_placeholder:
            mpr_layout = self.mpr_tab_widget.layout()
            self.mpr_placeholder = QLabel("Load CT scan to enable MPR viewer")
            self.mpr_placeholder.setAlignment(Qt.AlignCenter)
            self.mpr_placeholder.setStyleSheet("color: #666666; font-size: 14pt;")
            mpr_layout.addWidget(self.mpr_placeholder)
        
        # Clear the part lists
        if hasattr(self, 'opacity_list_widget'):
            try:
                self.opacity_list_widget.itemSelectionChanged.disconnect(self.apply_opacity_logic)
            except TypeError:
                pass
            self.opacity_list_widget.clear()
            self.opacity_list_widget.itemSelectionChanged.connect(self.apply_opacity_logic)
        
        if hasattr(self, 'visibility_list_widget'):
            try:
                self.visibility_list_widget.itemSelectionChanged.disconnect(self.apply_visibility_logic)
            except TypeError:
                pass
            self.visibility_list_widget.clear()
            self.visibility_list_widget.itemSelectionChanged.connect(self.apply_visibility_logic)
        # ADD before self.vtk_widget.GetRenderWindow().Render() in clear_scene
        if self.mpr_manager:
            self.mpr_manager.remove_all_planes()
            self.mpr_manager = None

        # Reset clipping mode UI
        self.simple_clip_radio.setChecked(True)
        self.current_clipping_mode = 'simple'
        self.simple_clipping_group.setVisible(True)
        self.mpr_clipping_group.setVisible(False)

        # Reset MPR UI
        self.mpr_x_check.setChecked(False)
        self.mpr_y_check.setChecked(False)
        self.mpr_z_check.setChecked(False)
        self.mpr_x_slider.setValue(50)
        self.mpr_y_slider.setValue(50)
        self.mpr_z_slider.setValue(50)
        
        
        # Render the empty scene
        self.vtk_widget.GetRenderWindow().Render()
        
        # Update status
        self.update_status("Scene cleared")
        if self.flythrough_manager:
            self.flythrough_manager.clear_manual_points()
            self.flythrough_manager.disable_picking_mode(self.interactor)
        
        if self.start_picking_btn.isChecked():
            self.start_picking_btn.setChecked(False)
        
        self.update_point_count()
            


    def reset_camera(self):
        self.renderer.ResetCamera()
        camera = self.renderer.GetActiveCamera()
        camera.Azimuth(30)
        camera.Elevation(20)
        self.renderer.ResetCameraClippingRange()
        self.vtk_widget.GetRenderWindow().Render()
        self.update_status("Camera view reset")
    
    # Render Timer
    def start_render_timer(self):
        if not hasattr(self, 'render_timer'):
            self.render_timer = QTimer()
            self.render_timer.timeout.connect(self.update_render)
        if not self.render_timer.isActive():
            self.render_timer.start(30)
    
    def stop_render_timer(self):
        animations_active = False
        if self.animation_manager:
            animations_active = (
                self.animation_manager.is_flow_running() or
                self.animation_manager.is_electrical_running() or
                self.animation_manager.is_contraction_running()
            )
        
        if self.virtual_endoscopy and self.virtual_endoscopy.is_running():
            animations_active = True
            
        # (تم الإصلاح) حذف الـ Manager الخاطئ
        # if self.flythrough_manager and self.flythrough_manager.is_running():
        #     animations_active = True
            
        if not animations_active and hasattr(self, 'render_timer'):
            self.render_timer.stop()
    
    def update_render(self):
        self.vtk_widget.GetRenderWindow().Render()
    
    def update_status(self, message, error=False):
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("QLabel#statusLabel { color: #ff4444; }")
        else:
            self.status_label.setStyleSheet("QLabel#statusLabel { color: #0078d4  ; }")
    
    def apply_professional_theme(self):
        """Apply modern professional theme with enhanced styling"""
        theme = """
        /* ========== TITLE BAR ========== */
        QFrame#titleBar {
            background-color: #0d1117;  /* نفس لون الخلفية */
            border-bottom: 3px solid #1f6feb;  /* خط أزرق تحتيه */
            padding: 5px;
        }

        QLabel#mainTitle {
            font-size: 16pt;  /* ✅ REDUCED from 24pt */
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 1px;  /* ✅ REDUCED from 2px */
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        QLabel#subtitle {
            font-size: 9pt;  /* ✅ REDUCED from 11pt */
            color: #e6edf3;
            font-style: italic;
            font-weight: 500;
        }
        
        /* ========== GLOBAL STYLES ========== */
        QMainWindow, QWidget {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
            font-size: 9pt;  /* ✅ Reduced from 10pt */
        }
        
        /* ... keep all other styles the same until BUTTONS section ... */
        
        /* ========== COMBO BOXES ========== */
        QComboBox {
            background-color: #161b22;
            border: 2px solid #30363d;
            border-radius: 6px;  /* ✅ REDUCED from 8px */
            padding: 6px 12px;  /* ✅ REDUCED from 10px 15px */
            color: #c9d1d9;
            min-height: 28px;  /* ✅ REDUCED from 35px */
            max-height: 34px;  /* ✅ ADDED */
            font-size: 9pt;  /* ✅ REDUCED from 10pt */
        }

        QComboBox:hover {
            border-color: #58a6ff;
            background-color: #21262d;
        }

        QComboBox:focus {
            border-color: #1f6feb;
            background-color: #0d1117;
        }

        QComboBox#organSelector {
            font-weight: bold;
            font-size: 10pt;  /* ✅ REDUCED from 11pt */
            border-color: #1f6feb;
            min-height: 32px;  /* ✅ REDUCED from 40px */
        }
        /* ========== GROUP BOXES ========== */
        QGroupBox {
            border: 2px solid #30363d;
            border-radius: 8px;
            margin-top: 15px;  /* ✅ REDUCED from 20px */
            padding-top: 18px;  /* ✅ REDUCED from 20px */
            font-weight: bold;
            color: #e6edf3;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #161b22, stop:1 #0d1117);
            font-size: 10pt;  /* ✅ REDUCED from 11pt */
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;  /* ✅ REDUCED from 20px */
            padding: 4px 12px;  /* ✅ REDUCED from 5px 15px */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #1f6feb, stop:1 #8b5cf6);
            color: #ffffff;
            border-radius: 5px;  /* ✅ REDUCED from 6px */
            font-weight: bold;
        }
        
        /* ========== STATUS BAR ========== */
        QFrame#statusBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #0d1117, stop:1 #161b22);
            border-top: 2px solid #30363d;
            padding: 6px;  /* ✅ REDUCED from 8px */
        }

        QLabel#statusLabel {
            color: #58a6ff;
            font-weight: 600;
            font-size: 9pt;  /* ✅ REDUCED from 10pt */
            padding: 4px 8px;  /* ✅ REDUCED from 5px 10px */
            background-color: rgba(88, 166, 255, 0.1);
            border-radius: 4px;
            border-left: 3px solid #58a6ff;
        }
        
        /* ========== TAB WIDGET ========== */
        QTabWidget::pane {
            border: 2px solid #30363d;
            background-color: #0d1117;
            border-radius: 8px;
            top: -2px;
        }

        QTabWidget#mainTabs::pane {
            border-color: #1f6feb;
        }

        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #21262d, stop:1 #161b22);
            color: #8b949e;
            padding: 10px 18px;  /* ✅ REDUCED from 14px 25px */
            border: 2px solid #30363d;
            border-bottom: none;
            margin-right: 2px;  /* ✅ REDUCED from 3px */
            border-top-left-radius: 6px;  /* ✅ REDUCED from 8px */
            border-top-right-radius: 6px;
            font-size: 9pt;  /* ✅ REDUCED from 10pt */
            font-weight: 500;
        }

        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #1f6feb, stop:1 #8b5cf6);
            color: #ffffff;
            font-weight: bold;
            border-color: #1f6feb;
            padding: 10px 20px;  /* ✅ REDUCED from 14px 28px */
        }
        
        
        
        /* ========== BUTTONS ========== */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #21262d, stop:1 #161b22);
            border: 2px solid #30363d;
            color: #c9d1d9;
            padding: 6px 10px;  /* ✅ REDUCED from 12px 20px */
            border-radius: 5px;  /* ✅ REDUCED from 8px */
            font-weight: 600;
            font-size: 8pt;  /* ✅ REDUCED from 10pt */
            text-align: center;
            min-height: 24px;  /* ✅ ADDED to control height */
            max-height: 30px;  /* ✅ ADDED to control height */
        }
        
        QPushButton:hover {
            border-color: #58a6ff;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #30363d, stop:1 #21262d);
            color: #ffffff;
        }
        
        QPushButton:pressed {
            background: #0d1117;
            border-color: #1f6feb;
            padding: 9px 11px 7px 13px;  /* ✅ ADJUSTED */
        }
        
        QPushButton:disabled {
            background-color: #0d1117;
            color: #484f58;
            border-color: #21262d;
        }
        
        /* Keep all the button variants (primaryButton, secondaryButton, etc.) */
        /* ... rest of your theme stays the same ... */
        """
        self.setStyleSheet(theme)
   
    def _clear_layout(self, layout):
        """Utility to remove all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())
                    
    def toggle_manual_waypoint_mode(self, checked):
        """Toggle manual waypoint placement mode"""
        if not self.virtual_endoscopy:
            self.virtual_endoscopy = VirtualEndoscopyManager(self.renderer, self.model_loader)
        
        if checked:
            # Enable mode
            self.virtual_endoscopy.enable_manual_waypoint_mode(self.interactor)
            self.manual_waypoint_btn.setText(" Stop Waypoint Mode")
            self.clear_waypoints_btn.setEnabled(True)
            self.update_status("Click on 3D model to place waypoints")
        else:
            # Disable mode
            self.virtual_endoscopy.disable_manual_waypoint_mode(self.interactor)
            self.manual_waypoint_btn.setText(" Enable Waypoint Mode")
            
            num_waypoints = len(self.virtual_endoscopy.waypoints)
            self.waypoint_count_label.setText(f"Waypoints: {num_waypoints}")
            
            if num_waypoints >= 2:
                self.generate_path_btn.setEnabled(True)
                self.update_status(f" {num_waypoints} waypoints placed. Generate path to start.")
            else:
                self.update_status("Need at least 2 waypoints", error=True)
        
        # Refresh render to show/hide markers
        self.vtk_widget.GetRenderWindow().Render()

    def clear_manual_waypoints(self):
        """Clear all manual waypoints"""
        if self.virtual_endoscopy:
            self.virtual_endoscopy.clear_waypoints()
            self.waypoint_count_label.setText("Waypoints: 0")
            self.generate_path_btn.setEnabled(False)
            self.vtk_widget.GetRenderWindow().Render()
            self.update_status("Waypoints cleared")

    def generate_path_from_waypoints(self):
        """Generate smooth camera path from manual waypoints"""
        if not self.virtual_endoscopy:
            return
        
        success = self.virtual_endoscopy.generate_path_from_waypoints(smoothness=50)
        
        if success:
            self.flythrough_btn.setEnabled(True)
            self.update_status(" Camera path generated! Click 'Start' to fly.")
            QMessageBox.information(self, "Path Generated",
                                f"Created smooth camera path with {len(self.virtual_endoscopy.camera_path)} positions.\n\n"
                                "Click 'Start Virtual Endoscopy' to begin fly-through.")
        else:
            self.update_status("Failed to generate path", error=True)
            QMessageBox.warning(self, "Generation Failed",
                            "Need at least 2 waypoints to generate path.") 
        
    def toggle_point_picking(self):
        """Toggle point picking mode for manual fly-through"""
        # Check if we have any actors loaded
        if not self.actors or len(self.actors) == 0:
            QMessageBox.warning(self, "No Data", 
                            "Please load 3D models first!\n\n"
                            "You can either:\n"
                            "1. Load OBJ/STL files, OR\n"
                            "2. Load CT + Segmentation and create 3D models")
            self.start_picking_btn.setChecked(False)
            return
        
        # Initialize flythrough manager if needed
        if not self.flythrough_manager:
            # Import here to avoid circular dependency
            from unified_navigation import FlythroughManager
            self.flythrough_manager = FlythroughManager(self.renderer, self.current_organ)
        
        if self.start_picking_btn.isChecked():
            # Enable picking mode
            success = self.flythrough_manager.enable_picking_mode(self.interactor)
            
            if success:
                self.start_picking_btn.setText("🛑 Stop Picking")
                self.update_status("Point picking mode ON - Click on 3D model to add points")
                
                # Start update timer to refresh point count
                if not hasattr(self, 'picking_update_timer'):
                    self.picking_update_timer = QTimer()
                    self.picking_update_timer.timeout.connect(self.update_point_count)
                self.picking_update_timer.start(500)  # Update every 500ms
            else:
                self.start_picking_btn.setChecked(False)
                self.update_status("Failed to enable picking mode", error=True)
        else:
            # Disable picking mode
            self.flythrough_manager.disable_picking_mode(self.interactor)
            self.start_picking_btn.setText("🖱️ Start Picking Points")
            self.update_status("Point picking mode OFF")
            
            if hasattr(self, 'picking_update_timer'):
                self.picking_update_timer.stop()
            
            # Update UI based on point count
            self.update_point_count()


    def update_point_count(self):
        """Update point count label and enable/disable fly-through button"""
        if not self.flythrough_manager:
            return
        
        count = self.flythrough_manager.get_manual_point_count()
        self.point_count_label.setText(f"Points selected: {count}")
        
        # Enable manual fly-through button if we have enough points
        if count >= 2:
            self.manual_flythrough_btn.setEnabled(True)
            self.point_count_label.setStyleSheet("font-weight: bold; color: #00ff88;")
        else:
            self.manual_flythrough_btn.setEnabled(False)
            self.point_count_label.setStyleSheet("font-weight: bold; color: #ff8800;")


    def clear_manual_points(self):
        """Clear manually picked points"""
        if not self.flythrough_manager:
            return
        
        self.flythrough_manager.clear_manual_points()
        self.update_point_count()
        self.vtk_widget.GetRenderWindow().Render()
        self.update_status("Manual points cleared")


    def start_manual_flythrough(self):
        """Start manual fly-through using picked points"""
        if not self.flythrough_manager:
            return
        
        if not self.flythrough_manager.has_manual_path():
            QMessageBox.warning(self, "Insufficient Points", 
                            "Please pick at least 2 points on the 3D model!")
            return
        
        # Disable picking mode if active
        if self.start_picking_btn.isChecked():
            self.start_picking_btn.setChecked(False)
            self.toggle_point_picking()
        
        speed = self.flythrough_speed.value()
        success = self.flythrough_manager.start_manual_flythrough(speed)
        
        if success:
            self.manual_flythrough_btn.setEnabled(False)
            self.stop_manual_flythrough_btn.setEnabled(True)
            self.flythrough_btn.setEnabled(False)
            self.stop_flythrough_btn.setEnabled(True)
            self.update_status("Manual fly-through started")
            self.start_render_timer()       