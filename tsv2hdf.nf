// nextflow run tsv2hdf.nf 


hdf5_study_glob = new File(params.hdf5_study_dir, "*/file_*.h5")
hdf5_study = Channel.fromPath(hdf5_study_glob)

tsv_glob = new File(params.tsv_in, "*.tsv.gz")
tsv_to_process = Channel.fromPath(tsv_glob)


process study_tsv_to_hdf5 {

  containerOptions "--bind $params.tsv_in"
  containerOptions "--bind $params.hdf5_study_dir"

  publishDir "$params.hdf5_study_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
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


process consolidate_hdfs_by_chrom {

  containerOptions "--bind $params.hdf5_study_dir"
  containerOptions "--bind $params.hdf5_chrom_dir"

  publishDir "$params.hdf5_chrom_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }
  //stageInMode 'copy'

  input:
  each chr from params.chromosomes
  each method from params.quant_methods
  val flag from study2hdf_complete.collect()
  file "${chr}/*.h5" from hdf5_study.collect()

  output:
  file "file_${chr}.${method}.h5" optional true into hdf5_chrom

  """
  echo $chr;
  echo $method;
  eqtl-consolidate -in_dir $params.hdf5_study_dir -out_file file_${chr}.${method}.h5 -meta  $params.meta_table -quant $method -chrom $chr
  """

}
