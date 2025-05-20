# eQTL Summary Statistics

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=EBISPOT/SumStats&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=Badge_Coverage)

EQTL Summary statistics with HDF5 and MongoDB

The concept is to leverage the fast query times and multidimensional indexing capabilities of HDF5 and MongoDB to enable fast, useful querying of very large summary statistics datasets. There are loading scripts to convert TSV summary statistics to HDF5 using [PyTables](https://www.pytables.org/). A Python FastAPI app serves the data via a REST API. This is containerized and deployed to the cloud using Kubernetes.

This REST API facilitates filtered requests of eQTL association data from the [eQTL Catalogue](https://www.ebi.ac.uk/eqtl).

## API v3 (Latest)

API v3 provides improved access to studies and datasets with enhanced search capabilities across the entire eQTL Catalogue. Key features include:

- **Studies API**: Browse and search study information
  - List all studies: `/eqtl/api/v3/studies`
  - Get study details: `/eqtl/api/v3/studies/{study_id}`
  - Search within a study: `/eqtl/api/v3/studies/{study_id}/search`

- **Datasets API**: Access and search dataset information
  - List all datasets: `/eqtl/api/v3/datasets`
  - Get dataset details: `/eqtl/api/v3/datasets/{dataset_id}`
  - Search within a dataset: `/eqtl/api/v3/datasets/{dataset_id}/search`

- **Search API**: Global search functionality
  - Search across all studies: `/eqtl/api/v3/search`
  <!-- - Chunked search for large result sets: `/eqtl/api/v3/search_chunked` -->

### Search Filters
V3 endpoints support the following search filters:
- `gene_id`: Filter by Ensembl gene identifier (e.g., ENSG00000139618)
- `rsid`: Filter by RS ID of the variant (e.g., rs1234567)
- `variant`: Filter by variant in format chr_pos_ref_alt (e.g., 1_12345_A_G)
- `molecular_trait_id`: Filter by molecular trait identifier
- `chromosome`: Filter by chromosome (e.g., 1, 2, 3, ..., X, Y)
- `study_id`: Filter by study identifier
- `dataset_id`: Filter by dataset identifier

## API v2

Each study in the catalogue is split by QTL context and these splits are
assigned their own dataset IDs (QTD#). Datasets can be browsed at the `/datasets`
endpoint.

To retrieve the summary statistics for a dataset, use the
`/datasets/<DATASETID>/associations` endpoint and apply
any required filters.

## API v1

This will be deprecated and is maintained only for existing integrations.


# Installation

Requires the HDF5 library. Easiest way to manage this is to use the docker image. There's a public image: ebispot/eqtl-sumstats-api or for development you can clone this repo and run `docker build -t ebispot/eqtl-sumstats-api:local .`

# Running
## The web app
`docker run -v <path to API_v2>:/files/output -p 8000:8000 -e HDF5_ROOT_DIR:/files/output ebispot/eqtl-sumstats-api:local uvicorn sumstats.main:app --host 0.0.0.0`

Visit Swagger docs here: http://127.0.0.1:8000/eqtl/api/docs


## Data loading

Data loading means converting TSV data to HDF5 for API v2 or importing into MongoDB for API v3.

### For API v2: Convert sumstats TSVs to HDF5

Requires nextflow and docker installation, or singularity if run `-with-singularity` instead of `-with-docker`
The TSVs are in a single dir (--tsv_dir).
The HDF5 will be written to --hdf5_dir.
```bash
nextflow run sumstats/api_v2/workflows/tsv2hdf.nf --tsv_dir ./tsv/ --hdf5_dir ./hdf5/ -with-docker docker://ebispot/eqtl-sumstats-api:local
```

The nextflow pipeline runs a CLI:
```
tsv2hdf --help
usage: tsv2hdf [-h] -t T -hdf HDF -type {data,metadata}

optional arguments:
  -h, --help            show this help message and exit
  -t T                  tsv path
  -hdf HDF              hdf5 file label e.g. dataset1
  -type {data,metadata}
                        specify whether it is data or metadata
```
Nextflow pipeline will run the above cli for _each_ TSV (`$tsv_file`). The `$id` is the dataset id:
```
tsv2hdf -t $tsv_file -hdf $id -type data;
```
It will not run for the metadata. To run for the metadata do the following:
`$tsv_file` is the metadata tsv e.g. [here](https://github.com/eQTL-Catalogue/eQTL-Catalogue-resources/blob/master/data_tables/dataset_metadata.tsv)
```
tsv2hdf -t $tsv_file -hdf qtl_metadata -type metadata
```

### For API v3: Import data into MongoDB

API v3 uses MongoDB for faster search and more flexible data querying. We have a separate ETL pipeline that consumes FTP sources and loads data into MongoDB. Provide your MongoDB URL in an `.env` file at [sumstats/api_v3/core](sumstats/api_v3/core).

```
MONGO_URI=<MONGO_URI>
DB_NAME=<DB_NAME>
HOST=<HOST>
PORT=<PORT>
DEBUG=true
```

## Project structure
There are three versions of the API: v1, v2, and v3. The code is separated in the [sumstats](sumstats) directory:

- [sumstats/api_v1](sumstats/api_v1/): Legacy API (deprecated)
- [sumstats/api_v2](sumstats/api_v2/): Current production API using HDF5
- [sumstats/api_v3](sumstats/api_v3/): New API with improved search capabilities using MongoDB

The [sumstats/main.py](sumstats/main.py) file is where the FastAPI app is configured, including all three API versions. Note that it needs to be updated if v1 and v2 are removed.
