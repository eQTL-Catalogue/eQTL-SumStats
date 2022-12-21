from fastapi import APIRouter, Depends, Request
import sumstats.api_v1.server.api_endpoints_impl as endpoints
from sumstats.api_v1.models import Args


router = APIRouter(
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root(request: Request):
    return endpoints.root(request)


@router.get("/associations")
@router.get("/associations/", include_in_schema=False)
async def get_assocs(request: Request, args: Args = Depends()):
    return endpoints.associations(request_args=args,
                                  request=request)


@router.get("/associations/{variant_id}")
async def get_variant(variant_id: str,
                      request: Request,
                      args: Args = Depends()):
    return endpoints.variants(variant=variant_id,
                              request_args=args,
                              request=request)


@router.get("/molecular_phenotypes")
@router.get("/molecular_phenotypes/", include_in_schema=False)
async def get_traits(request: Request,
                     start: int = 0,
                     size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.traits(request_args=args,
                            request=request)


@router.get("/molecular_phenotypes/{molecular_trait_id}")
async def get_trait(molecular_trait_id: str,
                    request: Request,
                    args: Args = Depends()):
    return endpoints.trait(trait=molecular_trait_id,
                           request_args=args,
                           request=request)


@router.get("/molecular_phenotypes/{molecular_trait_id}/associations")
async def get_trait_assocs(molecular_trait_id: str,
                           request: Request,
                           args: Args = Depends()):
    return endpoints.trait_associations(trait=molecular_trait_id,
                                        request_args=args,
                                        request=request)


@router.get("/studies")
async def get_studies(request: Request,
                      start: int = 0,
                      size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.studies(request_args=args,
                             request=request)


@router.get("/studies/{study}/associations")
@router.get("/tissues/{tissue}/studies/{study}/associations")
async def get_tissue_study_assocs(study: str,
                                  request: Request,
                                  args: Args = Depends(),
                                  tissue: str = None):
    return endpoints.tissue_study_associations(study=study,
                                               tissue=tissue,
                                               request_args=args,
                                               request=request)


@router.get("/tissues")
async def get_tissues(request: Request,
                      start: int = 0,
                      size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.tissues(request_args=args,
                             request=request)


@router.get("/tissues/{tissue}")
async def get_tissue(tissue: str,
                     request: Request,
                     start: int = 0,
                     size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.tissue(tissue=tissue,
                            request_args=args,
                            request=request)


@router.get("/tissues/{tissue}/studies")
async def get_studies_for_tissue(tissue: str,
                                 request: Request,
                                 start: int = 0,
                                 size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.studies_for_tissue(tissue=tissue,
                                        request_args=args,
                                        request=request)


@router.get("/tissues/{tissue}/associations")
async def get_tissue_assocs(tissue: str,
                            request: Request,
                            args: Args = Depends()):
    return endpoints.tissue_associations(tissue=tissue,
                                         request_args=args,
                                         request=request)


@router.get("/studies/{study}")
@router.get("/tissues/{tissue}/studies/{study}")
async def get_tissue_study(study: str,
                           request: Request,
                           tissue: str = None):
    return endpoints.tissue_study(study=study,
                                  tissue=tissue,
                                  request=request)


@router.get("/chromosomes")
@router.get("/chromosomes/", include_in_schema=False)
async def get_chromosomes(request: Request):
    return endpoints.chromosomes(request=request)


@router.get("/chromosomes/{chromosome}")
async def get_chromosome(chromosome: str,
                         request: Request):
    return endpoints.chromosome(chromosome=chromosome,
                                request=request)


@router.get("/chromosomes/{chromosome}/associations")
async def get_chromosome_assocs(chromosome: str,
                                request: Request,
                                args: Args = Depends()):
    return endpoints.chromosome_associations(chromosome=chromosome,
                                             request_args=args,
                                             request=request)


@router.get("/chromosomes/{chromosome}/associations/{variant_id}")
async def get_chromosome_variants(variant_id: str,
                                  chromosome: int,
                                  request: Request,
                                  args: Args = Depends()):
    return endpoints.variants(variant=variant_id,
                              chromosome=chromosome,
                              request_args=args,
                              request=request)


@router.get("/qtl_groups")
async def get_qtl_groups(request: Request,
                         start: int = 0,
                         size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.qtl_groups(request_args=args,
                                request=request)


@router.get("/genes")
async def get_genes(request: Request,
                    start: int = 0,
                    size: int = 20):
    args = Args()
    args.start = start
    args.size = size
    return endpoints.genes(request_args=args,
                           request=request)


@router.get("/genes/{gene_id}")
async def get_gene(gene_id: str,
                   request: Request):
    return endpoints.gene(gene=gene_id,
                          request=request)


@router.get("/genes/{gene_id}/associations")
async def get_gene_assocs(gene_id: str,
                          request: Request,
                          args: Args = Depends()):
    return endpoints.gene_associations(gene=gene_id,
                                       request_args=args,
                                       request=request)