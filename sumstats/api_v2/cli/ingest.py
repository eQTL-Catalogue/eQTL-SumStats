import pandas as pd

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.services.qtl_data import QTLDataService
from sumstats.api_v2.schemas.eqtl import QTLMetadata, VariantAssociation
from sumstats.api_v2.utils.helpers import (properties_from_model,
                                           pandas_dtype_from_model)



MAX_STRING_LEN = 100

def tsv_to_hdf5(tsv_path: str,
                hdf5_label: str,
                service: object,
                model: object,
                pa_schema: object) -> None:
    """
    key: hdf5 group key
    model: pydantic schema/model
    pa_schema: pandera schema
    """
    print('read_tsv')
    df_iter = tsv_to_df_iter(tsv_path=tsv_path,
                             usecols=[*tsv_header_map(model)],
                             chunksize=500000,
                             converters={},
                             dtype=dtype(model),
                             float_precision='high')
    print('start service')
    hdf_interface = service(hdf5_label)
    for df in df_iter:
        #valid_df = validate_df(df=df, schema=pa_schema)
        print('writing to hdf')
        hdf_interface.create(data=df,
                             key=hdf5_label,
                             complib='blosc',
                             complevel=9,
                             append=True,
                             data_columns=[*searchable_fields(model)],
                             min_itemsize=field_size(model),
                             index=False)
        
def placeholder_if_allele_string_too_long(df, field):
    mask = df[field].str.len() <= MAX_STRING_LEN
    df[field].where(mask, "LONG_STRING", inplace=True)


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
    return properties_from_model(model, "searchable")


def field_size(model) -> dict:
    return properties_from_model(model, "min_size")


def dtype(model) -> dict:
    return pandas_dtype_from_model(model)


def converters(field_size: dict) -> dict:
    pass
    # replace value with converter 


def swap_keys_for_values(d: dict) -> dict:
    return dict((v, k) for k, v in d.items())


def qtl_metadata_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    tsv_to_hdf5(tsv_path=tsv_path,
                hdf5_label=hdf5_label,
                service=QTLMetadataService,
               model=QTLMetadata)


def qtl_sumstats_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    print('tsv 2 hdf')
    tsv_to_hdf5(tsv_path=tsv_path,
                hdf5_label=hdf5_label,
                service=QTLDataService,
                model=VariantAssociation)
    #TODO: reindex
