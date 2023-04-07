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
import json
import glob
import datetime
import traceback
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


def run(datadir, outdir, simg_file, name="dmriprep",
        process=False, njobs=10, use_pbs=False, test=False):
    """ Parse data and execute the processing with hopla.

    Parameters
    ----------
    datadir: str
        path to the BIDS rawdata directory.
    outdir: str
        path to the BIDS derivatives directory.
    simg_file: str
        path to the brainprep singularity image.
    name: str, default 'dmriprep'
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
    list_sub_ses = [
        path for path in glob.glob(os.path.join(datadir, "sub-*", "ses-*"))
        if os.path.isdir(path)]
    list_dwi, list_bvec, list_bval, list_pe, list_readout, list_outdir = (
        [], [], [], [], [], [])
    for sub_ses in list_sub_ses:

        # Check input DWI data
        _dwi = glob.glob(os.path.join(sub_ses, "dwi",
                                      "*_acq-DWI*_run-*_dwi.nii.gz"))
        _dwi.sort()
        if len(_dwi) != 2:
            print(f"The current session don't have 2 valid TOPUP DWI files: "
                  f"{sub_ses}")
            continue
        dwi_files = ",".join(_dwi)
        _bvec = glob.glob(os.path.join(sub_ses, "dwi",
                                       "*_acq-DWI*_run-*_dwi.bvec"))
        _bvec.sort()
        if len(_bvec) != 2:
            print(f"The current session don't have 2 BVEC files: "
                  f"{sub_ses}")
            continue
        bvec_files = ",".join(_bvec)
        _bval = glob.glob(os.path.join(sub_ses, "dwi",
                                       "*_acq-DWI*_run-*_dwi.bval"))
        _bval.sort()
        if len(_bval) != 2:
            print(f"The current session don't have 2 BVAL files: "
                  f"{sub_ses}")
            continue
        bval_files = ",".join(_bval)
        _json = glob.glob(os.path.join(sub_ses, "dwi",
                                       "*_acq-DWI*_run-*_dwi.json"))
        _json.sort()
        if len(_json) != 2:
            print(f"The current session don't have 2 JSON sidecars: "
                  f"{sub_ses}")
            continue

        # PhaseEncodingAxis and EstimatedTotalReadoutTime
        _pe = []
        _readout = []
        for path in _json:
            data = {}
            with open(path, "r") as of:
                try:
                    data = json.load(of)
                except:
                    traceback.print_exc()
                    continue
            if data.get("PhaseEncodingDirection") is not None:
                _pe.append(str(data["PhaseEncodingDirection"]))
            if data.get("TotalReadoutTime") is not None:
                _readout.append(str(data["TotalReadoutTime"]))
            if data.get("EstimatedTotalReadoutTime") is not None:
                _readout.append(str(data["EstimatedTotalReadoutTime"]))
        if len(_pe) != 2:
            print(f"The current session don't have 2 phase encoding axis: "
                  f"{sub_ses}")
            continue
        pe_extracted = ",".join(_pe)
        if len(_readout) != 2:
            print(f"The current session don't don't have 2 readout time: "
                  f"{sub_ses}")
            continue
        readout_extracted = ",".join(_readout)

        # Outdir
        only_sub_ses = os.sep.join(sub_ses.split("/")[-2:])
        _outdir = os.path.join(outdir, name, only_sub_ses)
        if not os.path.isdir(_outdir):
            os.makedirs(_outdir)

        # Append in list
        list_outdir.append(_outdir)
        list_dwi.append(dwi_files)
        list_bvec.append(bvec_files)
        list_bval.append(bval_files)
        list_pe.append(pe_extracted)
        list_readout.append(readout_extracted)
    if test:
        list_dwi = list_dwi[:1]
        list_bvec = list_bvec[:1]
        list_bval = list_bval[:1]
        list_pe = list_pe[:1]
        list_readout = list_readout[:1]
        list_outdir = list_outdir[:1]

    print(f"number of runs: {len(list_dwi)}")
    header = ["dwi", "bvec", "bval", "pe", "readout_time", "ouput_dir"]
    print("{:>8} {:>8} {:>8} {:>8}".format(*header))
    first = [item[0].replace(datadir, "").replace(outdir, "")
             for item in (list_dwi, list_bvec, list_bval, list_pe,
                          list_readout, list_outdir)]
    print("{:>8} {:>8} {:>8} {:>8}".format(*first))
    print("...")
    last = [item[-1].replace(datadir, "").replace(outdir, "")
            for item in (list_dwi, list_bvec, list_bval, list_pe,
                         list_readout, list_outdir)]
    print("{:>8} {:>8} {:>8} {:>8}".format(*last))

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
        cmd = (f"singularity run --bind {os.path.dirname(datadir)} "
               f"{simg_file} brainprep dmriprep")
        status, exitcodes = hopla(
            cmd,
            dwi=list_dwi,
            bvec=list_bvec,
            bval=list_bval,
            pe=list_pe,
            readout_time=list_readout,
            output_dir=list_outdir,
            hopla_iterative_kwargs=["dwi", "bvec", "bval",
                                    "pe", "readout_time", "output_dir"],
            hopla_optional=["dwi", "bvec", "bval",
                            "pe", "readout_time", "output_dir"],
            hopla_cpus=njobs,
            hopla_logfile=logfile,
            hopla_use_subprocess=True,
            hopla_verbose=1,
            hopla_python_cmd=None,
            **pbs_kwargs)


if __name__ == "__main__":
    import fire
    fire.Fire(run)
