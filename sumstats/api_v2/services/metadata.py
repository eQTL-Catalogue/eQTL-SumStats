"""
Metadata interface
"""

from sumstats.api_v2.services.main import HDF5Interface


class MetadataService(HDF5Interface):
    def __init__(self, hdf5: str, size: int, start: int, **kwargs):
        super().__init__(hdf5=hdf5)
    
    def get_many(self):
        return [{'study_id': 'hello'}, {'study_id': 'world'}]
        
    