import pandas as pd
from sumstats.api_v2.services.qtl_meta import QTLMetadataService


def tsv_to_hdf5(tsv_path, hdf5_path, mode):
    pass


def tsv_to_df(tsv_path, **kwargs) -> iter(pd.DataFrame):
    return pd.read_table(tsv_path, iterator=True, **kwargs)


def qtl_metadata_tsv_to_hdf5(tsv_path, hdf5_path):
    qms = QTLMetadataService()
    qms.create()
