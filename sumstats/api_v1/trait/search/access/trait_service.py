"""
    Data is stored in the hierarchy of /Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    'snp' list will hold the snp ids
    'mantissa' list will hold each snp's p-value mantissa for this study
    'exp' list will hold each snp's p-value exponent for this study
    'chr' list will hold the chromosome that each snp belongs to
    e.t.c.
    You can see the lists that will be loaded in the constants.py module

    the positions in the vectors correspond to each other
    snp[0], mantissa[0], exp[0], and chr[0] hold the information for SNP 0

    Query: Retrieve all information for trait: input = trait name

    You can query based on trait and apply restrictions.
"""

import sumstats.api_v1.trait.search.access.repository as repo
import sumstats.api_v1.utils.group as gu
from sumstats.api_v1.utils.query import *
import sumstats.api_v1.utils.restrictions as rst
from sumstats.api_v1.common_constants import *
import logging
from sumstats.api_v1.utils import register_logger
import sumstats.api_v1.utils.sqlite_client as sql_client

logger = logging.getLogger(__name__)
register_logger.register(__name__)


class TraitService:
    def __init__(self, file):
        # Open the file with read permissions
        #self.file = pd.HDFStore(h5file, 'r')
        self.datasets = {}
        #self.groups = self.file.keys()
        #for (path, subgroups, subkeys) in self.file.walk():
        #    for subkey in subkeys:
        #        self.groups.append('/'.join([path, subkey]))
        #self.groups = ['/'.join([path, subkey]) for subkey in subkeys for (path, subgroups, subkeys) in self.file.walk()]
        self.file = file



    def list_traits(self):
        sq = sql_client.sqlClient(self.file)
        traits = sq.get_traits()
        #traits = []
        #for group in self.groups:
        #    traits.extend(get_data(hdf=self.file, key=group, fields=['phenotype_id'])['phenotype_id'].drop_duplicates().values.tolist())
        return list(set(traits))

    def list_genes(self):
        sq = sql_client.sqlClient(self.file)
        genes = sq.get_genes()
        return list(set(genes))

    def has_trait(self, trait):
        sq = sql_client.sqlClient(self.file)
        search = sq.get_trait(trait)
        if search:
            return True
        return False

    def has_gene(self, gene):
        sq = sql_client.sqlClient(self.file)
        search = sq.get_gene(gene)
        if search:
            return True
        return False

    def chrom_from_trait(self, trait):
        sq = sql_client.sqlClient(self.file)
        chroms_found = sq.get_chrom_from_trait(trait)
        #for group in self.groups:
        #    chroms_found.extend(self.file.select(group, where='phenotype_id == trait', columns=['chromosome'], index=False).drop_duplicates().values.tolist())
        chroms_found = list(set(chroms_found)) # remove dupes
        return chroms_found

    def chrom_from_gene(self, gene):
        sq = sql_client.sqlClient(self.file)
        chroms_found = sq.get_chrom_from_gene(gene)
        #for group in self.groups:
        #    chroms_found.extend(self.file.select(group, where='gene_id == gene', columns=['chromosome'], index=False).drop_duplicates().values.tolist())
            #chroms_found.extend(get_data(hdf=self.file, key=group, condition=condition, fields=['chromosome'])['chromosome'].drop_duplicates().values.tolist())
        chroms_found = list(set(chroms_found)) # remove dupes
        return chroms_found


#    def query(self, trait, start, size):
#        logger.debug("Starting query for trait %s, start %s, size %s", trait, str(start), str(size))
#        trait_group = self.file_group.get_subgroup(trait)
#        self.datasets = repo.get_dsets_from_trait_group(trait_group, start, size)
#        logger.debug("Query for trait %s, start %s, size %s done...", trait, str(start), str(size))
#
#    def apply_restrictions(self, snp=None, study=None, chromosome=None, pval_interval=None, bp_interval=None):
#        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s",
#                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))
#        self.datasets = rst.apply_restrictions(self.datasets, snp, study, chromosome, pval_interval, bp_interval)
#        logger.debug("Applying restrictions: snp %s, study %s, chromosome %s, pval_interval %s, bp_interval %s done...",
#                     str(snp), str(study), str(chromosome), str(pval_interval), str(bp_interval))
#
#    def get_result(self):
#        return self.datasets
#
#    def get_trait_size(self, trait):
#        trait_group = self.file_group.get_subgroup(trait)
#        trait_size = sum(study_group.get_dset_shape(REFERENCE_DSET)[0] for study_group in trait_group.get_all_subgroups())
#        logger.debug("Trait %s has group size %s", trait, str(trait_size))
#        return trait_size
#
#    def list_traits(self):
#        traits = self.file_group.get_all_subgroups_keys()
#        return traits
#


    def close_file(self):
        logger.debug("Closing file %s...", self.file)
        self.file.close()
