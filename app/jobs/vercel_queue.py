import anyio
import os

from vercel.queue import (
    ALL_DEPLOYMENTS,
    send,
    QueueClient,
)

TOPIC = "ig-jobs"


async def _enqueue(
    job_id: str,
) -> None:
    
    
    client = QueueClient(
        base_url=os.environ["IG_QUEUE_BASE_URL"],
        token=os.environ["VERCEL_OIDC_TOKEN"],
        region=os.getenv("VERCEL_REGION", "dev1"),
        deployment=ALL_DEPLOYMENTS,
    )

    await client.send(
        TOPIC,
        {
            "job_id": job_id,
        },
        idempotency_key=job_id,
        
    )


class VercelJobQueue:
    def enqueue(
        self,
        job_id: str,
    ) -> None:
        anyio.run(
            _enqueue,
            job_id,
        )