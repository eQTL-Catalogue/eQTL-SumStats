from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.core.config import settings
from sumstats.api_v3.models.schemas import StudyModel


async def list_studies(client: AsyncIOMotorClient) -> List[StudyModel]:
    """
    Fetches all studies from 'pipeline_status' collection.
    Each document is expected to have at least a 'study_id'.
    Using an aggregation pipeline to get unique study IDs
    and a representative status.
    """
    pipeline = [
        {"$sort": {"date": -1}},
        {"$group": {"_id": "$study_id", "status": {"$first": "$status"}}},
    ]
    agg_cursor = client[settings.db_name]["pipeline_status"].aggregate(
        pipeline
    )
    results = []
    async for doc in agg_cursor:
        results.append(StudyModel(study_id=doc["_id"], status=doc["status"]))
    return results


async def get_single_study(
    client: AsyncIOMotorClient, study_id: str
) -> Optional[StudyModel]:
    """
    Gets the latest entry for a given study_id from 'pipeline_status'
    (sort by date descending) and returns it as a StudyModel.
    """
    pipeline = [
        {"$match": {"study_id": study_id}},
        {"$sort": {"date": -1}},
        {"$limit": 1},
    ]

    docs = (
        await client[settings.db_name]["pipeline_status"]
        .aggregate(pipeline)
        .to_list(length=1)
    )
    if not docs:
        return None

    doc = docs[0]
    return StudyModel(study_id=doc["study_id"], status=doc.get("status"))
