#!/bin/bash

source_dir=$1
quant=$2
chrom=$3
out_file=$4

for f in $hdf_study/$chrom/*+"$quant".h5; do
        echo $f
done
