"""
General methods used across the modules
"""

from sumstats.utils.dataset import *
import sumstats.utils.pval as pu
from os import listdir
from os.path import isfile, join, isdir


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


def is_valid_dir_path(path, dir_name):
    directory = join(path, dir_name)
    return isdir(directory)


def get_file_path(path, file):
    file_path = join(path, file)
    if not isfile(file_path):
        raise RuntimeError("Something went wrong when trying to get path for file", file)
    return file_path


def create_h5file_path(path, dir_name, file_name):
    file_path = join(path, dir_name, "file_" + str(file_name) + ".h5")
    return file_path


def get_h5files_in_dir(path, dir_name):
    try:
        trait_dir_path = join(path, dir_name)
        return [join(trait_dir_path, f) for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
    except Exception:
        raise RuntimeError("Something went wrong when trying to get h5files for directory", dir_name)
