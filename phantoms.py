import numpy as np
import matplotlib.pyplot as plt

from skimage.draw import line as draw_line

from skimage.transform import resize
from skimage import data
from skimage.color import rgb2gray

from helpers import make_disk, create_shepp_logan, save_phantom_sequence, display_sequence, make_ellipse

def create_phantom1(size, no_frames, full_int, empty_int,
                    fill_mode="linear", seed=42):
    """Generates Phantom 1: two chambers, with liquid filling from left to right
    
    TO-DO: Implement sigmoid/exponential if needed?"""
    generator   = np.random.default_rng(seed)
    scale = size // 2

    
    rand_factor = generator.uniform(0.85, 1.15)

    base      = create_shepp_logan(size)
    chamber_l = make_ellipse(size, -0.15 * scale, 0,
                             0.1 * scale * rand_factor, 0.15 * scale, 0)
    chamber_r = make_ellipse(size,  0.15 * scale, 0,
                             0.1 * scale * rand_factor, 0.15 * scale, 0)
    chamber_mask = np.maximum(chamber_l, chamber_r)

    phantoms = np.zeros((no_frames, size, size))

    for t in range(no_frames):
        frac = t / (no_frames - 1)

        if fill_mode == "sigmoid":
            frac = 1.0 / (1.0 + np.exp(-10 * (frac - 0.5)))

        fill_l = full_int  * (1 - frac) + empty_int * frac
        fill_r = empty_int * (1 - frac) + full_int  * frac

        frame = base.copy()
        frame = frame + chamber_l * fill_l + chamber_r * fill_r
        phantoms[t] = frame
    meta_data = {
        "phantom_type": 1,
        "fill_mode": fill_mode,
        "rand_factor": rand_factor
    }
    return phantoms, chamber_mask, meta_data


def create_phantom2(size, no_frames, full_int, empty_int, seed = 42):
    """Generate Phantom 2: one ellipse mask, with the texture under it shifting from left to right"""
    generator = np.random.default_rng(seed)
    scale = size // 2
    
    rad1 = generator.integers(int(0.15 * scale), int(0.25 * scale))
    rad2 = generator.integers(int(0.25 * scale), int(0.35 * scale))
    
    texture_width = generator.integers(int(0.3 * scale), int(0.5 * scale))
    texture_height = generator.integers(int(0.3 * scale), int(0.5 * scale))
    
    
    tex       = data.kidney().astype(float)
    tex = rgb2gray(tex)
    tex = tex.mean(axis=0)
    tex = (tex - tex.min()) / (tex.max() - tex.min())  
    tex = resize(tex, (texture_height, texture_width), preserve_range=True, anti_aliasing=True)
    tex = np.squeeze(tex)
    tex_h, tex_w = tex.shape
    
    inner_mask = make_disk(size, 0, 0, rad1)
    
    base = create_shepp_logan(size)
    phantoms = np.zeros((no_frames, size, size))
    variable_mask = inner_mask.copy()
    
    total_shift = texture_width - rad1 * 2
    
    for t in range(no_frames):
        frac = t / (no_frames - 1) 
        shift = int(frac * total_shift)
        canvas = np.zeros((size, size))
        start_y = size//2 - tex_h//2
        start_x = size//2 - rad1 - shift
        # shifting the texture
        for i in range(tex_h):
            for j in range(tex_w):
                cy = start_y + i
                cx = start_x + j
                # texture bound
                if 0 <= cy < size and 0 <= cx < size:
                    canvas[cy, cx] = tex[i, j]
        
        # ellipse mask
        masked = canvas * inner_mask
        frame = base.copy()
        frame = frame + masked * full_int
        phantoms[t] = frame

    #save meta data for runs
    meta_data = {
        "phantom_type": 2,
        "rad1": rad1,
        "rad2": rad2,
        "texture_width": texture_width,
        "texture_height": texture_height,
        "total_shift": total_shift,
    }
    return phantoms, variable_mask,meta_data


def create_phantom4(size, no_frames, full_int, empty_int,seed=42):

    """Create Phantom 4: Shepp-Logan with crack apeparing at 1/3 of total frames. 
    TO-DO: implement rotate"""
    from skimage.transform import rotate
    generator = np.random.default_rng(seed)

    stresspoint = generator.integers(no_frames // 3, no_frames // 2) 
    no_cracks = generator.integers(7, 11)
    scale = size // 2
    crack_length = generator.integers(int(0.1 * scale), int(0.3 * scale))

    # base = create_shepp_logan(size)
    tex       = data.kidney().astype(float)
    tex = rgb2gray(tex)
    tex = tex.mean(axis=0)
    tex       = (tex - tex.min()) / (tex.max() - tex.min()) 
    tex       = resize(tex, (size, size), preserve_range=True, anti_aliasing=True)
    tex = np.squeeze(tex)

    disk_mask = make_disk(size, 0, 0, int(0.45 * size))

    # first crack starts in upper half and grows downward.
    y_start = -size // 4
    init_angle = generator.uniform(80, 100)
    crack_mask, x_end, y_end = make_crack(size, 0, y_start, crack_length, init_angle)
    active_tips = [(x_end, y_end, init_angle)]
 
   
    phantoms = np.zeros((no_frames, size, size))
  
    meta_angles = [init_angle]
    crack_speed = range(stresspoint, min(no_frames, stresspoint + 5 * no_cracks), 5)
    for t in range(no_frames):

        # disk_mask for outer vignette
        frame = tex.copy() * disk_mask
        if stresspoint <=t:
            crack_in_disk = crack_mask * disk_mask
            frame = frame + crack_in_disk * empty_int
            if t in crack_speed:
                next_tips = []
                for x_tip, y_tip, angle_tip in active_tips[:3]:
                    main_angle = angle_tip + generator.uniform(-18, 18)
                    crack_new, x_new, y_new = make_crack(size, x_tip, y_tip, crack_length, main_angle)
                    crack_mask = np.maximum(crack_mask, crack_new)
                    next_tips.append((x_new, y_new, main_angle))
                    meta_angles.append(main_angle)

                active_tips = next_tips[:4] if next_tips else active_tips
                crack_in_disk = crack_mask * disk_mask
                frame = frame + crack_in_disk * empty_int
                # last_coords = (x_end, y_end)
        meta_data = {
            "phantom_type": 4,
            "stresspoint": stresspoint,
            "no_cracks": no_cracks,
            "crack_length": crack_length,
            "crack_speed": crack_speed,
            "meta_angles": meta_angles
        }
        phantoms[t] = frame
    
    return phantoms, crack_mask, meta_data


if __name__ == "__main__":
    SIZE = 500
    no_frames = 300
    SEED = 42
    phantoms, masks, meta_data = create_phantom1(
        size=SIZE,
        no_frames=no_frames,
        full_int=2.0,  
        empty_int=0.0,
        seed=SEED
    )
    display_sequence(phantoms, masks, samples=5)
    phantoms, masks, meta_data = create_phantom2(
        size=SIZE,
        no_frames=no_frames,
        full_int=2.0,  
        empty_int=0.0,
        seed = SEED

    )
    display_sequence(phantoms, masks, samples=5)
    phantoms, masks, meta_data = create_phantom4(
        size=SIZE,
        no_frames=no_frames,
        full_int=0,  
        empty_int=0.5,
        seed = SEED
    )
    
    display_sequence(phantoms, masks, samples=5)
    
