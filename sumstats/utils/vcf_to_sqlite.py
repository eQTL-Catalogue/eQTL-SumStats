import pandas as pd
import argparse
import os
import sumstats.utils.sqlite_client as sq 


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-vcf', help='The name of the vcf to be processed', required=False)
    argparser.add_argument('-db', help='The name of the database to load to', required=True)
    argparser.add_argument('-index', help='create index on the rsid', required=False, action='store_true')
    args = argparser.parse_args()
    db = args.db
    if args.vcf:
        vcf = args.vcf 

        vcfdf = pd.read_csv(vcf, sep='\t', 
                            comment='#', 
                            header=None, 
                            dtype=str, 
                            usecols=[0, 1, 2], 
                            names=['CHROM', 'POS', 'RSID']
                            )
            
        vcfdf.RSID = vcfdf.RSID.str.replace("rs","")

        sql = sq.sqlClient(db)
        sql.drop_rsid_index()
        list_of_tuples = list(vcfdf.itertuples(index=False, name=None))
        sql.cur.execute('BEGIN TRANSACTION')
        sql.cur.executemany("insert or ignore into snp(chr, position, rsid) values (?, ?, ?)", list_of_tuples)
        sql.cur.execute('COMMIT')
    if args.index:
        sql = sq.sqlClient(db)
        sql.drop_rsid_index()
        sql.create_rsid_index()
    else:
        print("nothing left to do")


if __name__ == '__main__':
    main()
