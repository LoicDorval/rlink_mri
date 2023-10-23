# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2023
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Imports
import subprocess


def qc(datadir, regex, outdir, simg_file,
       cmd=None, sub_idx=-4, thr_low=0.3, thr_up=0.75):
    """ Launch the dMRI pre-processing quality control workflow.

    Parameters
    ----------
    datadir: str
        folder to mount inside the containeur, must contain the data and the
        outdir (derivatives folder should be ok).
    regex: str
        regex to the dmriprep 'stats.csv' files.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str
        path to the brainprep singularity image.
    cmd: str, default None
        path to the local install of brainprep.
    sub_idx: int, default -4
        the position of the subject identifier in the input path.
    thr_low: float, defaultt 0.3
        FA lower treshold for outlier selection.
    thr_up: float, default 0.75
        FA upper treshold for outlier selection.
    """
    if cmd is None:
        cmd = (f"singularity run --bind {datadir} --cleanenv "
               f"{simg_file} brainprep dmriprep-qc ")
    else:
        cmd = f"python3 {cmd} dmriprep-qc "
    cmd += (f"--data_regex {regex} "
            f"--outdir {outdir} "
            f"--sub_idx {sub_idx} "
            f"--thr_low {thr_low} "
            f"--thr_up {thr_up}")
    with subprocess.Popen(cmd.split(" "),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            print(line.decode("utf8"))


if __name__ == "__main__":
    import fire
    fire.Fire(qc)
