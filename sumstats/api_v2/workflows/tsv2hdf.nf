nextflow.enable.dsl=2

/*
NEXTFLOW PIPELINE to convert a directory of eqtl sumstats in TSV format
to HDF5 format.

Example usage:
nextflow run sumstats/api_v2/workflows/tsv2hdf.nf --tsv_dir ./tsv/ --hdf5_dir ./hdf5/ -with-singularity docker://ebispot/eqtl-sumstats-api:dev
*/


// Processes

process tsv_to_hdf5 {

  containerOptions "--bind $params.tsv_dir --bind $params.hdf5_dir"
  publishDir "$params.hdf5_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  tuple val(id), path(tsv_file)

  output:
  path "eqtl_hdf5_files/data/${id}.h5" 

  """
  mkdir -p eqtl_hdf5_files/data/
  tsv2hdf -t $tsv_file -hdf $id -type data;
  """
  
}


// Workflow

workflow {
    /* tsv_files
    Channel of tsv files matching the *.tsv* pattern from the tsv_dir
    
    Returns:
        [id, path]
    */
    tsv_files=Channel.fromPath("${params.tsv_dir}/*.tsv*").map{get_input_path_and_id(it)}
    tsv_to_hdf5(tsv_files)
}


// Functions

def get_input_path_and_id(Path input) {
    return [input.getSimpleName(), input]
}