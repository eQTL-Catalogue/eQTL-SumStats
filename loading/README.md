# eQTL SumStats tsv to hdf5 loading pipeline (Nextflow)

This pipeline takes eQTL summary statistics tsv data and converts to HDF5 ready for querying by the eQTL SumStats REST API.

## Summary of tasks
- Inputs: 
  - *.tsv.gz files in the directory, <tsv_in>
  - metadata table tsv like [example_metadata.tsv](example_metadata.tsv)
- Outputs: 
  - hdf5 files for each tsv split by chromosome and quantification method published in the directory, <hdf5_study_dir>
  - hdf5 files for all data in ./<hdf5_study_dir>/ split by chromosome and quantification method published in the directory, <hdf5_chrom_dir>
- Processes
  ```
  for each chromosome in the config:
    create hdf5 for that chromosome + dataset combination and write that file to <hdf5_study_dir>/chromosome/
  ```
  - after above is complete:
  ```
  for each chromosome + quantification method in the config:
    consolidate the hdf5 in <hdf5_study_dir> and write new hdf5 to <hdf5_chrom_dir>
  ```
- Configuration
  - see [nextflow.config](nextflow.config)
- tested using nextflow version 20.10.0.5430

## Example run
```
nextflow run eQTL-SumStats/loading/tsv2hdf.nf -c eQTL-SumStats/loading/nextflow.config -with-singularity docker://ebispot/eqtl-sumstats-api:latest
```
