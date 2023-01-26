from typing import List
from fastapi import APIRouter, Depends, Request

from sumstats.api_v2.services.qtl_meta import QTLMetadataService
from sumstats.api_v2.services.qtl_data import QTLDataService
from sumstats.api_v2.schemas.eqtl import (RequestFilters,
                                          VariantAssociation,
                                          QTLMetadata,
                                          QTLMetadataFilterable)
from sumstats.api_v2.schemas.requests import (CommonParams,
                                              MetadataFilters,
                                              DatasetID,
                                              SumStatsFilters)


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/datasets",
            response_model=List[QTLMetadata],
            response_model_exclude={"_links"},
            response_model_exclude_unset=True)
@router.get("/datasets/", include_in_schema=False)
async def get_datasets(req_filters: MetadataFilters = Depends(),
                       common_params: CommonParams = Depends()):
    start = common_params.start
    size = common_params.size
    filters = QTLMetadataFilterable.parse_obj(vars(req_filters))
    metadata_list = QTLMetadataService().select(filters=filters,
                                                start=start,
                                                size=size)
    return metadata_list


@router.get("/datasets/{dataset_id}",
            response_model=QTLMetadata)
async def get_dataset_metadata(dataset_id: DatasetID = Depends()):
    filters = QTLMetadata.parse_obj(vars(dataset_id))
    metadata = QTLMetadataService().select(filters=filters, many=False)
    return metadata


@router.get("/datasets/{dataset_id}/associations",
            response_model=List[VariantAssociation])
async def get_dataset_associations(dataset_id: DatasetID = Depends(),
                                   common_params: CommonParams = Depends(),
                                   req_filters: SumStatsFilters = Depends()):
    start = common_params.start
    size = common_params.size
    hdf5_label = dataset_id.dataset_id
    filters = RequestFilters.parse_obj(vars(req_filters))
    sumstats_list = QTLDataService(hdf5_label=hdf5_label).select(filters=filters,
                                                                 start=start,
                                                                 size=size)
    return sumstats_list
