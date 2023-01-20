import os


"""
HDF5 file organisation:
HDF5_ROOT_DIR/
- HDF5_DATA_DIR/
- - dataset1.h5
- - dataset2.h5
- HDF5_METADATA_DIR/
- - HDF5_QTL_METADATA.h5
"""


def _get_env_var(name, default):
    var = os.environ.get(name) if os.environ.get(name) else default
    return var


HDF5_ROOT_DIR = _get_env_var("HDF5_ROOT_DIR", "eqtl_hdf5_files")
HDF5_DATA_DIR = _get_env_var("HDF5_DATA_DIR", "data")
HDF5_METADATA_DIR = _get_env_var("HDF5_METADATA_DIR", "metadata")
HDF5_QTL_METADATA_LABEL = _get_env_var("HDF5_QTL_METADATA_LABEL", "qtl_metadata")
HDF5_EXT = _get_env_var("HDF5_EXT", ".h5")
