# 🏥 3D Medical Visualization System
### Professional Interactive Anatomical Viewer with Advanced Navigation & Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![VTK](https://img.shields.io/badge/VTK-9.0+-green.svg)](https://vtk.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-Educational-purple.svg)](LICENSE)

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Quick Start Guide](#-quick-start-guide)
- [Detailed Feature Documentation](#-detailed-feature-documentation)
- [Supported Data Formats](#-supported-data-formats)
- [Technical Specifications](#-technical-specifications)
- [Troubleshooting](#-troubleshooting)
- [Performance Tips](#-performance-tips)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

A **state-of-the-art 3D medical visualization system** built with VTK and PyQt5 that provides:

- **4 Anatomical Systems**: Cardiovascular (Heart), Nervous (Brain), Musculoskeletal, Dental
- **3 Visualization Methods**: Surface Rendering, Clipping Planes, Interactive MPR
- **3 Navigation Techniques**: Manual Opacity Control, Manual Path Fly-through, Automatic Fly-through
- **Advanced Animations**: Realistic blood flow with heartbeat simulation, electrical signals, organ deformation

**Perfect for**: Medical students, researchers, educators, and healthcare professionals who need powerful 3D anatomical visualization tools.

---

## ✨ Key Features

### 🎨 **Visualization Methods**

#### 1. **Surface Rendering**
- High-quality 3D surface reconstruction
- Anatomically accurate color coding (e.g., arteries=red, veins=blue, ventricles=dark red)
- Individual part visibility control with multi-select interface
- Smooth rendering with proper lighting and materials

#### 2. **Dual Clipping Modes**

**Simple Clipping** (for 3D Models):
- ✂️ Independent X, Y, Z axis planes
- Real-time slice position control (0-100%)
- Multiple plane intersection support
- Perfect for exploring internal structures

**Interactive MPR Planes** (for CT Data):
- 🖼️ Real-time CT slice visualization
- Sagittal, Coronal, and Axial views
- Window/Level adjustment
- Synchronized with 3D view
- Proper texture mapping with optimal contrast

#### 3. **Integrated MPR Viewer**
- 📊 Professional 2×2 grid layout (Axial, Coronal, Sagittal, Curved MPR)
- Interactive crosshair navigation
- Synchronized slice positions across all views
- Window/Level controls per view
- **Curved MPR**: Draw custom paths on any slice to extract curved reformations
- **Cine Mode**: Automatic slice scrolling animation
- Click-to-navigate: Click on any view to jump to that anatomical position

---

### 🧭 **Navigation Techniques**

#### 1. **Manual Opacity Control**
- 🎯 Multi-select parts to make transparent
- Independent opacity slider (0-100%)
- Reverse logic: Selected parts become transparent, others stay opaque
- Real-time visual feedback
- Perfect for studying overlapping structures

#### 2. **Manual Path Fly-through**
- ✈️ Click directly on 3D model to place camera waypoints
- Automatic smooth path interpolation between points
- Visual markers show entry (green) and exit (red) points
- Adjustable speed (1-10)
- Perfect for custom anatomical exploration

#### 3. **Automatic Fly-through**
- 🚁 Predefined anatomical paths (e.g., "Coronary Artery", "Cerebral Arteries")
- Cinematic camera movements
- Organ-specific trajectories
- Educational demonstration mode

---

### 🎬 **Advanced Animations**

#### 1. **Realistic Blood Flow** 💉
- 50+ glowing particles with color gradients (deep crimson → red → orange → yellow)
- Heartbeat-synchronized pulsation (75 BPM)
- Semi-transparent vessel tubes
- Motion blur effect for realism
- **Two Modes**:
  - **Automatic**: Predefined anatomical paths (Aorta, Pulmonary Artery, etc.)
  - **Manual**: Use your own picked points from the Navigation tab

#### 2. **Organ Deformation** 💗
- Realistic heartbeat contraction/expansion
- Scale-based deformation (no position drift)
- Synchronized with blood flow
- Separate standalone contraction mode

#### 3. **Electrical Signals** ⚡
- Yellow particle propagation
- Follows neural/cardiac conduction pathways
- Adjustable speed (1-10)

---

### 📦 **Data Loading Capabilities**

#### **3D Model Files** (OBJ/STL)
- Load entire folders at once
- Automatic color assignment by anatomical structure
- Supports both ASCII and binary formats
- Part name detection from filenames

#### **Medical Imaging** (NIfTI)
- **CT Scans**: `.nii`, `.nii.gz`
- **Segmentation Files**: 
  - Single file: Multiple labels in one NIfTI
  - Folder: One file per anatomical structure
- Automatic 3D surface generation from segmentation
- Morphological cleaning (hole filling, noise removal)
- Advanced marching cubes with smoothing

---

## 🏗️ System Architecture

```
medical_visualization/
│
├── main.py                          # Application entry point
├── config.py                        # Color coding & organ configurations
├── model_loader.py                  # File I/O and 3D model generation
│
├── gui/
│   ├── __init__.py
│   └── main_window.py               # Main GUI (700+ lines)
│
├── visualization/
│   ├── __init__.py
│   ├── unified_visualization.py     # Clipping + MPR managers
│   └── integrated_mpr_ct_viewer.py  # Professional MPR viewer
│
└── navigation/
    ├── __init__.py
    ├── unified_navigation.py        # Focus + Flythrough managers
    └── animations.py                # Blood flow + organ deformation
```

**Design Pattern**: Manager-based architecture with clear separation of concerns

---

## 💻 Installation

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 4 GB | 8 GB+ |
| **GPU** | Integrated | Dedicated with OpenGL 3.2+ |
| **OS** | Windows 10, macOS 10.14, Ubuntu 18.04 | Latest versions |

### **Step 1: Install Dependencies**

```bash
pip install PyQt5 vtk numpy SimpleITK scipy matplotlib
```

**Package Breakdown**:
- **PyQt5** (>=5.15.0): GUI framework
- **VTK** (>=9.0.0): 3D visualization engine
- **NumPy** (>=1.20.0): Numerical computing
- **SimpleITK** (>=2.0.0): Medical image I/O
- **SciPy** (optional): Advanced mask cleaning
- **Matplotlib** (>=3.0.0): MPR slice visualization

### **Step 2: Verify Installation**

```python
python -c "import PyQt5, vtk, numpy, SimpleITK, matplotlib; print('✅ All packages installed')"
```

### **Step 3: Run the Application**

```bash
python main.py
```

---

## 🚀 Quick Start Guide

### **Scenario 1: Loading 3D Models (OBJ/STL)**

```
1. Select Anatomical System → "🫀 Cardiovascular System (Heart)"
2. Choose Data Type → "📦 3D Model Files (OBJ/STL)"
3. Click "📂 Load OBJ/STL Folder"
4. Browse to your folder containing .obj or .stl files
5. ✅ Models load with automatic anatomical coloring
```

**Example File Structure**:
```
heart_models/
├── left_ventricle.obj
├── right_ventricle.obj
├── aorta.obj
├── left_atrium.obj
└── right_atrium.obj
```

---

### **Scenario 2: CT Scan with Segmentation**

```
1. Select System → "🧠 Nervous System (Brain)"
2. Choose Data Type → "🏥 CT Scan (NIfTI)"
3. Click "📂 Load CT NIfTI File"
4. Select your CT scan (e.g., brain_ct.nii.gz)
5. Click "📂 Load Segmentation NIfTI"
6. Select segmentation file (e.g., brain_seg.nii.gz)
7. Click "🔨 Create 3D from Segmentation"
8. Wait for progress bar to complete
9. ✅ 3D models appear with unique colors
```

**Expected Processing Time**:
- 10 regions: ~30 seconds
- 50 regions: ~2 minutes
- 100+ regions: ~5 minutes

---

### **Scenario 3: Interactive MPR Exploration**

```
1. Load CT scan (as in Scenario 2)
2. Switch to "Visualization" tab
3. Select "Clipping Mode" → "Interactive MPR Planes (CT Slices)"
4. Enable planes:
   ☑ Show Sagittal (X)
   ☑ Show Coronal (Y)
   ☑ Show Axial (Z)
5. Use sliders to navigate through slices
6. Switch to "MPR View" tab for detailed 2D analysis
```

---

### **Scenario 4: Manual Fly-through with Blood Flow**

```
1. Load 3D models (Scenario 1 or 2)
2. Go to "Navigation" tab
3. Click "🖱️ Start Picking Points"
4. Click 5-10 points on the model to define camera path
5. Click "🛑 Stop Picking"
6. Go to "Animations" tab
7. Select "Flow Mode" → "Manual Path (Use Picked Points)"
8. Set "Animation Speed" → 7
9. Click "▶️ Start Blood Flow"
10. Watch realistic blood flowing along your custom path!
```

---

## 📚 Detailed Feature Documentation

### **Anatomical Color Coding System**

The system uses **intelligent keyword-based coloring** for anatomical accuracy:

| Structure Type | Color | Example Parts |
|---------------|-------|---------------|
| **Ventricles** | Dark Red (0.85, 0.15, 0.15) | Left Ventricle, Right Ventricle |
| **Atria** | Light Red/Pink (0.90, 0.35, 0.35) | Left Atrium, Right Atrium |
| **Aorta** | Bright Red (1.0, 0.2, 0.2) | Aorta, Aortic Arch |
| **Arteries** | Red/Orange (1.0, 0.4, 0.3) | Coronary Arteries, Cerebral Arteries |
| **Veins** | Blue (0.3, 0.4, 0.9) | Vena Cava, Pulmonary Veins |
| **Valves** | Yellow/Gold (0.95, 0.85, 0.5) | Mitral, Tricuspid, Aortic Valve |
| **Brain Lobes** | Vibrant Colors | Frontal (Red), Parietal (Green), Temporal (Blue), Occipital (Yellow) |
| **Teeth** | White Shades (0.96, 0.96, 0.92) | Incisors, Molars, Enamel |

**Fallback**: If no anatomical keyword matches, the system uses **HSV color distribution** for maximum visual distinction.

---

### **Mouse Controls**

| Action | Control |
|--------|---------|
| **Rotate View** | Left-click + drag |
| **Pan View** | Right-click + drag |
| **Zoom In/Out** | Scroll wheel |
| **Pick Point** | Left-click (when point picking is enabled) |
| **Navigate MPR** | Left-click on any slice view |

---

### **Blood Flow Animation Details**

**Visual Components**:
- **Particles**: 50 spheres (radius 1.5 units)
- **Vessel Tube**: Semi-transparent (15% opacity, radius 2.0)
- **Entry Marker**: Green sphere (radius 2.5)
- **Exit Marker**: Red sphere (radius 2.5)

**Color Gradient** (simulates oxygenation):
```
Progress   Color          Meaning
0.0-0.4    Deep Crimson   Deoxygenated blood
0.4-0.7    Bright Red     Mixed blood
0.7-1.0    Yellow-Orange  Oxygenated blood
```

**Physics**:
- Base speed: 0.4 units/frame × slider value (1-10)
- Heartbeat modulation: ±30% using sine wave (75 BPM)
- Jitter: Gaussian noise (σ=0.02) for realistic wobble

---

### **MPR Curved Reformation Algorithm**

```python
# User draws curve on any MPR slice
# System performs:
1. Curve Interpolation:
   - Input: N user points
   - Output: 200-300 smooth points (cubic spline)
   
2. Perpendicular Slice Extraction:
   - For each curve point:
     * Calculate tangent vector (curve direction)
     * Generate orthonormal basis (perpendicular directions)
     * Sample 80 points perpendicular to curve
     * Use trilinear interpolation for smooth values
   
3. Straightened View Generation:
   - Stack all perpendicular slices horizontally
   - Each slice becomes one vertical column
   - Result: "Unrolled" view of curved anatomy
   
4. 3D Visualization:
   - Create yellow tube along curve path
   - Add red spheres at sample points (every 10th)
   - Render in 3D view for spatial context
```

---

## 📊 Supported Data Formats

### **3D Model Files**

| Format | Extension | Notes |
|--------|-----------|-------|
| **Wavefront OBJ** | `.obj` | ASCII or binary, with/without normals |
| **STL (Stereolithography)** | `.stl` | ASCII or binary |

**Naming Convention** (for automatic color detection):
- Use descriptive names: `left_ventricle.obj` ✅
- Avoid generic names: `part1.obj` ❌
- Underscores/hyphens/spaces work: `Left-Ventricle.obj` ✅

---

### **Medical Imaging Files**

| Format | Extension | Use Case |
|--------|-----------|----------|
| **NIfTI** | `.nii` | Uncompressed CT/MRI scans |
| **NIfTI Compressed** | `.nii.gz` | Compressed (recommended for large files) |

**Segmentation Types**:

1. **Single File** (Multi-label):
```
brain_segmentation.nii.gz
├── Label 0: Background
├── Label 1: Gray Matter
├── Label 2: White Matter
├── Label 3: Cerebellum
└── Label 4: Brainstem
```

2. **Folder** (One file per structure):
```
brain_segmentation_folder/
├── Gray_Matter.nii.gz
├── White_Matter.nii.gz
├── Cerebellum.nii.gz
└── Brainstem.nii.gz
```

**System automatically**:
- Detects label values
- Assigns colors based on part names
- Generates smooth 3D surfaces
- Cleans meshes (fills holes, removes noise)

---

## 🔧 Technical Specifications

### **3D Surface Generation Pipeline**

```python
Segmentation Mask (Binary Array)
    ↓
[Morphological Cleaning]
- Binary fill holes (SciPy)
- Remove small objects
- Keep largest connected component
    ↓
[Gaussian Smoothing] (σ=1.0, radius=1.5)
    ↓
[Marching Cubes] (threshold=0.3)
    ↓
[Mesh Processing]
- Clean polydata (remove duplicates)
- Fill holes (max hole size: 10.0)
- Smooth (20 iterations, λ=0.15)
- Generate normals (consistent orientation)
- Decimate (30% reduction, preserve topology)
    ↓
High-Quality 3D Surface
```

---

### **Rendering Specifications**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Background Color** | (0.15, 0.15, 0.20) | Dark blue-gray (easy on eyes) |
| **Diffuse Lighting** | 1.0 | Show true anatomical colors |
| **Specular Lighting** | 0.0 | Disable glare (was causing color washing) |
| **Ambient Lighting** | 0.3 | Gentle fill light |
| **Anti-aliasing** | Enabled (8× MSAA) | Smooth edges |
| **Depth Peeling** | 4 layers | Proper transparency |

---

## ⚠️ Troubleshooting

### **Problem: "Failed to load OBJ models"**

**Possible Causes & Solutions**:
1. ❌ **Empty folder** → Ensure folder contains `.obj` or `.stl` files
2. ❌ **Corrupted files** → Open files in Blender/MeshLab to verify
3. ❌ **No geometry** → Check file size (should be > 1KB)
4. ❌ **Wrong format** → Only OBJ and STL are supported

---

### **Problem: "Segmentation dimensions mismatch"**

**Error Message**: `"Shape mismatch: CT is (512, 512, 200), Segmentation is (256, 256, 200)"`

**Solution**:
```python
# Use resampling tools like SimpleITK
import SimpleITK as sitk

seg = sitk.ReadImage('segmentation.nii.gz')
ct = sitk.ReadImage('ct_scan.nii.gz')

# Resample segmentation to match CT
resampler = sitk.ResampleImageFilter()
resampler.SetReferenceImage(ct)
resampler.SetInterpolator(sitk.sitkNearestNeighbor)
seg_resampled = resampler.Execute(seg)
sitk.WriteImage(seg_resampled, 'segmentation_resampled.nii.gz')
```

---

### **Problem: "MPR planes not showing"**

**Checklist**:
1. ✅ Load CT scan first (`📂 Load CT NIfTI File`)
2. ✅ Select "Interactive MPR Planes" mode (not "Simple Clipping")
3. ✅ Enable at least one plane checkbox
4. ✅ Adjust sliders (default 50% might be outside data range)
5. ✅ Check console for errors

**Debug Output**:
```
[MPRManager] Creating plane widgets...
[MPRManager] ✅ Plane widgets created with texture mapping
[Main] Updating MPR x plane: enabled=True, position=50%
```

If you don't see this, check that `model_loader.ct_image` is not `None`.

---

### **Problem: "Blood flow particles not visible"**

**Fixes**:
1. **Increase particle size**: Edit `animations.py` line 50:
   ```python
   self.PARTICLE_RADIUS = 3.0  # Increase from 1.5
   ```
2. **Check opacity**: Particles should be opaque (1.0)
3. **Verify path creation**: Look for green/red entry/exit markers
4. **Try manual path**: Use point picking for better control

---

### **Problem: "Application crashes with large CT scans"**

**Memory Management**:
```python
# For 1024×1024×500 CT (500MB+):
1. Close other applications
2. Use compressed NIfTI (.nii.gz)
3. Consider downsampling:

import SimpleITK as sitk
img = sitk.ReadImage('large_ct.nii.gz')
img_downsampled = sitk.Shrink(img, [2, 2, 2])  # Reduce by 50%
sitk.WriteImage(img_downsampled, 'ct_smaller.nii.gz')
```

---

## 🚀 Performance Tips

### **For Large CT Scans** (>512³)
1. **Use Compression**: `.nii.gz` saves 60-80% space
2. **Load Progressively**: Load one slice plane at a time
3. **Reduce Resolution**: Downsample before loading
4. **Increase Swap Space**: Allows virtual memory usage

---

### **For Many 3D Models** (>100 parts)
1. **Hide Unused Parts**: Use visibility list to show only relevant structures
2. **Reduce Polygon Count**: Use decimation (30% reduction)
3. **Disable Animations**: Stop blood flow when exploring static structures
4. **Batch Loading**: Load models in groups rather than all at once

---

### **For Smooth Rendering**
1. **Dedicated GPU**: Discrete graphics card vastly improves performance
2. **Update Drivers**: Latest OpenGL drivers are critical
3. **Close Background Apps**: Free up GPU resources
4. **Reduce Anti-aliasing**: If FPS drops, disable MSAA in VTK settings

---

## 🖼️ Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────────┐
│  🏥 Medical Visualization  │  3D View  │  MPR View  │
├────────────┬────────────────────────────────────────────┤
│  📊 Data   │                                            │
│  Loading   │           3D Viewer                        │
│            │         (VTK OpenGL)                       │
│  🎨 Visual │                                            │
│  ization   │                                            │
│            │         ┌─────────────────────┐           │
│  🧭 Naviga │         │  Rotating 3D Model  │           │
│  tion      │         │  with Clipping      │           │
│            │         └─────────────────────┘           │
│  ▶️ Anima  │                                            │
│  tions     │         Blood Flow Particles               │
│            │         with Heartbeat                     │
└────────────┴────────────────────────────────────────────┘
```

### MPR Viewer
```
┌──────────────┬──────────────┐
│   Axial      │   Coronal    │
│   (Top)      │   (Front)    │
│              │              │
│   🔴━━━━     │   🟢         │
│   ┃          │   ┃          │
│   🟢         │   🔴━━━━     │
├──────────────┼──────────────┤
│  Sagittal    │ Curved MPR   │
│  (Side)      │ (Unrolled)   │
│              │              │
│   🔴         │  ────────    │
│   ┃          │ ╱╲╱╲╱╲╱╲╱   │
│   🟢━━━━     │ ────────     │
└──────────────┴──────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

### **High Priority**
- [ ] DICOM series support
- [ ] Volume rendering for CT
- [ ] Real-time segmentation editing
- [ ] Multi-user collaboration

### **Medium Priority**
- [ ] Measurement tools (distance, angle, volume)
- [ ] Annotation system with text labels
- [ ] Export capabilities (screenshots, videos, 3D models)
- [ ] Batch processing for multiple datasets

### **Nice to Have**
- [ ] VR/AR integration
- [ ] Cloud storage integration
- [ ] Machine learning-based auto-segmentation
- [ ] Multi-language support

**How to Contribute**:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is for **educational use** only.

**Developed for**: Medical Visualization Course, Fall 2025  
**Framework**: VTK + PyQt5  
**Medical I/O**: SimpleITK

---

## 🎓 Educational Use Cases

### **Medical School**
- **Anatomy Lab**: Explore 3D models before/after cadaver dissection
- **Radiology Training**: Practice identifying structures on CT/MRI
- **Surgery Planning**: Visualize surgical approach with fly-through

### **Research**
- **Data Visualization**: Publish-quality 3D renderings
- **Algorithm Development**: Test segmentation algorithms
- **Comparative Anatomy**: Study multiple specimens side-by-side

### **Patient Education**
- **Pre-operative Consultation**: Show surgical plan to patients
- **Diagnosis Explanation**: Visualize pathology location
- **Treatment Planning**: Demonstrate treatment approach

---

## 📞 Support & Documentation

### **Getting Help**
1. **Console Output**: Check terminal for detailed error messages
2. **Status Bar**: Bottom of control panel shows current operation status
3. **Message Boxes**: Pop-ups provide specific error descriptions

### **Useful Resources**
- **VTK Documentation**: https://vtk.org/documentation/
- **PyQt5 Tutorial**: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **SimpleITK Guide**: https://simpleitk.readthedocs.io/

---

## 🏆 Acknowledgments

**Built with**:
- VTK (Visualization Toolkit) - 3D rendering engine
- PyQt5 - GUI framework
- SimpleITK - Medical image processing
- NumPy - Numerical operations
- Matplotlib - 2D plotting for MPR

**Special Thanks**:
- Medical Visualization Course Instructors
- VTK Community for extensive documentation
- Open-source medical imaging community

---

## 📊 Project Statistics

- **Total Lines of Code**: ~5,000+
- **Main Files**: 11
- **Supported Anatomical Systems**: 4
- **Visualization Modes**: 3
- **Navigation Techniques**: 3
- **Animation Types**: 3
- **Color Definitions**: 100+
- **Development Time**: Fall 2025

---

<div align="center">

### ⭐ Star this repository if it helped your medical visualization project! ⭐

Made with ❤️ for the medical imaging community

</div>
