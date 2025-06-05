from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.db.client import get_mongo_client
from sumstats.api_v3.db.repositories.datasets import (
    get_single_dataset,
    list_datasets,
)
from sumstats.api_v3.db.repositories.search import search_in_dataset
from sumstats.api_v3.models.schemas import (
    AssociationModel,
    DatasetModel,
    SearchFilters,
)
from sumstats.config import API_BASE

router = APIRouter(prefix=f"{API_BASE}/v3/datasets", tags=["eQTL API v3"])


@router.get("", summary="Get Datasets", response_model=List[DatasetModel])
async def get_datasets_route(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    Lists all datasets.
    """
    return await list_datasets(client)


@router.get(
    "/{dataset_id}",
    summary="Get Dataset Metadata",
    response_model=DatasetModel,
)
async def get_dataset_route(
    dataset_id: str, client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """
    Fetch single dataset details.
    """
    dataset = await get_single_dataset(client, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.get(
    "/{dataset_id}/associations",
    summary="Search Associations Within A Dataset",
    response_model=List[AssociationModel],
)
async def search_within_dataset_route(
    dataset_id: str,
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
    Search associations within a specific dataset by search filters.
    """
    filters = SearchFilters(
        gene_id=gene_id,
        rsid=rsid,
        variant=variant,
        molecular_trait_id=molecular_trait_id,
        chromosome=chromosome,
    )
    return await search_in_dataset(client, dataset_id, filters, start, size)
