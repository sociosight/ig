import asyncio
import os

# Change from specific deployment ID to ALL_DEPLOYMENTS to listen for all deployments
# from vercel.queue import poll_and_handle
from vercel.queue import (
    ALL_DEPLOYMENTS,
    QueueClient,
)

from app.jobs.vercel_subscriber import (
    process_job,
)

def get_queue_client() -> QueueClient:
    kwargs = {
        "deployment": ALL_DEPLOYMENTS,
    }

    if base_url := os.getenv("IG_QUEUE_BASE_URL"):
        kwargs["base_url"] = base_url

    if region := os.getenv("VERCEL_REGION"):
        kwargs["region"] = region

    if token := os.getenv("VERCEL_OIDC_TOKEN"):
        kwargs["token"] = token

    return QueueClient(**kwargs)

async def main() -> None:
#    await poll_and_handle(
#        process_job,
#        interval=1.0,
#    )

    # Use QueueClient to poll and handle all deployments instead of a specific deployment ID
    client = get_queue_client()

    await client.poll_and_handle(
        process_job,
        interval=1.0,
    )

if __name__ == "__main__":
    asyncio.run(main())