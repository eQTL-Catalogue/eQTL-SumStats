from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.core.config import settings
from sumstats.api_v3.models.schemas import DatasetModel


async def list_datasets(client: AsyncIOMotorClient) -> List[DatasetModel]:
    """
    Fetch all unique dataset_ids from 'pipeline_status'
    returning latest status and study_id.
    """
    pipeline = [
        {"$sort": {"date": -1}},
        {
            "$group": {
                "_id": "$dataset_id",
                "study_id": {"$first": "$study_id"},
                "status": {"$first": "$status"},
            }
        },
    ]
    agg_cursor = client[settings.db_name]["pipeline_status"].aggregate(
        pipeline
    )
    results = []
    async for doc in agg_cursor:
        if doc["_id"]:  # skip any docs missing dataset_id
            results.append(
                DatasetModel(
                    dataset_id=doc["_id"],
                    study_id=doc["study_id"],
                    status=doc["status"],
                )
            )
    return results


async def get_single_dataset(
    client: AsyncIOMotorClient, dataset_id: str
) -> Optional[DatasetModel]:
    """
    Get the latest entry (sorted by date desc)
    for a given dataset_id from 'pipeline_status'.
    """
    pipeline = [
        {"$match": {"dataset_id": dataset_id}},
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
    return DatasetModel(
        dataset_id=doc["dataset_id"],
        study_id=doc.get("study_id"),
        status=doc.get("status"),
    )
