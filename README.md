# eQTL Summary Statistics

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=EBISPOT/SumStats&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/01c24035b9634ad1aaa7f66598be2483)](https://www.codacy.com/app/spot-ebi/SumStats?utm_source=github.com&utm_medium=referral&utm_content=EBISPOT/SumStats&utm_campaign=Badge_Coverage)

EQTL Summary statistics with HDF5

The concept is to leverage the fast query times and multidimensional indexing capabilities of HDF5 to enable fast, useful querying of very large summary statistics datasets. There are loading scripts to convert TSV summary statistics to HDF5 using [PyTables](https://www.pytables.org/). A Python fast-api app to serves the data via a REST API. This is conterised and deployed to the cloud using Kubernetes.

This REST API is for facilitating  a filtered request of eQTL association data.

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

Visit Swagger docs are here: http://127.0.0.1:8000/eqtl/api/docs


## Data loading

Data loading means converting tsv data to HDF5.

### Convert sumstats TSVs to HDF5

Requires nextflow and docker installation, or singularity if run `-with-singularity` instead of `-with-docker`
The TSVs are in a single dir (--tsv_dir). 
The HDF5 will be written to --hdf5_dir.
```
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

## Project structure
There are two versions of the API, v1, and v2. The code is seperated here [sumstats](sumstats), so that when the v1 api is ready to be removed, [sumstats/api_v1](sumstats/api_v1/) can simply be deleted. The [sumstats/main.py](sumstats/main.py) which is where the fast-api app is run, will also need to be updated if v1 is removed.

