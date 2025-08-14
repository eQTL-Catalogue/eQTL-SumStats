from typing import Optional

from pydantic import BaseModel, Field


class StudyModel(BaseModel):
    study_id: str
    status: Optional[str] = Field(None, exclude=True)


class FileStatusModel(BaseModel):
    dataset_id: str
    file_name: str
    study_id: str
    date: Optional[str] = None
    status: Optional[str] = Field(None, exclude=True)


class DatasetModel(BaseModel):
    dataset_id: str
    study_id: str
    status: Optional[str] = Field(None, exclude=True)


class AssociationModel(BaseModel):
    molecular_trait_id: str
    chromosome: str
    position: int
    ref: str
    alt: str
    variant: str
    pvalue: float
    beta: float
    se: float
    gene_id: str
    rsid: str
    study_id: str
    dataset_id: str


class SearchFilters(BaseModel):
    gene_id: Optional[str] = None
    rsid: Optional[str] = None
    variant: Optional[str] = None
    molecular_trait_id: Optional[str] = None
    chromosome: Optional[str] = None
    study_id: Optional[str] = None
    dataset_id: Optional[str] = None
