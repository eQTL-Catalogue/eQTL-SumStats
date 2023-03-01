import pkg_resources

APP_VERSION = pkg_resources.get_distribution("eqtl-sumstats").version

API_BASE = "/eqtl/api"

API_DESCRIPTION = """
<img src='https://raw.githubusercontent.com/eQTL-Catalogue/eQTL-Catalogue-website/gh-pages/static/eQTL_icon.png' alt="eqtl_icon" width="10%">

Welcome to the [eQTL Catalogue](https://www.ebi.ac.uk/eqtl) RESTful API.

This API is for facilitating  a filtered request of 
eQTL association data.

## API v2

Each study in the catalogue is split by QTL context and these splits are
assigned their own dataset IDs (QTD#). Datasets can be browsed at the `/datasets` 
endpoint. 

To retrieve the summary statistics for a dataset, use the 
`/datasets/<DATASETID>/associations` endpoint and apply 
any required filters. 

## API v1

This will be deprecated and is maintained only for existing integrations. 

## All associations
If you are interested in downloading 
_all_ the association data for a dataset, the recommended 
method would be via the FTP.
"""

TAGS_METADATA = [
    {
        "name": "eQTL API v2",
        "description": "REST API for accessing eQTL summary statistics data",
    },
    {
        "name": "eQTL API v1",
        "description": "**Deprecated** REST API for accessing eQTL summary statistics data",
    }
]
