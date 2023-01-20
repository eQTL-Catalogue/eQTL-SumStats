"""
General helper functions
"""


import os
import pathlib
from sumstats.api_v2.config import (HDF5_ROOT_DIR,
                                    HDF5_DATA_DIR,
                                    HDF5_METADATA_DIR,
                                    HDF5_EXT)


def get_hdf5_path(label: str, type=None):
    hdf_path = _construct_path(par_dir=get_hdf5_dir(type=type),
                               label=label)
    return hdf_path


def get_hdf5_dir(type=None):
    if type == "data":
        return os.path.join(HDF5_ROOT_DIR, HDF5_DATA_DIR)
    elif type == "metadata":
        return os.path.join(HDF5_ROOT_DIR, HDF5_METADATA_DIR)
    else:
        raise ValueError("Can't construct HDF5 path "
                         "because the type is neither data "
                         "or metadata.")


def _construct_path(par_dir, label):
    return os.path.join(par_dir, label + HDF5_EXT)


def mkdir(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)


def properties_from_model(model, key) -> dict:
    props = {}
    for field_name, field in model.schema()["properties"].items():
        if key in field:
            props[field_name] = field.get(key)
    return props