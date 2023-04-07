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
import glob
import pandas as pd


def psc2_to_site(psc2, ses, df):
    return df[df["participant_id"] == psc2][f"{ses}_center"].values[0]


def make_csv(hanat_regex, outdir, template_mni=None, participants=None):
    """ Launch the li2mni preprocessing quality control workflow.

    Parameters
    ----------
    hanat_regex: str
        regex to hanat.nii.gz files
    outdir: str
        path to the destination folder.
    template_mni: str, default None
        path to the mni template nifti file.
    participants: str, default None
        path to the participants.tsv file (in order to get site in the qc.csv)
    """
    list_sujet_hanat = glob.glob(hanat_regex)
    list_sujet = [path.split(os.sep)[-3] for path in list_sujet_hanat]
    roots = [path.split("hanat")[0] for path in list_sujet_hanat]
    fsl_commands = []
    for root in roots:
        fsleyes = (f'export TMP_DIR_FOR_FSL="{root}"; '
                   'fsleyes $TMP_DIR_FOR_FSL/li2hanat.nii.gz '
                   '$TMP_DIR_FOR_FSL/hanat.nii.gz '
                   '$TMP_DIR_FOR_FSL/h2mnianat.nii.gz '
                   '$TMP_DIR_FOR_FSL/li2mnianat.nii.gz '
                   '$TMP_DIR_FOR_FSL/li2mni.nii.gz '
                   f'{template_mni or ""}')
        print(fsleyes)
        fsl_commands.append(fsleyes)

    df_qc = pd.DataFrame({"participant_id": list_sujet,
                          "fsleyes": fsl_commands})
    df_qc["ses"] = "M03Li"
    df_qc["qc"] = 1
    if participants is not None:
        df_participants = pd.read_csv(participants, sep="\t")
    for index, row in df_qc.iterrows():
        psc2 = row["participant_id"]
        if participants is not None:
            site = psc2_to_site(psc2, "ses-M03Li", df_participants)
            df_qc.loc[index, "site"] = site
    df_qc = df_qc.reindex(columns=["participant_id", "ses", "site", "fsleyes",
                                   "visual_qc_score", "qc"])
    df_qc.sort_values(by=['participant_id'], inplace=True)
    print(df_qc)
    df_qc.to_csv(os.path.join(outdir, "qc.csv"), sep="\t", index=False)


if __name__ == "__main__":
    import fire
    fire.Fire(make_csv)
