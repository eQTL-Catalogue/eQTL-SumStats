from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.db.client import get_mongo_client
from sumstats.api_v3.db.repositories.search import search_in_study
from sumstats.api_v3.db.repositories.studies import (
    get_single_study,
    list_studies,
)
from sumstats.api_v3.models.schemas import (
    AssociationModel,
    SearchFilters,
    StudyModel,
)
from sumstats.config import API_BASE

router = APIRouter(prefix=f"{API_BASE}/v3/studies", tags=["eQTL API v3"])


@router.get("", summary="Get Studies", response_model=List[StudyModel])
async def get_studies_route(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    List all studies.
    """
    return await list_studies(client)


@router.get(
    "/{study_id}", summary="Get Study Metadata", response_model=StudyModel
)
async def get_study_route(
    study_id: str, client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """
    Fetch single study details.
    """
    study = await get_single_study(client, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found.")
    return study


@router.get(
    "/{study_id}/search",
    summary="Search Within A Study",
    response_model=List[AssociationModel],
)
async def search_within_study_route(
    study_id: str,
    gene_id: Optional[str] = Query(None),
    rsid: Optional[str] = Query(None),
    variant: Optional[str] = Query(None),
    molecular_trait_id: Optional[str] = Query(None),
    chromosome: Optional[str] = Query(None),
    start: int = Query(0, ge=0, description="Pagination start index"),
    size: int = Query(20, gt=0, description="Number of records to return"),
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    Search within a specific study by search filters.
    """
    filters = SearchFilters(
        gene_id=gene_id,
        rsid=rsid,
        variant=variant,
        molecular_trait_id=molecular_trait_id,
        chromosome=chromosome,
    )
    return await search_in_study(client, study_id, filters, start, size)
