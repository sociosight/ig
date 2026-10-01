import os

from app.jobs.queue import JobQueue




def get_job_queue() -> JobQueue:
    provider = os.getenv(
        "JOB_QUEUE_PROVIDER",
        "rq",
    )

    if provider == "rq":
        from app.jobs.rq_queue import RQJobQueue

        return RQJobQueue()

    if provider == "vercel":
        from app.jobs.vercel_queue import VercelJobQueue

        return VercelJobQueue()

    raise RuntimeError(
        f"Unsupported job queue provider: {provider}"
    )