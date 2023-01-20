from typing import List
from fastapi import APIRouter, Depends, Request

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.schemas import (CommonParams,
                                     RequestParams,
                                     VariantAssociation,
                                     QTLMetadata,
                                     QTLMetadataFilterable)


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/datasets",
            response_model=List[QTLMetadata],
            response_model_exclude={"_links"},
            response_model_exclude_unset=True)
@router.get("/datasets/", include_in_schema=False)
async def get_datasets(filters: QTLMetadataFilterable = Depends(),
                       common_params: CommonParams = Depends()):
    metadata_list = QTLMetadataService().get_many(filters=filters,
                                                  params=common_params)
    return metadata_list


@router.get("/datasets/{qtl_id}",
            response_model=QTLMetadata)
async def get_dataset_metadata(qtl_id: str,
                               request: Request):
    return {}


@router.get("/datasets/{qtl_id}/associations",
            response_model=List[VariantAssociation])
async def get_dataset_associations(qtl_id: str,
                                   params: RequestParams = Depends()):
    return []
