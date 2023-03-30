import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import pandas as pd
import glob
import fire


def plot_hists(data, outdir, title=None):
    """ Plot hisograms with optional vertical bars.
    Parameters
    ----------
    data: dict
        containes the data to display in 'data' and optionnaly the coordianate
        of the vertical line in 'bar_low' and 'bar_up'.
    outdir: str
        the destination folder.
    title: str
        Title of the histogram.
    Returns
    -------
    snap: str
        the generated snap.
    """
    fig, axs = plt.subplots(len(data))
    if not isinstance(axs, np.ndarray):
        axs = [axs]
    for cnt, (name, item) in enumerate(data.items()):
        arr = item["data"].astype(np.single)
        arr = arr[~np.isnan(arr)]
        arr = arr[~np.isinf(arr)]
        sns.histplot(arr, color="gray", alpha=0.6, ax=axs[cnt],
                     kde=True, stat="density", label=name)
        coord_low = item.get("bar_low")
        coord_up = item.get("bar_up")
        if coord_low is not None:
            axs[cnt].axvline(x=coord_low, color="red")
        if coord_up is not None:
            axs[cnt].axvline(x=coord_up, color="red")
        axs[cnt].spines["right"].set_visible(False)
        axs[cnt].spines["top"].set_visible(False)
        axs[cnt].legend()
    plt.subplots_adjust(wspace=0, hspace=0, top=0.9, bottom=0.1)
    if title is not None:
        plt.title(title)
        snap_path = os.path.join(outdir, f"hists_{title}.png")
    else:
        snap_path = os.path.join(outdir, "hists.png")
    plt.savefig(snap_path)
    return snap_path


def brainprep_prequal_qc(data_regex, outdir, sub_idx=-4, thr_low=0.3,
                         thr_up=0.75):
    """ Define the dMRI pre-processing quality control workflow.

    Parameters
    ----------
    datadir: str
        regex to the dmriprep 'stats.csv' files.
    outdir: str
        path to the destination folder.

    Optionnal
    ---------
    thr_low: float
        lower treshold for outlier selection.
    thr_up: float
        upper treshold for outlier selection.
    sub_idx: int, default -4
        the position of the subject identifier in the input path.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt

    print("Loading PreQual dtiQA stats files...")
    stat_files = glob.glob(data_regex)
    stats = []
    for path in stat_files:
        df = pd.read_csv(path, index_col=0, header=None).T
        sid = path.split(os.sep)[sub_idx]
        ses = path.split(os.sep)[sub_idx+1]
        df["ses"] = ses
        df["participant_id"] = sid
        stats.append(df)
    df = pd.concat(stats)
    df.to_csv(os.path.join(outdir, "transformation.tsv"), sep="\t",
              index=False)
    print(os.path.join(outdir, "transformation.tsv"))
    print("Computing box plot by category...")
    for score_name in ("fa", "md", "rd", "ad"):
        _cols = [name for name in df.columns
                 if name.endswith(f"_{score_name}")]
        _df = pd.melt(df, id_vars=["participant_id"], value_vars=_cols,
                      var_name="metric", value_name="value")
        _df["label"] = _df.metric.values
        sns.set(style="whitegrid")
        ax = sns.boxplot(x="label", y="value", data=_df)
        plt.setp(ax.get_xticklabels(), rotation=90)
        ax.tick_params(labelsize=3.5)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{score_name}.png"), dpi=400)
    _cols = ["eddy_avg_rotations_x", "eddy_avg_rotations_y",
             "eddy_avg_rotations_z", "eddy_avg_translations_x",
             "eddy_avg_translations_y", "eddy_avg_translations_z",
             "eddy_avg_abs_displacement", "eddy_avg_rel_displacement"]
    _df = pd.melt(df, id_vars=["participant_id"], value_vars=_cols,
                  var_name="metric", value_name="value")
    sns.set(style="whitegrid")
    ax = sns.boxplot(x="metric", y="value", data=_df)
    plt.setp(ax.get_xticklabels(), rotation=90)
    ax.tick_params(labelsize=3.5)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "transformation.png"), dpi=400)

    print("Outlier hist")
    choosen_bundle = ["Genu_of_corpus_callosum_med_fa",
                      "Body_of_corpus_callosum_med_fa",
                      "Splenium_of_corpus_callosum_med_fa",
                      "Corticospinal_tract_L_med_fa",
                      "Corticospinal_tract_R_med_fa"]
    choosen_bundle_pid = choosen_bundle.copy()
    choosen_bundle_pid.append("participant_id")
    choosen_bundle_pid.append("ses")
    for fiber_bundle in choosen_bundle:
        data = {"fa": {"data": df[fiber_bundle].values,
                       "bar_low": thr_low,
                       "bar_up": thr_up}}
        snap = plot_hists(data, outdir, fiber_bundle)
        print(snap)
    result_df = df.loc[:, choosen_bundle_pid]
    result_df["qc"] = 1
    for faisceaux in choosen_bundle:
        result_df.loc[result_df[faisceaux] <= thr_low, 'qc'] = 0
        result_df.loc[result_df[faisceaux] >= thr_up, 'qc'] = 0
    result_df.sort_values(by=["qc"], inplace=True)
    result_df = result_df.reindex(columns=["participant_id", "ses"] +
                                  choosen_bundle +
                                  ["qc"])
    outdir_csv = os.path.join(outdir, "qc.tsv")
    result_df.to_csv(outdir_csv, index=False, sep="\t")
    print(outdir_csv)


fire.Fire(brainprep_prequal_qc)
