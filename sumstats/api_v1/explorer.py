import argparse
import sys
from os.path import isfile
import os
import sumstats.api_v1.utils.filesystem_utils as fsutils
import sumstats.api_v1.trait.search.access.trait_service as trait_service
import sumstats.api_v1.study.search.access.study_service as study_service
import sumstats.api_v1.chr.search.access.chromosome_service as chrom_service
import sumstats.api_v1.chr.search.chromosome_search as chr_search
import sumstats.api_v1.utils.sqlite_client as sql_client
import sumstats.api_v1.chr.retriever as cr
from sumstats.api_v1.errors.error_classes import *
from sumstats.api_v1.utils import properties_handler
from sumstats.api_v1.utils.properties_handler import properties
from sumstats.api_v1.common_constants import *


class Explorer:
    def __init__(self, config_properties=None):
        self.properties = properties_handler.get_properties(config_properties)
        self.search_path = properties_handler.get_search_path(self.properties)
        self.study_dir = self.properties.study_dir
        self.trait_dir = self.properties.trait_dir
        self.sqlite_db = self.properties.sqlite_path
        self.trait_file = os.path.join(self.search_path, self.trait_dir, "file_phen_meta.sqlite")

    def get_list_of_studies(self):
        sq = sql_client.sqlClient(self.sqlite_db)
        studies = sq.get_studies()
        return sorted(list(set(studies)))

    def get_list_of_traits(self):
        service = trait_service.TraitService(self.trait_file)
        traits = service.list_traits()
        return traits

    def get_list_of_genes(self):
        service = trait_service.TraitService(self.trait_file)
        genes = service.list_genes()
        return genes

    def get_list_of_studies_for_trait(self, trait): 
        sq = sql_client.sqlClient(self.sqlite_db)
        studies = sq.get_studies_for_trait(trait)
        if studies:
            return sorted(list(set(studies)))
        else:
            raise NotFoundError("Trait " + trait)

    def get_list_of_tissues(self):
        sq = sql_client.sqlClient(self.sqlite_db)
        tissues = sq.get_tissue_ontos()
        return sorted(list(set(tissues)))

    def get_tissue_ont_dict(self):
        sq = sql_client.sqlClient(self.sqlite_db)
        tissue_ont_dict = sq.get_tissue_ont_dict()
        return tissue_ont_dict

    def get_qtl_list(self):
        sq = sql_client.sqlClient(self.sqlite_db)
        qtl_list = sq.get_qtl_list()
        return sorted(list(set(qtl_list)))

    def get_studies_of_tissue(self, tissue): 
        sq = sql_client.sqlClient(self.sqlite_db)
        studies = sq.get_studies_for_tissue(tissue)
        if studies:
            return sorted(list(set(studies)))
        else:
            raise NotFoundError("Tissue " + tissue)

    def get_trait_of_study(self, study_to_find):
        sq = sql_client.sqlClient(self.sqlite_db)
        traits = sq.get_traits_for_study(study_to_find)
        if traits:
            return sorted(list(set(traits)))
        else:
            # study not found
            raise NotFoundError("Study " + study_to_find)


    def has_trait(self, trait):
        service = trait_service.TraitService(self.trait_file)
        #search = cr.search_all_assocs(trait=trait, start=0, size=0, properties=self.properties)
        #if search[-1] > 0:
        #    return True
        if service.has_trait(trait):
            return True
        raise NotFoundError("Trait " + trait)
        


    def has_gene(self, gene):
        service = trait_service.TraitService(self.trait_file)
        #search = cr.search_all_assocs(gene=gene, start=0, size=0, properties=self.properties)
        #if search[-1] > 0:
        #    return True
        if service.has_gene(gene):
            return True
        raise NotFoundError("Gene " + gene)

    def check_study(self, study):
        sq = sql_client.sqlClient(self.sqlite_db)
        if sq.check_study(study):
            return True
        raise NotFoundError("Study " + study)



    def get_list_of_chroms(self):
        #return CHROMOSOMES
        return sorted(CHROMOSOMES)


    def has_chromosome(self, chromosome):
        # raises Not Found Error
        """To do: Store the chromosome list as an attribute in the hdf5 file."""
        h5files = fsutils.get_h5files_in_dir(self.search_path, self.study_dir)
        #chromosomes = []
        #for h5file in h5files:
        #    service = trait_service.StudyService(h5file=h5file)
        #    traits.extend(service.list_traits())
        #    service.close_file()
        search = cr.search_all_assocs(chromosome=chromosome, start=0, size=0, properties=self.properties)
        if search[-1] > 0:
            print('checked')
            return True
        raise NotFoundError("Chromosome " + str(chromosome))


def get_study_attr(h5file):
    service = study_service.StudyService(h5file=h5file)
    study = service.study
    service.close_file()
    return study


def get_trait_attr(h5file):
    service = study_service.StudyService(h5file=h5file)
    traits = service.traits
    service.close_file()
    return traits


def main():

    args = argument_parser(sys.argv[1:])  # pragma: no cover
    explorer = Explorer(properties)  # pragma: no cover

    if args.molecular_phenotypes:  # pragma: no cover
        traits = explorer.get_list_of_traits()
        for trait in traits:
            print(trait)

    if args.genes:  # pragma: no cover
        genes = explorer.get_list_of_genes()
        for gene in genes:
            print(gene)

    if args.molecular_phenotype is not None:  # pragma: no cover
        studies = explorer.get_list_of_studies_for_trait(args.molecular_phenotype)
        for study in studies:
            print(study)

    if args.chromosomes:  # pragma: no cover
        chroms = explorer.get_list_of_chroms()
        for chrom in chroms:
            print(chrom)

    if args.studies:  # pragma: no cover
        studies = explorer.get_list_of_studies()
        for study in studies:
            print(study)

    if args.study is not None:  # pragma: no cover
        traits = explorer.get_trait_of_study(args.study)
        if traits is None:
            print("The study does not exist: ", args.study)
        else:
            for trait in traits:
                print(trait + ":" + args.study)


    if args.tissues:  # pragma: no cover
        tissues = explorer.get_list_of_tissues()
        for tissue in tissues:
            print(tissue)

    if args.tissue is not None:  # pragma: no cover
        studies = explorer.get_studies_of_tissue(args.tissue)
        study_list = [study for study in studies]
        if studies is None:
            print("The tissue does not exist: ", args.tissue)
        else:
            print("Tissue " + args.tissue + " belongs to the following studies: " + ','.join(study_list))

if __name__ == "__main__":
    main()  # pragma: no cover


def argument_parser(args):
    parser = argparse.ArgumentParser()  # pragma: no cover
    parser.add_argument('-molecular_phenotypes', action='store_true', help='List all the molecular_phenotypes')  # pragma: no cover
    parser.add_argument('-molecular_phenotype', help='List all the studies for a molecular_phenotype')  # pragma: no cover
    parser.add_argument('-studies', action='store_true', help='List all the studies')  # pragma: no cover
    parser.add_argument('-study', help='Will list \'trait: study\' if it exists')  # pragma: no cover
    parser.add_argument('-tissues', action='store_true', help='List all the tissues')  # pragma: no cover
    parser.add_argument('-tissue', help='Will list \'study: tissue\' if it exists')  # pragma: no cover
    parser.add_argument('-chromosomes', action='store_true', help='Will list all the chromosomes')  # pragma: no cover
    parser.add_argument('-genes', action='store_true', help='List all the genes')  # pragma: no cover
    properties_handler.set_properties()  # pragma: no cover

    return parser.parse_args(args)  # pragma: no cover
