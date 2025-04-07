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

router = APIRouter(
    prefix=f"{API_BASE}/v3/datasets", tags=["eQTL API v3 Datasets"]
)


@router.get("", response_model=List[DatasetModel])
async def get_datasets_route(
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    Lists all unique dataset_ids with their latest study_id and status.
    """
    return await list_datasets(client)


@router.get("/{dataset_id}", response_model=DatasetModel)
async def get_dataset_route(
    dataset_id: str, client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """
    Retrieves the latest info for a given dataset_id.
    """
    dataset = await get_single_dataset(client, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.get("/{dataset_id}/search", response_model=List[AssociationModel])
async def search_within_dataset_route(
    dataset_id: str,
    gene_id: Optional[str] = Query(None),
    rsid: Optional[str] = Query(None),
    variant: Optional[str] = Query(None),
    molecular_trait_id: Optional[str] = Query(None),
    chromosome: Optional[str] = Query(None),
    client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    Search within a specific dataset by gene_id, rsid, or variant.
    """
    filters = SearchFilters(
        gene_id=gene_id,
        rsid=rsid,
        variant=variant,
        molecular_trait_id=molecular_trait_id,
        chromosome=chromosome,
    )
    return await search_in_dataset(client, dataset_id, filters)
