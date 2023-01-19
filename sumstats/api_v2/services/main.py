"""
HDF5/Pytables interface
"""

import os
import pandas as pd
import tables as tb


class HDF5Interface:
    def __init__(self, hdf5: str):
        self.hdf5 = hdf5
            
    def select(self, condition: str = None, size: int = 20, start: int = 0):
        results_df = pd.DataFrame()
        with pd.HDFStore(self.hdf5, mode='r') as store:
            key = store.keys()[0]
            if condition:
                chunks = store.select(key,
                                      chunksize=size,
                                      start=start,
                                      where=condition)
            else:
                chunks = store.select(key,
                                      chunksize=size,
                                      start=start)
            for i, chunk in enumerate(chunks):
                results_df = results_df.append(chunk)
                if len(results_df) >= size:
                    break
            data_dict = results_df[:size].to_dict()
            return data_dict
    
    def create(self, data: pd.DataFrame, key: str, mode: str, **kwargs) -> None:
        with pd.HDFStore(self.hdf5) as store:
            data.to_hdf(store, key, mode, **kwargs)
        
    def reindex(self, index_fields: list, cs_index: str = None):
        """
        index_fields = list of fields to enable searching on
        cs_index = column sorted index (primary column to sort by)
        """
        with pd.HDFStore(self.hdf5) as store:
            try:
                key = store.keys()[0]
                [self._create_index(i, key) for i in index_fields]
                if cs_index:
                    self._create_cs_index(cs_index, key)
            except IndexError:
                os.remove(self.hdf5)
            
    def _create_index(self, field: str, key: str, optlevel=6, kind="medium") -> None:
        with tb.open_file(self.hdf5, "a") as hdf:
            col = hdf.root[key].table.cols._f_col(field)
            col.remove_index()
            col.create_index(optlevel=optlevel, kind=kind)

    def _create_cs_index(self, field: str, key: str) -> None:
        with tb.open_file(self.h5file, "a") as hdf:
            col = hdf.root[key].table.cols._f_col(field)
            col.remove_index()
            col.create_csindex()
        
        
        