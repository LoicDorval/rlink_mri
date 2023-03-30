# li2mni processings

See the [main documentation](https://github.com/rlink7/rlink_mri/blob/main/README.md) for an overview of the processings.  
The code is organized in two parts:
* **runtime.py**: perform the analysis with hopla (by default in a multi-cpus setting).
* **qc1.py**: Perform the creation of the .csv to manually do the quality check for the T1wLi file and all the Li part-mag lithium images.
visual qc code for T1wLi:
1 : good -> accepted
2 : middle quality -> accepted
3 : bad -> rejected
* **qc2.py**: Perform the creation of the .csv to manually do the quality check on the li2mni preprocessing.
quality check step:

1) check afine comparing li2hanat and hanat
2) check registration of hanat on mni by comparing to mni template.
3) check registration of li2mni et li2mnianat on mni by comparing to mni template

visual qc code:
1 : good quality -> accepted
2 : medium quality -> accepted
3 : bad -> rejected
