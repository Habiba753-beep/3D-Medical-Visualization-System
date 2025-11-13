"""
Enhanced Anatomical Color Coding System
Replaces config.py with intelligent keyword-based coloring
"""

import colorsys

# Background color for VTK renderer (dark blue-gray)
BACKGROUND_COLOR = (0.15, 0.15, 0.20)

# ========== ANATOMICAL COLOR MAPPING ==========
# Each organ system has color rules based on keywords in part names

ANATOMICAL_COLOR_RULES = {
    'heart': {
        # PRIORITY ORDER: Most specific keywords first
        'keywords': [
            # Ventricles - Dark Red
            ('left_ventricle', (0.85, 0.15, 0.15)),
            ('right_ventricle', (0.80, 0.20, 0.20)),
            ('ventricle', (0.82, 0.18, 0.18)),
            ('lv', (0.85, 0.15, 0.15)),
            ('rv', (0.80, 0.20, 0.20)),
            
            # Atria - Light Red/Pink
            ('left_atrium', (0.90, 0.35, 0.35)),
            ('right_atrium', (0.88, 0.38, 0.38)),
            ('atrium', (0.89, 0.36, 0.36)),
            ('la', (0.90, 0.35, 0.35)),
            ('ra', (0.88, 0.38, 0.38)),
            
            # Aorta - Bright Red
            ('aorta', (1.0, 0.2, 0.2)),
            ('aortic', (0.98, 0.25, 0.25)),
            
            # Arteries - Red/Orange
            ('pulmonary_artery', (0.95, 0.4, 0.5)),
            ('coronary', (1.0, 0.5, 0.2)),
            ('artery', (1.0, 0.4, 0.3)),
            ('arterial', (0.98, 0.42, 0.32)),
            
            # Veins - Blue
            ('vena_cava', (0.3, 0.4, 0.9)),
            ('pulmonary_vein', (0.4, 0.45, 0.95)),
            ('vein', (0.35, 0.42, 0.92)),
            ('venous', (0.38, 0.43, 0.90)),
            
            # Valves - Yellow/Gold
            ('mitral', (0.95, 0.85, 0.5)),
            ('tricuspid', (0.92, 0.82, 0.45)),
            ('aortic_valve', (0.90, 0.80, 0.40)),
            ('pulmonary_valve', (0.88, 0.78, 0.42)),
            ('valve', (0.91, 0.81, 0.44)),
            
            # Heart structures
            ('myocardium', (0.70, 0.15, 0.15)),
            ('endocardium', (0.85, 0.25, 0.25)),
            ('pericardium', (0.75, 0.60, 0.50)),
            ('septum', (0.78, 0.22, 0.22)),
            ('papillary', (0.82, 0.30, 0.30)),
            ('chordae', (0.88, 0.75, 0.60)),
        ],
        'default': (0.82, 0.20, 0.20)  # Default red for unmatched
    },
    
    'brain': {
        'keywords': [
            # 🧠 ألوان أكثر إشباعاً لضمان ظهور التباين
            
            # Brainstem - Darker Gray/Greenish
            ('brainstem', (0.30, 0.60, 0.30)), 
            ('brain_stem', (0.30, 0.60, 0.30)),

            # Cerebellum (المخيخ) و Vermis (الدودة)
            ('vermis', (0.85, 0.50, 0.35)), # Tan/Copper Vibrant
            ('cerebellum', (0.80, 0.70, 0.50)), # Beige Darker
            ('left_cerebellum', (0.80, 0.70, 0.50)), 
            ('right_cerebellum', (0.85, 0.75, 0.55)), 
            
            # Frontal Lobe (الفص الجبهي) - Red/Pink (واضح)
            ('left_frontal_lobe', (1.0, 0.30, 0.30)), 
            ('right_frontal_lobe', (0.90, 0.25, 0.25)), 
            ('frontal_lobe', (0.95, 0.28, 0.28)), 
            ('frontal', (0.95, 0.28, 0.28)),
            
            # Parietal Lobe (الفص الجداري) - Green (واضح)
            ('left_parietal_lobe', (0.30, 0.90, 0.30)), 
            ('right_parietal_lobe', (0.25, 0.80, 0.25)), 
            ('parietal_lobe', (0.28, 0.85, 0.28)),
            ('parietal', (0.28, 0.85, 0.28)),
            
            # Temporal Lobe (الفص الصدغي) - Blue (واضح)
            ('left_temporal_lobe', (0.30, 0.30, 0.95)), 
            ('right_temporal_lobe', (0.25, 0.25, 0.85)), 
            ('temporal_lobe', (0.28, 0.28, 0.90)),
            ('temporal', (0.28, 0.28, 0.90)),
            
            # Occipital Lobe (الفص القفوي) - Yellow (واضح)
            ('left_occipital_lobe', (0.95, 0.95, 0.30)), 
            ('right_occipital_lobe', (0.85, 0.85, 0.25)), 
            ('occipital_lobe', (0.90, 0.90, 0.28)), 
            ('occipital', (0.90, 0.90, 0.28)),
            
            # Insular Lobe (الفص الجزيري) - Cyan (واضح)
            ('left_insular_lobe', (0.30, 0.95, 0.95)),
            ('right_insular_lobe', (0.25, 0.85, 0.85)),
            ('insular_lobe', (0.28, 0.90, 0.90)), 
            ('insular', (0.28, 0.90, 0.90)),
            
            # Limbic Lobe (الفص الحوفي) - Magenta/Purple (واضح)
            ('left_limbic_lobe', (0.95, 0.30, 0.95)),
            ('right_limbic_lobe', (0.85, 0.25, 0.85)),
            ('limbic_lobe', (0.90, 0.28, 0.90)), 
            ('limbic', (0.90, 0.28, 0.90)),
            
            # General Lobe Fallback
            ('lobe', (0.85, 0.75, 0.70)),
            
            # General brain regions
            ('cerebrum', (0.92, 0.82, 0.72)),
            ('brain_stem', (0.84, 0.74, 0.64)),
            
            # White vs Gray matter
            ('corpus_callosum', (0.95, 0.95, 1.0)),
            ('white_matter', (0.98, 0.98, 0.98)),
            ('gray_matter', (0.70, 0.70, 0.70)),
            ('grey_matter', (0.70, 0.70, 0.70)),
            ('cortex', (0.85, 0.75, 0.70)),
            
            # Ventricles - Blue
            ('ventricle', (0.4, 0.5, 0.95)),
            ('ventricular', (0.42, 0.52, 0.93)),
            
            # Blood vessels - Red/Blue
            ('artery', (1.0, 0.3, 0.3)),
            ('vein', (0.3, 0.4, 0.9)),
            ('vessel', (0.9, 0.4, 0.4)),
            
            # Specific structures
            ('hippocampus', (0.9, 0.7, 0.5)),
            ('amygdala', (0.8, 0.6, 0.7)),
            ('thalamus', (0.7, 0.8, 0.6)),
            ('hypothalamus', (0.75, 0.75, 0.6)),
            ('basal_ganglia', (0.65, 0.70, 0.80)),
            ('putamen', (0.70, 0.65, 0.75)),
            ('caudate', (0.68, 0.68, 0.78)),
            ('pons', (0.80, 0.70, 0.65)),
            ('medulla', (0.78, 0.68, 0.63)),
        ],
        'default': (0.88, 0.78, 0.70)
    },
    
    'muscles': {
        'keywords': [
            # Upper body muscles - Red shades
            ('biceps', (0.85, 0.25, 0.25)),
            ('triceps', (0.88, 0.28, 0.28)),
            ('deltoid', (0.90, 0.30, 0.30)),
            ('pectoralis', (0.82, 0.22, 0.22)),
            ('pecs', (0.82, 0.22, 0.22)),
            ('latissimus', (0.78, 0.18, 0.18)),
            ('lats', (0.78, 0.18, 0.18)),
            ('trapezius', (0.86, 0.26, 0.26)),
            ('traps', (0.86, 0.26, 0.26)),
            
            # Lower body muscles - Darker red
            ('quadriceps', (0.90, 0.35, 0.35)),
            ('quads', (0.90, 0.35, 0.35)),
            ('hamstrings', (0.88, 0.33, 0.33)),
            ('hamstring', (0.88, 0.33, 0.33)),
            ('gastrocnemius', (0.92, 0.38, 0.38)),
            ('soleus', (0.89, 0.36, 0.36)),
            ('calf', (0.90, 0.37, 0.37)),
            ('glute', (0.85, 0.30, 0.30)),
            ('gluteus', (0.85, 0.30, 0.30)),
            
            # Core muscles
            ('abdominal', (0.80, 0.28, 0.28)),
            ('abs', (0.80, 0.28, 0.28)),
            ('oblique', (0.83, 0.31, 0.31)),
            ('rectus', (0.81, 0.29, 0.29)),
            
            # Tendons - Light brown/tan
            ('tendon', (0.85, 0.75, 0.60)),
            ('achilles', (0.88, 0.78, 0.63)),
            
            # Fascia - Light gray
            ('fascia', (0.75, 0.70, 0.65)),
            
            # Ligaments - White/cream
            ('ligament', (0.92, 0.88, 0.80)),
        ],
        'default': (0.85, 0.30, 0.30)
    },
    
    'teeth': {
        'keywords': [
            # Tooth types - White shades
            ('incisor', (1.0, 1.0, 0.96)),
            ('canine', (0.98, 0.98, 0.93)),
            ('premolar', (0.96, 0.96, 0.91)),
            ('molar', (0.94, 0.94, 0.89)),
            
            # Tooth parts
            ('crown', (1.0, 1.0, 0.98)),
            ('root', (0.93, 0.89, 0.82)),
            ('enamel', (1.0, 1.0, 1.0)),
            ('dentin', (0.96, 0.93, 0.87)),
            ('pulp', (0.95, 0.65, 0.65)),
            ('cementum', (0.90, 0.87, 0.80)),
            
            # Jaw bones - Beige/tan
            ('maxilla', (0.92, 0.87, 0.78)),
            ('mandible', (0.90, 0.85, 0.76)),
            ('jaw', (0.91, 0.86, 0.77)),
            ('alveolar', (0.88, 0.83, 0.74)),
            ('bone', (0.89, 0.84, 0.75)),
            
            # Soft tissues
            ('gum', (0.95, 0.70, 0.70)),
            ('gingiva', (0.94, 0.68, 0.68)),
            ('periodontal', (0.93, 0.88, 0.83)),
            ('ligament', (0.92, 0.87, 0.82)),
            
            # Nerves and vessels
            ('nerve', (1.0, 0.95, 0.70)),
            ('canal', (0.98, 0.93, 0.75)),
            ('vessel', (0.95, 0.50, 0.50)),
        ],
        'default': (0.96, 0.96, 0.92)
    }
}

# Default colors if organ not found
DEFAULT_ORGAN_COLORS = {
    'heart': (0.82, 0.20, 0.20),
    'brain': (0.88, 0.78, 0.70),
    'muscles': (0.85, 0.30, 0.30),
    'teeth': (0.96, 0.96, 0.92)
}

def get_color_for_part(organ_type, part_name):
    """
    Get anatomically appropriate color for a part based on keywords
    Uses longest-match priority (most specific keywords checked first)
    """
    if organ_type not in ANATOMICAL_COLOR_RULES:
        # Fallback to golden ratio for unknown organs
        return get_color_for_label(organ_type, hash(part_name) % 100)
    
    # Normalize part name for matching
    part_lower = part_name.lower().replace('-', '_').replace(' ', '_')
    
    # Get color rules for this organ
    rules = ANATOMICAL_COLOR_RULES[organ_type]
    
    # Check keywords in order (most specific first)
    for keyword, color in rules['keywords']:
        if keyword in part_lower:
            return color
    
    # No match found, use default for organ
    return rules['default']


def get_color_for_label(organ_type, label_value):
    """
    Get color for a segmentation label using golden ratio
    Used when part name doesn't match any keywords
    """
    # Use golden ratio for maximum color separation
    golden_ratio = 0.618033988749895
    hue = (label_value * golden_ratio) % 1.0
    
    # Adjust saturation and value based on organ type
    if organ_type == 'heart':
        saturation = 0.85
        value = 0.90
    elif organ_type == 'brain':
        saturation = 0.75
        value = 0.95
    elif organ_type == 'muscles':
        saturation = 0.80
        value = 0.88
    elif organ_type == 'teeth':
        saturation = 0.70
        value = 0.96
    else:
        saturation = 0.80
        value = 0.90
    
    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return rgb


def get_color_by_name_similarity(organ_type, part_name):
    """
    Advanced color matching using partial string matching
    Finds best matching keyword even with partial matches
    """
    if organ_type not in ANATOMICAL_COLOR_RULES:
        return DEFAULT_ORGAN_COLORS.get(organ_type, (0.8, 0.8, 0.8))
    
    part_lower = part_name.lower().replace('-', '_').replace(' ', '_')
    rules = ANATOMICAL_COLOR_RULES[organ_type]
    
    # Find best match with scoring
    best_match = None
    best_score = 0
    
    for keyword, color in rules['keywords']:
        # Calculate match score (longer matches = better)
        if keyword in part_lower:
            score = len(keyword)
            if score > best_score:
                best_score = score
                best_match = color
    
    if best_match:
        return best_match
    
    return rules['default']


# ========== ORGAN CONFIGURATIONS ==========
ORGAN_CONFIGS = {
    'heart': {
        'name': 'Cardiovascular System (Heart)',
        'mpr_paths': [
            'Coronary Artery Path',
            'Aorta Path',
            'Pulmonary Artery Path'
        ],
        'animations': [
            'Blood Flow - Aorta',
            'Blood Flow - Pulmonary',
            'Electrical Signal - Bundle of His',
            'Heartbeat Contraction'
        ],
    },
    'brain': {
        'name': 'Nervous System (Brain)',
        'mpr_paths': [
            'Cerebral Arteries Path',
            'Ventricular System Path',
            'White Matter Tracts Path'
        ],
        'animations': [
            'Neural Signal Flow - Cortex',
            'Blood Flow - Cerebral Arteries',
            'CSF Flow - Ventricles'
        ],
    },
    'muscles': {
        'name': 'Musculoskeletal System',
        'mpr_paths': [
            'Muscle Fiber Path',
            'Tendon Attachment Path',
            'Fascia Path'
        ],
        'animations': [
            'Muscle Contraction Wave',
            'Blood Flow - Muscle Tissue',
            'Tendon Movement'
        ],
    },
    'teeth': {
        'name': 'Dental System',
        'mpr_paths': [
            'Root Canal Path',
            'Alveolar Bone Path',
            'Periodontal Ligament Path'
        ],
        'animations': [
            'Blood Flow - Dental Pulp',
            'Nerve Signal - Tooth Sensitivity',
            'Jaw Movement'
        ],
    }
}


def print_color_debug(organ_type, part_name, color):
    """Print debug information about color assignment"""
    rgb_int = tuple(int(c * 255) for c in color)
    print(f"  🎨 {part_name:30s} -> RGB{rgb_int} (float: {color})")


    # ========== HSV COLOR GENERATION ==========

def generate_hsv_colors(num_colors):
    """
    Generate visually distinct colors using HSV color space.
    Colors are evenly spaced around the hue wheel for maximum distinction.
    
    Args:
        num_colors (int): Number of distinct colors to generate
        
    Returns:
        list: List of RGB tuples (r, g, b) with values in [0.0, 1.0]
        
    Mathematical approach:
    - Hue: Evenly spaced in [0, 1] for maximum distinction
    - Saturation: Fixed at 0.85 (vibrant but not overwhelming)
    - Value: Fixed at 0.95 (bright but comfortable)
    
    Example:
        For 5 colors: hues = [0.0, 0.2, 0.4, 0.6, 0.8]
        → Red, Yellow, Cyan, Blue, Magenta
        
    Color wheel distribution:
        0.00 = Red       0.17 = Orange    0.33 = Yellow
        0.50 = Cyan      0.67 = Blue      0.83 = Magenta
    """
    if num_colors <= 0:
        return []
    
    colors = []
    for i in range(num_colors):
        # Calculate evenly-spaced hue (0.0 to 1.0)
        hue = i / num_colors
        
        # Fixed saturation and value for vibrant, consistent colors
        saturation = 0.85  # Not too pale, not too intense
        value = 0.95       # Bright but comfortable
        
        # Convert HSV to RGB (colorsys returns 0.0-1.0 range)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        
        colors.append((r, g, b))
    
    return colors


def get_color_for_part_hsv(organ_key, part_name, all_part_names):
    """
    HYBRID color assignment system:
    1. Try anatomical color first (for known structures like "aorta", "ventricle")
    2. If no match, assign HSV color based on alphabetical position
    
    This gives you:
    - Meaningful colors for major anatomical structures
    - Distinct, evenly-spaced colors for unknown/unlabeled parts
    
    Args:
        organ_key (str): Organ system identifier ('heart', 'brain', etc.)
        part_name (str): Name of the specific part
        all_part_names (list): All part names in the current scene
        
    Returns:
        tuple: RGB color (r, g, b) with values in [0.0, 1.0]
    """
    # 1. Try anatomical color first (existing keyword-based system)
    anatomical_color = get_color_for_part(organ_key, part_name)
    
    # 2. Check if it's a meaningful anatomical color (not the default)
    default_color = DEFAULT_ORGAN_COLORS.get(organ_key, (0.8, 0.8, 0.8))
    
    # If the anatomical color is NOT the default, use it
    if anatomical_color != default_color:
        return anatomical_color
    
    # 3. No anatomical match found, use HSV color distribution
    # Sort parts alphabetically for consistent color assignment across sessions
    sorted_parts = sorted(all_part_names)
    
    # Generate HSV colors for all parts
    hsv_colors = generate_hsv_colors(len(sorted_parts))
    
    # Find this part's index and return its HSV color
    if part_name in sorted_parts:
        index = sorted_parts.index(part_name)
        return hsv_colors[index]
    
    # Fallback to default gray if something goes wrong
    return (0.7, 0.7, 0.7)


def get_color_for_part_pure_hsv(part_name, all_part_names):
    """
    PURE HSV color assignment (ignores anatomical meanings).
    Use this if you want maximum color distinction without semantic meaning.
    
    Args:
        part_name (str): Name of the specific part
        all_part_names (list): All part names in the current scene
        
    Returns:
        tuple: RGB color (r, g, b) with values in [0.0, 1.0]
    """
    # Sort parts alphabetically for consistent color assignment
    sorted_parts = sorted(all_part_names)
    
    # Generate HSV colors
    hsv_colors = generate_hsv_colors(len(sorted_parts))
    
    # Find this part's index
    if part_name in sorted_parts:
        index = sorted_parts.index(part_name)
        return hsv_colors[index]
    
    # Fallback
    return (0.7, 0.7, 0.7)


def print_hsv_color_map(all_part_names):
    """
    Debug function: Print the complete HSV color mapping
    Useful for verifying color distribution
    """
    print(f"\n{'='*80}")
    print(f"HSV COLOR MAPPING FOR {len(all_part_names)} PARTS")
    print(f"{'='*80}")
    
    sorted_parts = sorted(all_part_names)
    hsv_colors = generate_hsv_colors(len(sorted_parts))
    
    for i, (part, color) in enumerate(zip(sorted_parts, hsv_colors)):
        rgb_int = tuple(int(c * 255) for c in color)
        hex_color = f"#{rgb_int[0]:02x}{rgb_int[1]:02x}{rgb_int[2]:02x}"
        
        # Calculate hue in degrees
        hue_degrees = int((i / len(sorted_parts)) * 360)
        
        print(f"  {i:3d}. {part:35s} RGB{rgb_int} {hex_color}  (Hue: {hue_degrees:3d}°)")
    
    print(f"{'='*80}\n")
