import sumstats.api_v1.controller as search
import sumstats.api_v1.utils.dataset_utils as utils
from sumstats.api_v1.trait.constants import *
from tests.search.test_utils import *
from sumstats.api_v1.utils.interval import *
from config import properties


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        properties.h5files_path = "./outputtrait"
        self.searcher = search.Search(properties)

    def test_search_t3_0_20_lower_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0.0000000001, 0.0000000001)
        datasets, index_marker = self.searcher.search_trait(trait='t3', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s5'])
        assert index_marker == 40
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1_0_50_lower_pval(self):
        start = 0
        size = 50
        pval_interval = FloatInterval().set_tuple(0.00001, 0.00001)
        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 25)
        assert_studies_from_list(datasets, ['s1'])
        # next index is the sum of the elements actually retrieved from the studies before restrictions are applied.
        # So in this case in the first search (start = 0, size = 50), we get 50 elements back from s1 without
        # restrictions. With restrictions it is 25.
        # So it will finish searching t1 until it can fill up the required size or run out of things to look for
        assert index_marker == 100
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1_0_20_upper_pval(self):
        start = 0
        size = 20
        pval_interval = FloatInterval().set_tuple(0.00005, 0.1)
        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1'])

        assert index_marker == 45
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1_0_50_upper_pval(self):
        start = 0
        size = 50
        pval_interval = FloatInterval().set_tuple(0.00005, 0.1)
        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 25)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 25)

        assert index_marker == 75
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t1_40_60_returns_empty(self):
        start = 40
        size = 20

        pval_interval = FloatInterval().set_tuple(0.006, 0.1)
        datasets, index_marker = self.searcher.search_trait(trait='t1', start=start, size=size, pval_interval=pval_interval)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)

        # total trait size - start size == 100 - 40
        assert index_marker == 60
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_search_t2_45_65(self):
        start = 45
        size = 20

        pval_interval = FloatInterval().set_tuple(0.006, 0.1)
        datasets, index_marker = self.searcher.search_trait(trait='t2', start=start, size=size,
                                                          pval_interval=pval_interval)
        assert_studies_from_list(datasets, ['s3', 's4'])
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 5)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 15)

        # looped over to the next study, so 65 - 45
        # when added to our start it will give us 65
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_loop_through_t2_size_5_w_restriction_to_s4(self):
        start = 0
        size = 5

        looped_through = 1
        pval_interval = FloatInterval().set_tuple(0.06, 0.3)
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        while True:
            datasets, index_marker = self.searcher.search_trait(trait='t2', start=start, size=size, pval_interval=pval_interval)
            d = utils.extend_dsets_with_subset(d, datasets)
            if len(datasets[REFERENCE_DSET]) <= 0:
                break

            # already on the first loop I want to have reached s4
            if looped_through == 1:
                # all of s3 + the first 5 elements of s4
                assert index_marker == 55
            assert_number_of_times_study_is_in_datasets(datasets, 's4', 5)
            assert_studies_from_list(datasets, ['s4'])

            looped_through += 1
            start = start + index_marker

        assert looped_through == 11
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])
