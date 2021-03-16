// nextflow run tsv2hdf.nf

/*
================================================================================
   Convert eQTL summary statistics to HDF5 for using in the eQTL SumStats API
================================================================================
*/


// Input files _must_ be of the *.tsv.gz residing in the tsv_in directory
def tsv_glob = []
params.quant_methods.each {
                tsv_glob.add(new File(params.tsv_in, "*_$it.*.tsv.gz"))
        }
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

  containerOptions "--bind $params.tsv_in --bind $params.meta_table --bind $params.hdf5_study_dir --bind $params.hdf5_chrom_dir"
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

  containerOptions "--bind $params.meta_table --bind $params.hdf5_study_dir"

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  each chr from params.chromosomes
  each method from params.quant_methods
  file "${chr}/*.h5" from study.collect()

  output:
  file "${chr}.${method}.h5" optional true into hdf5_chrom

  script:
  """
  hdf="${chr}.${method}.h5"
  out="file_${chr}.${method}.h5"
  for f in $params.hdf5_study_dir/$chr/*+"$method".h5; do
        echo \$f;
        if [ -f \$f ]; then
                eqtl-consolidate -in_file \$f -out_file \$hdf -meta $params.meta_table -quant $method -chrom $chr
        fi
  done
  """
}

/*
================================================================================
                        Index the consolodated hdf5
================================================================================
*/

process index_consolidated_hdfs {

  containerOptions "--bind $params.meta_table --bind $params.hdf5_study_dir --bind $params.hdf5_chrom_dir"
  publishDir "$params.hdf5_chrom_dir", mode: 'move'

  memory { 8.GB * task.attempt }
  maxRetries 3
  errorStrategy { task.exitStatus == 130 ? 'retry' : 'terminate' }

  input:
  file hdf5 from hdf5_chrom

  output:
  file "file_$hdf5" optional true into indexed_hdf5_chrom

  script:
  """
  eqtl-reindex -f $hdf5
  ptrepack --chunkshape=auto --propindexes --complevel=9 --complib=blosc $hdf5 file_$hdf5
  """

}


