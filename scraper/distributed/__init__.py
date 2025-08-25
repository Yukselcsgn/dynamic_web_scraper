"""
Distributed Scraping Module

This module provides distributed scraping capabilities with job queues,
worker pools, and parallel processing for large-scale scraping operations.
"""

from .job_queue import JobPriority, JobQueue, JobStatus, ScrapingJob
from .worker import DistributedScraper, Worker, WorkerPool

__all__ = [
    "JobQueue",
    "ScrapingJob",
    "JobStatus",
    "JobPriority",
    "Worker",
    "WorkerPool",
    "DistributedScraper",
]
