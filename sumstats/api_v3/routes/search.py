import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.db.client import get_mongo_client
from sumstats.api_v3.db.repositories.search import (
    search_all_studies,
    search_chunked,
)
from sumstats.api_v3.models.schemas import AssociationModel, SearchFilters
from sumstats.config import API_BASE

router = APIRouter(prefix=f"{API_BASE}/v3", tags=["eQTL API v3 Search"])


@router.get("/search", response_model=List[AssociationModel])
async def search_all_studies_route(
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
    Type 3: Search across all studies by gene_id, rsid, or variant.
    """
    filters = SearchFilters(
        gene_id=gene_id,
        rsid=rsid,
        variant=variant,
        molecular_trait_id=molecular_trait_id,
        chromosome=chromosome,
    )
    logging.info(
        f"""Filters: gene_id: '{gene_id}' rsid='{rsid}' variant='{variant}'
        molecular_trait_id='{molecular_trait_id}' chromosome='{chromosome}'"""
    )
    return await search_all_studies(client, filters, start, size)


@router.get(
    "/search_chunked",
    response_model=List[AssociationModel],
    summary="Chunk-based search across collections",
)
async def search_all_studies_chunked_route(
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
    Similar to /search but uses a chunk-based approach to
    avoid unioning every collection up front.
    We iterate through each study_{study_id} collection in turn,
    skipping documents until we've satisfied 'start', then collecting
    up to 'size' documents in total across all collections.
    """
    filters = SearchFilters(
        gene_id=gene_id,
        rsid=rsid,
        variant=variant,
        molecular_trait_id=molecular_trait_id,
        chromosome=chromosome,
    )
    logging.info(
        f"""Filters: gene_id='{gene_id}' rsid='{rsid}' variant='{variant}'
        molecular_trait_id='{molecular_trait_id}' chromosome='{chromosome}'"""
    )
    return await search_chunked(client, filters, start, size)
