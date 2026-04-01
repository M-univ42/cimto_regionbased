### CIMTO Region Based: Phantoms, Synograms and SIRT

##### Marcell Nemeth (S4456394) 
#### Description
This project attempts to replicate Van Eyndhoven et al. 2014, a research paper on iteratively reconstructing structural changes in CT scans, by distinguihing between stationary and "dynamic" areas.

For this purpose, a phantom generator of 4 structurally different phantom types was implemented, with randomly varying parameters for the change in structures. These phantoms were generated in a resolution of 500 by 500 pixels, with 300 sequence steps. From these phantoms synograms were generated, which forms the basis for the reconstruciton algortithm (SIRT as baseline and rSIRT as implemented in the paper). 

Performance is measured by RSME in pixel values between the original and reconstructed image.

#### Structure
The project is stuctured in the following way:

##### Project Structure
| Filename | Description | Functions | Status |
|---|---|---|---|
|phantoms_generator.py| This script holds the functions needed to generate different types of phantoms. The generated phantoms have randomly assigned parameters reproducible by using the same seed. The output is 500 by 500 phantom sequences of 300 steps in .npy format, with randomized parameters saved as meta data in JSON format. |create_phantom1(), create_phantom2(),create_phantom4()|Phantom 3 needs to be implemented|
|synogram_generator.py| This script generates synograms from the phantoms, and visualizes samples. Additionally it also stores important meta data neccesary for reconstruction (vol_geom and proj_geom) the output is synogram sequences in .npy format and meta data in JSON format.|make_beam(), generate_synogram(), generate_synogram_sqeuence(), save_synogram_sequence(), display_synogram(), display_synogram_seq(), save_syno_meta()| Most of the functions are correclty implemented|
|sirt.py| This script holds the functions for reconstruction from the generated synograms. The reconstruciton function is based on SIRT, and uses synogram meta data saved.| generate_from_meta(), sirt_reconstruction(), save_reconstruction()| The functions are not fully implemented, CUDA integration is needed for performance|
|metrics.py| Holds functions for metric evaluation (RMSE for the paper), on both stationary and sequential images|rmse(), rmse_seq()| TODO: optional heatmap on high error areas for analysis|
|helpers.py| Contains all the helper functions for phantom generation and a logger class for verbosity||Done|

##### Phantom types
| No. | Description | Sample Meta Data | Status |
|---|---|---|---|
|1. | Shepp-Logan phantom with two chambers, fluid flows from one to another (linear/sigmoid transfer). The two chambers currently only change intensity, not the area the fluid covers. This will be implemented later.| {'phantom_type': 1, 'fill_mode': 'linear', 'rand_factor': 1.082186814566789}|Linear implemented (Sigmoid if needed)
|2.| Shepp-Logan phantom with one chamber, the underlying texture is shifted to simulate fluid movement. A predefined texture is shifted behind an ellipse mask (chamber), to simulate fluid movement. In the original paper it seems a swirl transformation was also applied. | {'phantom_type': 2, 'rad1': 39, 'rad2': 81, 'texture_width': 107, 'texture_height': 96, 'total_shift': 29}|Implemented, swirl can be added as optional|
|3.| Random Blob, with two connected chamber, fluid movment is simulated by texture shift/swirl. The mask for the "8-shaped" chamber and the background of the blob still needs to be implemented.| TBD|Not yet implemented, but just combination on 1) and 2)|
|4.| Circular background with (Gaussian?) organic texture and sudden crack (angled). The crack is formed by an initial elongated triangle, to which additional triangles are transposed to 5 frames per triangle (to simulate sudden crack). There is a bright hue around the crack in the original paper, and it seems to use elongated poligons instead. | {'phantom_type': 4, 'stresspoint': 104, 'no_cracks': 10, 'crack_length': 57, 'crack_speed': [104, 109, 114, 119, 124, 129, 134, 139, 144, 149], 'meta_angles': [list]}|Straight crack implemented (angle not yet)|

---
#### TODO
##### Phantoms Feedback
- [x] Remove Paths/Replace texture
- [x] Create readnom seed/ parameters 
- [x] Documentation for parameter/seed 

##### Synogram
- [x] Scanning protocol for projection angle sequence
- [x] Strip kernel projector
- [ ] Poisson noise

##### Code reconstruction
- [ ] Implement 500x500 to 100x100 pipeline
- [ ] CUDA integration
- [x] Implement SIRT (from ASTRA)
- [ ] SIRT per angular subset
- [ ] Implmenet rSIRT
- [ ] Create Table 1
- [ ] Convergence Plot
#### Results



---

##### Phantom 1  and its Synogram
![Phantom 1](readme_img/phantom1.png)
![Synogram 1](readme_img/syno1.png)

##### Phantom 2  and its Synogram
![Phantom 2](readme_img/phantom2.png)
![Synogram 2](readme_img/syno2.png)
##### Phantom 4  and its Synogram
![Phantom 4](readme_img/phantom4.png)
![Synogram 4](readme_img/syno4.png)


---

#### Original Paper
Van Eyndhoven, G., Batenburg, K. J., & Sijbers, J. (2014). Region-based iterative reconstruction of structurally changing objects in CT. IEEE Transactions on Image Processing, 23(2), 909–919. https://doi.org/10.1109/TIP.2013.2297024

---

#### Resources:

https://astra-toolbox.com/docs/algs/SIRT.html
##### Scikit
https://sigpy.readthedocs.io/en/latest/generated/sigpy.shepp_logan.html
https://github.com/mckib2/phantominator/blob/main/phantominator/ct_shepp_logan.py
https://scikit-image.org/docs/stable/auto_examples/transform/plot_transform_types.html#sphx-glr-auto-examples-transform-plot-transform-types-py
https://scikit-image.org/docs/stable/auto_examples/transform/plot_geometric.html



