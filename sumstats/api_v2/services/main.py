"""
HDF5/Pytables interface
"""

import os
import pandas as pd
import tables as tb

from sumstats.api_v2.utils.helpers import (mkdir,
                                           properties_from_model)


class HDF5Interface:
    def __init__(self):
        self.hdf5 = None
        self.par_dir = None

    def select(self, key: str = None, filters: object = None, many = True, size: int = 20, start: int = 0):
        results_df = pd.DataFrame()
        self._check_hdf5_exists()
        condition = self._filters_to_condition(filters=filters)
        with pd.HDFStore(self.hdf5, mode='r') as store:
            key = store.keys()[0] if key is None else key
            if condition:
                chunks = store.select(key,
                                      chunksize=size,
                                      start=start,
                                      where=condition)
            else:
                chunks = store.select(key,
                                      chunksize=size,
                                      start=start)
            for _, chunk in enumerate(chunks):
                results_df = results_df.append(chunk)
                if len(results_df) >= size:
                    break
            data_dict = results_df[:size].to_dict('records')
            if many:
                return data_dict
            else:
                return data_dict[0] if len(data_dict) > 0 else {}
            #TODO: utils.service_result and process - if empty

    def select_many(self):
        pass

    def create(self,
               data: pd.DataFrame,
               key: str,
               **kwargs) -> None:
        mkdir(self.par_dir)
        with pd.HDFStore(self.hdf5) as store:
            data.to_hdf(store, key, format="table", **kwargs)

    def reindex(self, index_fields: list, cs_index: str = None):
        """
        index_fields = list of fields to enable searching on
        cs_index = column sorted index (primary column to sort by)
        """
        with pd.HDFStore(self.hdf5) as store:
            try:
                key = store.keys()[0]
                [self._create_index(i, key) for i in index_fields if i != cs_index]
                if cs_index:
                    self._create_cs_index(cs_index, key)
            except IndexError:
                os.remove(self.hdf5)

    def _check_hdf5_exists(self):
        if not os.path.exists(self.hdf5):
            raise ValueError("Can't find any data for the requested resource")

    def _filters_to_condition(self, filters) -> str:
        lt_filters = properties_from_model(filters, 'lt_filter')
        gt_filters = properties_from_model(filters, 'gt_filter')
        filter_on = properties_from_model(filters, 'filter_on')
        conditions = []
        for key, value in filters.dict(exclude_none=True).items():
            filter_field = filter_on[key] if key in filter_on else key
            if key in lt_filters:
                conditions.append(f"{filter_field} <= '{value}'")
            elif key in gt_filters:
                conditions.append(f"{filter_field} >= '{value}'")
            else:
                conditions.append(f"{filter_field} == '{value}'")
        statement = " & ".join(conditions) if len(conditions) > 0 else None
        return statement
    
    def _create_index(self,
                      field: str,
                      key: str,
                      optlevel=6,
                      kind="medium") -> None:
        with tb.open_file(self.hdf5, "a") as hdf:
            col = hdf.root[key].table.cols._f_col(field)
            col.remove_index()
            col.create_index(optlevel=optlevel, kind=kind)

    def _create_cs_index(self, field: str, key: str) -> None:
        with tb.open_file(self.hdf5, "a") as hdf:
            col = hdf.root[key].table.cols._f_col(field)
            col.remove_index()
            col.create_csindex()
