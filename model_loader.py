"""
Enhanced Model Loader with Segmentation Folder Support
Supports: OBJ files, CT NIfTI data, single segmentation file, and segmentation folders
"""

import vtk
import os
import numpy as np
from pathlib import Path
# After line 10 (after "from pathlib import Path")
try:
    from vtkmodules.util import numpy_support
    NUMPY_SUPPORT_AVAILABLE = True
except ImportError:
    NUMPY_SUPPORT_AVAILABLE = False
try:
    import SimpleITK as sitk
    SITK_AVAILABLE = True
except ImportError:
    SITK_AVAILABLE = False
    print("Warning: SimpleITK not available. CT/NIfTI support disabled.")

try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: SciPy not available. Advanced mask cleaning disabled.")

from config import get_color_for_part, get_color_for_label

def _clean_part_name(filename):
    """
    Utility to remove common NIfTI file extensions from a filename
    to get the clean anatomical part name. (e.g., 'Vermis.nii.gz' -> 'Vermis')
    """
    # Get the file name part
    name = Path(filename).name
    
    # 1. Remove .nii.gz first
    if name.endswith('.nii.gz'):
        name = name[:-7]
    # 2. Remove .nii second
    elif name.endswith('.nii'):
        name = name[:-4]
    
    # After removing extensions, Path.stem is used in the caller, 
    # but we return the cleaned name here just to ensure
    return name

    

class ModelLoader:
    """Loads 3D models from user-uploaded data with folder support"""
    
    def __init__(self):
        """Initialize model loader"""
        self.loaded_models = {}
        self.ct_image = None
        self.ct_image_data = None
        self.segmentation_data = None
        self.current_data_type = None
        self.unique_labels = []
        self.segmentation_files = {}  # Store individual segmentation files
        
    def load_obj_folder(self, folder_path, organ_type):
        """Load OBJ/STL files from user-selected folder"""
        print(f"\n{'='*70}")
        print(f"Loading OBJ files from: {folder_path}")
        print(f"{'='*70}")
        
        if not os.path.exists(folder_path):
            print("Error: Folder does not exist!")
            return None
        
        folder = Path(folder_path)
        
        # Find all 3D model files (case insensitive)
        model_files = []
        for ext in ['*.obj', '*.OBJ', '*.stl', '*.STL']:
            model_files.extend(list(folder.glob(ext)))
        
        if not model_files:
            print("No OBJ/STL files found in folder!")
            return None
        
        print(f"Found {len(model_files)} model files")
        
        models = {}
        loaded_count = 0
        failed_count = 0
        
        for model_file in model_files:
            part_name = model_file.stem
            print(f"  Loading: {part_name}...", end=" ")
            
            try:
                polydata = self.load_model_file(str(model_file))
                
                if polydata and polydata.GetNumberOfPoints() > 0:
                    models[part_name] = polydata
                    loaded_count += 1
                    print(f"OK ({polydata.GetNumberOfPoints()} points)")
                else:
                    failed_count += 1
                    print(f"FAILED (No data)")
            except Exception as e:
                failed_count += 1
                print(f"FAILED Error: {e}")
        
        print(f"{'='*70}")
        print(f"Successfully loaded {loaded_count} parts")
        if failed_count > 0:
            print(f"Failed to load {failed_count} files")
        print(f"{'='*70}\n")
        
        self.loaded_models = models
        self.current_data_type = 'obj'
        return models if models else None
    
    def load_ct_nifti(self, ct_file_path, organ_type):
        """Load CT scan from NIfTI file"""
        if not SITK_AVAILABLE:
            print("SimpleITK not available! Cannot load NIfTI files.")
            print("   Install with: pip install SimpleITK")
            return None
        
        try:
            print(f"\n{'='*70}")
            print(f"Loading CT NIfTI: {ct_file_path}")
            print(f"{'='*70}")
            
            if not os.path.exists(ct_file_path):
                print(f"File not found: {ct_file_path}")
                return None
            
            print("  Reading NIfTI file...")
            ct_image = sitk.ReadImage(ct_file_path)
            ct_array = sitk.GetArrayFromImage(ct_image)
            
            print(f"  CT loaded successfully")
            print(f"    Shape: {ct_array.shape}")
            print(f"    Spacing: {ct_image.GetSpacing()}")
            print(f"    Origin: {ct_image.GetOrigin()}")
            print(f"    Data range: [{ct_array.min()}, {ct_array.max()}]")
            
            self.ct_image = ct_image
            self.ct_image_data = ct_array
            self.current_data_type = 'ct'
            
            print(f"CT loaded and ready")
            print(f"{'='*70}\n")
            
            return ct_image
            
        except Exception as e:
            print(f"Failed to load CT: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_segmentation_nifti(self, seg_file_path, organ_type):
        """Load segmentation mask from single NIfTI file"""
        if not SITK_AVAILABLE:
            print("SimpleITK not available! Cannot load NIfTI files.")
            return None
        
        try:
            print(f"\n{'='*70}")
            print(f"Loading Segmentation: {seg_file_path}")
            print(f"{'='*70}")
            
            if not os.path.exists(seg_file_path):
                print(f"File not found: {seg_file_path}")
                return None
            
            print("  Reading segmentation file...")
            seg_image = sitk.ReadImage(seg_file_path)
            seg_array = sitk.GetArrayFromImage(seg_image)
            
            print(f"  Segmentation loaded")
            print(f"    Shape: {seg_array.shape}")
            
            # Get unique labels (excluding background = 0)
            unique_labels = np.unique(seg_array)
            unique_labels = unique_labels[unique_labels > 0]
            
            print(f"    Unique labels: {unique_labels}")
            print(f"    Number of regions: {len(unique_labels)}")
            
            self.segmentation_data = seg_array
            self.unique_labels = unique_labels
            self.segmentation_files = {}  # Clear folder data
            
            print(f"Segmentation ready for 3D model creation")
            print(f"{'='*70}\n")
            
            return seg_array
            
        except Exception as e:
            print(f"Failed to load segmentation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_segmentation_folder(self, folder_path, organ_type):
        """Load segmentation from folder with multiple NIfTI files"""
        if not SITK_AVAILABLE:
            print("SimpleITK not available! Cannot load NIfTI files.")
            return None
        
        try:
            print(f"\n{'='*70}")
            print(f"Loading Segmentation Folder: {folder_path}")
            print(f"{'='*70}")
            
            if not os.path.exists(folder_path):
                print(f"Folder not found: {folder_path}")
                return None
            
            folder = Path(folder_path)
            
            # Find all NIfTI files
            seg_files = []
            for ext in ['*.nii', '*.nii.gz']:
                seg_files.extend(list(folder.glob(ext)))
            
            if not seg_files:
                print("No NIfTI files found in folder!")
                return None
            
            print(f"  Found {len(seg_files)} segmentation files")
            
            # Get dimensions from CT if available
            if self.ct_image_data is not None:
                combined_shape = self.ct_image_data.shape
            else:
                # Use first file to determine shape
                first_image = sitk.ReadImage(str(seg_files[0]))
                first_array = sitk.GetArrayFromImage(first_image)
                combined_shape = first_array.shape
            
            # Initialize combined segmentation array
            combined_seg = np.zeros(combined_shape, dtype=np.uint16)
            
            loaded_files = {}
            current_label = 1
            
            print("\n  Loading individual segmentation files:")
            
            for i, seg_file in enumerate(seg_files):
                try:
                    print(f"    [{i+1}/{len(seg_files)}] {seg_file.name}...", end=" ")
                    
                    seg_image = sitk.ReadImage(str(seg_file))
                    seg_array = sitk.GetArrayFromImage(seg_image)
                    
                    # Check dimensions match
                    if seg_array.shape != combined_shape:
                        print(f"SKIPPED (shape mismatch: {seg_array.shape} vs {combined_shape})")
                        continue
                    
                    # Get mask (non-zero values)
                    mask = seg_array > 0
                    
                    if mask.sum() == 0:
                        print("SKIPPED (empty mask)")
                        continue
                    
                    # Assign new label to this segmentation
                    combined_seg[mask] = current_label
                    
                    # Store file information
                    loaded_files[current_label] = {
                        'filename': seg_file.name,
                        'original_labels': np.unique(seg_array[mask]),
                        'voxel_count': mask.sum()
                    }
                    
                    print(f"OK (label {current_label}, {mask.sum()} voxels)")
                    current_label += 1
                    
                except Exception as e:
                    print(f"FAILED: {e}")
                    continue
            
            if current_label == 1:
                print("\n  No valid segmentation files loaded!")
                return None
            
            # Get unique labels
            unique_labels = np.unique(combined_seg)
            unique_labels = unique_labels[unique_labels > 0]
            
            print(f"\n{'='*70}")
            print(f"  Successfully combined {len(loaded_files)} segmentation files")
            print(f"  Total unique regions: {len(unique_labels)}")
            print(f"\n  Label assignments:")
            for label_id, info in loaded_files.items():
                print(f"    Label {label_id}: {info['filename']} ({info['voxel_count']} voxels)")
            print(f"{'='*70}\n")
            
            self.segmentation_data = combined_seg
            self.unique_labels = unique_labels
            self.segmentation_files = loaded_files
            
            return combined_seg
            
        except Exception as e:
            print(f"Failed to load segmentation folder: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_models_from_segmentation(self, organ_type, progress_callback=None):
        """Create 3D surface models from segmentation labels"""
        if self.segmentation_data is None:
            print("Error: No segmentation data loaded")
            return None
        
        print(f"\n{'='*70}")
        print(f"Creating 3D Models from Segmentation")
        print(f"{'='*70}")
        
        models = {}
        
        for i, label_value in enumerate(self.unique_labels):
            # Create part name based on whether from folder or file
            if self.segmentation_files and label_value in self.segmentation_files:
                file_info = self.segmentation_files[label_value]
                # 💡 استخدام الدالة الجديدة للحصول على اسم الجزء النظيف
                part_name = _clean_part_name(file_info['filename']) 
            else:
                part_name = f"Region_{int(label_value)}"
            
            print(f"  [{i+1}/{len(self.unique_labels)}] Creating: {part_name}...", end=" ")
            
            if progress_callback:
                progress_callback(i)
            
            try:
                # Create binary mask for this label
                binary_mask = (self.segmentation_data == label_value).astype(np.uint8)
                
                # Check if mask has data
                voxel_count = binary_mask.sum()
                if voxel_count == 0:
                    print(f"FAILED (Empty mask)")
                    continue
                
                # Skip very small regions (likely noise)
                if voxel_count < 50:
                    print(f"SKIPPED (Too small: {voxel_count} voxels)")
                    continue
                
                print(f"({voxel_count} voxels) ", end="")
                
                # Apply morphological operations to clean the mask (if scipy available)
                if SCIPY_AVAILABLE:
                    # Fill small holes
                    binary_mask = ndimage.binary_fill_holes(binary_mask).astype(np.uint8)
                    
                    # Remove small objects (noise)
                    labeled, num_features = ndimage.label(binary_mask)
                    if num_features > 1:
                        # Keep only the largest connected component
                        sizes = ndimage.sum(binary_mask, labeled, range(num_features + 1))
                        max_label = sizes.argmax()
                        binary_mask = (labeled == max_label).astype(np.uint8)
                    
                    print("cleaned ", end="")
                
                # Convert to VTK image
                vtk_image = self._numpy_to_vtk_image(binary_mask)
                
                # Apply spacing if CT image is available
                if self.ct_image is not None:
                    spacing = self.ct_image.GetSpacing()
                    origin = self.ct_image.GetOrigin()
                    vtk_image.SetSpacing(spacing)
                    vtk_image.SetOrigin(origin)
                else:
                    # Use uniform spacing if no CT
                    vtk_image.SetSpacing(1.0, 1.0, 1.0)
                    vtk_image.SetOrigin(0.0, 0.0, 0.0)
                
                # Apply Gaussian smoothing to the volume first
                gaussian = vtk.vtkImageGaussianSmooth()
                gaussian.SetInputData(vtk_image)
                gaussian.SetStandardDeviations(1.0, 1.0, 1.0)
                gaussian.SetRadiusFactors(1.5, 1.5, 1.5)
                gaussian.Update()
                
                # Create surface mesh using marching cubes
                marching_cubes = vtk.vtkMarchingCubes()
                marching_cubes.SetInputConnection(gaussian.GetOutputPort())
                marching_cubes.SetValue(0, 0.3)  # Lower threshold for smoother results
                marching_cubes.ComputeNormalsOn()
                marching_cubes.ComputeGradientsOn()
                marching_cubes.Update()
                
                # Check if surface was created
                if marching_cubes.GetOutput().GetNumberOfPoints() == 0:
                    print(f"FAILED (No surface)")
                    continue
                
                # Clean the polydata to remove duplicate points
                cleaner = vtk.vtkCleanPolyData()
                cleaner.SetInputConnection(marching_cubes.GetOutputPort())
                cleaner.Update()
                
                # Fill holes in the mesh
                fill_holes = vtk.vtkFillHolesFilter()
                fill_holes.SetInputConnection(cleaner.GetOutputPort())
                fill_holes.SetHoleSize(10.0)
                fill_holes.Update()
                
                # Smooth the surface
                smoother = vtk.vtkSmoothPolyDataFilter()
                smoother.SetInputConnection(fill_holes.GetOutputPort())
                smoother.SetNumberOfIterations(20)
                smoother.SetRelaxationFactor(0.15)
                smoother.FeatureEdgeSmoothingOn()
                smoother.BoundarySmoothingOn()
                smoother.Update()
                
                # Generate normals for better rendering
                normals = vtk.vtkPolyDataNormals()
                normals.SetInputConnection(smoother.GetOutputPort())
                normals.ComputePointNormalsOn()
                normals.ComputeCellNormalsOff()
                normals.SplittingOff()
                normals.ConsistencyOn()
                normals.AutoOrientNormalsOn()
                normals.Update()
                
                # Decimate to reduce polygon count (optional, for large models)
                decimate = vtk.vtkDecimatePro()
                decimate.SetInputConnection(normals.GetOutputPort())
                decimate.SetTargetReduction(0.3)  # Reduce less to preserve quality
                decimate.PreserveTopologyOn()
                decimate.BoundaryVertexDeletionOff()
                decimate.Update()
                
                polydata = decimate.GetOutput()
                
                if polydata and polydata.GetNumberOfPoints() > 0:
                    models[part_name] = polydata
                    print(f"OK ({polydata.GetNumberOfPoints()} points, {polydata.GetNumberOfCells()} cells)")
                else:
                    print(f"FAILED (Invalid surface)")
                    
            except Exception as e:
                print(f"FAILED Error: {e}")
        
        if progress_callback:
            progress_callback(len(self.unique_labels))
        
        print(f"{'='*70}")
        print(f"Created {len(models)}/{len(self.unique_labels)} models from segmentation")
        print(f"{'='*70}\n")
        
        self.loaded_models = models
        self.current_data_type = 'ct'
        return models if models else None
    
    def get_ct_volume_actor(self):
        """Get VTK volume actor for CT data"""
        if self.ct_image is None or self.ct_image_data is None:
            return None
        
        try:
            vtk_image = self._numpy_to_vtk_image_scalar(self.ct_image_data)
            
            spacing = self.ct_image.GetSpacing()
            origin = self.ct_image.GetOrigin()
            vtk_image.SetSpacing(spacing)
            vtk_image.SetOrigin(origin)
            
            return vtk_image
            
        except Exception as e:
            print(f"Error converting CT to VTK: {e}")
            return None
    
    def _numpy_to_vtk_image(self, numpy_array):
        """Convert binary numpy array to VTK image with proper orientation"""
        # Ensure array is in the correct format
        numpy_array = numpy_array.astype(np.uint8)
        
        depth, height, width = numpy_array.shape
        
        # Create VTK image data
        vtk_data = vtk.vtkImageData()
        vtk_data.SetDimensions(width, height, depth)
        vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        
        # Convert numpy array to VTK format (needs to be transposed)
        # VTK uses Fortran ordering (column-major), numpy uses C ordering (row-major)
        flat_array = numpy_array.transpose(2, 1, 0).flatten('F')
        
        # Copy data to VTK
        vtk_array = vtk_data.GetPointData().GetScalars()
        for i, value in enumerate(flat_array):
            vtk_array.SetValue(i, int(value))
        
        vtk_data.Modified()
        return vtk_data
    
    def _numpy_to_vtk_image_scalar(self, numpy_array):
        """
        Convert a scalar NumPy array (like CT data) to a vtkImageData object.
        This version ensures the memory layout is correctly handled by transposing
        the array axes before passing the data to VTK.
        """
        # The NumPy array is loaded by SimpleITK in (Z, Y, X) order.
        # VTK expects the dimensions and data in (X, Y, Z) order.
        
        # 1. Transpose the array to re-order the axes from (Z, Y, X) to (X, Y, Z).
        transposed_array = numpy_array.transpose(2, 1, 0)
        
        if NUMPY_SUPPORT_AVAILABLE:
            # 2. Convert using numpy_support (much faster)
            vtk_array = numpy_support.numpy_to_vtk(
                num_array=transposed_array.ravel(order='F'),
                deep=True,
                array_type=vtk.VTK_SHORT
            )
            
            # 3. Create the vtkImageData object.
            vtk_data = vtk.vtkImageData()
            
            # 4. Set the dimensions using the transposed shape.
            vtk_data.SetDimensions(transposed_array.shape)
            
            # 5. Attach the VTK array to the vtkImageData object.
            vtk_data.GetPointData().SetScalars(vtk_array)
        else:
            # Fallback to manual method (slower but works)
            vtk_data = vtk.vtkImageData()
            depth, height, width = numpy_array.shape
            vtk_data.SetDimensions(width, height, depth)
            vtk_data.SetSpacing(1.0, 1.0, 1.0)
            vtk_data.SetOrigin(0.0, 0.0, 0.0)
            
            vtk_array = vtk.vtkShortArray()
            vtk_array.SetNumberOfComponents(1)
            vtk_array.SetName("ImageScalars")
            
            flat_array = numpy_array.transpose(2, 1, 0).flatten()
            
            for value in flat_array:
                vtk_array.InsertNextValue(int(value))
            
            vtk_data.GetPointData().SetScalars(vtk_array)
        
        print(f"[ModelLoader] Successfully converted NumPy array ({numpy_array.shape}) to vtkImageData")
        
        return vtk_data
    
    def load_model_file(self, filepath):
        """Load a single OBJ or STL file"""
        try:
            ext = Path(filepath).suffix.lower()
            
            if ext == '.obj':
                reader = vtk.vtkOBJReader()
                reader.SetFileName(filepath)
                reader.Update()
                
                output = reader.GetOutput()
                if output and output.GetNumberOfPoints() > 0:
                    return output
                else:
                    print(f"    Warning: OBJ file has no geometry")
                    return None
            
            elif ext == '.stl':
                reader = vtk.vtkSTLReader()
                reader.SetFileName(filepath)
                reader.Update()
                
                output = reader.GetOutput()
                if output and output.GetNumberOfPoints() > 0:
                    return output
                else:
                    print(f"    Warning: STL file has no geometry")
                    return None
            else:
                print(f"    Unsupported file format: {ext}")
                return None
                
        except Exception as e:
            print(f"    Error loading file: {e}")
            return None
    
    def has_segmentation(self):
        """Check if segmentation data is loaded"""
        return self.segmentation_data is not None
    
    def get_unique_labels(self):
        """Get unique labels from segmentation"""
        return self.unique_labels if self.unique_labels is not None else []
    
    def get_segmentation_info(self):
        """Get information about loaded segmentation"""
        if not self.segmentation_files:
            return None
        return self.segmentation_files
    
    def clear(self):
        """Clear all loaded data and reset internal state."""
        self.loaded_models.clear()
        self.ct_image = None
        self.ct_image_data = None
        self.segmentation_data = None
        self.current_data_type = None
        self.unique_labels = []
        self.segmentation_files = {}
        print("Model loader cleared")
