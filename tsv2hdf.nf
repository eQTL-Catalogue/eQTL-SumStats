// nextflow run  tsv2hdf.nf --meta_table eqtl_meta.tsv --properties $EQSS_CONFIG --tsv_in ./tsv/ --hdf5_study_dir ./studies/

params.meta_table = 'metadata.tsv'
params.properties = 'properties.py'
params.tsv_in = './tsv/'
params.hdf5_study_dir = './studies/'
params.hdf5_chrom_dir = './chroms/'

tsv_glob = new File(params.tsv_in, "*.tsv.gz")
tsv_to_process = Channel.fromPath(tsv_glob)
chrom_files_glob = new File(params.hdf5_chrom_dir, "file_*.h5")
chrom_files = Channel.fromPath(chrom_files_glob)


//chromosomes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X']
chromosomes = ['1', '10', 'X']
quant_methods = ['ge', 'microarray', 'exon', 'tx', 'txrev']


process study_tsv_to_hdf5 {

  containerOptions "--bind $params.tsv_in"
  containerOptions "--bind $params.hdf5_study_dir"

  publishDir "$params.hdf5_study_dir", mode: 'copy'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }

  input:
  each chr from chromosomes
  file tsv from tsv_to_process

  output:
  file "${chr}/*.h5" optional true into hdf5_study

  """
  mkdir $chr;
  eqtl-load -f $tsv -metadata $params.meta_table -chr $chr -loader study;
  """
}


process consolidate_hdfs_by_chrom {

  containerOptions "--bind $params.hdf5_study_dir"
  containerOptions "--bind $params.hdf5_chrom_dir"

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }

  input:
  each chr from chromosomes
  each method from quant_methods
  file "${chr}/*${method}.h5" from hdf5_study.collect()

  output:
  file "file_${chr}.${method}.h5" optional true into hdf5_chrom

  """
  echo $chr;
  echo $method;
  eqtl-consolidate -in_dir $params.hdf5_study_dir -out_file $params.hdf5_chrom_dir/file_${chr}.${method}.h5 -meta  $params.meta_table -quant $method -chrom $chr
  """

}
 




// consolidate and reindex
