"""
Summmary statistics data interface
"""

from sumstats.api_v2.services.main import HDF5Interface
from sumstats.api_v2.utils.helpers import get_hdf5_path, get_hdf5_dir


class QTLDataService(HDF5Interface):
    
    BP_DISTANCE = 1_000_000  # distance from genetic feature

    def __init__(self, hdf5_label: str):
        self.hdf5 = get_hdf5_path(type="data",
                                  label=hdf5_label)
        self.par_dir = get_hdf5_dir(type="data")

    def query(self, filters, start, size):
        """
        Convert: position query to select
                 rsID to postion
                 variant id tp position
                 gene_id to position +-1mb
                 trait to position +-1mb 
        """
        variant_search = filters.variant
        rsid_search = filters.rsid
        genomic_region_search = (filters.chromosome and
                                 filters.position_start and
                                 filters.position_end)
        genomic_context_search = (filters.gene_id or
                                  filters.molecular_trait_id)
        if variant_search:
            # TODO: parse variant 
            pass
        if rsid_search:
            # TODO: genomic_region_from_rsid()
            pass
        if genomic_region_search:
            return self.select(filters=filters,
                               key="sumstats",
                               start=start,
                               size=size)
        elif genomic_context_search:
            self._genomic_region_from_genomic_context(filters=filters,
                                                      start=start,
                                                      size=size)
        else:
            return self.select(filters=filters,
                               key="sumstats",
                               start=start,
                               size=size)

    def _genomic_region_from_genomic_context(self, filters, start, size):
        gc_filters = filters.copy(include={'gene_id',
                                           'molecular_trait_id'})
        region_to_search = self.select(filters=gc_filters,
                                       key="genomic_context")
        if len(region_to_search) > 0:
            first_record = region_to_search[0]
            chromosome, position = first_record['chromosome'], first_record['position']
            filters.chromosome = chromosome
            filters.position_start = position - self.BP_DISTANCE if position > self.BP_DISTANCE else 0
            filters.position_end = position + self.BP_DISTANCE
            print(filters)
        return self.select(filters=filters,
                           key="sumstats",
                           start=start,
                           size=size)
