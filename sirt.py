
import astra
import matplotlib.pyplot as plt
import numpy as np
import os
import json
from helpers import logger

def generate_from_meta(filepath):
    """Load meta for synogram and generate vol_geom, proj_geom"""
    meta_data = json.load(open(filepath.replace('.npy', '_meta.json'), 'r'))

    
    n_angles = meta_data["n_angles"]
    det_count = meta_data["det_count"]
    det_spacing = meta_data["det_spacing"]
    n_rows = meta_data["n_rows"]
    n_cols = meta_data["n_cols"]
    angles = np.linspace(0.0, np.pi, n_angles, endpoint=False)
    vol_geom = astra.create_vol_geom(n_rows, n_cols)
    proj_geom = astra.create_proj_geom("parallel", det_spacing, det_count, angles)
    return vol_geom, proj_geom

def sirt_reconstruction(filepath, iterations=100, show=False):
    """SIRT reconstruction over a sinogram sequence (T, angles, det_count).
    SRC: https://astra-toolbox.com/docs/algs/SIRT.html"""
    vol_geom, proj_geom = generate_from_meta(filepath)
    projector_id = astra.create_projector('linear', proj_geom, vol_geom)

    sinogram = np.load(filepath)
    # Support both single frame (2D) and sequence (3D).
    frames = [sinogram] if sinogram.ndim == 2 else list(sinogram)

    reconstructions = []
    for sino_frame in frames:
        sinogram_id = astra.data2d.create('-sino', proj_geom, sino_frame)
        recon_id = astra.data2d.create('-vol', vol_geom)

        cfg = astra.astra_dict('SIRT')
        cfg['ProjectorId'] = projector_id
        cfg['ProjectionDataId'] = sinogram_id
        cfg['ReconstructionDataId'] = recon_id
        cfg['option'] = {'MinConstraint': 0.0}
        algorithm_id = astra.algorithm.create(cfg)

        astra.algorithm.run(algorithm_id, iterations=iterations)
        reconstructions.append(astra.data2d.get(recon_id))

        astra.data2d.delete([sinogram_id, recon_id])
        astra.algorithm.delete(algorithm_id)

    astra.projector.delete(projector_id)

    result = reconstructions[0] if sinogram.ndim == 2 else np.stack(reconstructions, axis=0)

    if show:
        plt.imshow(reconstructions[0], cmap='gray')
        plt.show()

    return result
def save_reconstruction(reconstruction, filename):
    """Save reconstruction as .npy"""
    np.save(filename, reconstruction)
    print(f"Reconstruction saved to {filename}")


if __name__ == "__main__":
    ROOT = "data"
    input_dir = os.path.join(ROOT, "synograms")
    output_dir = os.path.join(ROOT, "reconstructions")
    SIZE = 500
    no_frames = 300
    SEED = 42
    input_dir = os.path.join(input_dir, f"{SIZE}x{SIZE}_{no_frames}_{SEED}_syno")
    output_dir = os.path.join(output_dir, f"{SIZE}x{SIZE}_{no_frames}_{SEED}_recon")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".npy"):
            filepath = os.path.join(input_dir, filename)
            logger().log(f"Processing {filepath}")
            reconstruction = sirt_reconstruction(filepath, iterations=100, show=True)
            save_reconstruction(reconstruction, os.path.join(output_dir, f"reconstruction_{filename}"))

   