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


def run(datadir, outdir, template_dir, fs_license_file, simg_file,
        name="freesurfer_long", process=False, njobs=10, use_pbs=False,
        test=False):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS derivatives directory of the freesurfer process.
    outdir: str
        path to the BIDS derivatives directory.
    template_dir: str
        path to the fsaverage_sym template.
    fs_license_file: str
        path to the FreeSurfer license file.
    simg_file: str
        path to the brainprep singularity image.
    name: str, default 'freesurfer_long'
        the name of the current analysis.
    process: bool, default False
        optionnaly launch the process.
    njobs: int, default 10
        the number of parallel jobs.
    use_pbs: bool, default False
        optionnaly use PBSPRO batch submission system.
    test: bool, default False
        optionnaly, select only one subject.
    """
    subjects, sub_outdirs = [], []
    timepoints = ["ses-M00", "ses-M03"]
    fsdirs = [os.path.join(outdir, "freesurfer", tp) for tp in timepoints]
    for subject in os.listdir(datadir):
        session = 'ses-M03'
        sesdir = os.path.join(datadir, subject, session)
        if not os.path.isdir(sesdir):
            print(f"no '{sesdir}' session available!")
            continue
        _outdir = os.path.join(outdir, name, subject)
        if not os.path.isdir(_outdir):
            os.makedirs(_outdir)
        subjects.append(subject)
        sub_outdirs.append(_outdir)
    if test:
        subjects = subjects[:1]
        sub_outdirs = sub_outdirs[:1]
    print(f"number of runs: {len(subjects)}")
    header = ["subject", "outdir"]
    print("{:>8} {:>8}".format(*header))
    first = [item[0].replace(datadir, "").replace(outdir, "")
             for item in (subjects, sub_outdirs)]
    print("{:>8} {:>8}".format(*first))
    print("...")
    last = [item[-1].replace(datadir, "").replace(outdir, "")
            for item in (subjects, sub_outdirs)]
    print("{:>8} {:>8}".format(*last))

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
        cmd = (f"singularity run --bind {fs_license_file}:/opt/freesurfer/"
               f".license --bind {os.path.dirname(datadir)} --cleanenv "
               f"{simg_file} brainprep fsreconall-longitudinal")
        status, exitcodes = hopla(
            cmd,
            sid=subjects,
            fsdirs=fsdirs,
            outdir=sub_outdirs,
            timepoints=",".join(timepoints),
            template_dir=template_dir,
            hopla_name_replace=True,
            hopla_iterative_kwargs=["sid", "outdir"],
            hopla_optional=["sid", "outdir"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)


if __name__ == "__main__":
    fire.Fire(run)
