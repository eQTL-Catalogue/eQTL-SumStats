"""
Summmary statistics data interface
"""

from sumstats.api_v2.services.main import HDF5Interface
from sumstats.api_v2.utils.helpers import get_hdf5_path, get_hdf5_dir


class QTLDataService(HDF5Interface):
    def __init__(self, hdf5_label: str):
        self.hdf5 = get_hdf5_path(type="data",
                                  label=hdf5_label)
        self.par_dir = get_hdf5_dir(type="data")
