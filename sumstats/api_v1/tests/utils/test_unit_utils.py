import os
import numpy as np
import pytest
import sumstats.api_v1.utils.dataset_utils as utils
from sumstats.api_v1.utils.dataset import Dataset
from tests.test_constants import *


class TestUnitUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_filter_dictionary_by_mask(self):
        loader_dictionary = {'dset1': Dataset([1, 2, 3]), 'dset2': Dataset([1, 3, 3])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(1)
        print(mask)
        loader_dictionary = utils.filter_dictionary_by_mask(loader_dictionary, mask)
        for dset in loader_dictionary:
            assert np.array_equal(loader_dictionary[dset], [1])

        loader_dictionary = {'dset1': Dataset(["a", "b", "c"]), 'dset2': Dataset(["c", "d", "e"])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(1)
        print(mask)
        loader_dictionary = utils.filter_dictionary_by_mask(loader_dictionary, mask)
        assert np.array_equal(loader_dictionary["dset1"], ["a"])
        assert np.array_equal(loader_dictionary["dset2"], ["c"])

        loader_dictionary = {'dset1': Dataset(["a", "b", "c"]), 'dset2': Dataset(["c", "d", "e"])}
        pvals = Dataset([1, 2, 2])
        mask = pvals.equality_mask(2, )
        print(mask)
        loader_dictionary = utils.filter_dictionary_by_mask(loader_dictionary, mask)
        assert np.array_equal(loader_dictionary["dset1"], ["b", "c"])
        assert np.array_equal(loader_dictionary["dset2"], ["d", "e"])

    def test_evaluate_datasets(self):
        datasets = {}
        utils.assert_datasets_not_empty(datasets)

        datasets = {SNP_DSET: ["rs1", "rs2", "rs3"], PVAL_DSET: [0.1, 3.1, 2.1],
                           CHR_DSET: [1, 2, 3]}
        utils.assert_datasets_not_empty(datasets)

        datasets = {SNP_DSET: None}
        with pytest.raises(AssertionError):
            utils.assert_datasets_not_empty(datasets)

        datasets = {SNP_DSET: []}
        with pytest.raises(AssertionError):
            utils.assert_datasets_not_empty(datasets)

    def test_empty_array(self):
        assert utils.empty_array(None)
        assert utils.empty_array([])
        assert not utils.empty_array("not an array")
        assert not utils.empty_array([1, 2, 3])
        assert not utils.empty_array(Dataset([1, 2, 3]))

    def test_create_dataset_objects(self):
        datasets = {'dset1' : [1, 2, 3], 'dset2' : ['1,' '2', '3'], 'dset3' : [1., 2., 3.]}
        datasets = utils.create_datasets_from_lists(datasets)
        for dataset in datasets.values():
            assert isinstance(dataset, Dataset)

    def test_create_dictionary_of_empty_dsets(self):
        datasets = utils.create_dictionary_of_empty_dsets(['dset1', 'dset2'])

        assert len(datasets) == 2

        assert isinstance(datasets['dset1'], Dataset)
        assert len(datasets['dset1']) == 0

        assert isinstance(datasets['dset2'], Dataset)
        assert len(datasets['dset2']) == 0


