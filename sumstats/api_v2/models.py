from enum import Enum
from pydantic import BaseModel, constr, validator


class Chromosome(str, Enum):
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


class GenomicRegion(BaseModel):
    chromosome: Chromosome = None
    start: int = None
    end: int = None


class Variant(BaseModel):
    chromosome: Chromosome
    pos: int
    ref: constr(regex=r"^[ACGT]+$")
    alt: constr(regex=r"^[ACGT]+$")


class Params(BaseModel):
    start: int = 0
    size: int = 20
    pos: str = None
    nlog10p: float = None
    rsid: constr(regex=r"^rs.+$") = None
    variant_id: str = None
    molecular_trait_id: str = None
    gene_id: str = None
    variant: Variant = None
    genomic_region: GenomicRegion = None

    @validator('genomic_region', pre=True)
    def _split_pos(pos: str):
        if pos:
            chromosome = pos.split(':')[0]
            start, end = pos.split(':')[1].split('-')
            return GenomicRegion(chromosome, start, end)

    @validator('variant', pre=True)
    def _split_variant_id(variant_id: str):
        if variant_id:
            chromosome, position, ref, alt = variant_id.split('_')
            return Variant(chromosome, position, ref, alt)


class VariantAssociation(BaseModel):
    ac: int = None
    alt: str = None
    an: int = None
    beta: float = None
    chromosome: Chromosome = None
    maf: float = None
    median_tpm: float = None
    position: int = None
    pvalue: float = None
    r2: float = None
    ref: str = None
    rsid: constr(regex=r"^rs.+$") = None
    se: float = None
    type: str = None
    variant: Variant = None
    nlog10p: float = None


class SumStatsMetadata(BaseModel):
    study_id: str = None
    qtl_group: str = None
    condition: str = None
    condition_label: str = None
    tissue_label: str = None
    molecular_trait_id: str = None
    gene_id: str = None
    tissue: str = None
    _links: dict = None


