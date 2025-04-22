from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from sumstats.api_v3.core.config import settings

# Global variable to store the client instance
_mongo_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get or create a MongoDB client using the singleton pattern.
    This ensures we only create one client instance during the
    application lifecycle.
    """
    global _mongo_client
    if _mongo_client is None:
        print(">>>>>>>>>>>>>>>>")
        print(settings.mongo_uri)
        print(settings.db_name)
        print("<<<<<<<<<<<<<<<<")
        _mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    return _mongo_client
