from pydantic import BaseModel


class Args(BaseModel):
    start: int = 0
    size: int = 20
    p_lower: float = None
    p_upper: float = None
    quant_method: str = None
    snp: str = None
    tissue: str = None
    gene_id: str = None
    study: str = None
    molecular_trait_id: str = None
    paginate: bool = True
    links: bool = False
    qtl_group: str = None


class SumStats(BaseModel):
    ac: int = None
    alt: str = None
    an: int = None
    beta: float = None
    chromosome: str = None
    maf: float = None
    median_tpm: float = None
    position: int = None
    pvalue: float = None
    r2: float = None
    ref: str = None
    rsid: str = None
    se: float = None
    type: str = None
    variant: str = None
    study_id: str = None
    qtl_group: str = None
    condition: str = None
    condition_label: str = None
    tissue_label: str = None
    neg_log10_pvalue: float = None
    molecular_trait_id: str = None
    gene_id: str = None
    tissue: str = None
    _links: dict = None