"""
    Stored as /CHR/BLOCK/DATA
    Where DATA:
    under each BLOCK directory we store 3 (or more) vectors
    'study' list will hold the study ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    for a SNP group:
    study[0], mantissa[0], exp[0], and bp[0] hold the information for this SNP for study[0]
"""

import numpy as np


from sumstats.api_v1.utils import fileload as fl
from sumstats.api_v1.utils import dataset_utils
from sumstats.api_v1.chr.constants import *
import sumstats.api_v1.chr.constants as const
import sumstats.api_v1.utils.group as gu
import sumstats.api_v1.chr.block as bk
from sumstats.api_v1.errors.error_classes import *


def initialize_block_limits():
    block_floor = 0
    block_ceil = BLOCK_SIZE
    return block_floor, block_ceil


def increment_block_limits(block_ceil):
    block_floor = block_ceil + 1
    block_ceil += BLOCK_SIZE
    return block_floor, block_ceil


def block_limit_not_reached_max(block_ceil, max_bp):
    return int(block_ceil) <= (int(max_bp) + int(BLOCK_SIZE))


def save_info_in_block_group(block_uuid_group, datasets):
    block_uuid_group.check_datasets_consistent(TO_STORE_DSETS)

    for dset_name in TO_STORE_DSETS:
        block_uuid_group.expand_dataset(dset_name, datasets[dset_name])

    block_group = block_uuid_group.get_parent()
    _save_block_max_size_attribute(block_group)


def _max_bp_location(datasets):
    bp_list_chr = datasets[BP_DSET]
    return max(bp_list_chr)

def _save_block_max_size_attribute(block_group):
    subgroups = block_group.get_all_subgroups()
    size = sum(subgroup.get_max_group_size() for subgroup in subgroups)
    block_group.set_attribute("size", size)

def _save_chr_max_size_attribute(chr_group):
    all_chr_sub_groups = chr_group.get_all_subgroups()
    size = sum(int(sub_group.get_attribute("size")) for sub_group in all_chr_sub_groups if sub_group.get_attribute("size"))
    chr_group.set_attribute("size", size)


class Loader:
    def __init__(self, tsv, h5file, study, uuid, dict_of_data=None):
        self.study = study
        self.uuid = uuid
        assert self.uuid is not None, "You need to specify a uuid"

        datasets_as_lists = fl.read_datasets_from_input(tsv, dict_of_data, const)
        self.datasets = fl.format_datasets(datasets_as_lists, study, const)

        # Open the file with read/write permissions and create if it doesn't exist
        self.file = h5py.File(h5file, 'a')
        self.file_group = gu.Group(self.file)

    def load(self):
        if self._is_loaded():
            self.close_file()
            raise AlreadyLoadedError(self.study)

        chromosome_array = self._get_chromosome_array()

        for chromosome in chromosome_array:
            self._save_chr_info_to_file(chromosome)

    def _is_loaded(self):
        first_chromosome = self.datasets[CHR_DSET][0]
        first_bp = self.datasets[BP_DSET][0]
        last_chromosome = self.datasets[CHR_DSET][-1]
        last_bp = self.datasets[BP_DSET][-1]

        first_bp_loaded = self._is_block_loaded_with_uuid(first_chromosome, first_bp)
        last_bp_loaded = self._is_block_loaded_with_uuid(last_chromosome, last_bp)

        if first_bp_loaded ^ last_bp_loaded:
            raise RuntimeError("uuid is half loaded! uuid:", self.uuid)
        return first_bp_loaded and last_bp_loaded

    def _is_block_loaded_with_uuid(self, chromosome, bp_position):
        chromosome = str(chromosome)
        block_number = bk.get_block_number(bp_position)
        block_number_uuid = "/".join([str(block_number), str(self.uuid)])
        if not self.file_group.subgroup_exists(chromosome):
            return False
        chr_group = self.file_group.get_subgroup(chromosome)

        if not chr_group.subgroup_exists(block_number_uuid):
            return False

        block_uuid_group = chr_group.get_subgroup(block_number_uuid)
        return block_uuid_group.is_value_in_dataset(self.study, STUDY_DSET)

    def _get_chromosome_array(self):
        datasets = self.datasets
        unique_chromosomes_in_file = set(datasets[CHR_DSET])
        return np.array([x for x in unique_chromosomes_in_file])

    def _save_chr_info_to_file(self, chromosome):
        print("Loading chromosome:", chromosome)
        self.file_group.create_subgroup(chromosome)
        chr_group = self.file_group.get_subgroup(chromosome)
        dsets_sliced_by_chr = self._slice_datasets_where_chromosome(chromosome)

        max_bp = _max_bp_location(dsets_sliced_by_chr)
        print("max base pair location in chromosome:", max_bp)

        block_floor, block_ceil = initialize_block_limits()

        while block_limit_not_reached_max(block_ceil, max_bp):
            block_uuid = "/".join([str(block_ceil),self.uuid])
            chr_group.create_subgroup(block_uuid)
            block_uuid_group = chr_group.get_subgroup(block_uuid)
            block_mask = dsets_sliced_by_chr[BP_DSET].interval_mask(block_floor, block_ceil)
            self._save_block(block_uuid_group, block_mask, dsets_sliced_by_chr)

            block_floor, block_ceil = increment_block_limits(block_ceil)
        _save_chr_max_size_attribute(chr_group)

    def _slice_datasets_where_chromosome(self, chromosome):
        # get the slices from all the arrays where chromosome position == i
        chr_mask = self.datasets[CHR_DSET].equality_mask(chromosome)
        return dataset_utils.filter_dictionary_by_mask(self.datasets, chr_mask)

    @staticmethod
    def _save_block(block_group, block_mask, datasets):
        if np.any(block_mask):
            dsets_block_slices = dataset_utils.filter_dictionary_by_mask(datasets, block_mask)
            save_info_in_block_group(block_group, dsets_block_slices)

    def close_file(self):
        self.file.close()
