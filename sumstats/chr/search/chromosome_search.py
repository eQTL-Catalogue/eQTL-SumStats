import os.path

import sumstats.chr.search.access.service as service
import sumstats.utils.utils as utils
from sumstats.chr.constants import *


class ChromosomeSearch:
    def __init__(self, chromosome, start, size, path=None):
        self.chromosome = chromosome
        self.start = start
        self.size = size
        if path is None:
            print("Retriever: setting default location for output files")
            path = "/output"
        self.path = path

        self.datasets = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        self.index_marker = 0

        self.h5file = utils.create_file_path(path=self.path, dir_name="bychr", file_name=chromosome)

        if not os.path.isfile(self.h5file):
            raise ValueError("Chromosome does not exist!", chromosome)
        self.searcher = service.Service(self.h5file)

    def search_chromosome(self, study=None, pval_interval=None):
        max_size = self.searcher.get_chromosome_size(chromosome=self.chromosome)
        return self._search(max_size=max_size, study=study, pval_interval=pval_interval)

    def search_chromosome_block(self, bp_interval, study=None, pval_interval=None):
        max_size = self.searcher.get_block_range_size(chromosome=self.chromosome, bp_interval=bp_interval)
        return self._search(max_size=max_size, bp_interval=bp_interval, study=study, pval_interval=pval_interval)

    def _search(self, max_size, study=None, pval_interval=None, bp_interval=None):
        iteration_size = self.size

        while True:
            if bp_interval is None:
                self.searcher.query_for_chromosome(chromosome=self.chromosome, start=self.start, size=iteration_size)
            else:
                self.searcher.query_chr_for_block_range(chromosome=self.chromosome, start=self.start, size=self.size, bp_interval=bp_interval)

            result_before_filtering = self.searcher.get_result()

            if self._traversed(result_before_filtering, max_size):
                break

            self._increase_search_index(iteration_size=iteration_size, max_size=max_size,
                                        result=result_before_filtering)

            # after search index is increased, we can apply restrictions
            self.searcher.apply_restrictions(study=study, pval_interval=pval_interval)

            self.datasets = utils.extend_dsets_with_subset(self.datasets, self.searcher.get_result())
            self.start = self.start + iteration_size
            iteration_size = self._next_iteration_size()

            if self._search_complete():
                break

        self.searcher.close_file()
        return self.datasets, self.index_marker

    def _traversed(self, result, max_size):
        return (len(result[REFERENCE_DSET]) == 0) and (self.start >= max_size)

    def _increase_search_index(self, iteration_size, max_size, result):
        if (self.start + iteration_size) >= max_size:
            # will not search again, we have reached the end of the current group
            self.index_marker += min(iteration_size, len(result[REFERENCE_DSET]))
        else:
            self.index_marker += iteration_size

    def _next_iteration_size(self):
        return self.size - len(self.datasets[REFERENCE_DSET])

    def _search_complete(self):
        return len(self.datasets[REFERENCE_DSET]) >= self.size
