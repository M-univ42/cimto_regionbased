import os
import json
import astra
import numpy as np
from helpers import logger
import matplotlib.pyplot as plt

def make_beam(size,n_angles, det_count=None, det_spacing=1.0):
    """Creates vol_geom, proj_geom
    SRC: """
    n_rows, n_cols = size
    if det_count is None:
        det_count = int(np.ceil(np.sqrt(2) * n_cols))
    vol_geom = astra.create_vol_geom(n_rows, n_cols)
    angles = np.linspace(0.0, np.pi, n_angles, endpoint=False)
    proj_geom = astra.create_proj_geom("parallel", det_spacing, det_count, angles)
    return vol_geom, proj_geom

def generate_synogram(img, n_angles=180, det_count=None, det_spacing=1.0):
    """ Generates synogram from stationary img in sequence"""

    img = np.asarray(img, dtype=np.float32)
    vol_geom, proj_geom = make_beam(img.shape, n_angles, det_count, det_spacing)
    projector = astra.create_projector("line", proj_geom, vol_geom)
    sino_id = None
    try:
        sino_id, sino = astra.create_sino(img, projector)
    finally:
        if sino_id is not None:
            astra.data2d.delete(sino_id)
        astra.projector.delete(projector)
    return sino


def generate_synogram_sequence(phantom_seq, n_angles=180, det_count=None, det_spacing=1.0):
    """Generates synograms for each frame in phantom sequence"""
    synograms = []
    angle_array = np.linspace(0.0, np.pi, n_angles, endpoint=False).tolist()
    resolved_det_count = int(det_count) if det_count is not None else int(np.ceil(np.sqrt(2) * phantom_seq.shape[2]))
    meta_data = {
        "n_rows": int(phantom_seq.shape[1]),
        "n_cols": int(phantom_seq.shape[2]),
        "n_angles": int(n_angles),
        "det_count": resolved_det_count,
        "det_spacing": float(det_spacing),
        "geom_type": "parallel",
        "angle_array": angle_array,
    }

    for frame in phantom_seq:
        synograms.append(
            generate_synogram(frame, n_angles, det_count, det_spacing)
        )
    return np.stack(synograms, axis=0), meta_data

def save_synogram_sequence(synogram_seq, filename):
    """Save synogram sequence"""
    np.save(filename, synogram_seq)
    logger().log(f"Synogram sequence saved to {filename}")

def display_synogram(synogram, title=""):
    """Display stationary synogram"""
    plt.imshow(synogram, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()


def display_synogram_seq(synogram_seq, title="", samples=5):
    """Display samples from synogram sequence"""
    syno_length = len(synogram_seq)
    indices = np.linspace(0, syno_length - 1, samples, dtype=int)


    # set upper/lower threshold
    vmin, vmax = synogram_seq.min(), synogram_seq.max()
    fig, axes = plt.subplots(1, samples, figsize=(3 * samples, 3))

    fig.suptitle(title)
    for plot_idx, t in enumerate(indices):
        axes[plot_idx].imshow(synogram_seq[t], cmap="gray", vmin=vmin, vmax=vmax)
        axes[plot_idx].axis("off")
        axes[plot_idx].set_title(f"t={t}")

    plt.tight_layout()
    plt.show()


def save_syno_meta(filename, meta_data):
    """Save synogram metadata like phantoms for reconstruction"""
    meta_filename = filename.replace('.npy', '_meta.json')
    with open(meta_filename, 'w') as f:
        json.dump(meta_data, f, indent=4)
    logger().log(f"Synogram metadata saved to {meta_filename} META: {meta_data}")


if __name__ == "__main__":
    ROOT = "data"
    input_dir = os.path.join(ROOT, "phantoms")
    output_dir = os.path.join(ROOT, "synograms")
    SIZE = 500
    no_frames = 300
    SEED = 42
    input_dir = os.path.join(input_dir, f"{SIZE}x{SIZE}_{no_frames}_{SEED}")
    output_dir = os.path.join(output_dir, f"{SIZE}x{SIZE}_{no_frames}_{SEED}_syno")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger().log(f"Starting syn generaton for phantom 1")
    phantom_seq = np.load(os.path.join(input_dir, "phantom1.npy"))
    synogram_seq, meta_data = generate_synogram_sequence(phantom_seq)
    display_synogram_seq(synogram_seq, title="Synogram for phantom 1", samples=5)
    save_synogram_sequence(synogram_seq, os.path.join(output_dir, "synogram1.npy"))
    save_syno_meta(os.path.join(output_dir, "synogram1.npy"), meta_data)

    logger().log(f"Starting syn generaton for phantom 2")
    phantom_seq = np.load(os.path.join(input_dir, "phantom2.npy"))
    synogram_seq, meta_data = generate_synogram_sequence(phantom_seq)
    display_synogram_seq(synogram_seq, title="Synogram for phantom 2", samples=5)
    save_synogram_sequence(synogram_seq, os.path.join(output_dir, "synogram2.npy"))
    save_syno_meta(os.path.join(output_dir, "synogram2.npy"), meta_data)

    logger().log(f"Starting syn generaton for phantom 4")
    phantom_seq = np.load(os.path.join(input_dir, "phantom4.npy"))
    synogram_seq, meta_data = generate_synogram_sequence(phantom_seq)
    display_synogram_seq(synogram_seq, title="Synogram for phantom 4", samples=5)
    save_synogram_sequence(synogram_seq, os.path.join(output_dir, "synogram4.npy"))
    save_syno_meta(os.path.join(output_dir, "synogram4.npy"), meta_data)

