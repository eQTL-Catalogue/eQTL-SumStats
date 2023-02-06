"""
The data models/schema are defined with Pydantic.

to generate pandera schema which can be used to 
Pandera uses these schema as the source of truth
validate pandas dataframes.

Data ingest is like so:
tsv --> pd.DataFrame --> HDF5
So we need use pandera schema to validate the
ingested data.
"""


import pandera as pa
from pandera.engines.pandas_engine import PydanticModel

from sumstats.api_v2.schemas.eqtl import QTLMetadata, VariantAssociation


class QTLMetadataPa(pa.SchemaModel):
    class Config:
        dtype = PydanticModel(QTLMetadata)
        coerce = True


class QTLSumstatsPa(pa.SchemaModel):
    class Config:
        dtype = PydanticModel(VariantAssociation)
        coerce = True
