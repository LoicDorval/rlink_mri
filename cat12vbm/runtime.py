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


def iter_replace(item, replace, by):
    """ Iteratively replace by.
    """
    if not isinstance(item, list):
        return item
    return [sub_item.replace(replace, by) if isinstance(sub_item, str)
            else sub_item for sub_item in item]


def run(datadir, outdir, simg_file, name="cat12vbm", process=False, njobs=10,
        use_pbs=False, test=False):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS rawdata directory.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str
        path to the brainprep singularity image.
    name: str, default 'cat12vbm'
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
    anat_files, sessions, sub_outdirs, is_longs = [], [], [], []
    for subject in os.listdir(datadir):
        _long_anat_files = []
        _long_sessions = []
        for session in ("ses-M00", "ses-M03"):
            sesdir = os.path.join(datadir, subject, session)
            if not os.path.isdir(sesdir):
                print(f"no '{sesdir}' session available!")
                continue
            _anat_files = glob.glob(os.path.join(
                sesdir, "anat", f"sub-*_{session}_*T1w.nii.gz"))
            _long_anat_files.append(get_best_anat(_anat_files))
            _long_sessions.append(session)
        if len(_long_anat_files) == 0:
            continue
        _outdir = os.path.join(outdir, name, subject)
        if not os.path.isdir(_outdir):
            os.makedirs(_outdir)
        if len(_long_anat_files) > 1:
            is_longs.append(True)
        else:
            is_longs.append(False)
        anat_files.append(_long_anat_files)
        sessions.append(_long_sessions)
        sub_outdirs.append(_outdir)
    if len(anat_files) == 0:
        raise RuntimeError("No data to process!")
    if test:
        anat_files = anat_files[:1]
        sessions = sessions[:1]
        is_longs = is_longs[:1]
        sub_outdirs = sub_outdirs[:1]
    print(f"number of runs: {len(anat_files)}")
    header = ["anat", "session", "longitudinal", "outdir"]
    print("{:>8} {:>8} {:>8} {:>8}".format(*header))
    first = [iter_replace(iter_replace(item[0], datadir, ""), outdir, "")
             for item in (anat_files, sessions, is_longs, sub_outdirs)]
    print("{} {} {} {}".format(*first))
    print("...")
    last = [iter_replace(iter_replace(item[-1], datadir, ""), outdir, "")
            for item in (anat_files, sessions, is_longs, sub_outdirs)]
    print("{} {} {} {}".format(*last))

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
        cmd = (f"singularity run --bind {os.path.dirname(datadir)} --cleanenv "
               f"{simg_file} brainprep cat12vbm")
        status, exitcodes = hopla(
            cmd,
            anatomical=anat_files,
            outdir=sub_outdirs,
            session=sessions,
            longitudinal=is_longs,
            model_long=1,
            hopla_name_replace=True,
            hopla_iterative_kwargs=["anatomical", "outdir", "session",
                                    "longitudinal"],
            hopla_optional=["anatomical", "outdir", "session", "longitudinal"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)


if __name__ == "__main__":
    fire.Fire(run)
