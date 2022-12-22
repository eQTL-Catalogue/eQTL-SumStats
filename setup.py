from distutils.core import setup

setup(
    name='eqtl-sumstats',
    version='0.1.0',
    packages=['sumstats.api_v1', 'sumstats.api_v1.utils', 'sumstats.api_v1.server', 'sumstats.api_v1.study', 'sumstats.api_v1.study.search', 'sumstats.api_v1.study.search.access', 'sumstats.api_v1.trait', 'sumstats.api_v1.trait.search',
              'sumstats.api_v1.trait.search.access', 'sumstats.api_v1.chr', 'sumstats.api_v1.chr.search', 'sumstats.api_v1.chr.search.access', 'config', 'sumstats.dependencies.errors'],
    entry_points={
        "console_scripts": ['eqtl-load = sumstats.api_v1.load:main',
                            'eqtl-search = sumstats.api_v1.controller:main',
                            'eqtl-explore = sumstats.api_v1.explorer:main',
                            'eqtl-rebuild-snps = sumstats.api_v1.utils.vcf_to_sqlite:main',
                            'eqtl-prep-file = sumstats.api_v1.utils.split_by_chrom:main',
                            'eqtl-reindex = sumstats.api_v1.reindex:main',
                            'eqtl-delete = sumstats.api_v1.deleter:main',
                            'eqtl-consolidate = sumstats.api_v1.utils.consolidate_hdf:main']
    },
    url='https://github.com/EBISPOT/SumStats',
    license='',
    description='Package for saving and querying large eqtl summary statistics'
)
