import os

from redis import Redis
from rq import Queue
import logging

from app.core.logging import job_trace_enabled

from app.jobs.worker import execute_job

logger = logging.getLogger(__name__)

class RQJobQueue:
    def __init__(self):
        redis_url = os.environ["REDIS_URL"]

        self.redis = Redis.from_url(redis_url)

        self.queue = Queue(
            "ig",
            connection=self.redis,
        )

    def enqueue(self, job_id: str) -> None:
        if job_trace_enabled():
            logger.info(
                "rq.enqueue.start job_id=%s queue=%s",
                job_id,
                self.queue.name,
            )
        self.queue.enqueue(
            execute_job,
            job_id,
            job_timeout=600,
        )
        if job_trace_enabled():
            logger.info(
                "rq.enqueue.complete job_id=%s queue=%s",
                job_id,
                self.queue.name,
            )
