import os

import sumstats.api_v1.snp.loader as loader
import sumstats.api_v1.snp.search.access.repository as query
from tests.prep_tests import *
from sumstats.api_v1.snp.constants import *


class TestUnitQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")
        self.start = 0
        self.size = 20

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_dsets_group(self):
        snp_group = gu.Group(self.f.get("rs7085086"))
        all_subgroups = snp_group.get_all_subgroups()

        datasets = query.get_dsets_from_parent_group(all_subgroups, self.start, self.size)
        assert len(datasets) == len(TO_QUERY_DSETS)
        for dset_name, dset in datasets.items():
            if dset_name is STUDY_DSET:
                assert len(set(dset)) == 3
            else:
                assert len(set(dset)) == 1

