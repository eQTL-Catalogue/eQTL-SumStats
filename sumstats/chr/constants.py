import h5py
from sumstats.common_constants import *

TO_LOAD_DSET_HEADERS = ['snp', 'pval', 'chr', 'or', 'bp', 'effect', 'other', 'freq']
TO_STORE_DSETS = ['snp', 'mantissa', 'exp', 'or', 'study', 'bp', 'effect', 'other', 'freq']
TO_QUERY_DSETS = ['snp', 'mantissa', 'exp', 'or', 'study', 'bp', 'effect', 'other', 'freq']

vlen_dtype = h5py.special_dtype(vlen=str)
DSET_TYPES = {'snp' : vlen_dtype, 'pval' : vlen_dtype, 'mantissa': float, 'exp': int, 'study' : vlen_dtype,
              'chr': int, 'or' : float, 'bp' : int, 'effect' : vlen_dtype, 'other' : vlen_dtype, 'freq': float}

BLOCK_SIZE = 100000
