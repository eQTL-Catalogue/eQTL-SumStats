import pandas as pd
import argparse
import os
 
 
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-vcf', help='The name of the vcf to be processed', required=True)
    argparser.add_argument('-f', help='The name of the f to be processed', required=True)
    args = argparser.parse_args()
    file = args.f
    vcf = args.vcf
    filename = os.path.basename(file)
    file_dir = os.path.dirname(file)
    outfile = os.path.join(file_dir, "rs_" + filename + ".gz")
 
    vcfdf = pd.read_csv(vcf, sep='\t', comment='#', header=None, usecols=[0, 1, 2, 3, 4], names=['CHROM', 'POS', 'RSID', 'REF', 'ALT'])
 
    vcfdf.ALT = vcfdf.ALT.str.split(",")
    vcfdf = vcfdf.explode('ALT')
 
    fdf = pd.read_csv(file, sep='\t', names=['CHROM', 'POS', 'ID', 'REF', 'ALT', 'TYPE', 'AC', 'AN', 'MAF', 'R2'])
 
    result = pd.merge(vcfdf, fdf, how='right', on=['CHROM', 'POS', 'REF', 'ALT'])
    result.drop_duplicates(inplace=True)
 
    result.to_csv(outfile, compression='infer', columns=['CHROM', 'POS', 'ID', 'REF', 'ALT', 'TYPE', 'AC', 'AN', 'MAF', 'R2', 'RSID'],
                                   index=False, mode='w', sep='\t', encoding='utf-8', na_rep="NA")
 
if __name__ == '__main__':
    main()
