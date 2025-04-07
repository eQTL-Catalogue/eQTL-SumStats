import logging
from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.core.config import settings
from sumstats.api_v3.db.repositories.studies import list_studies
from sumstats.api_v3.models.schemas import AssociationModel, SearchFilters


async def search_in_study(
    client: AsyncIOMotorClient, study_id: str, filters: SearchFilters
) -> List[AssociationModel]:
    """
    Searches documents in collection 'study_{study_id}' using filters.
    """
    query = {}
    if filters.gene_id:
        query["gene_id"] = filters.gene_id
    if filters.rsid:
        query["rsid"] = filters.rsid
    if filters.variant:
        query["variant"] = filters.variant
    if filters.molecular_trait_id:
        query["molecular_trait_id"] = filters.molecular_trait_id
    if filters.chromosome:
        query["chromosome"] = filters.chromosome

    collection_name = f"study_{study_id}"
    cursor = client[settings.db_name][collection_name].find(query)
    results = []
    async for doc in cursor:
        results.append(AssociationModel(**doc))
    return results


async def search_in_dataset(
    client: AsyncIOMotorClient, dataset_id: str, filters: SearchFilters
) -> List[AssociationModel]:
    """
    Finds the study_id for the given dataset from 'pipeline_status',
    then searches in collection 'study_{study_id}' by provided filters.
    """
    doc = await client[settings.db_name]["pipeline_status"].find_one(
        {"dataset_id": dataset_id}
    )
    if not doc:
        # Optionally raise an HTTPException if dataset not found
        return []

    study_id = doc["study_id"]
    collection_name = f"study_{study_id}"

    query = {"dataset_id": dataset_id}
    if filters.gene_id:
        query["gene_id"] = filters.gene_id
    if filters.rsid:
        query["rsid"] = filters.rsid
    if filters.variant:
        query["variant"] = filters.variant
    if filters.molecular_trait_id:
        query["molecular_trait_id"] = filters.molecular_trait_id
    if filters.chromosome:
        query["chromosome"] = filters.chromosome

    cursor = client[settings.db_name][collection_name].find(query)
    results = []
    async for record in cursor:
        results.append(AssociationModel(**record))

    return results


async def search_all_studies(
    client: AsyncIOMotorClient, filters: SearchFilters, start: int, size: int
) -> List[AssociationModel]:
    """
    Use MongoDB aggregation with $unionWith to gather results
    from each 'study_{study_id}' collection, then apply a
    single skip/limit at the end.
    """
    all_studies = await list_studies(client)
    logging.info(f"Fetch all studies: {len(all_studies)} studies.")

    # 1) Build the base match query
    query = {}
    if filters.gene_id:
        query["gene_id"] = filters.gene_id
    if filters.rsid:
        query["rsid"] = filters.rsid
    if filters.variant:
        query["variant"] = filters.variant
    if filters.molecular_trait_id:
        query["molecular_trait_id"] = filters.molecular_trait_id
    if filters.chromosome:
        query["chromosome"] = filters.chromosome

    # 2) Build a pipeline starting with a match
    # that returns no docs from pipeline_status
    # so we have a base pipeline to union onto.
    pipeline: List[Dict[str, Any]] = [{"$match": {"_id": {"$exists": False}}}]

    # 3) For each study, union its collection with the match query
    logging.info("Getting studies...")
    for st in all_studies:
        study_coll = f"study_{st.study_id}"
        pipeline.append(
            {
                "$unionWith": {
                    "coll": study_coll,
                    "pipeline": [{"$match": query}],
                }
            }
        )
    logging.info("Getting studies... DONE.")

    # 4) Apply skip and limit to the entire union
    pipeline.append({"$skip": start})
    pipeline.append({"$limit": size})

    # 5) Run aggregation on any collection (pipeline_status is used as base).
    logging.info("Running the query...")
    cursor = client[settings.db_name]["pipeline_status"].aggregate(pipeline)
    logging.info("Running the query...DONE.")

    logging.info("Gathering results...")
    results = []
    async for doc in cursor:
        results.append(AssociationModel(**doc))
    logging.info("Gathering results...DONE.")

    return results


async def search_chunked(
    client: AsyncIOMotorClient, filters: SearchFilters, start: int, size: int
) -> List[AssociationModel]:
    """
    Chunk-based approach:
    1) We get the sorted list of study IDs.
    2) For each 'study_{id}' collection, we do:
       - Count how many docs match the query.
       - If 'start' >= that count, decrement 'start' by count and move on.
       - Otherwise, query the partial chunk we need from this collection
         (skip=start, limit=(size - collected_so_far)).
       - Decrement 'size' by the number of docs fetched from that collection.
       - Reset 'start' to 0 (we've already accounted for skipping).
       - Move on to the next collection if we still need more docs.
    3) Return once we've collected 'size' docs or exhausted all collections.
    """
    # 1) gather the query
    query = {}
    if filters.gene_id:
        query["gene_id"] = filters.gene_id
    if filters.rsid:
        query["rsid"] = filters.rsid
    if filters.variant:
        query["variant"] = filters.variant
    if filters.molecular_trait_id:
        query["molecular_trait_id"] = filters.molecular_trait_id
    if filters.chromosome:
        query["chromosome"] = filters.chromosome

    # 2) get all studies to know which collections to read from
    #    optionally sort them by study_id or by date
    studies = await list_studies(client)
    studies_sorted = sorted(studies, key=lambda s: s.study_id)

    final_results: List[AssociationModel] = []
    skip_remaining = start
    size_remaining = size

    # 3) loop over each study
    logging.info("Iterating study collections...")
    for st in studies_sorted:
        logging.info(f"study_{st.study_id}")
        if size_remaining <= 0:
            break  # we've collected enough

        coll_name = f"study_{st.study_id}"
        coll = client[settings.db_name][coll_name]

        # count how many docs match
        logging.info("Counting match...")
        match_count = await coll.count_documents(query)
        logging.info("Counting match...DONE.")

        if skip_remaining >= match_count:
            # skip all in this collection, continue to next
            skip_remaining -= match_count
            continue

        # partial docs in this collection
        # skip only the leftover skip_remaining if any
        partial_skip = skip_remaining
        partial_limit = size_remaining

        # we've accounted for skip
        skip_remaining = 0

        # 4) fetch docs
        logging.info("Fetching docs...")
        cursor = coll.find(query).skip(partial_skip).limit(partial_limit)
        async for doc in cursor:
            final_results.append(AssociationModel(**doc))
        logging.info("Fetching docs...DONE.")

        # now we've filled part or all of size_remaining
        fetched_count = len(final_results) - (size - size_remaining)
        size_remaining -= fetched_count

        if size_remaining <= 0:
            break

    logging.info("Iterating study collections...DONE.")

    return final_results
