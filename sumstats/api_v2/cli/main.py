import argparse

from sumstats.api_v2.cli.ingest import (qtl_metadata_tsv_to_hdf5,
                                        qtl_sumstats_tsv_to_hdf5)


def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-t',
                           help='tsv path',
                           required=True)
    argparser.add_argument('-hdf', 
                           help='hdf5 file label e.g. dataset1',
                           required=True)
    argparser.add_argument('-type',
                           help='specify whether it is data or metadata',
                           choices=['data', 'metadata'],
                           required=True)
    args = argparser.parse_args()
    return args


def main():
    args = get_args()
    if args.type == 'data':
        qtl_sumstats_tsv_to_hdf5(tsv_path=args.t, hdf5_label=args.hdf)
    if args.type == 'metadata':
        qtl_metadata_tsv_to_hdf5(tsv_path=args.t, hdf5_label=args.hdf)

 
if __name__ == "__main__":
    main()