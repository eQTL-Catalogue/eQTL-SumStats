import pandas as pd

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.schemas.ingest import QTLMetadataPa
from sumstats.api_v2.schemas.eqtl import QTLMetadata


def tsv_to_hdf5(tsv_path, hdf5_path, mode):
    pass


def tsv_to_df_iter(tsv_path, **kwargs) -> (pd.DataFrame):
    return pd.read_table(tsv_path, sep="\t", iterator=True, **kwargs)


def validate_df(df, schema) -> pd.DataFrame:
    return schema(df)


def properties_from_model(model, key) -> dict:
    props = {}
    for field_name, field in model.schema()["properties"].items():
        if key in field:
            props[field_name] = field.get(key)
    return props


def tsv_header_map(model) -> dict:
    """
    returns: Dict of tsv headers: model field names
    """
    return swap_keys_for_values(properties_from_model(model, "ingest_label"))


def searchable_fields(model) -> dict:
    return properties_from_model(model, "searchable")


def swap_keys_for_values(d: dict) -> dict:
    return dict((v,k) for k,v in d.items())


def qtl_metadata_tsv_to_hdf5(tsv_path, hdf5_label) -> None:
    df_iter = tsv_to_df_iter(tsv_path=tsv_path,
                             usecols=[*tsv_header_map(QTLMetadata)],
                             chunksize=1000000)
    qms = QTLMetadataService(hdf5_label)
    for df in df_iter:
        print(df.head())
        valid_df = validate_df(df=df, schema=QTLMetadataPa)
        print(valid_df.head())
        qms.create(data=valid_df, 
                   key="qtl_metadata",
                   append=True,
                   data_columns=[*searchable_fields(QTLMetadata)],
                   index=False)
