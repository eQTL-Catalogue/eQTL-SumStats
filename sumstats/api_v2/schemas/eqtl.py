from enum import Enum
from pydantic import (BaseModel,
                      constr,
                      Field,
                      PositiveInt,
                      conint,
                      root_validator)


MAX_GENOMIC_WINDOW = 1_000_000


"""
Enums
"""


class ChromosomeEnum(str, Enum):
    chr1 = '1'
    chr2 = '2'
    chr3 = '3'
    chr4 = '4'
    chr5 = '5'
    chr6 = '6'
    chr7 = '7'
    chr8 = '8'
    chr9 = '9'
    chr10 = '10'
    chr11 = '11'
    chr12 = '12'
    chr13 = '13'
    chr14 = '14'
    chr15 = '15'
    chr16 = '16'
    chr17 = '17'
    chr18 = '18'
    chr19 = '19'
    chr20 = '20'
    chr21 = '21'
    chr22 = '22'
    chrX = 'X'
    chrY = 'Y'
    chrMT = 'MT'


class VariantTypeEnum(str, Enum):
    snp = "SNP"
    indel = "INDEL"
    other = "OTHER"


class QuantMethodEnum(str, Enum):
    gene_counts = "ge"
    exon_counts = "exon"
    microarray = "microarray"
    transcript_usage = "tx"
    txrevise = "txrev"
    leafcutter = "leafcutter"


"""
Models
"""


class Chromosome(BaseModel):
    chr: ChromosomeEnum = Field(None, alias='chromosome',
                                description='GRCh38 chromosome name of the variant',
                                      example="19",
                                      ingest_label='chromosome',
                                      searchable=True,
                                      min_size=2,
                                      pa_dtype='str')
    
    class Config:
        allow_population_by_field_name = True


class VariantIdentifer(BaseModel):
    variant: str = Field(None,
                         description="The variant ID (CHR_BP_REF_ALT)",
                         example="chr19_80901_G_T",
                         ingest_label='variant',
                         searchable=True,
                         min_size=100,
                         pa_dtype='str')
    rsid: constr(regex=r"^rs\d+$") = Field(None,
                                           description="The rsID, if given, for the variant",
                                           example="rs879890648",
                                           ingest_label='rsid',
                                           searchable=True,
                                           min_size=24,
                                           pa_dtype='str')


class Variant(Chromosome):
    position: PositiveInt = Field(None,
                                  description="GRCh38 position of the variant",
                                  example=80901,
                                  ingest_label='position',
                                  searchable=True,
                                  cs_index=True,
                                  pa_dtype='int')
    ref: constr(regex=r'^[ACGT]+$',
                strip_whitespace=True) = Field(None,
                                       description="GRCh38 reference allele",
                                       example="G",
                                       ingest_label='ref',
                                       searchable=False,
                                       min_size=255,
                                       pa_dtype='str')
    alt: constr(regex=r'^[ACGT]+$',
                strip_whitespace=True) = Field(None,
                                       description="GRCh38 alt allele (effect allele)",
                                       example="T",
                                       ingest_label='alt',
                                       searchable=False,
                                       min_size=255,
                                       pa_dtype='str')
    type: VariantTypeEnum = Field(None,
                                  description="Variant",
                                  example="SNP",
                                  ingest_label='type',
                                  searchable=False,
                                  min_size=5,
                                  pa_dtype='str')


class GenomicRegion(Chromosome):
    position_start: PositiveInt = Field(None,
                           description='Start genomic position',
                           gt_filter=True,
                           filter_on='position')
    position_end: PositiveInt = Field(None,
                           description='End genomic position',
                           lt_filter=True,
                           filter_on='position')

    @root_validator
    def validate_region(cls, values):
        chromosome, pos_start, pos_end = values.get('chr'), values.get('position_start'), values.get('position_end')
        var_count = sum(bool(x) for x in [chromosome, pos_start, pos_end])
        if var_count > 0 and var_count != 3:
            raise ValueError("Chromosome, start and end position must all be provided together")
        if pos_start and pos_start:
            if pos_start > pos_end:
                raise ValueError(("Start position must not be "
                                 "greater than end position"))
            requested_window = pos_end - pos_start
            if requested_window > MAX_GENOMIC_WINDOW:
                raise ValueError(("Requested region is larger than the "
                                 f"maximum allowable window of {MAX_GENOMIC_WINDOW}"))
        return values

    class Config:
        allow_population_by_field_name = True


class GenomicContext(BaseModel):
    molecular_trait_id: str = Field(None,
                                    description='ID of the molecular trait used for QTL mapping',
                                    example="ENSG00000282458",
                                    ingest_label='molecular_trait_id',
                                    searchable=True,
                                    min_size=100,
                                    pa_dtype='str')
    gene_id: str = Field(None,
                         description='Ensembl gene ID of the molecular trait',
                         example="ENSG00000282458",
                         ingest_label='gene_id',
                         searchable=True,
                         min_size=15,
                         pa_dtype='str')

class PValue(BaseModel):
    nlog10p: float = Field(None,
                           description="Negative log10 p-value",
                           example=0.7650602694601004,
                           searchable=False,
                           gt_filter=True,
                           pa_dtype='float')
    pvalue: float = Field(None,
                          description="P-value of association between the variant and the phenotype",
                          example=0.171767,
                          ingest_label='pvalue',
                          searchable=True,
                          lt_filter=True,
                          pa_dtype='float')


class VariantAssociation(VariantIdentifer,
                         Variant,
                         GenomicContext,
                         PValue):
    ac: int = Field(None,
                    description='Allele count',
                    example=2,
                    ingest_label='ac',
                    searchable=False,
                    pa_dtype='int')
    an: int = Field(None,
                    description='Total number of allele',
                    example=334,
                    ingest_label='an',
                    searchable=False,
                    pa_dtype='int')
    beta: float = Field(None,
                        description="Regression coefficient from the linear model",
                        example=0.984304,
                        ingest_label='beta',
                        searchable=False,
                        pa_dtype='float')
    maf: float = Field(None,
                       description="Minor allele frequency within the QTL mapping study",
                       example=0.00598802,
                       ingest_label='maf',
                       searchable=False,
                       pa_dtype='float')
    median_tpm: float = Field(None,
                              description="Expression value for the associated gene + qtl_group",
                              example=1.75669,
                              ingest_label='median_tpm',
                              searchable=False,
                              pa_dtype='float')
    r2: float = Field(None,
                      description='Imputation quality score from the imputation software',
                      example=None,
                      ingest_label='r2',
                      searchable=False,
                      pa_dtype='float')
    se: float = Field(None,
                      description='Standard error',
                      example=0.716219,
                      ingest_label='se',
                      searchable=False,
                      pa_dtype='float')


class QTLMetadataFilterable(BaseModel):
    study_id: str = Field(None,
                          description='Study ID',
                          example="QTS000001",
                          ingest_label="study_id",
                          searchable=True,
                          pa_dtype='str')
    quant_method: QuantMethodEnum = Field(None,
                                          description='Quantification method',
                                          example='ge',
                                          ingest_label='quant_method',
                                          searchable=True,
                                          pa_dtype='str')
    sample_group: str = Field(None,
                              description='Controlled vocabulary for the QTL group',
                              example="macrophage_naive",
                              ingest_label='sample_group',
                              searchable=True,
                              pa_dtype='str')
    tissue_id: str = Field(None,
                           description='Ontology term for the tissue/cell type',
                           example="CL_0000235",
                           ingest_label='tissue_id',
                           searchable=True,
                           pa_dtype='str')
    study_label: str = Field(None,
                             description='Study label',
                             example="Alasoo_2018",
                             ingest_label='study_label',
                             searchable=True,
                             pa_dtype='str')
    tissue_label: str = Field(None,
                              description='Controlled vocabulary for the tissue/cell type',
                              example="macrophage",
                              ingest_label='tissue_label',
                              searchable=True,
                              pa_dtype='str')
    condition_label: str = Field(None,
                                 description='More verbose condition description',
                                 example='naive',
                                 ingest_label='condition_label',
                                 searchable=True,
                                 pa_dtype='str')


class QTLMetadata(QTLMetadataFilterable):
    dataset_id: str = Field(None,
                            description=('Dataset ID. A dataset represents '
                                         'a study & QTL context for a single '
                                         'quantification method'),
                            example="QTD000001",
                            ingest_label='dataset_id',
                            searchable=True,
                            pa_dtype='str')
    sample_size: int = Field(None,
                             description='Sample size',
                             example=84,
                             ingest_label='sample_size',
                             searchable=False,
                             pa_dtype='str')
    _links: dict = None


class CommonParams(BaseModel):
    start: int = 0
    size: conint(gt=0, le=1000) = 20


class RequestFilters(GenomicRegion,
                     VariantIdentifer,
                     GenomicContext,
                     PValue):

    @root_validator
    def xor_genomic_context_filters(cls, values):
        variant, rsid, genomic_region = values.get('variant'), values.get('rsid'), values.get('chr')
        if sum(bool(x) for x in [variant, rsid, genomic_region]) > 1:
            raise ValueError("There can only be one genomic context "
                             "filter from: 'variant', 'rsid' "
                             "and ('chr', 'position_start', 'position_end')")
        return values
