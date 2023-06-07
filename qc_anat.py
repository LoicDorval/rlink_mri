# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2023
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


# Imports
import pandas as pd
import os
import fire


def psc2_to_psc1(psc1, df):
    return df[df["psc2"] == int(psc1)]["psc1"].values[0]


def add_site(df, transcoding):
    list_psc1 = [psc2_to_psc1(df["participant_id"][i], transcoding)
                 for i in range(0, len(df["participant_id"]))]
    list_site = [str(list_psc1[i])[0:-3]
                 for i in range(0, len(df["participant_id"]))]
    df["site"] = list_site
    return df


def rename_dfcol(df, suffixe):
    new_col = []
    for i in range(len(df.columns)):
        if df.columns[i] in ["participant_id", "session", "run", "site"]:
            new_col.append(df.columns[i])
        else:
            new_col.append(df.columns[i] + suffixe)
    df.columns = new_col
    return df


def run(derivatives, outdir, transcoding=None):
    """ Concatenate the cat12vbm, freesurfer and quasiraw quality check to
        identify the images that pass all the QCs.
    Parameters
    ----------
    derivatives: str
        path to the derivatives directory where are the 3 qc folders, named as
        "cat12vbm_qc", "freesurfer_qc" and "quasiraw_qc".
    outdir: str
        path to the destination folder.
    Optionnal
    ---------
    transcoding: str
        path to the transcoding file (in order to get site in the qc.csv)
    """

    df_cat12 = pd.read_csv(os.path.join(derivatives, "cat12vbm_qc/qc.tsv"),
                           sep="\t")
    df_quasiraw = pd.read_csv(os.path.join(derivatives, "quasiraw_qc/qc.tsv"),
                              sep="\t")
    df_fs = pd.read_csv(os.path.join(derivatives, "freesurfer_qc/qc.tsv"),
                        sep="\t")
    filout = os.path.join(outdir, "qc_anat.xlsx")

    df_cat12 = rename_dfcol(df_cat12, "_cat12")
    df_quasiraw = rename_dfcol(df_quasiraw, "_quasiraw")
    df_fs = rename_dfcol(df_fs, "_fs")

    df_tmp = pd.merge(df_cat12, df_quasiraw, on=['participant_id', 'session',
                      'run'], how='outer')
    df_all = pd.merge(df_tmp, df_fs, on=['participant_id', 'session', 'run'],
                      how='outer')

    if transcoding is not None:
        transcoding = pd.read_csv(transcoding, sep="\t")
        df_all = add_site(df_all, transcoding)
    else:
        df_all["site"] = None

    QC = []
    for i in range(0, len(df_all["participant_id"])):
        if ((df_all["qc_cat12"][i] == 0) | (df_all["qc_fs"][i] == 0) |
           (df_all["qc_quasiraw"][i] == 0)):
            QC.append(0)
        else:
            QC.append(1)

    df_all["qc"] = QC
    print(df_all)
    df_all = df_all[["participant_id", "session", "site", "qc_cat12",
                    "qc_quasiraw", "qc_fs", "qc"]]
    print(df_all)
    writer = pd.ExcelWriter(filout)
    df_all.to_excel(writer, sheet_name="qc_anat")

    if transcoding is not None:
        # Par Site
        ind_site = [int(df_all["site"].unique()[i])
                    for i in range(0, len(df_all["site"].unique()))]

        for site in sorted(ind_site):
            df_site = df_all[(df_all["site"] == str(site))]
            nbQC = len(df_all[(df_all["site"] == str(site)) &
                       (df_all["qc"] == 1)])
            tot = len(df_all[df_all["site"] == str(site)])
            print(f"Site {site}: {nbQC} / {tot}")
            df_site.to_excel(writer, sheet_name=f"site{site}")
    writer.close()


if __name__ == "__main__":
    fire.Fire(run)
