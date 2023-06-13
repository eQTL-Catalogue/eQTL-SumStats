from distutils.core import setup

setup(
    name='eqtl-sumstats',
    version='2.0.0',
    packages=['sumstats.api_v2',
              'sumstats.api_v2.cli',
              'sumstats.api_v2.services',
              'sumstats.api_v2.schemas',
              'sumstats.api_v2.utils',
              'config',
              'sumstats.dependencies'],
    entry_points={
        "console_scripts": ['tsv2hdf = sumstats.api_v2.cli.main:main']
    },
    url='https://github.com/EBISPOT/SumStats',
    license='',
    description='Package for saving and querying large eqtl summary statistics'
)