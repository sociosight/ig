import logging
import os


def configure_logging() -> None:
    level_name = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    level = getattr(
        logging,
        level_name,
        logging.INFO,
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )


def job_trace_enabled() -> bool:
    return (
        os.getenv(
            "IG_TRACE_JOBS",
            "false",
        ).lower()
        in {"1", "true", "yes", "on"}
    )