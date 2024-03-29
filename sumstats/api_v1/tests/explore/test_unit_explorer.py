import os
import shutil
from sumstats.api_v1.errors.error_classes import *
import sumstats.api_v1.explorer as ex
import sumstats.api_v1.trait.loader as trait_loader
import sumstats.api_v1.chr.loader as chr_loader
from tests.prep_tests import *
import pytest
from config import properties


@pytest.yield_fixture(scope="class", autouse=True)
def load_studies(request):
    os.makedirs('./outputexplorer/bytrait')
    os.makedirs('./outputexplorer/bychr')
    trait_output_location = './outputexplorer/bytrait/'
    chr_output_location = './outputexplorer/bychr/'

    h5file = trait_output_location + 'file_t1.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s1', trait='t1', loader=trait_loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s2', trait='t1', loader=trait_loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s11', trait='t1', loader=trait_loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s12', trait='t1', loader=trait_loader)
    load.load()

    h5file = trait_output_location + 'file_t2.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s3', trait='t2', loader=trait_loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s4', trait='t2', loader=trait_loader)
    load.load()

    h5file = trait_output_location + 'file_t3.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s5', trait='t3', loader=trait_loader)
    load.load()

    # load by chromosome
    h5file = chr_output_location + 'file_1.h5'
    load = prepare_load_object_with_study(h5file=h5file, study='s1', loader=chr_loader)
    load.load()

    request.addfinalizer(remove_dir)


def remove_dir():
    shutil.rmtree('./outputexplorer')


class TestLoader(object):
    def setup_method(self):
        # initialize explorer with local path
        properties.h5files_path = "./outputexplorer"
        self.explorer = ex.Explorer(properties)
        self.loaded_traits = ['t1', 't2', 't3']
        self.loaded_studies = ['s1', 's2', 's11', 's12', 's3', 's4', 's5']
        self.loaded_studies_t1 = ['s1', 's2', 's11', 's12']
        self.loaded_studies_t3 = ['s5']

    def test_get_list_of_traits(self):
        list_of_traits = self.explorer.get_list_of_traits()
        assert len(list_of_traits) == len(self.loaded_traits)
        for trait in self.loaded_traits:
            assert trait in list_of_traits

    def test_get_list_of_studies_for_trait_t1(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t1')
        assert len(list_of_studies) == len(self.loaded_studies_t1)
        for study in self.loaded_studies_t1:
            assert study in list_of_studies

    def test_get_list_of_studies_for_trait_t3(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t3')
        assert len(list_of_studies) == len(self.loaded_studies_t3)
        for study in self.loaded_studies_t3:
            assert study in list_of_studies

    def test_get_list_of_studies_for_non_existing_trait_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_list_of_studies_for_trait('t4')

    def test_get_list_of_studies(self):
        list_of_studies = self.explorer.get_list_of_studies()
        assert len(list_of_studies) == len(self.loaded_studies)
        for study in self.loaded_studies:
            assert study in list_of_studies

    def test_get_info_from_study_s1(self):
        trait = self.explorer.get_trait_of_study('s1')
        assert trait == 't1'

    def test_get_info_from_non_exising_study_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_trait_of_study('s6')

    def test_traits_return_in_same_order(self):
        traits1 = self.explorer.get_list_of_traits()
        traits2 = self.explorer.get_list_of_traits()
        for i in range(len(traits1)):
            assert traits1[i] == traits2[i]

    def test_studies_return_in_same_order(self):
        studies1 = self.explorer.get_list_of_studies_for_trait('t1')
        studies2 = self.explorer.get_list_of_studies_for_trait('t1')
        for i in range(len(studies1)):
            assert studies1[i] == studies2[i]

    def test_trait_exists(self):
        for trait in self.loaded_traits:
            assert self.explorer.has_trait(trait)

    def test_trait_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            assert not self.explorer.has_trait('foo')

    def test_chromosome_exists(self):
        assert self.explorer.has_chromosome(1)

    def test_chromosome_doesnt_exist_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.has_chromosome(3)