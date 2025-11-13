"""
Automatic Dependency Installer for 3D Medical Visualization System
Run this script to install all required packages
"""

import subprocess
import sys

def install_package(package_name):
    """Install a package using pip"""
    print(f"\n{'='*60}")
    print(f"Installing {package_name}...")
    print(f"{'='*60}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package_name}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is already installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} is already installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False

def main():
    """Main installation function"""
    print("\n" + "="*60)
    print("3D Medical Visualization System - Dependency Installer")
    print("="*60 + "\n")
    
    packages = [
        ("PyQt5", "PyQt5"),
        ("vtk", "vtk"),
        ("numpy", "numpy"),
        ("SimpleITK", "SimpleITK")
    ]
    
    # Check current status
    print("Checking current installation status...\n")
    to_install = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            to_install.append(package_name)
    
    # Install missing packages
    if to_install:
        print(f"\n{'='*60}")
        print(f"Need to install: {', '.join(to_install)}")
        print(f"{'='*60}\n")
        
        user_input = input("Proceed with installation? (y/n): ")
        
        if user_input.lower() == 'y':
            failed = []
            for package in to_install:
                if not install_package(package):
                    failed.append(package)
            
            print(f"\n{'='*60}")
            if failed:
                print("Installation completed with errors:")
                print(f"Failed packages: {', '.join(failed)}")
                print("\nPlease install these manually:")
                for pkg in failed:
                    print(f"  pip install {pkg}")
            else:
                print("✓ All packages installed successfully!")
                print("\nYou can now run the application:")
                print("  python main.py")
            print(f"{'='*60}\n")
        else:
            print("\nInstallation cancelled.")
    else:
        print(f"\n{'='*60}")
        print("✓ All required packages are already installed!")
        print("\nYou can run the application:")
        print("  python main.py")
        print(f"{'='*60}\n")
    
    # Verify installation
    print("Verifying installation...\n")
    all_ok = True
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False
    
    if all_ok:
        print("\n✓ Installation verification successful!")
        print("\n" + "="*60)
        print("🎉 Ready to use! Run: python main.py")
        print("="*60 + "\n")
    else:
        print("\n✗ Some packages are still missing.")
        print("Please install them manually and try again.")

if __name__ == "__main__":
    main()