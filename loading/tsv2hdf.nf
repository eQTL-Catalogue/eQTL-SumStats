// nextflow run tsv2hdf.nf

/*
================================================================================
   Convert eQTL summary statistics to HDF5 for using in the eQTL SumStats API
================================================================================
*/


// Input files _must_ be of the *.tsv.gz residing in the tsv_in directory

tsv_glob = new File(params.tsv_in, "*.tsv.gz")
tsv_to_process = Channel.fromPath(tsv_glob)

/* Any previously generated HDF5 files in the hdf5_study_dir will be included
   in the chromosome + quant_method files.
*/


/*
================================================================================
              Split tsvs by chromosome, convert to hdf5 and index
================================================================================
*/

process study_tsv_to_hdf5 {

  containerOptions "--bind $params.data_dir"
  publishDir "$params.hdf5_study_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  file tsv from tsv_to_process

  output:
  file "${chr}/*.h5" optional true into study

  """
  mkdir $chr;
  eqtl-load -f $tsv -metadata $params.meta_table -chr $chr -loader study;
  """
}


/*
================================================================================
Consolidate all chromosome + quant method combinations into their own HDF5 files
================================================================================
*/

process consolidate_hdfs_by_chrom {

  containerOptions "--bind $params.data_dir"
  publishDir "$params.hdf5_chrom_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  each method from params.quant_methods
  file "${chr}/*.h5" from study.collect()

  output:
  file "file_${chr}.${method}.h5" optional true into hdf5_chrom

  """
  echo $chr;
  echo $method;
  eqtl-consolidate -in_dir $params.hdf5_study_dir -out_file file_${chr}.${method}.h5 -meta  $params.meta_table -quant $method -chrom $chr
  """

}
