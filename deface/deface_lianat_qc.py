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
import glob
import datetime
from hopla.converter import hopla


def get_best_anat(files):
    """ Select the best anat file.
    """
    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        select = [path for path in files if "yGC" in path]
        assert len(select) == 1, files
        return select[0]
    else:
        raise ValueError("No anatomical file provided!")


def run(datadir, outdir, simg_file, cmd=None, name="deface", process=False,
        njobs=10, use_pbs=False, test=False):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS rawdata directory.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str
        path to the brainprep singularity image.
    cmd: str, default None
        optionnaly, overload the execution command.
    name: str, default 'deface'
        the name of the cirrent analysis.
    process: bool, default False
        optionnaly launch the process.
    njobs: int, default 10
        the number of parallel jobs.
    use_pbs: bool, default False
        optionnaly use PBSPRO batch submission system.
    test: bool, default False
        optionnaly, select only one subject.
    """
    anat_files, deface_anat_files, deface_roots = [], [], []
    for subject in os.listdir(datadir):
        for session in ("ses-M03Li", "ses-M03H"):
            sesdir = os.path.join(datadir, subject, session)
            if not os.path.isdir(sesdir):
                print(f"no '{sesdir}' session available!")
                continue
            if not os.path.isdir(os.path.join(sesdir, "anat")):
                print("no anat in ses-M03Li")
                continue
            _outdir = os.path.join(outdir, name, subject, session)
            if not os.path.isdir(_outdir):
                print(f"no '{outdir}' folder available!")
                continue
            _anat_files = glob.glob(os.path.join(
                sesdir, "anat", f"sub-*_{session}_*T1w.nii.gz"))
            best_anat = get_best_anat(_anat_files)
            basename = os.path.basename(best_anat)
            deface_anat = os.path.join(_outdir, basename)
            if not os.path.isfile(deface_anat):
                print(f"no '{deface_anat}' file!")
                continue
            anat_files.append(best_anat)
            deface_anat_files.append(deface_anat)
            root = os.path.join(
                _outdir, basename.replace("_T1w.nii.gz", "_defacemask"))
            deface_roots.append(root)
    if len(anat_files) == 0:
        raise RuntimeError("No data to process!")
    if test:
        anat_files = anat_files[:1]
        deface_anat_files = deface_anat_files[:1]
        deface_roots = deface_roots[:1]
    print(f"number of runs: {len(anat_files)}")
    header = ["anat", "deface", "root"]
    print("{:>8} {:>8} {:>8}".format(*header))
    first = [item[0].replace(datadir, "").replace(outdir, "")
             for item in (anat_files, deface_anat_files, deface_roots)]
    print("{:>8} {:>8} {:>8}".format(*first))
    print("...")
    last = [item[-1].replace(datadir, "").replace(outdir, "")
            for item in (anat_files, deface_anat_files, deface_roots)]
    print("{:>8} {:>8} {:>8}".format(*last))

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
        logfile = os.path.join(logdir, f"{name}-qc_{date}.log")
        if cmd is None:
            cmd = (f"singularity run --bind {os.path.dirname(datadir)} "
                   f"--cleanenv {simg_file} brainprep deface-qc")
        status, exitcodes = hopla(
            cmd,
            anatomical=anat_files,
            anatomical_deface=deface_anat_files,
            deface_root=deface_roots,
            thr_mask=0.6,
            hopla_name_replace=True,
            hopla_iterative_kwargs=["anatomical", "anatomical-deface",
                                    "deface-root"],
            hopla_optional=["anatomical", "anatomical-deface", "deface-root"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)


if __name__ == "__main__":
    fire.Fire(run)
