import pandas as pd

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.services.qtl_data import QTLDataService
from sumstats.api_v2.schemas.eqtl import QTLMetadata, VariantAssociation
from sumstats.api_v2.utils.helpers import (properties_from_model,
                                           pandas_dtype_from_model)


MAX_STRING_LEN = 255
LONG_STRING_PLACEHOLDER = "LONG_STRING"


def tsv_to_hdf5(tsv_path: str,
                hdf5_label: str,
                service: object,
                model: object) -> None:
    """
    key: hdf5 group key
    model: pydantic schema/model
    """
    df_iter = tsv_to_df_iter(tsv_path=tsv_path,
                             usecols=[*tsv_header_map(model)],
                             chunksize=1000000,
                             converters={},
                             dtype=dtype(model),
                             float_precision='high')
    hdf_interface = service(hdf5_label)
    for df in df_iter:
        hdf_interface.create(data=df,
                             key=hdf5_label,
                             complib='blosc',
                             complevel=9,
                             append=True,
                             data_columns=[*searchable_fields(model)],
                             min_itemsize=field_size(model),
                             index=False)
    hdf_interface.reindex(index_fields=[*searchable_fields(model)],
                          cs_index=cs_index(model))



def tsv_to_df_iter(tsv_path, **kwargs) -> (pd.DataFrame):
    return pd.read_table(tsv_path, sep="\t", iterator=True, **kwargs)


def validate_df(df, schema) -> pd.DataFrame:
    return schema(df)


def tsv_header_map(model) -> dict:
    """
    returns: Dict of tsv headers: model field names
    """
    return swap_keys_for_values(properties_from_model(model, "ingest_label"))


def searchable_fields(model) -> dict:
    searchable_dict = properties_from_model(model, "searchable")
    return {k: v for k, v in searchable_dict.items() if v is True}


def cs_index(model) -> str:
    """
    The Column Sorted (main) index field.
    There can only be one.
    """
    cs_index_dict = properties_from_model(model, "cs_index")
    return [k for k in cs_index_dict][0]


def field_size(model) -> dict:
    return properties_from_model(model, "min_size")


def dtype(model) -> dict:
    return pandas_dtype_from_model(model)


def converters(field_size: dict) -> dict:
    return {k: replace_string_if_too_long(v) for k, v in field_size.items()}


def replace_string_if_too_long(x: str) -> str:
    return LONG_STRING_PLACEHOLDER if len(x) > MAX_STRING_LEN else x


def swap_keys_for_values(d: dict) -> dict:
    return {v: k for k, v in d.items()}


def qtl_metadata_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    tsv_to_hdf5(tsv_path=tsv_path,
                hdf5_label=hdf5_label,
                service=QTLMetadataService,
                model=QTLMetadata)


def qtl_sumstats_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    """
    TODO: Data pre-split by chrom then store:
    data/
      QTD0001/
         1.h5
         2.h5
         ...
    """
    tsv_to_hdf5(tsv_path=tsv_path,
                hdf5_label=hdf5_label,
                service=QTLDataService,
                model=VariantAssociation)
