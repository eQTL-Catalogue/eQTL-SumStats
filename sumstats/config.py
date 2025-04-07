import pkg_resources

APP_VERSION = pkg_resources.get_distribution("eqtl-sumstats").version

API_BASE = "/eqtl/api"

API_DESCRIPTION = """
<img src='https://raw.githubusercontent.com/eQTL-Catalogue/eQTL-Catalogue-website/gh-pages/static/eQTL_icon.png' alt="eqtl_icon" width="10%">

Welcome to the [eQTL Catalogue](https://www.ebi.ac.uk/eqtl) RESTful API.

This API is for facilitating a filtered request of
eQTL association data.

## API v3

API v3 provides improved access to studies and datasets with enhanced search
capabilities. Use the `/studies` endpoints to browse and search studies, and
the `/datasets` endpoints to access and search specific datasets. The global
`/search` endpoints allow querying across all available data.

### Search Filters
The following search filters are available for v3 endpoints:
- `gene_id`: Filter by Ensembl gene identifier
- `rsid`: Filter by RS ID of the variant
- `variant`: Filter by variant in format chr_pos_ref_alt
- `molecular_trait_id`: Filter by molecular trait identifier
- `chromosome`: Filter by chromosome
- `study_id`: Filter by study identifier
- `dataset_id`: Filter by dataset identifier

## API v2

Each study in the catalogue is split by QTL context and these splits are
assigned their own dataset IDs (QTD#). Datasets can be browsed at the
`/datasets` endpoint.

To retrieve the summary statistics for a dataset, use the
`/datasets/<DATASETID>/associations` endpoint and apply
any required filters.

## API v1

This will be deprecated and is maintained only for existing integrations.

## All associations
If you are interested in downloading
_all_ the association data for a dataset, the recommended
method would be via the FTP.
"""  # noqa: E501

# API v3 endpoint descriptions
STUDIES_DESCRIPTION = (
    "Retrieve a list of all available eQTL studies with their metadata"
)
STUDY_DESCRIPTION = (
    "Retrieve detailed information for a specific eQTL study by ID"
)
STUDY_SEARCH_DESCRIPTION = (
    "Search for specific variants, genes, or phenotypes within a single study"
)

DATASETS_DESCRIPTION = (
    "Retrieve a list of all available eQTL datasets across studies"
)
DATASET_DESCRIPTION = (
    "Retrieve detailed information for a specific eQTL dataset by ID"
)
DATASET_SEARCH_DESCRIPTION = """Search for specific variants, genes,
or phenotypes within a single dataset"""

SEARCH_DESCRIPTION = (
    "Search for eQTL associations across all studies in the database"
)
# SEARCH_CHUNKED_DESCRIPTION = "Retrieve large search results"

# API v3 search filter descriptions
FILTER_GENE_ID = "Ensembl gene identifier (e.g., ENSG00000139618)"
FILTER_RSID = "RS ID of the variant (e.g., rs1234567)"
FILTER_VARIANT = "Variant in format chr_pos_ref_alt (e.g., 1_12345_A_G)"
FILTER_MOLECULAR_TRAIT_ID = "Molecular trait identifier"
FILTER_CHROMOSOME = "Chromosome (e.g., 1, 2, 3)"
FILTER_STUDY_ID = "Study identifier"
FILTER_DATASET_ID = "Dataset identifier"

TAGS_METADATA = [
    {
        "name": "eQTL API v3",
        "description": "REST API for accessing eQTL summary statistics data",
    },
    {
        "name": "eQTL API v2",
        "description": "REST API for accessing eQTL summary statistics data",
    },
    {
        "name": "eQTL API v1",
        "description": """**Deprecated** REST API for accessing eQTL
        summary statistics data""",
    },
]
