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
import collections
from hopla.converter import hopla


def run(datadir, outdir, simg_file=None, cmd=None, name="dmriprep-qc",
        process=False, njobs=10):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS derivatives dmriprep directory.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str
        path to the brainprep singularity image.
    cmd: str, default None
        optionnaly, overload the execution command.
    name: str, default 'dmriprep-qc'
        the name of the cirrent analysis.
    process: bool, default False
        optionnaly launch the process.
    njobs: int, default 10
        the number of parallel jobs.
    """
    regex = os.path.join(datadir, "sub-*", "ses-*", "STATS", "stats.csv")
    _outdir = os.path.join(outdir, name)
    if not os.path.isdir(_outdir):
        os.makdir(_outdir)
    if process:
        date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        logdir = os.path.join(outdir, "logs")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logfile = os.path.join(logdir, f"{name}_{date}.log")
        if cmd is None:
            cmd = (f"singularity run --bind {os.path.dirname(datadir)} "
                   f"--cleanenv  {simg_file} brainprep dmriprep-qc")
        else:
            cmd = f"{cmd} dmriprep-qc"
        status, exitcodes = hopla(
            cmd,
            data_regex=[f"'{regex}'"],
            outdir=_outdir,
            hopla_name_replace=True,
            hopla_iterative_kwargs=["data-regex"],
            hopla_optional=["data-regex", "outdir"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None)


if __name__ == "__main__":
    fire.Fire(run)
