#!/bin/bash

file_list=$(curl 'https://raw.githubusercontent.com/eQTL-Catalogue/eQTL-Catalogue-resources/master/tabix/tabix_ftp_paths.tsv' | tail -n+2 | cut -f 8 | sed 's/ftp:\/\/ftp.ebi.ac.uk\///')
remote_file_list=$(lftp -c "open ftp://ftp.ebi.ac.uk && find pub/databases/spot/eQTL/csv/")
files_not_found_count=0
for file in $file_list; do
        if echo $remote_file_list | grep -q $file; then
                :
        else
                echo "${file} not found on ftp server"
                files_not_found_count=$(( $files_not_found_count + 1 ))
        fi
done
echo "Number of files not found on FTP server: ${files_not_found_count}"
