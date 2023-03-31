# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2023
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


# Imports
import os
import fire
import datetime
from hopla.converter import hopla


def run(cat12dir, outdir, simg_file, name="cat12vbm_qc", process=False,
        njobs=10, use_pbs=False, test=False):
    """ Parse data and execute the processing with hopla.
    Parameters
    ----------
    cat12dir: str
        path to the BIDS cat12 derivatives directory.
    outdir: str
        path to the output directory.
    simg_file: str
        path to the brainprep singularity image.
    name: str, default 'cat12vbm_qc'
        the name of the current analysis.
    process: bool, default False
        optionnaly launch the process.
    njobs: int, default 10
        the number of parallel jobs.
    use_pbs: bool, default False
        optionnaly use PBSPRO batch submission system.
    """

    imgs = [f"{cat12dir}/sub-*/ses-*/mri/mwp1usub*_T1w.nii",
            f"{cat12dir}/sub-*/ses-*/mri/mwp1rusub*_T1w.nii"]
    reports = [f"{cat12dir}/sub-*/ses-*/report/cat_usub-*_T1w.xml",
               f"{cat12dir}/sub-*/ses-*/report/cat_rusub-*_T1w.xml"]

    outdirs = [os.path.join(outdir, dir) for dir in (name, f"{name}_long")]
    for dir in outdirs:
        if not os.path.isdir(dir):
            os.makedirs(dir)

    if process:
        pbs_kwargs = {}
        if use_pbs:
            clusterdir = os.path.join(outdir, f"{name}_pbs")
            if not os.path.isdir(clusterdir):
                os.makedirs(clusterdir)
            pbs_kwargs = {
                "hopla_cluster": True,
                "hopla_cluster_logdir": clusterdir,
                "hopla_cluster_queue": "Nspin_long"}
        date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        logdir = os.path.join(outdir, "logs")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logfile = os.path.join(logdir, f"{name}_{date}.log")
        cmd = (f"singularity run --bind {cat12dir} --bind {outdir} --cleanenv"
               f" {simg_file} brainprep cat12vbm-qc")
        status, exitcodes = hopla(
            cmd,
            img_regex=imgs,
            qc_regex=reports,
            outdir=outdirs,
            hopla_iterative_kwargs=["img_regex", "qc_regex", "outdir"],
            hopla_optional=["img_regex", "qc_regex", "outdir"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)


if __name__ == "__main__":
    fire.Fire(run)
