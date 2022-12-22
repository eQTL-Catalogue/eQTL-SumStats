process consolidate_hdfs_by_chrom {

  containerOptions "--bind $params.meta_table --bind $params.hdf5_study_dir --bind $params.hdf5_chrom_dir"
  publishDir "$params.hdf5_chrom_dir", mode: 'move'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  each method from params.quant_methods

  output:
  file "file_${chr}.${method}.h5" optional true into hdf5_chrom

  script:
  """
  echo $chr;
  echo $method;
  hdf="${chr}.${method}.h5"
  out="file_${chr}.${method}.h5"
  for f in $params.hdf5_study_dir/$chr/*+"$method".h5; do
        echo \$f;
        if [ -f \$f ]; then
                eqtl-consolidate -in_file \$f -out_file \$hdf -meta $params.meta_table -quant $method -chrom $chr
        fi
  done
  #if [ -f \$hdf ]; then
  #      eqtl-reindex -f \$hdf
  #      ptrepack --chunkshape=auto --propindexes --complevel=9 --complib=blosc \$hdf \$out
  #fi
  """

}
