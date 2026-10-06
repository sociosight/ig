import anyio
import os

from vercel.queue import (
    ALL_DEPLOYMENTS,
    send,
    QueueClient,
)

TOPIC = "ig-jobs"

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

async def _enqueue(
    job_id: str,
) -> None:
    
    
    client = get_queue_client()

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