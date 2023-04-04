# li2mni processings

See the [main documentation](https://github.com/rlink7/rlink_mri/blob/main/README.md) for an overview of the processings. 

The code is organized in two parts:

* **runtime.py**: performs the analysis with hopla (by default in a multi-cpus setting).
* **qc1.py**: creates the .csv to manually perform the quality check for the T1wLi file and all the Li part-mag lithium images. 

Visual QC code for T1wLi:
- 1 : good -> accepted
- 2 : middle quality -> accepted
- 3 : bad -> rejected

* **qc2.py**: creates the .csv to manually perform the quality check on the li2mni preprocessing.

Quality check steps:
- 1 : check affine comparing li2hanat and hanat
- 2 : check registration of hanat on mni.
- 3 : check registration of li2mni and li2mnianat.

Visual QC code:
- 1 : good quality -> accepted
- 2 : medium quality -> accepted
- 3 : bad -> rejected
