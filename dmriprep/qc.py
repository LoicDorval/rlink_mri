import fire
import subprocess


def qc(datadir, regex, outdir, simg_file,
       cmd=None, sub_idx=-4, thr_low=0.3, thr_up=0.75):
    """ Launch the dMRI pre-processing quality control workflow.

    Parameters
    ----------
    datadir: str
        folder to mount inside the containeur, must contain the data and the
        outdir. (derivatives folder should be ok)
    regex: str
        regex to the dmriprep 'stats.csv' files.
    outdir: str
        path to the destination folder.

    Optionnal
    ---------
    cmd: str
        path to the local install of brainprep.
    thr_low: float
        lower treshold for outlier selection.
    thr_up: float
        upper treshold for outlier selection.
    sub_idx: int, default -4
        the position of the subject identifier in the input path.
    """
    if cmd is None:
        _cmd = (f"singularity run --bind {datadir} --cleanenv "
                f"{simg_file} brainprep dmriprep-qc "
                f"--data_regex {regex} "
                f"--outdir {outdir} "
                f"--sub_idx {sub_idx} "
                f"--thr_low {thr_low} "
                f"--thr_up {thr_up}")
    else:
        _cmd = "python3 " + cmd + (" dmriprep-qc "
                                   f"--data_regex {regex} "
                                   f"--outdir {outdir} "
                                   f"--sub_idx {sub_idx} "
                                   f"--thr_low {thr_low} "
                                   f"--thr_up {thr_up}")
    with subprocess.Popen(_cmd.split(' '),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            print(line.decode('utf8'))


if __name__ == "__main__":
    fire.Fire(qc)
