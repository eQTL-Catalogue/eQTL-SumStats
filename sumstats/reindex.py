import argparse
import pandas as pd
import tables as tb
from sumstats.common_constants import *
import os


class H5Indexer():
    def __init__(self, h5file):
        self.h5file = h5file

    def reindex_file(self):
        with pd.HDFStore(self.h5file) as store:
            try:
                group = store.keys()[0]
                for i in TO_INDEX:
                    self.create_index(i, group)
                self.create_cs_index(BP_DSET, group)
            except IndexError as e:
                print(e)
                os.remove(self.h5file)
                


    def create_index(self, field, group):
        with tb.open_file(self.h5file, "a") as hdf:
            col = hdf.root[group].table.cols._f_col(field)
            col.remove_index()
            col.create_index(optlevel=6, kind="medium")


    def create_cs_index(self, field, group):
        with tb.open_file(self.h5file, "a") as hdf:
            col = hdf.root[group].table.cols._f_col(field)
            col.remove_index()
            col.create_csindex()

    def reindex_trait_file(self):
        with pd.HDFStore(self.h5file) as store:
            group = store.keys()[0]
            for i in TRAIT_FILE_INDEX:
                self.create_index(i, group)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The path to the HDF5 file to be processed', required=True)
    argparser.add_argument('-filetype', help='The type HDF5 file to be processed', default='sumstats', choices=['sumstats', 'trait_meta'], required=False)
    args = argparser.parse_args()

    file = args.f

    indexer = H5Indexer(file)
    if args.filetype == 'sumstats':
        indexer.reindex_file()
    if args.filetype == 'trait_meta':
        indexer.reindex_trait_file()
    

if __name__ == "__main__":
    main()
