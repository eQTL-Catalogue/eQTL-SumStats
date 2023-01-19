from typing import List
from fastapi import APIRouter, Depends
from sumstats.api_v2.models import (RequestParams,
                                    VariantAssociation,
                                    QTLMetadata)


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/datasets")
@router.get("/datasets/", include_in_schema=False)
async def get_datasets():
    pass


@router.get("/datasets/{qtl_id}",
            response_model=QTLMetadata)
async def get_dataset_metadata(qtl_id: str):
    return {}


@router.get("/datasets/{qtl_id}/associations",
            response_model=List[VariantAssociation])
async def get_dataset_associations(qtl_id: str,
                                   params: RequestParams = Depends()):
    return []
