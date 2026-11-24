"""Durable RQ worker entry point."""
from .main import run_job


def execute_job(job_id: str) -> dict:
    return run_job(job_id)
