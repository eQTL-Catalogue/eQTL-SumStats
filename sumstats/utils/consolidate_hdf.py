import pandas as pd
import numpy as np
from sumstats.common_constants import *
import sumstats.reindex as ri
import os
import argparse
import sys
import glob


def append_to_file(in_file, out_file, study, key, qtl_group, tissue_ont):
    print(in_file, out_file, study, key, qtl_group, tissue_ont)
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
            df = df.astype(dict((k, DSET_TYPES[k]) for k in df.columns.values.tolist()))
            df[SE_DSET] = np.nan
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


def parse_meta(file, quant, chrom, meta):
    key = chrom + "_" + quant
    name_split = os.path.basename(file).split('+')
    study = name_split[0].replace('file_', '')
    qtl_group = name_split[1]
    meta_df = pd.read_csv(meta, sep='\t')
    meta_for_file = meta_df[(meta_df['study'] == study) & (meta_df['qtl_group'] == qtl_group) & (meta_df['quant_method'] == quant)]
    if meta_for_file.empty:
        print("filename {} not found in metadata".format(ss_file))
        sys.exit(1)
    elif len(meta_for_file) > 1:
        print("filename {} found more than once in metadata".format(ss_file))
        sys.exit(1)
    else:
        tissue_ont = meta_for_file['tissue_ontology_id'].values[0]
        return study, key, qtl_group, tissue_ont


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-in_dir', help='The path to the hdf in dir e.g. study dir', required=False)
    argparser.add_argument('-out_file', help='The path to the hdf out file e.g. chrom + quant file ', required=False)
    argparser.add_argument('-meta', help='The metadata tsv file', required=False)
    argparser.add_argument('-quant', help='The quant method', required=False)
    argparser.add_argument('-chrom', help='The chromosome', required=False)



    #argparser.add_argument('-key', help='The hdf key/group', required=False)
    #argparser.add_argument('-study', help='The study identifier', required=False)
    #argparser.add_argument('-qtl_group', help='The qtl group e.g. "LCL"', required=False)
    #argparser.add_argument('-tissue_ont', help='The tissue ontology term', required=False)

    args = argparser.parse_args()

    in_dir = args.in_dir
    out_file = args.out_file
    meta = args.meta
    quant = args.quant
    chrom = args.chrom
    #study = args.study
    #key = args.key
    #qtl_group = args.qtl_group
    #tissue_ont = args.tissue_ont

    print(out_file)
    matching_files = glob.glob(os.path.join(in_dir, chrom, "*+" + quant + ".h5"))
    for file in matching_files:
        study, key, qtl_group, tissue_ont = parse_meta(file, quant, chrom, meta)
        append_to_file(file, out_file, study, key, qtl_group, tissue_ont)
    indexer = ri.H5Indexer(out_file)
    indexer.reindex_file()


if __name__ == "__main__":
    main()
