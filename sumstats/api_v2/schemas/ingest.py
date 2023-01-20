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

from sumstats.api_v2.schemas.eqtl import QTLMetadata


class QTLMetadataPa(pa.SchemaModel):
    """Pandera schema using the pydantic model."""
    class Config:
        """Config with dataframe-level data type."""
        dtype = PydanticModel(QTLMetadata)
        coerce = True
