// nextflow run  tsv2hdf.nf --meta_table eqtl_meta.tsv --properties $EQSS_CONFIG --tsv_in ./tsv/ --hdf5_study_dir ./studies/

params.meta_table = 'metadata.tsv'
params.properties = 'properties.py'
params.tsv_in = './tsv/'
params.hdf5_study_dir = './studies/'
tsv_glob = new File(params.tsv_in, "*.tsv.gz")
tsv_to_process = Channel.fromPath(tsv_glob)

//chromosomes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X']
chromosomes = ['1', 'X']


process study_tsv_to_hdf5 {

  containerOptions "--bind $params.tsv_in"
  containerOptions "--bind $params.hdf5_study_dir"

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 140 ? 'retry' : 'terminate' }

  input:
  each chr from chromosomes
  file tsv from tsv_to_process

  output:
  file "study.h5" optional true into hdf5_study_no_index

  """
  EQSS_CONFIG=$params.properties;
  eqtl-load -f $tsv -metadata $params.meta_table -chr $chr -loader study;
  eqtl-reindex -f study.h5
  """

}


