# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2023
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Imports
import sys
import os
import glob
import shutil
import datetime
from hopla.converter import hopla


def run(datadir, outdir, simg_file=None, target=None, target_skel=None,
        name="tbss", process=False, njobs=10, use_pbs=False, cmd=None,
        test=False):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS rawdata directory.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str, default None
        path to the brainprep singularity image.
    target: str, default None
        optionally define a target image to use during the non-linear
        registration, otherwise use the **FMRIB58_FA_1mm** target.
    target_skel: str, default None
        optionally define a target skeleton image for TBSS prestats.
    name: str, default 'tbss-preproc'
        the name of the cirrent analysis.
    process: bool, default False
        optionnaly launch the process.
    njobs: int, default 10
        the number of parallel jobs.
    use_pbs: bool, default False
        optionnaly use PBSPRO batch submission system.
    cmd: str, default None
        the command to execute.
    test: bool, default False
        optionnaly, select only one subject.
    """
    files = glob.glob(os.path.join(
        datadir, "sub-*", "ses-*", "SCALARS", "dwmri_tensor_fa.nii.gz"))
    tbss_dir = os.path.join(outdir, name)
    tbss_md_dir = os.path.join(tbss_dir, "MD")
    if not os.path.isdir(tbss_md_dir):
        os.makedirs(tbss_md_dir)
    fa_files, md_files = [], []
    for fa_file in files:
        sub, ses = fa_file.split(os.sep)[-4: -2]
        final_file = os.path.join(tbss_dir, "FA",
                                  f"{sub}_{ses}_FA_to_target_warp.msf")
        if os.path.isfile(final_file):
            continue
        md_file = os.path.join(os.path.dirname(fa_file),
                               "dwmri_tensor_md.nii.gz")
        assert os.path.isfile(md_file), "No MD file."
        dest_fa_file = os.path.join(tbss_dir, f"{sub}_{ses}.nii.gz")
        if not os.path.isfile(dest_fa_file):
            shutil.copy(fa_file, dest_fa_file)
        fa_files.append(dest_fa_file)
        dest_md_file = os.path.join(tbss_md_dir, f"{sub}_{ses}.nii.gz")
        if not os.path.isfile(dest_md_file):
            shutil.copy(md_file, dest_md_file)
        md_files.append(dest_md_file)
    if len(fa_files) == 0:
        process = False
    if test:
        fa_files = fa_files[:1]
        md_files = md_files[:1]
    print(f"number of FA: {len(fa_files)}")
    if len(fa_files) > 0:
        header = ["fa", "md", "hanat", "outdir"]
        print("{:>40} {:>40}".format(*header))
        first = [item[0].replace(tbss_dir, "")
                 for item in (fa_files, md_files)]
        print("{:>40} {:>40}".format(*first))
        print("...")
        last = [item[-1].replace(tbss_dir, "")
                for item in (fa_files, md_files)]
        print("{:>40} {:>40}".format(*last))
    if cmd is None:
        cmd = (f"singularity run --bind {os.path.dirname(datadir)} "
               f"--cleanenv  {simg_file} brainprep tbss-preproc")
    else:
        cmd = f"{cmd} tbss-preproc"

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
        status, exitcodes = hopla(
            cmd,
            outdir=tbss_dir,
            fa_file=fa_files,
            target=target,
            hopla_name_replace=True,
            hopla_iterative_kwargs=["fa-file"],
            hopla_optional=["fa-file", "outdir"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)

    cmd = [
        "python", cmd.replace("tbss-preproc", "tbss"),
        "--outdir", tbss_dir,
        "--target", target,
        "--target-skel", target_skel]
    cmd = " ".join(cmd)
    print(cmd)


if __name__ == "__main__":
    import fire
    fire.Fire(run)
