from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, conint, model_validator

MAX_GENOMIC_WINDOW = 1_000_000


"""
Enums
"""


class ChromosomeEnum(str, Enum):
    chr1 = "1"
    chr2 = "2"
    chr3 = "3"
    chr4 = "4"
    chr5 = "5"
    chr6 = "6"
    chr7 = "7"
    chr8 = "8"
    chr9 = "9"
    chr10 = "10"
    chr11 = "11"
    chr12 = "12"
    chr13 = "13"
    chr14 = "14"
    chr15 = "15"
    chr16 = "16"
    chr17 = "17"
    chr18 = "18"
    chr19 = "19"
    chr20 = "20"
    chr21 = "21"
    chr22 = "22"
    chrX = "X"
    chrY = "Y"
    chrMT = "MT"


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
    aptamer = "aptamer"


"""
Models
"""


class GenomicLocation(BaseModel):
    position: Optional[PositiveInt] = Field(
        default=None,
        description="GRCh38 position of the variant",
        example=80901,
        ingest_label="position",
        searchable=True,
        cs_index=True,
        pa_dtype="int",
    )
    chromosome: Optional[ChromosomeEnum] = Field(
        default=None,
        description="GRCh38 chromosome name of the variant",
        example="19",
        ingest_label="chromosome",
        searchable=True,
        min_size=2,
        pa_dtype="str",
    )
    model_config = {"use_enum_values": True, "extra": "ignore"}


class VariantIdentifer(BaseModel):
    variant: Optional[str] = Field(
        default=None,
        description="The variant ID (CHR_BP_REF_ALT)",
        example="chr19_80901_G_T",
        ingest_label="variant",
        searchable=True,
        min_size=100,
        pa_dtype="str",
    )
    rsid: Optional[str] = Field(
        default=None,
        description="The rsID, if given, for the variant",
        example="rs879890648",
        ingest_label="rsid",
        searchable=True,
        min_size=24,
        pa_dtype="str",
    )
    model_config = {"extra": "ignore"}


class Variant(GenomicLocation):
    ref: Optional[str] = Field(
        default=None,
        description="GRCh38 reference allele",
        example="G",
        ingest_label="ref",
        searchable=False,
        min_size=255,
        pa_dtype="str",
    )
    alt: Optional[str] = Field(
        default=None,
        description="GRCh38 alt allele (effect allele)",
        example="T",
        ingest_label="alt",
        searchable=False,
        min_size=255,
        pa_dtype="str",
    )
    type: Optional[VariantTypeEnum] = Field(
        default=None,
        description="Variant",
        example="SNP",
        ingest_label="type",
        searchable=False,
        min_size=5,
        pa_dtype="str",
    )
    model_config = {"use_enum_values": True, "extra": "ignore"}


class GenomicRegion(BaseModel):
    position_start: Optional[PositiveInt] = Field(
        default=None,
        description="Start genomic position",
        gt_filter=True,
        filter_on="position",
    )
    position_end: Optional[PositiveInt] = Field(
        default=None,
        description="End genomic position",
        lt_filter=True,
        filter_on="position",
    )
    chromosome: Optional[ChromosomeEnum] = Field(
        default=None,
        description="GRCh38 chromosome name of the variant",
        example="19",
        ingest_label="chromosome",
        searchable=True,
        min_size=2,
        pa_dtype="str",
    )

    @model_validator(mode="after")
    def validate_region(self):
        chromosome, pos_start, pos_end = (
            self.chromosome,
            self.position_start,
            self.position_end,
        )

        var_count = sum(bool(x) for x in [chromosome, pos_start, pos_end])

        if var_count > 0 and var_count != 3:
            raise ValueError(
                """Chromosome, start and end position
                must all be provided together"""
            )
        if pos_start and pos_start:
            if pos_start > pos_end:
                raise ValueError(
                    ("Start position must not be " "greater than end position")
                )
            requested_window = pos_end - pos_start
            if requested_window > MAX_GENOMIC_WINDOW:
                raise ValueError(
                    (
                        "Requested region is larger than the "
                        f"maximum allowable window of {MAX_GENOMIC_WINDOW}"
                    )
                )
        return self

    model_config = {
        "allow_population_by_field_name": True,
        "use_enum_values": True,
        "extra": "ignore",
    }


class GenomicContext(BaseModel):
    molecular_trait_id: Optional[str] = Field(
        default=None,
        description="ID of the molecular trait used for QTL mapping",
        example="ENSG00000282458",
        ingest_label="molecular_trait_id",
        searchable=True,
        min_size=100,
        pa_dtype="str",
    )
    gene_id: Optional[str] = Field(
        default=None,
        description="Ensembl gene ID of the molecular trait",
        example="ENSG00000282458",
        ingest_label="gene_id",
        searchable=True,
        min_size=15,
        pa_dtype="str",
    )
    model_config = {"extra": "ignore"}


class GenomicContextIngest(GenomicLocation, GenomicContext):
    pass


class RsIdMapper(GenomicLocation):
    rsid: str = Field(
        None,
        description="The rsID, if given, for the variant",
        example="rs879890648",
        ingest_label="rsid",
        searchable=True,
        cs_index=True,
        min_size=24,
        pa_dtype="str",
    )
    position: PositiveInt = Field(
        None,
        description="GRCh38 position of the variant",
        example=80901,
        ingest_label="position",
        searchable=False,
        pa_dtype="int",
    )
    chromosome: ChromosomeEnum = Field(
        None,
        description="GRCh38 chromosome name of the variant",
        example="19",
        ingest_label="chromosome",
        searchable=False,
        min_size=2,
        pa_dtype="str",
    )


class PValue(BaseModel):
    nlog10p: Optional[float] = Field(
        default=None,
        description="Negative log10 p-value",
        example=0.7650602694601004,
        searchable=False,
        gt_filter=True,
        pa_dtype="float",
    )
    pvalue: Optional[float] = Field(
        default=None,
        description="""
            P-value of association between
            the variant and the phenotype""",
        example=0.171767,
        ingest_label="pvalue",
        searchable=True,
        lt_filter=True,
        pa_dtype="float",
    )


class VariantAssociation(VariantIdentifer, Variant, GenomicContext, PValue):
    ac: Optional[int] = Field(
        default=None,
        description="Allele count",
        example=2,
        ingest_label="ac",
        searchable=False,
        pa_dtype="int",
    )
    an: Optional[int] = Field(
        default=None,
        description="Total number of allele",
        example=334,
        ingest_label="an",
        searchable=False,
        pa_dtype="int",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Regression coefficient from the linear model",
        example=0.984304,
        ingest_label="beta",
        searchable=False,
        pa_dtype="float",
    )
    maf: Optional[float] = Field(
        default=None,
        description="Minor allele frequency within the QTL mapping study",
        example=0.00598802,
        ingest_label="maf",
        searchable=False,
        pa_dtype="float",
    )
    median_tpm: Optional[float] = Field(
        default=None,
        description="Expression value for the associated gene + qtl_group",
        example=1.75669,
        ingest_label="median_tpm",
        searchable=False,
        pa_dtype="float",
    )
    r2: Optional[float] = Field(
        default=None,
        description="Imputation quality score from the imputation software",
        example=None,
        ingest_label="r2",
        searchable=False,
        pa_dtype="float",
    )
    se: Optional[float] = Field(
        default=None,
        description="Standard error",
        example=0.716219,
        ingest_label="se",
        searchable=False,
        pa_dtype="float",
    )


class QTLMetadataFilterable(BaseModel):
    study_id: Optional[str] = Field(
        default=None,
        description="Study ID",
        example="QTS000001",
        ingest_label="study_id",
        searchable=True,
        pa_dtype="str",
    )
    quant_method: Optional[QuantMethodEnum] = Field(
        default=None,
        description="Quantification method",
        example="ge",
        ingest_label="quant_method",
        searchable=True,
        pa_dtype="str",
    )
    sample_group: Optional[str] = Field(
        default=None,
        description="Controlled vocabulary for the QTL group",
        example="macrophage_naive",
        ingest_label="sample_group",
        searchable=True,
        pa_dtype="str",
    )
    tissue_id: Optional[str] = Field(
        default=None,
        description="Ontology term for the tissue/cell type",
        example="CL_0000235",
        ingest_label="tissue_id",
        searchable=True,
        pa_dtype="str",
    )
    study_label: Optional[str] = Field(
        default=None,
        description="Study label",
        example="Alasoo_2018",
        ingest_label="study_label",
        searchable=True,
        pa_dtype="str",
    )
    tissue_label: Optional[str] = Field(
        default=None,
        description="Controlled vocabulary for the tissue/cell type",
        example="macrophage",
        ingest_label="tissue_label",
        searchable=True,
        pa_dtype="str",
    )
    condition_label: Optional[str] = Field(
        default=None,
        description="More verbose condition description",
        example="naive",
        ingest_label="condition_label",
        searchable=True,
        pa_dtype="str",
    )

    # Pydantic V2 configuration
    model_config = {
        "extra": "ignore",
        "from_attributes": True,
        "use_enum_values": True,
    }


class QTLMetadata(QTLMetadataFilterable):
    dataset_id: str = Field(
        None,
        description=(
            "Dataset ID. A dataset represents "
            "a study & QTL context for a single "
            "quantification method"
        ),
        example="QTD000001",
        ingest_label="dataset_id",
        searchable=True,
        pa_dtype="str",
    )
    sample_size: int = Field(
        None,
        description="Sample size",
        example=84,
        ingest_label="sample_size",
        searchable=False,
        pa_dtype="str",
    )
    _links: dict = None


class CommonParams(BaseModel):
    start: int = 0
    size: conint(gt=0, le=1000) = 20


class RequestFilters(PValue, GenomicContext, VariantIdentifer, GenomicRegion):
    """
    The order of the inherited models is important because
    this is the order that the filters are applied.
    """

    @model_validator(mode="after")
    def xor_filter_types(self):
        variant, rsid, genomic_region = (
            self.variant,
            self.rsid,
            self.chromosome,
        )
        if sum(bool(x) for x in [variant, rsid, genomic_region]) > 1:
            raise ValueError(
                "There can only be one of the following filter: "
                "'variant', 'rsid' "
                "and ('chr', 'position_start', 'position_end')"
            )
        return self

    @model_validator(mode="after")
    def xor_genomic_context(self):
        gene_id, molecular_trait_id = self.gene_id, self.molecular_trait_id
        if sum(bool(x) for x in [gene_id, molecular_trait_id]) > 1:
            raise ValueError(
                "There can only be one genomic context "
                "filter from: 'gene_id' and 'molecular_trait_id'"
            )
        return self

    model_config = {
        "extra": "ignore",
        "from_attributes": True,
        "use_enum_values": True,
    }
