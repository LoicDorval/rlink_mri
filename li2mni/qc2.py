import pandas as pd
import glob
import fire
import os


def psc2_to_psc1(psc2, df):
    return df[df["psc2"] == int(psc2)]["psc1"].values[0]


def make_csv(hanat_regex, outdir, template_mni="", transcoding=None):
    """ Launch the li2mni quality control workflow.

    Parameters
    ----------
    hanat_regex: str
        regex to hanat.nii.gz files
    outdir: str
        path to the destination folder.

    Optionnal
    ---------
    template_mni: str
        path to the mni template nifti file.
    transcoding: str
        path to the transcoding file (in order to get site in the qc.csv)
    """
    list_sujet_hanat = glob.glob(hanat_regex)
    list_sujet = [i.split("li2mni/")[1].split("/ses-M")[0]
                  for i in list_sujet_hanat]
    roots = [i.split("hanat")[0] for i in list_sujet_hanat]
    fsl_commands = []
    for i in roots:
        fsleyes = (f'export TMP_DIR_FOR_FSL="{i}"; '
                   'fsleyes $TMP_DIR_FOR_FSL/li2hanat.nii.gz '
                   '$TMP_DIR_FOR_FSL/hanat.nii.gz '
                   '$TMP_DIR_FOR_FSL/h2mnianat.nii.gz '
                   '$TMP_DIR_FOR_FSL/li2mnianat.nii.gz '
                   '$TMP_DIR_FOR_FSL/li2mni.nii.gz '
                   f'{template_mni}')
        print(fsleyes)
        fsl_commands.append(fsleyes)

    df_qc = pd.DataFrame({"participant_id": list_sujet,
                          "fsleyes": fsl_commands})
    df_qc["ses"] = "M03Li"
    df_qc["qc"] = 1
    if transcoding is not None:
        df_transcoding = pd.read_csv(transcoding, sep="\t")
    for index, row in df_qc.iterrows():
        psc2 = row["participant_id"].split("-")[1]
        if transcoding is not None:
            psc1 = str(psc2_to_psc1(psc2, df_transcoding))
            if len(psc1) == 5:
                site = psc1[0:2]
            elif len(psc1) == 4:
                site = psc1[0:1]
            df_qc.loc[index, "site"] = site

    df_qc = df_qc.reindex(columns=["participant_id", "ses", "site", "fsleyes",
                                   "visual_qc_score", "qc"])

    df_qc.sort_values(by=['participant_id'], inplace=True)
    print(df_qc)

    df_qc.to_csv(os.path.join(outdir, "qc.csv"), sep="\t", index=False)


fire.Fire(make_csv)
