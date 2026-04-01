import numpy as np
import matplotlib.pyplot as plt
import json
from phantominator import shepp_logan

from skimage.draw import polygon, ellipse, disk, line as draw_line
from skimage.data import camera, gravel
from skimage.transform import resize, rotate
from scipy.ndimage import binary_dilation
from skimage import data
from skimage.color import rgb2gray




class logger():
    def __init__(self, verbose=True):
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(msg)

def make_disk(size, x_center, y_center, radius):
    """Binary mask with a filled circle.
    """
    mask = np.zeros((size, size))
    rr, cc = disk(
        (size // 2 + round(y_center), size // 2 + round(x_center)),
        radius,
        shape=(size, size),
    )
    mask[rr, cc] = 1.0
    return mask

def create_shepp_logan(size):
    """Create Shepp-Logan phantom
    SRC: https://scikit-image.org/docs/stable/auto_examples/transform/plot_radon_transform.html"""
    phantom = shepp_logan(size).astype(float)
    return phantom

def save_phantom_sequence(phantom_seq, filename,meta_data=None):
    """Saves generated sequency as .npy and additional meta data for replication"""
    np.save(filename, phantom_seq)
    if meta_data:
        meta_filename = filename.replace('.npy', '_meta.json')
        with open(meta_filename, 'w') as f:
            json.dump(meta_data, f, indent=4)
    logger().log(f"Phantom saved to {filename} META: {meta_data}")

def display_sequence(phantom_seq, mask, title="", samples=5):
    """Display variable number of samples from sequence"""
    n = len(phantom_seq)
    indices = np.linspace(0, n - 1, samples, dtype=int)

    vmin, vmax = phantom_seq.min(), phantom_seq.max()
    fig, axes = plt.subplots(1, samples, figsize=(3 * samples, 3))
    fig.suptitle(title)
    for plot_idx, t in enumerate(indices):
        axes[plot_idx].imshow(phantom_seq[t], cmap="gray", vmin=vmin, vmax=vmax)
        axes[plot_idx].axis("off")
        axes[plot_idx].set_title(f"t={t}")
    plt.tight_layout()
    plt.show()


def make_ellipse(size, x_center, y_center, rad1, rad2, angle):
    mask = np.zeros((size, size))
    center_row = size // 2 + round(y_center)
    center_col = size // 2 + round(x_center)
    rr, cc = ellipse(center_row, center_col,
                     int(rad2), int(rad1),
                     shape=(size, size), rotation=angle)
    mask[rr, cc] = 1.0
    return mask


def make_crack(size, x_start, y_start, length, angle):
    """Creates line from x,y start to length plus angle (can be randomized)"""
    mask = np.zeros((size, size), dtype=bool)

    
    x_end = x_start + length * np.cos(np.radians(angle))
    y_end = y_start + length * np.sin(np.radians(angle))

    # convert to realtive coords and check bounds
    rel_min = -size // 2 + 1
    rel_max = size // 2 - 1
    x_end = float(np.clip(x_end, rel_min, rel_max))
    y_end = float(np.clip(y_end, rel_min, rel_max))
    x0,x1,y0,y1 = size // 2 + np.round([x_start, x_end, y_start, y_end]).astype(int)
 

    # map np clip out of bound line points

    x0,x1,y0,y1 = map(int, np.clip([x0, x1, y0, y1], 0, size - 1))
    rr,cc = draw_line(y0, x0,
                        y1,
                        x1)

    mask[rr, cc] = True

    # dilate for visibility
    mask = binary_dilation(mask, iterations=4)
    return mask.astype(float),x_end, y_end