import pandas as pd
from sumstats.common_constants import *
import os
import argparse


def consolidate(in_file, out_file, study, key, qtl_group, tissue_ont):
    max_string = 255
    dfin = pd.read_hdf(in_file, chunksize=1000000)
    group = key
    with pd.HDFStore(out_file) as store:
        count = 1
        for df in dfin:
            print(count)
            df[STUDY_DSET] = study
            df[TISSUE_DSET] = tissue_ont
            df[QTL_GROUP_DSET] = qtl_group
            df.astype(dict((k, DSET_TYPES[k]) for k in df.columns.values.tolist()))
            df.to_hdf(store, group,
                         complib='blosc',
                         complevel=9,
                         format='table',
                         mode='a',
                         append=True,
                         data_columns=list(TO_INDEX),
                         min_itemsize={OTHER_DSET: max_string,
                                       EFFECT_DSET: max_string,
                                       PHEN_DSET: max_string,
                                       GENE_DSET: max_string,
                                       MTO_DSET: max_string,
                                       STUDY_DSET: max_string,
                                       QTL_GROUP_DSET: max_string,
                                       TISSUE_DSET: max_string,
                                       RSID_DSET: 24,
                                       CHR_DSET: 2,
                                       SNP_DSET: max_string},
                         index = False
                         )
            count += 1


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-in_file', help='The path to the hdf in file', required=False)
    argparser.add_argument('-out_file', help='The path to the hdf out file', required=False)
    argparser.add_argument('-key', help='The hdf key/group', required=False)
    argparser.add_argument('-study', help='The study identifier', required=False)
    argparser.add_argument('-qtl_group', help='The qtl group e.g. "LCL"', required=False)
    argparser.add_argument('-tissue_ont', help='The tissue ontology term', required=False)

    args = argparser.parse_args()

    in_file = args.in_file
    out_file = args.out_file
    study = args.study
    key = args.key
    qtl_group = args.qtl_group
    tissue_ont = args.tissue_ont

    consolidate(in_file, out_file, study, key, qtl_group, tissue_ont)



if __name__ == "__main__":
    main()
