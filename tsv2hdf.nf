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

hdf5_study_glob = new File(params.hdf5_study_dir, "*/file_*.h5")
hdf5_study = Channel.fromPath(hdf5_study_glob)


/*
================================================================================
              Split tsvs by chromosome, convert to hdf5 and index
================================================================================
*/

process study_tsv_to_hdf5 {

  containerOptions "--bind $params.tsv_in"
  containerOptions "--bind $params.hdf5_study_dir"
  containerOptions "--bind $params.meta_table"


  publishDir "$params.hdf5_study_dir", mode: 'copy'

  memory { 2.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  file tsv from tsv_to_process

  output:
  file "${chr}/*.h5" optional true into study
  val true into study2hdf_complete

  """
  mkdir $chr;
  eqtl-load -f $tsv -metadata $params.meta_table -chr $chr -loader study;
  """
}


hdf5_study.mix(study)

hdf5_study.view()
/*
================================================================================
Consolidate all chromosome + quant method combinations into their own HDF5 files
================================================================================
*/

//process consolidate_hdfs_by_chrom {
//
//  containerOptions "--bind $params.hdf5_study_dir"
//  containerOptions "--bind $params.hdf5_chrom_dir"
//  containerOptions "--bind $params.meta_table"
//
//  publishDir "$params.hdf5_chrom_dir", mode: 'copy'
//
//  memory { 2.GB * task.attempt }
//  maxRetries 3
//  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }
//  //stageInMode 'copy'
//
//  input:
//  each chr from params.chromosomes
//  each method from params.quant_methods
//  val flag from study2hdf_complete.collect()
//  file "${chr}/*.h5" from hdf5_study.collect()
//
//  output:
//  file "file_${chr}.${method}.h5" optional true into hdf5_chrom
//
//  """
//  echo $chr;
//  echo $method;
//  eqtl-consolidate -in_dir $params.hdf5_study_dir -out_file file_${chr}.${method}.h5 -meta  $params.meta_table -quant $method -chrom $chr
//  """
//
//}
