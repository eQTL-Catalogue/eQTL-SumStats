"""
Summmary statistics data interface
"""
import logging

from sumstats.api_v2.services.main import HDF5Interface
from sumstats.api_v2.utils.helpers import (get_hdf5_path,
                                           get_hdf5_dir,
                                           pval_to_neg_log_10_pval)


logger = logging.getLogger(__name__)


class QTLDataService(HDF5Interface):

    BP_DISTANCE = 1_000_000  # distance from genetic feature
    BP_ERROR_MARGIN = 100  # an position error margin to add the rsid search

    def __init__(self, hdf5_label: str):
        self.hdf5 = get_hdf5_path(type="data",
                                  label=hdf5_label)
        self.par_dir = get_hdf5_dir(type="data")
        self.filters = None
        self.result = []

    def query(self, filters, start, size) -> list:
        """
        Convert: position query to select
                 rsID to postion
                 variant id tp position
                 gene_id to position +-1mb
                 trait to position +-1mb
        """
        self.filters = filters
        self._resolve_genomic_region_based_on_search_type()
        if self._is_genomic_region_search() or self._is_not_filtered():
            self.result = self.select(filters=self.filters,
                                      key="sumstats",
                                      start=start,
                                      size=size)
            return self._format_result()
        else:
            raise ValueError(("Query is not permitted. Apply filters "
                              "to narrow your search by "
                              "variant, genomic region or "
                              "gene/molecular trait id"))

    def _format_result(self):
        return [self._add_neg_log_p(hit) for hit in self.result]

    @staticmethod
    def _add_neg_log_p(record):
        if 'pvalue' in record:
            record['nlog10p'] = pval_to_neg_log_10_pval(record['pvalue'])
            return record

    def _resolve_genomic_region_based_on_search_type(self):
        if self._is_variant_search():
            self._parse_genomic_region_from_variant_id()
        elif self._is_rsid_search():
            rs_filters = self.filters.copy(include={'rsid'})
            rs_filters.rsid = rs_filters.rsid.replace("rs", "")
            self._resolve_genomic_region(context_filters=rs_filters,
                                         key='rsid',
                                         distance=self.BP_ERROR_MARGIN)
        elif self._is_genomic_context_search():
            gc_filters = self.filters.copy(include={'gene_id',
                                                    'molecular_trait_id'})
            self._resolve_genomic_region(context_filters=gc_filters,
                                         key='genomic_context',
                                         distance=self.BP_DISTANCE)

    def _is_variant_search(self) -> bool:
        return self.filters.variant is not None

    def _is_rsid_search(self) -> bool:
        return self.filters.rsid is not None

    def _is_genomic_region_search(self) -> bool:
        return (self.filters.chromosome is not None and
                self.filters.position_start is not None and
                self.filters.position_end is not None)

    def _is_genomic_context_search(self) -> bool:
        return (self.filters.gene_id is not None or
                self.filters.molecular_trait_id is not None) and not (
                    self._is_variant_search() and
                    self._is_rsid_search() and
                    self._is_genomic_region_search()
                    )

    def _is_not_filtered(self) -> bool:
        return (self.filters.gene_id is None and
                self.filters.molecular_trait_id is None and
                self.filters.pvalue is None and not (
                    self._is_variant_search() and
                    self._is_rsid_search() and
                    self._is_genomic_region_search()
                    )
                )

    def _resolve_genomic_region(self, context_filters, key, distance):
        region_to_search = self.select(filters=context_filters, key=key)
        if len(region_to_search) > 0:
            first_record = region_to_search[0]
            chromosome, position = (first_record['chromosome'],
                                    first_record['position'])
            self.filters.chromosome = chromosome
            self.filters.position_start = position - distance if position > distance else 0
            self.filters.position_end = position + distance
        else:
            raise ValueError(("Could not find resource with the following "
                              f"filters {self.filters.dict(exclude_none=True)}"))

    def _parse_genomic_region_from_variant_id(self):
        parts = self.filters.variant.split("_")
        chr_part, pos_part = parts[0], parts[1]
        self.filters.chromosome = chr_part.replace("chr", "")
        self.filters.position_start = pos_part
        self.filters.position_end = pos_part
