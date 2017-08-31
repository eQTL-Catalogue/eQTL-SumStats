import h5py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file to be created/updated')
parser.add_argument('study_name', help = 'The name of the first group this will belong to')
parser.add_argument('snp', help = 'The SNP I am looking for')
args = parser.parse_args()

h5file = args.HDF5_output_file
study = args.study_name
snp = args.snp

f = h5py.File(h5file, 'r')

def snp_hash(snp):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique characters
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in snp]

    h = sum(pow(p, i) * s for i, s in enumerate(SNP))

    return h % N #MODULO


dataset = f.get("hash_table")
N = dataset.shape[0]
print "N is: %s" % (N)
snp_h = snp_hash(snp)
print "snp_h is: %s" % (snp_h)
array = dataset[snp_h]
snp = array[array["snp"] == snp]

print snp
