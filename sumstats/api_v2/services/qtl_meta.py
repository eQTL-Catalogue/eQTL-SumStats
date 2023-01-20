"""
Metadata interface
"""

import pandas as pd

from sumstats.api_v2.config import HDF5_QTL_METADATA_LABEL
from sumstats.api_v2.services.main import HDF5Interface
from sumstats.api_v2.utils.helpers import get_hdf5_path, get_hdf5_dir
from sumstats.api_v2.schemas.eqtl import (QTLMetadataFilterable,
                                          CommonParams)


class QTLMetadataService(HDF5Interface):
    def __init__(self, qtl_meta_hdf5=HDF5_QTL_METADATA_LABEL):
        self.hdf5 = get_hdf5_path(type="metadata",
                                  label=qtl_meta_hdf5)
        self.par_dir = get_hdf5_dir(type="metadata")

    def get_many(self, params: CommonParams,
                 filters: QTLMetadataFilterable):
        # construct select statement self.select()
        return self.select()
        #return [{'study_id': 'hello'}, {'study_id': 'world'}]

