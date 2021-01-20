process consolidate_hdfs_by_chrom {

  containerOptions "--bind $params.data_dir"
  publishDir "$params.hdf5_chrom_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  each method from params.quant_methods

  output:
  file "file_${chr}.${method}.h5" optional true into hdf5_chrom

  """
  echo $chr;
  echo $method;
  eqtl-consolidate -in_dir $params.hdf5_study_dir -out_file file_${chr}.${method}.h5 -meta  $params.meta_table -quant $method -chrom $chr
  """

}
