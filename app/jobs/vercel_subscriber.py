from typing import Any

from vercel.queue import subscribe

from app.jobs.worker import execute_job


@subscribe(
    topic="ig-jobs",
    consumer_group="ig-worker",
    max_attempts=3,
)
async def process_job(
    message: dict[str, Any],
) -> None:
    job_id = str(message["job_id"])

    execute_job(job_id)