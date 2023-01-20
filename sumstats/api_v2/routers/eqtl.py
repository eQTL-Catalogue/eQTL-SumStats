from typing import List
from fastapi import APIRouter, Depends, Request

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.services.qtl_data import QTLDataService
from sumstats.api_v2.schemas.eqtl import (CommonParams,
                                          RequestFilters,
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
    start = common_params.start
    size = common_params.size
    metadata_list = QTLMetadataService().select(filters=filters,
                                                start=start,
                                                size=size)
    return metadata_list


@router.get("/datasets/{qtl_id}",
            response_model=QTLMetadata)
async def get_dataset_metadata(qtl_id: str,
                               request: Request):
    filters = QTLMetadata(dataset_id=qtl_id)
    metadata = QTLMetadataService().select(filters=filters)[0]
    return metadata


@router.get("/datasets/{qtl_id}/associations",
            response_model=List[VariantAssociation])
async def get_dataset_associations(qtl_id: str,
                                   common_params: CommonParams = Depends(),
                                   filters: RequestFilters = Depends()):
    start = common_params.start
    size = common_params.size
    sumstats_list = QTLDataService(hdf5_label=qtl_id).select(filters=filters,
                                                             start=start,
                                                             size=size)
    return sumstats_list
