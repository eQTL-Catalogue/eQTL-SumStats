from fastapi import APIRouter, Depends
from sumstats.api_v2.models import Params


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root():
    pass


@router.get("/datasets")
@router.get("/datasets/", include_in_schema=False)
async def get_datasets():
    pass


@router.get("/datasets/{qtl_id}")
async def get_dataset_metadata(qtl_id: str):
    pass


@router.get("/datasets/{qtl_id}/associations")
async def get_dataset_associations(qtl_id: str,
                                   params: Params = Depends()):
    return params.dict()
