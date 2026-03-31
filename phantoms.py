from skimage.draw import polygon
import numpy as np
import matplotlib.pyplot as plt
from skimage.draw import ellipse
from skimage.data import shepp_logan_phantom
from scipy.ndimage import map_coordinates
from skimage.io import imread
from skimage.transform import resize


def make_triangle(size, x_center,  y_center, base_width, height):
    """create traingle from center (x_center,y_center)
    SRC: https://scikit-image.org/docs/stable/api/skimage.draw.html#skimage.draw.polygon"""
    mask = np.zeros((size, size))
    # top
    p1 = (y_center - height//2, x_center)
    # left
    p2 = (y_center + height//2, x_center - base_width//2)
    # right
    p3 = (y_center + height//2, x_center + base_width//2)
    # triangle_coords = [p1, p2, p3]
    rows_coord = np.array([p1[0], p2[0], p3[0]]) + size//2
    cols_coord = np.array([p1[1], p2[1], p3[1]]) + size//2
    
    rr, cc = polygon(rows_coord, cols_coord, shape=(size, size))
    mask[rr, cc] = 1.0
    
    return mask

def make_ellipse(size, x_center, y_center, rad1, rad2, angle):
    mask = np.zeros((size, size))
    center_row = size//2 + int(y_center)
    center_col = size//2 + int(x_center)
    rr, cc = ellipse(center_row, center_col, int(rad2), int(rad1), shape=(size,size), rotation=angle)
    mask[rr, cc] = 1.0
    
    return mask

def create_shepp_logan(size):
    """Create Shepp-Logan phantom
    SRC: https://scikit-image.org/docs/stable/auto_examples/transform/plot_radon_transform.html"""
    phantom = shepp_logan_phantom()  
    phantom = resize(phantom, (size, size), preserve_range=True)
    return phantom

def display_sequence(phantoms, masks, samples=5):
    """Display variable number of samples from sequence"""
    fig, axes = plt.subplots(1, samples, figsize=(15, 3))
    axes = axes.flatten()
    plot_idx = 0
    # print(len(phantoms))
    vmin = phantoms.min()
    vmax = phantoms.max()
    for t in range(len(phantoms)):
        if t % (len(phantoms) // samples)  == 0 and plot_idx < samples:
            axes[plot_idx].imshow(phantoms[t], cmap='gray', vmin=vmin, vmax=vmax)
            axes[plot_idx].axis('off')
            axes[plot_idx].set_title(f"t= {t}")
            plot_idx +=1
    plt.show()


def create_phantom1(size,no_frames,full_int,empty_int,fill_mode="linear"):
    """Generates Phantom 1: two chambers, with liquid filling from left to right
    
    TO-DO: Implement sigmoid/exponential if needed?"""
    scale = size//2
    base = create_shepp_logan(size)
    chamber_l = make_ellipse(size, -0.15*scale, 0, 0.1*scale, 0.15*scale, 0)
    chamber_r = make_ellipse(size,  0.15*scale, 0, 0.1*scale, 0.15*scale, 0)
    chamber_mask = np.maximum(chamber_l, chamber_r)
 
    phantoms = np.zeros((no_frames, size, size))

    for t in range(no_frames):
        frac = t / (no_frames - 1)

        if fill_mode == "linear":
            fill_l = full_int * (1-frac) + empty_int*frac
            fill_r = empty_int * (1-frac) + full_int*frac
        
        # build the frame
        frame = base.copy()
        frame = frame + chamber_l * fill_l
        frame = frame + chamber_r * fill_r
        
        phantoms[t] = frame
    
    return phantoms, chamber_mask

def create_phantom2(size, no_frames, full_int, empty_int, texture_path='texture2.png'):
    """Generate Phantom 2: one ellipse mask, with the texture under it shifting from left to right"""
    scale = size // 2
    
    rad1 = int(0.2 * scale)
    rad2 = int(0.2 * scale)
    
    texture_width = int(0.6 * scale)
    texture_height = int(0.4 * scale)
    

    img_orig = imread(texture_path, as_gray=True)
    texture = resize(img_orig, (texture_height, texture_width))
    
    inner_mask = make_ellipse(size, 0, 0, rad1, rad2, 0)
    
    base = create_shepp_logan(size)
    phantoms = np.zeros((no_frames, size, size))
    variable_mask = inner_mask.copy()
    
    total_shift = texture_width - rad1 * 2
    
    for t in range(no_frames):
        frac = t / (no_frames - 1) 
        shift = int(frac * total_shift)
        canvas = np.zeros((size, size))
        start_y = size//2 - texture_height//2
        start_x = size//2 - rad1 - shift
        # shifting the texture
        for i in range(texture_height):
            for j in range(texture_width):
                cy = start_y + i
                cx = start_x + j
                # texture bound
                if 0 <= cy < size and 0 <= cx < size:
                    canvas[cy, cx] = texture[i, j]
        
        # ellipse mask
        masked = canvas * inner_mask
        frame = base.copy()
        frame = frame + masked * full_int
        phantoms[t] = frame
    
    return phantoms, variable_mask


def create_phantom4(size, no_frames, full_int, empty_int,texture_path ="phantom4_texture.png"):

    """Create Phantom 4: Shepp-Logan with crack apeparing at 1/3 of total frames. 
    TO-DO: implement rotate"""
    from skimage.transform import rotate

    stresspoint = no_frames // 3  
    no_cracks = 4
    scale = size // 2
    triangle_height = 100

    # base = create_shepp_logan(size)
    base = imread(texture_path, as_gray=True)
    base = resize(base, (size,size))

    # first crack
    crack_mask = make_triangle(size, 0, size//3, 20, triangle_height)
 
   
    phantoms = np.zeros((no_frames, size, size))
    last_coords = (0, size//3)

    crack_speed = range(stresspoint, stresspoint+5*no_cracks, 5)
    for t in range(no_frames):
        
        frame = base.copy()
        if stresspoint <=t:
            # frame = frame + crack_mask*full_int 
            frame = frame + crack_mask*empty_int
            if t in crack_speed:
                last_coords = (last_coords[0], last_coords[1] -triangle_height//4)   
                crack_new = make_triangle(size, last_coords[0], last_coords[1], 20, triangle_height)
                crack_mask = np.maximum(crack_mask, crack_new)
                frame = frame + crack_mask*empty_int
                if t == crack_speed[-1]:

                    # TO-DO: Rotate last triangle by x degrees
                    last_coords = (last_coords[0], last_coords[1] -triangle_height//4)   
                    crack_new = make_triangle(size, last_coords[0], last_coords[1], 20, triangle_height)
                    
                    # rotated = rotate(crack_new, center=(base_row, base_col), angle=45, preserve_range=True) 
                    crack_mask = np.maximum(crack_mask, crack_new)
                    frame = frame + crack_mask*empty_int
        
        phantoms[t] = frame
    return phantoms, crack_mask


if __name__ == "__main__":
    SIZE = 500
    no_frames = 300
    texture_path = 'texture2.png'
    phantoms, masks = create_phantom1(
        size=SIZE,
        no_frames=no_frames,
        full_int=2.0,  
        empty_int=0.0
    )
    display_sequence(phantoms, masks, samples=5)
    phantoms, masks = create_phantom2(
        size=SIZE,
        no_frames=no_frames,
        full_int=2.0,  
        empty_int=0.0
    , texture_path=texture_path
    )
    display_sequence(phantoms, masks, samples=5)
    phantoms, masks = create_phantom4(
        size=SIZE,
        no_frames=no_frames,
        full_int=0,  
        empty_int=0.5
    )
    
    display_sequence(phantoms, masks, samples=5)
    
