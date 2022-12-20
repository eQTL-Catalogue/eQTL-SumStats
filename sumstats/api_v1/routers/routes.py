from fastapi import APIRouter, Depends, Request
import sumstats.api_v1.server.api_endpoints_impl as endpoints
from sumstats.api_v1.models import Args


router = APIRouter(
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root(request: Request):
    return endpoints.root(request)


@router.get("/molecular_phenotypes")
@router.get("/molecular_phenotypes/")
async def get_traits(request: Request, args: Args = Depends()):
    return endpoints.traits(request_args=args, request=request)

@router.get("/molecular_phenotypes/{molecular_trait_id}")
async def get_trait(molecular_trait_id: str, request: Request, args: Args = Depends()):
    return endpoints.trait(trait=molecular_trait_id, request_args=args, request=request)

@router.get("/molecular_phenotypes/{molecular_trait_id}/associations")
async def get_trait_assocs(molecular_trait_id: str, request: Request, args: Args = Depends()):
    return endpoints.trait_associations(trait=molecular_trait_id, request_args=args, request=request)

@router.get("/associations")
@router.get("/associations/")
async def get_assocs(request: Request, args: Args = Depends()):
    return endpoints.associations(request_args=args, request=request)


@router.get("/associations/{variant_id}")
async def get_variant(variant_id: str, request: Request, args: Args = Depends()):
    return endpoints.variants(variant=variant_id, request_args=args, request=request)


@router.get("/chromosomes/{chromosome}/associations/{variant_id}")
async def get_chromosome_variants(variant_id: str,  chromosome: int, request: Request, args: Args = Depends()):
    return endpoints.variants(variant=variant_id, chromosome=chromosome, request_args=args, request=request)
