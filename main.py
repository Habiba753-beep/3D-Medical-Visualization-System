"""
3D Medical Visualization System - Main Entry Point
Task 3: 4×3×3 Implementation

Author: Medical Visualization Project
Date: Fall 2025

Features:
- 4 Anatomical Systems (Cardiovascular, Nervous, Musculoskeletal, Dental)
- 3 Visualization Methods (Surface Rendering, Clipping Planes, Curved MPR)
- 3 Navigation Techniques (Focus, Moving Stuff, Fly-through)

Usage:
1. Install dependencies: pip install PyQt5 vtk numpy
2. Ensure proper directory structure (see README)
3. Run: python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MedicalVisualizationWindow


def main():
    """Main entry point for the medical visualization system"""
    print("=" * 80)
    print("3D Medical Visualization System - Task 3 (4×3×3)")
    print("=" * 80)
    print("\nFeatures:")
    print("  - 4 Anatomical Systems: Heart, Brain, Muscles, Teeth")
    print("  - 3 Visualization Methods: Surface, Clipping, Curved MPR")
    print("  - 3 Navigation Techniques: Focus, Animations, Fly-through")
    print("=" * 80)
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Medical 3D Visualization System")
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MedicalVisualizationWindow()
    window.showMaximized()
    
    print("\nApplication launched successfully!")
    print("  -> Select an anatomical system from the dropdown to begin\n")
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()