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


async def main() -> None:
#    await poll_and_handle(
#        process_job,
#        interval=1.0,
#    )

    # Use QueueClient to poll and handle all deployments instead of a specific deployment ID
    client = QueueClient(
        base_url=os.environ["IG_QUEUE_BASE_URL"],
        token=os.environ["VERCEL_OIDC_TOKEN"],
        region=os.environ["VERCEL_REGION"],
        deployment=ALL_DEPLOYMENTS,
    )

    await client.poll_and_handle(
        process_job,
        interval=1.0,
    )

if __name__ == "__main__":
    asyncio.run(main())