"""
Request parameters
"""

from fastapi import Query, Path
from typing import Union

from sumstats.api_v2.schemas.eqtl import QuantMethodEnum
from sumstats.api_v2.utils.helpers import neg_log_10_pval_to_pval


class CommonParams():
    def __init__(self,
                 start: int = Query(default=0,
                                    ge=0,
                                    description="Page start"),
                 size: int = Query(default=20,
                                   gt=0,
                                   le=1000,
                                   description="Page size")
                 ):
        self.start = start
        self.size = size


class DatasetID:
    def __init__(self,
                 dataset_id: str = Path(description=('Dataset ID. A dataset represents '
                                                     'a study & QTL context for a single '
                                                     'quantification method'),
                                        example="QTD000370",
                                        regex="^QTD\d+$")
                 ):
        self.dataset_id = dataset_id


class MetadataFilters:
    def __init__(self,
                 study_id: Union[str, None] = Query(default=None,
                                                    description='Study ID, e.g. QTS000001', 
                                                    regex="^QTS\d+$"),
                 quant_method: Union[QuantMethodEnum, None] = Query(default=None,
                                                                    description='Quantification method',
                                                                    example='ge'),
                 sample_group: Union[str, None] = Query(default=None,
                                                        description='Controlled vocabulary for the QTL group',
                                                        example="macrophage_naive"),
                 tissue_id: Union[str, None] = Query(default=None,
                                                     description='Ontology term for the tissue/cell type',
                                                     example="CL_0000235"),
                 study_label: Union[str, None] = Query(default=None,
                                                       description='Study label',
                                                       example="Alasoo_2018"),
                 tissue_label: Union[str, None] = Query(default=None,
                                                        description='Controlled vocabulary for the tissue/cell type',
                                                        example="macrophage"),
                 condition_label: Union[str, None] = Query(default=None,
                                                           description='More verbose condition description',
                                                           example='naive')
                 ):
        self.study_id = study_id
        self.quant_method = quant_method
        self.sample_group = sample_group
        self.tissue_id = tissue_id
        self.study_label = study_label
        self.tissue_label = tissue_label
        self.condition_label = condition_label


class SumStatsFilters:
    def __init__(self,
                 pos: Union[str, None] = Query(default=None,
                                               description="Genomic region to filter, e.g 19:80000-90000",
                                               regex="^.{1,2}:\d+-\d+$"),
                 variant: Union[str, None] = Query(default=None,
                                                   description="The variant ID (CHR_BP_REF_ALT), e.g. chr19_80901_G_T",
                                                   regex=r"^chr\d\d?_\d+_[ACTG]+_[ACTG]+$"),
                 rsid: Union[str, None] = Query(default=None,
                                                description="The rsID, if given, for the variant, e.g. rs879890648",
                                                regex=r"^rs\d+$"),
                 molecular_trait_id: Union[str, None] = Query(default=None,
                                                              description='ID of the molecular trait used for QTL mapping, e.g. ENSG00000282458'),
                 gene_id: Union[str, None] = Query(default=None,
                                                   description='Ensembl gene ID of the molecular trait, e.g. ENSG00000282458'),
                 nlog10p: Union[float, None] = Query(default=None,
                                                     description='P-value cutoff, in -Log10 format, e.g. 10.0')
                 ):
        self.pos = pos
        self.variant = variant
        self.rsid = rsid
        self.molecular_trait_id = molecular_trait_id
        self.gene_id = gene_id
        self.nlog10p = nlog10p
        self.chromosome = None
        self.position_start = None
        self.position_end = None
        self.pvalue = None
        if self.pos:
            self._split_pos_field()
        if self.nlog10p:
            self._nlog10p_to_p_float()


    def _split_pos_field(self) -> None:
        self.chromosome, bp = self.pos.split(":")
        self.position_start, self.position_end = bp.split("-")


    def _nlog10p_to_p_float(self) -> None:
        self.pvalue = neg_log_10_pval_to_pval(self.nlog10p)
        self.nlog10p = None
