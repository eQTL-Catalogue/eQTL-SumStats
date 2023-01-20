"""
Metadata interface
"""

from sumstats.api_v2.config import HDF5_QTL_METADATA_LABEL
from sumstats.api_v2.services.main import HDF5Interface
from sumstats.api_v2.utils.helpers import get_hdf5_path
from sumstats.api_v2.schemas import (QTLMetadataFilterable,
                                     CommonParams)


class QTLMetadataService(HDF5Interface):
    def __init__(self):
        self.hdf5 = get_hdf5_path(type="metadata",
                                  label=HDF5_QTL_METADATA_LABEL)

    def get_many(self, params: CommonParams,
                 filters: QTLMetadataFilterable):
        return [{'study_id': 'hello'}, {'study_id': 'world'}]
