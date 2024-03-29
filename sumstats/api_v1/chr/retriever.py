import sumstats.api_v1.chr.search.chromosome_search as cs
import sumstats.api_v1.chr.search.block_search as bls
import sumstats.api_v1.chr.search.association_search as assoc_search


def search_chromosome(chromosome, start, size, properties=None, bp_interval=None, study=None, pval_interval=None, snp=None):
    if bp_interval is None:
        searcher = cs.ChromosomeSearch(chromosome=chromosome, start=start, size=size, config_properties=properties)
        return searcher.search_chromosome(study=study, pval_interval=pval_interval)
    else:
        searcher = bls.BlockSearch(chromosome=chromosome, start=start, size=size, config_properties=properties)
        return searcher.search_chromosome_block(bp_interval=bp_interval, study=study, pval_interval=pval_interval, snp=snp)

def search_all_assocs(start, size, pval_interval=None, properties=None, study=None, trait=None,
                      chromosome=None, bp_interval=None, tissue=None, snp=None, gene=None, quant_method=None, 
                      paginate=True, qtl_group=None):
    search_all = assoc_search.AssociationSearch(start=start, size=size, pval_interval=pval_interval, trait=trait,
                                                config_properties=properties, study=study, chromosome=chromosome,
                                                bp_interval=bp_interval, tissue=tissue, snp=snp, gene=gene, 
                                                quant_method=quant_method, paginate=paginate, qtl_group=qtl_group)
    return search_all.search_associations()

