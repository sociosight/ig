from typing import Any

from vercel.queue import subscribe

from app.jobs.worker import execute_job

import logging

from app.core.logging import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


@subscribe(
    topic="ig-jobs",
    consumer_group="ig-worker",
    max_attempts=3,
)
async def process_job(
    message: dict[str, Any],
) -> None:

    logger.info(
        "queue.message.received message=%s",
        message,
    )

    job_id = str(message["job_id"])

    logger.info(
        "queue.job.execute.start job_id=%s",
        job_id,
    )

    execute_job(job_id)

    logger.info(
        "queue.job.execute.complete job_id=%s",
        job_id,
    )