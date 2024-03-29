"""
General methods used across the modules
"""

from sumstats.api_v1.utils.dataset import *


def filter_dictionary_by_mask(dictionary, mask):
    return {dset: Dataset(dataset.filter_by_mask(mask)) for dset, dataset in dictionary.items()}


def assert_datasets_not_empty(datasets):
    for dset_name, dataset in datasets.items():
        assert not empty_array(dataset), "Array is None or empty: " + dset_name


def empty_array(array):
    if array is None:
        return True
    return len(array) == 0


def create_datasets_from_lists(datasets):
    return {dset_name : Dataset(dset_vector) for dset_name, dset_vector in datasets.items()}


def create_dictionary_of_empty_dsets(names):
    return {name : Dataset([]) for name in names}


def extend_dsets_with_subset(datasets, subset):
    extended_datasets = {}
    for dset_name, dataset in datasets.items():
        extended_datasets[dset_name] = Dataset(dataset)
        extended_datasets[dset_name].extend(subset[dset_name])
    return extended_datasets