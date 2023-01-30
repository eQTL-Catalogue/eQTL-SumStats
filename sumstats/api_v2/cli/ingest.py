import pandas as pd

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.services.qtl_data import QTLDataService
from sumstats.api_v2.schemas.eqtl import (QTLMetadata,
                                          VariantAssociation,
                                          GenomicContext,
                                          GenomicContextIngest)
from sumstats.api_v2.utils.helpers import (properties_from_model,
                                           pandas_dtype_from_model)


LONG_STRING_PLACEHOLDER = "LONG_STRING"


class TSV2HDF5:
    def __init__(self,
                 tsv_path: str,
                 hdf5_label: str,
                 key: str,
                 usecols: list,
                 service: object,
                 model: object) -> None:
        self.df = None
        self.tsv_path = tsv_path
        self.hdf5_label = hdf5_label
        self.key = key
        self.usecols = usecols
        self.service = service
        self.model = model
        self.hdf_interface = service(self.hdf5_label)

    def tsv_to_df(self, **kwargs) -> pd.DataFrame:
        return pd.read_table(self.tsv_path,
                             sep="\t",
                             usecols=self.usecols,
                             dtype=self._dtype(),
                             float_precision='high',
                             **kwargs)

    def df_to_hdf5(self, df: pd.DataFrame, **kwargs):
        self.hdf_interface.create(data=df,
                                  key=self.key,
                                  complib='blosc',
                                  complevel=9,
                                  append=True,
                                  data_columns=[*self._searchable_fields()],
                                  min_itemsize=self._field_size(),
                                  index=False)
        self.hdf_interface.reindex(index_fields=[*self._searchable_fields()],
                                   cs_index=self._cs_index())

    def replace_value_if_too_long(self, df: pd.DataFrame) -> pd.DataFrame:
        for field, len_limit in self._field_size().items():
            self._placeholder_if_string_too_long(df,
                                                 field=field,
                                                 len_limit=len_limit)

    @staticmethod
    def _placeholder_if_string_too_long(df, field, len_limit):
        mask = df[field].str.len() <= len_limit
        df[field].where(mask, LONG_STRING_PLACEHOLDER, inplace=True)

    def _dtype(self) -> dict:
        return pandas_dtype_from_model(self.model)

    def _searchable_fields(self) -> dict:
        searchable_dict = properties_from_model(self.model, "searchable")
        return {k: v for k, v in searchable_dict.items() if v is True}

    def _field_size(self) -> dict:
        return properties_from_model(self.model, "min_size")

    def _cs_index(self) -> str:
        """
        The Column Sorted (main) index field.
        There can only be one.
        """
        cs_index_dict = properties_from_model(self.model, "cs_index")
        if cs_index_dict:
            return [k for k in cs_index_dict][0]
        return None


def tsv_header_map(model) -> dict:
    """
    returns: Dict of tsv headers: model field names
    """
    return swap_keys_for_values(properties_from_model(model, "ingest_label"))


def swap_keys_for_values(d: dict) -> dict:
    return {v: k for k, v in d.items()}


def qtl_metadata_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    t2h = TSV2HDF5(tsv_path=tsv_path,
                   hdf5_label=hdf5_label,
                   key=hdf5_label,
                   usecols=[*tsv_header_map(QTLMetadata)],
                   service=QTLMetadataService,
                   model=QTLMetadata)
    df = t2h.tsv_to_df()
    t2h.replace_value_if_too_long(df=df)
    t2h.df_to_hdf5(df=df)


def qtl_sumstats_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    """
    data/
      QTD0001.h5
        - sumstats/
            - cs: pos
            - chr
            - pval
            - trait id
            - gene id
        - genomic_context/
            - trait id -> chr:pos
            - gene id -> chr:pos
        - rsid/
            - cs: rsid (int) -> chr: pos

         ...
    """
    t2h = TSV2HDF5(tsv_path=tsv_path,
                   hdf5_label=hdf5_label,
                   key="sumstats",
                   usecols=[*tsv_header_map(VariantAssociation)],
                   service=QTLDataService,
                   model=VariantAssociation)
    df_iter = t2h.tsv_to_df(chunksize=1000000)
    for df in df_iter:
        t2h.replace_value_if_too_long(df=df)
        t2h.df_to_hdf5(df=df)
    trait_and_gene_to_hdf5(tsv_path=tsv_path,
                           hdf5_label=hdf5_label)
    #TODO: rsid load


def trait_and_gene_to_hdf5(tsv_path, hdf5_label) -> None:
    t2h = TSV2HDF5(tsv_path=tsv_path,
                   hdf5_label=hdf5_label,
                   key="genomic_context",
                   usecols=[*tsv_header_map(GenomicContextIngest)],
                   service=QTLDataService,
                   model=GenomicContextIngest)
    df = t2h.tsv_to_df()
    genomic_context_fields_to_group_on = properties_from_model(GenomicContext, "searchable")
    df.drop_duplicates(subset=[*genomic_context_fields_to_group_on])
    t2h.replace_value_if_too_long(df=df)
    t2h.df_to_hdf5(df=df)
