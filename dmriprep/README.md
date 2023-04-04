# dmriprep processings

See the [main documentation](https://github.com/rlink7/rlink_mri/blob/main/README.md) for an overview of the processings.  
The code is organized in two parts:
* **runtime.py**: perform the analysis with hopla (by default in a multi-cpus setting).
* **qc.py**: perform the Quality Control (QC).

Methods Summary:
The diffusion data were preprocessed and quality-checked with the following pipeline built around the MRTrix3 [1], FSL [2], and ANTs [3] software packages. First, any volumes with a corresponding b value less than 50 were treated as b0 volume
for the remainder of the pipeline. The diffusion data were denoised with the provided dwidenoise (MP-PCA) function included with MRTrix3 [4][5][6]. The images were then intensity-normalized to the first image and concatenated for further
processing. FSL's topup and eddy algorithms were used to correct for susceptibilty-induced and motion artifacts and eddy currents and to remove outlier slices [7][8][9][10]. Lastly, the preprocessed data were fitted with a tensor model using the
dwi2tensor function included with MRTrix3 using an iterative reweighted least squares estimator [11]. The quality of this preprocessing pipeline was then assessed qualitatively for gross errors and quantitatively analyzed using a three-step
approach. In the first step, the preprocessed data were analyzed in accordance with the method outlined by Lauzon et al. [12]. The brain parenchyma without CSF were masked in a restrictive manner by using an eroded brain mask generated
on the average b0 image using the bet2 function included with FSL [13]. Then, the tensor fits of the masked data were backpropagated through the diffusion model to reconstruct the original diffusion signal. The goodness-of-fit for the tensor
model was then assessed using a modified pixel chi-squared value per slice per volume. In the second step, the tensor fit was converted to a fractional anisotropy (FA) image [14][15]. The ICBM FA MNI atlas with 48 white matter tract labels
provided with FSL were then non-rigidly registered to the subject's FA image with the ANTs software package [16][17][18][19]. The average FA for each tract was then quantified and assessed for physiologic congruence. Lastly, the gradient
orientations were visualized and checked using the dwigradcheck script included with MRTrix [20].

References:

[1] Tournier, J. D. et al. (2019). MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 116137.
[2] Jenkinson, M. et al. (2012). Fsl. Neuroimage, 62(2), 782-790.
[3] Tustison, N. J. et al. (2014). Large-scale evaluation of ANTs and FreeSurfer cortical thickness measurements. Neuroimage, 99, 166-179.
[4] Veraart, J. et al. (2016). Denoising of diffusion MRI using random matrix theory. Neuroimage, 142, 394-406.
[5] Veraart, J. et al. (2016). Diffusion MRI noise mapping using random matrix theory. Magnetic resonance in medicine, 76(5), 1582-1593.
[6] Cordero-Grande, L. et al. (2019). Complex diffusion-weighted image estimation via matrix recovery under general noise models. NeuroImage, 200, 391-404.
[7] Andersson, J. L. et al. (2003). How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. Neuroimage, 20(2), 870-888.
[8] Smith, S. M. et al. (2004). Advances in functional and structural MR image analysis and implementation as FSL. Neuroimage, 23, S208-S219.
[9] Andersson, J. L. et al. (2016). An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. Neuroimage, 125, 1063-1078.
[10] Andersson, J. L. et al. (2016). Incorporating outlier detection and replacement into a non-parametric framework for movement and distortion correction of diffusion MR images. NeuroImage, 141, 556-572.
[11] Veraart, J. et al. (2013). Weighted linear least squares estimation of diffusion MRI parameters: strengths, limitations, and pitfalls. Neuroimage, 81, 335-346.
[12] Lauzon, C. B. et al. (2013). Simultaneous analysis and quality assurance for diffusion tensor imaging. PloS one, 8(4).
[13] Smith, S. M. (2002). Fast robust automated brain extraction. Human brain mapping, 17(3), 143-155.
[14] Basser, P. J. et al. (1994). MR diffusion tensor spectroscopy and imaging. Biophysical journal, 66(1), 259-267.
[15] Westin, C. F. (1997). Geometrical diffusion measures for MRI from tensor basis analysis. Proc. ISMRM'97.
[16] Mori, S. et al. (2005). MRI atlas of human white matter. Elsevier.
[17] Wakana, S. et al. (2007). Reproducibility of quantitative tractography methods applied to cerebral white matter. Neuroimage, 36(3), 630-644.
[18] Hua, K. et al. (2008). Tract probability maps in stereotaxic spaces: analyses of white matter anatomy and tract-specific quantification. Neuroimage, 39(1), 336-347.
[19] Avants, B. B. et al. (2008). Symmetric diffeomorphic image registration with cross-correlation: evaluating automated labeling of elderly and neurodegenerative brain. Medical image analysis, 12(1), 26-41.
[20] Jeurissen, B. et al. (2014). Automated correction of improperly rotated diffusion gradient orientations in diffusion weighted MRI. Medical image analysis, 18(7), 953-962.

# dmriprep qc
The DMRIprep quality control process includes an automated check for the FA value of five specific bundles. These bundles are:

    - "Genu_of_corpus_callosum_med_fa" 
    - "Body_of_corpus_callosum_med_fa"
    - "Splenium_of_corpus_callosum_med_fa"
    - "Corticospinal_tract_L_med_fa"
    - "Corticospinal_tract_R_med_fa"

The acceptable range for their FA values is from 0.3 to 0.75.