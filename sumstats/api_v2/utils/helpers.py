"""
General helper functions
"""


import os
from sumstats.api_v2.config import (HDF5_ROOT_DIR,
                                    HDF5_DATA_DIR,
                                    HDF5_METADATA_DIR,
                                    HDF5_EXT)


def get_hdf5_path(label: str, type=None):
    if type == "data":
        hdf_path = _construct_path(par_dir=HDF5_DATA_DIR,
                                   label=label)
    elif type == "metadata":
        hdf_path = _construct_path(par_dir=HDF5_METADATA_DIR,
                                   label=label)
    else:
        raise ValueError("Can't construct HDF5 path "
                         "because the type is neither data "
                         "or metadata.")
    return hdf_path


def _construct_path(par_dir, label):
    return os.path.join(HDF5_ROOT_DIR, par_dir, label + HDF5_EXT)
