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
import datetime


def print_files_modified_on_date(path, date):
    """ Recursively traverses a directory and prints information about each
    file that was modified on the specified date.

    Parameters
    ----------
    path: str
        The path to the directory to traverse.
    date: str
        The date to filter files by, in the format "YYYY-MM-DD".
    """
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    for root, dirs, files in os.walk(path):
        for basename in files:
            full_path = os.path.join(root, basename)
            last_modified_time = os.path.getmtime(full_path)
            last_modified_date = datetime.datetimefromtimestamp(
                last_modified_time).date()
            if last_modified_date == date_obj:
                print(f"{full_path} was last modified on {last_modified_date}")


if __name__ == "__main__":
    import fire
    fire.Fire(print_files_modified_on_date)
