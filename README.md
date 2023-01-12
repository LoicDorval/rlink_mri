## Usage

![PythonVersion](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue)
![License](https://img.shields.io/badge/License-CeCILLB-blue.svg)
![PoweredBy](https://img.shields.io/badge/Powered%20by-CEA%2FNeuroSpin-blue.svg)

# R-Link MRI processings.

The following processings are available in the derivatives folder.

## quasiraw

Simple affine (no shearing) registration to the MNI template space from
T1w MRIs.

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> Minimally preprocessed data is generated using ANTS (<b>Avants et al. (2009)</b>) bias field correction, FSL FLIRT (<b>Jenkinson and Smith (2001)</b>) with a 9 degrees of freedom (no shearing) affine transformation to register data to the MNI template, and the application of a brain mask to remove non-brain tissues in the final images.
    <br><br>
    <b>Quality control:</b> First, we compute the correlation between each image and the mean of every other images to sort them by increasing correlation score. Then, images are manually inspected in-house following this sorting, and a first threshold is set to remove the first outlier images. Additionally, we use the average correlation (using Fisher's z-transform) between registered images as a metric of quality and we retained only images at a threshold higher than 0.5.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>

## cat12vbm

Voxel-wise estimation of the local amount or volume of a specific tissue
compartment from T1w MRIs. Use the longitudinal option to refine results.

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> Voxel-Based Morphometry (VBM) is performed with CAT12 (<b>Gaser and Dahnke (2016)<:b>). The analysis stream includes non-linear spatial registration to the MNI template, Gray Matter (GM), White Matter (WM), and CerebroSpinal Fluid (CSF) tissues segmentation, bias correction of intensity non-uniformities, and segmentations modulation by scaling with the amount of volume changes due to spatial registration. VBM is applied to investigate the GM, and the longitudinal model allows the detection of small changes, such as brain plasticity or treatement effects after a few weeks or months. The sensitivity of VBM in the WM is low, and usually, diffusion-weighted imaging is preferred for that purpose. For this reason, only the modulated GM images is considered. Moreover, CAT12 computes GM volumes averaged on the Neuromorphometrics atlas that includes 284 brain cortical and sub-cortical ROIs.
    <br><br>
    <b>Quality control:</b> We performe the same in-house QC visual analysis as for quasi-raw images. Additionally, we also monitored the Noise Contrast Ratio (NCR) and Image Quality Rating (IQR) as two metrics of quality and we retained only images at a threshold below 4.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>

## freesurfer

Parcellisation and segmentation of structural T1w MRI data with FreeSurfer.
Use the longitudinal option to refine results.

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> Cortical analysis is performed with FreeSurfer <i>recon-all</i>. The analysis stream includes intensity normalization, skull stripping, segmentation of GM (pial) and WM, hemispheric-based tessellations, topology corrections and inflation, and registration to the <i>fsaverag</i> template. Available morphological measures are summarized on the Desikan (<b>Desikan et al. (2006)</b>) and Destrieux (<b>Fischl et al. (2004)</b>) parcellations. Specifically, 7 ROI-based features computed both on Desikan and Destrieux atlases are shared including: the cortical thickness (mean and standard deviation), GM volume, surface area, integrated mean and Gaussian curvatures and intrinsic curvature index. Moreover, vertex-wise cortical thickness, curvature and average convexity features (<b>Fischl et al. (1999)</b>) (measuring the depth/height of a vertex above the average surface) are also accessible on the high-resolution seven order icosahedron. To allow inter-hemispheric cortical surface-based analysis, we further transform the right hemisphere features into the left one, using the symmetric <i>fsavarage_sym</i> Freesurfer template and the <i>xhemi</i> routines (<b>Greve et al. (2013)</b>). The final vertex-wise cortical features comprise 163,842 nodes per hemisphere.
    <br><br>
    <b>Quality control:</b> Similarly with quasi-raw and VBM, we first performe a visual analysis on images ranked by the correlation score. In addition we use the Euler number as a metric of quality and we retaine images at a threshold greater than -217, as specified in (<b>Rosen et al. (2018)</b>).
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>

  
## dmriprep

Preprocessing of DWI using topup susceptinility induced distortions
corrections.

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> coming soon.
    <br><br>
    <b>Quality control:</b> coming soon.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>

## tbss

Voxel-wise statistics on the skeletonized FA data using FA, MD, ...

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> coming soon.
    <br><br>
    <b>Quality control:</b> coming soon.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>

## li2mni

Registration of the Lithium image to the MNI template space using
intermediate Lithium and Hydrogen T1w images.

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
    <b>Copy/paste to your paper</b>
</p>
<p style='margin-left:1em;'>
    <b>Steps:</b> Lithium and Hydrogen T1w images are bias field corrected with FSL (<b>Jenkinson and Smith (2001)</b>). Then registration steps are performed with ANTS (<b>Avants et al. (2009)</b>). An affine transformation with 9 degrees of freedom (no shearing) coregisters the Lithium T1w and the Hydrogen T1w images, and an affine/non-linear deformation maps the Hydrogene T1w image to the 2mm isotropic MNI space. To automatically account for different field of views between the Lithium and Lithium T1w images, a translation is estimated from the eyes barycenters. Eyes in the Lithium images are detected by modeling the intensity distribution with a 2-components GMM. The second mode of the distribution enables the definition of a threshold to detect high-intensities locations. After morphological operations the two principal components are the eyes.
    <br><br>
    <b>Quality control:</b> coming soon.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'>
    <b>- NeuroSpin support team</b> <i>(Ways to Simplify Your Writing)</i>
</p>
</span>
</div>
