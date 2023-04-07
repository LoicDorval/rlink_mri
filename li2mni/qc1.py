# System import
import fire
import os
import nibabel
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import tempfile
from pdf2image import convert_from_path
import pandas as pd


def create_pdf(png_folder, pdf_output, pattern, font):
    with tempfile.TemporaryDirectory() as tmpdir:
        images = []
        titles = []
        for name in os.listdir(png_folder):
            if pattern == "Li":
                if name.endswith('ses-M03Li_acq-trufi'
                                 '_run-1_part-mag_limr.png'):
                    images.append(Image.open(os.path.join(png_folder, name))
                                  .convert('RGB'))
                    titles.append(name)
            if pattern == "T1wLi":
                if name.endswith('.png'):
                    images.append(Image.open(os.path.join(png_folder, name))
                                  .convert('RGB'))
                    titles.append(name)
        # # Create the font and size for the title
        font = ImageFont.truetype(font, size=70)

        # Add the title to each image
        for idx, image in enumerate(images):
            # Create a new ImageDraw object
            draw = ImageDraw.Draw(image)
            # Set the position and text for the title
            title = titles[idx]
            x = 20
            y = 20
            # Draw the title on the image
            draw.text((x, y), title, font=font, fill=(0, 0, 0))
            # Save the image as a PDF page
            tmp_outdir = os.path.join(tmpdir + '/page{}.pdf'.format(idx + 1))
            image.save(tmp_outdir, 'PDF',
                       resolution=100.0)
        # Merge the PDF pages into a single file
        pdf_pages = [convert_from_path(os.path.join(tmpdir, i))[0]
                     for i in os.listdir(tmpdir)
                     if i.endswith(".pdf")]
        pdf_pages[0].save(pdf_output, 'PDF', resolution=100.0, save_all=True,
                          append_images=pdf_pages[1:])
    df_qc = pd.DataFrame({"sub": titles, "qc": 1})
    df_qc.to_csv(pdf_output.replace(".pdf", ".csv"), sep="\t", index=False)


def make_png(anatomical, outdir, pattern="T1wli"):
    im = nibabel.load(anatomical)
    arr = im.get_fdata()

    outfile = os.path.join(outdir, f"{pattern}.png")
    plotting.plot_anat(im, display_mode="z",
                       cut_coords=25, black_bg=True,
                       output_file=outfile)
    arr = plt.imread(outfile)
    cut = int(arr.shape[1] / 5)
    plt.figure(figsize=(10, 10))
    arr = np.concatenate(
        [arr[:, idx * cut: (idx + 1) * cut] for idx in range(5)], axis=0)
    plt.imshow(arr)
    plt.axis("off")
    plt.savefig(outfile, dpi=300)
    plt.close()


def get_anat(path):
    with open(path) as flux:
        lignes = flux.readlines()
        for i in range(len(lignes)):
            lignes[i] = lignes[i].replace("\n", "")
    return lignes


def psc2_to_site(psc2, ses, df):
    return df[df["participant_id"] == psc2][f"{ses}_center"].values[0]


def all(list_nii, outdir, font, pattern="T1wli", skip_png=False,
        participants=None, skip_pdf=False):
    """ Launch the lithium rawdata quality control workflow.

    Parameters
    ----------
    list_nii: str
        path to a .txt with one line per .nii.gz
    pattern: str
        should be Li or T1wLi
    outdir: str
        path to the destination folder.
    font:
        path to the font file .ttf
    Optionnal
    ---------
    skip_png: bool
        skip png creation step.
    skip_pdf: float
        skip pdf creation step.
    participants: str
        path to the participants.tsv file (in order to get site in the qc.csv)
    """
    print("Start")
    if skip_png is False:
        path_images = get_anat(list_nii)
        count_max = len(path_images)
        for index, image in enumerate(path_images):
            pattern_png = os.path.basename(image).rstrip(".nii.gz")
            make_png(image, outdir, pattern=pattern_png)
            print(f"{index+1}/{count_max}")
    outdir_png = os.path.join(outdir, f"concat_{pattern}.pdf")
    print("making pdf")
    if skip_pdf is False:
        create_pdf(outdir, outdir_png, pattern, font)
    csv = outdir_png.replace(".pdf", ".csv")
    print("making csv")
    if participants is not None:
        df_participants = pd.read_csv(participants, sep="\t").fillna(0)
    df = pd.read_csv(csv, sep="\t")
    df["site"] = 0
    print(df)
    if pattern == "T1wLi":
        df["rec"] = ""
    for index, row in df.iterrows():
        psc2 = row["sub"].split("_")[0]
        ses = row["sub"].split("_")[1]
        if participants is not None:
            site = psc2_to_site(psc2, ses, df_participants)
            df.loc[index, "site"] = site
        df.loc[index, "sub"] = f"sub-{psc2}"
        if pattern == "T1wLi":
            df.loc[index, "rec"] = row["sub"].split("rec-")[1].split("_")[0]
    df["ses"] = "M03Li"
    df["visual_qc_score"] = 0
    df.rename(columns={"sub": "participant_id"}, inplace=True)
    if pattern == "T1wLi":
        df = df.reindex(columns=["participant_id", "ses", "site", "rec",
                                 "visual_qc_score", "qc"])
    else:
        df = df.reindex(columns=["participant_id", "ses", "site",
                                 "visual_qc_score", "qc"])

    df.sort_values(by=['participant_id'], inplace=True)
    print(df)
    df.to_csv(os.path.join(outdir, "qc.csv"), sep="\t", index=False)


if __name__ == "__main__":
    fire.Fire(all)
