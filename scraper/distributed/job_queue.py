#!/usr/bin/env python3
"""
Distributed Job Queue System

This module provides a job queue system for distributed scraping operations,
allowing multiple workers to process scraping tasks in parallel.
"""

import json
import logging
import queue
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class JobStatus(Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class JobPriority(Enum):
    """Job priority enumeration."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ScrapingJob:
    """Represents a scraping job in the queue."""

    id: str
    url: str
    config: Dict[str, Any]
    priority: JobPriority
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5 minutes
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScrapingJob":
        """Create job from dictionary."""
        data["priority"] = JobPriority(data["priority"])
        data["status"] = JobStatus(data["status"])

        # Convert datetime strings back to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("started_at"), str):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if isinstance(data.get("completed_at"), str):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])

        return cls(**data)


class JobQueue:
    """
    Thread-safe job queue for distributed scraping.
    """

    def __init__(self, storage_path: str = "data/job_queue"):
        """
        Initialize the job queue.

        Args:
            storage_path: Path to store job data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Thread-safe queues
        self.pending_jobs = queue.PriorityQueue()
        self.running_jobs: Dict[str, ScrapingJob] = {}
        self.completed_jobs: Dict[str, ScrapingJob] = {}
        self.failed_jobs: Dict[str, ScrapingJob] = {}

        # Threading
        self.lock = threading.RLock()
        self.running = True

        # Statistics
        self.stats = {
            "total_jobs": 0,
            "pending_jobs": 0,
            "running_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "avg_processing_time": 0.0,
        }

        # Load existing jobs
        self._load_jobs()

        # Start background tasks
        self._start_background_tasks()

    def _load_jobs(self):
        """Load jobs from storage."""
        try:
            jobs_file = self.storage_path / "jobs.json"
            if jobs_file.exists():
                with open(jobs_file, "r") as f:
                    jobs_data = json.load(f)

                for job_data in jobs_data:
                    try:
                        job = ScrapingJob.from_dict(job_data)
                        if job.status == JobStatus.PENDING:
                            self.pending_jobs.put(
                                (-job.priority.value, job.created_at.timestamp(), job)
                            )
                        elif job.status == JobStatus.RUNNING:
                            self.running_jobs[job.id] = job
                        elif job.status == JobStatus.COMPLETED:
                            self.completed_jobs[job.id] = job
                        elif job.status == JobStatus.FAILED:
                            self.failed_jobs[job.id] = job
                    except Exception as job_error:
                        logging.error(
                            f"Failed to load job {job_data.get('id', 'unknown')}: {job_error}"
                        )
                        continue

                self._update_stats()
                logging.info(f"Loaded {len(jobs_data)} jobs from storage")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse jobs.json: {e}")
            # Try to backup and recreate the file
            try:
                jobs_file = self.storage_path / "jobs.json"
                backup_file = self.storage_path / "jobs.json.backup"
                if jobs_file.exists():
                    jobs_file.rename(backup_file)
                    logging.info("Backed up corrupted jobs.json file")
            except Exception as backup_error:
                logging.error(f"Failed to backup corrupted file: {backup_error}")
        except Exception as e:
            logging.error(f"Failed to load jobs: {e}")

    def _save_jobs(self):
        """Save jobs to storage."""
        try:
            with self.lock:
                all_jobs = []

                # Get all jobs from different queues
                pending_jobs = []
                while not self.pending_jobs.empty():
                    try:
                        _, _, job = self.pending_jobs.get_nowait()
                        pending_jobs.append(job)
                    except queue.Empty:
                        break

                # Re-add pending jobs to queue
                for job in pending_jobs:
                    self.pending_jobs.put(
                        (-job.priority.value, job.created_at.timestamp(), job)
                    )

                all_jobs.extend(pending_jobs)
                all_jobs.extend(self.running_jobs.values())
                all_jobs.extend(self.completed_jobs.values())
                all_jobs.extend(self.failed_jobs.values())

                # Save to file
                jobs_file = self.storage_path / "jobs.json"
                with open(jobs_file, "w") as f:
                    json.dump(
                        [job.to_dict() for job in all_jobs], f, indent=2, default=str
                    )

        except Exception as e:
            logging.error(f"Failed to save jobs: {e}")

    def _start_background_tasks(self):
        """Start background tasks for job management."""
        # Job timeout checker
        self.timeout_thread = threading.Thread(target=self._check_timeouts, daemon=True)
        self.timeout_thread.start()

        # Job saver
        self.saver_thread = threading.Thread(target=self._periodic_save, daemon=True)
        self.saver_thread.start()

    def _check_timeouts(self):
        """Check for timed out jobs."""
        while self.running:
            try:
                with self.lock:
                    current_time = datetime.now()
                    timed_out_jobs = []

                    for job_id, job in self.running_jobs.items():
                        if (
                            job.started_at
                            and (current_time - job.started_at).total_seconds()
                            > job.timeout
                        ):
                            timed_out_jobs.append(job_id)

                    for job_id in timed_out_jobs:
                        job = self.running_jobs.pop(job_id)
                        job.status = JobStatus.TIMEOUT
                        job.completed_at = current_time
                        job.error = "Job timed out"
                        self.failed_jobs[job_id] = job
                        logging.warning(f"Job {job_id} timed out")

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logging.error(f"Error in timeout checker: {e}")
                time.sleep(60)

    def _periodic_save(self):
        """Periodically save jobs to storage."""
        while self.running:
            try:
                self._save_jobs()
                time.sleep(60)  # Save every minute
            except Exception as e:
                logging.error(f"Error in periodic save: {e}")
                time.sleep(120)

    def add_job(
        self,
        url: str,
        config: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Add a new scraping job to the queue.

        Args:
            url: Target URL to scrape
            config: Scraping configuration
            priority: Job priority
            tags: Job tags for categorization
            metadata: Additional metadata

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        job = ScrapingJob(
            id=job_id,
            url=url,
            config=config,
            priority=priority,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
            tags=tags or [],
            metadata=metadata or {},
        )

        with self.lock:
            self.pending_jobs.put((-priority.value, job.created_at.timestamp(), job))
            self.stats["total_jobs"] += 1
            self.stats["pending_jobs"] += 1

        logging.info(f"Added job {job_id} for URL: {url}")
        return job_id

    def get_job(self, worker_id: str) -> Optional[ScrapingJob]:
        """
        Get the next available job for a worker.

        Args:
            worker_id: ID of the worker requesting a job

        Returns:
            ScrapingJob or None if no jobs available
        """
        try:
            with self.lock:
                if self.pending_jobs.empty():
                    return None

                _, _, job = self.pending_jobs.get_nowait()
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now()
                job.worker_id = worker_id

                self.running_jobs[job.id] = job
                self.stats["pending_jobs"] -= 1
                self.stats["running_jobs"] += 1

                logging.info(f"Worker {worker_id} started job {job.id}")
                return job

        except queue.Empty:
            return None
        except Exception as e:
            logging.error(f"Error getting job: {e}")
            return None

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """
        Mark a job as completed.

        Args:
            job_id: Job ID to complete
            result: Job result data
        """
        with self.lock:
            if job_id in self.running_jobs:
                job = self.running_jobs.pop(job_id)
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.result = result

                self.completed_jobs[job_id] = job
                self.stats["running_jobs"] -= 1
                self.stats["completed_jobs"] += 1

                # Update average processing time
                processing_time = (job.completed_at - job.started_at).total_seconds()
                self._update_avg_processing_time(processing_time)

                logging.info(f"Job {job_id} completed successfully")
            else:
                logging.warning(f"Attempted to complete non-existent job: {job_id}")

    def fail_job(self, job_id: str, error: str):
        """
        Mark a job as failed.

        Args:
            job_id: Job ID to mark as failed
            error: Error message
        """
        with self.lock:
            if job_id in self.running_jobs:
                job = self.running_jobs.pop(job_id)
                job.error = error

                # Check if we should retry
                if job.retry_count < job.max_retries:
                    job.retry_count += 1
                    job.status = JobStatus.PENDING
                    job.started_at = None
                    job.worker_id = None
                    job.error = None

                    self.pending_jobs.put(
                        (-job.priority.value, job.created_at.timestamp(), job)
                    )
                    self.stats["running_jobs"] -= 1
                    self.stats["pending_jobs"] += 1

                    logging.info(
                        f"Job {job_id} will be retried (attempt {job.retry_count}/{job.max_retries})"
                    )
                else:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now()

                    self.failed_jobs[job_id] = job
                    self.stats["running_jobs"] -= 1
                    self.stats["failed_jobs"] += 1

                    logging.error(f"Job {job_id} failed permanently: {error}")
            else:
                logging.warning(f"Attempted to fail non-existent job: {job_id}")

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if job was cancelled, False otherwise
        """
        with self.lock:
            # Check if job is in pending queue
            pending_jobs = []
            found = False

            while not self.pending_jobs.empty():
                try:
                    _, _, job = self.pending_jobs.get_nowait()
                    if job.id == job_id:
                        job.status = JobStatus.CANCELLED
                        found = True
                        self.stats["pending_jobs"] -= 1
                        logging.info(f"Job {job_id} cancelled")
                    else:
                        pending_jobs.append(job)
                except queue.Empty:
                    break

            # Re-add other jobs
            for job in pending_jobs:
                self.pending_jobs.put(
                    (-job.priority.value, job.created_at.timestamp(), job)
                )

            return found

    def get_job_status(self, job_id: str) -> Optional[ScrapingJob]:
        """
        Get the status of a specific job.

        Args:
            job_id: Job ID to check

        Returns:
            ScrapingJob or None if not found
        """
        with self.lock:
            # Check all job collections
            for job in [self.running_jobs, self.completed_jobs, self.failed_jobs]:
                if job_id in job:
                    return job[job_id]
            return None

    def get_result(self, job_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed job.

        Args:
            job_id: Job ID to get result for
            timeout: Timeout in seconds

        Returns:
            Job result or None if not found or timed out
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self.lock:
                if job_id in self.completed_jobs:
                    job = self.completed_jobs[job_id]
                    return job.result
                elif job_id in self.failed_jobs:
                    job = self.failed_jobs[job_id]
                    return {"error": getattr(job, "error_message", "Unknown error")}

            time.sleep(1)  # Wait 1 second before checking again

        logging.warning(f"Timeout waiting for job {job_id} result")
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self.lock:
            return self.stats.copy()

    def _update_stats(self):
        """Update statistics."""
        self.stats["pending_jobs"] = self.pending_jobs.qsize()
        self.stats["running_jobs"] = len(self.running_jobs)
        self.stats["completed_jobs"] = len(self.completed_jobs)
        self.stats["failed_jobs"] = len(self.failed_jobs)
        self.stats["total_jobs"] = (
            self.stats["pending_jobs"]
            + self.stats["running_jobs"]
            + self.stats["completed_jobs"]
            + self.stats["failed_jobs"]
        )

    def _update_avg_processing_time(self, new_time: float):
        """Update average processing time."""
        current_avg = self.stats["avg_processing_time"]
        completed_count = self.stats["completed_jobs"]

        if completed_count > 0:
            self.stats["avg_processing_time"] = (
                current_avg * (completed_count - 1) + new_time
            ) / completed_count
        else:
            self.stats["avg_processing_time"] = new_time

    def cleanup_old_jobs(self, days: int = 7):
        """
        Clean up old completed and failed jobs.

        Args:
            days: Number of days to keep jobs
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        with self.lock:
            # Clean completed jobs
            old_completed = [
                job_id
                for job_id, job in self.completed_jobs.items()
                if job.completed_at and job.completed_at < cutoff_date
            ]
            for job_id in old_completed:
                del self.completed_jobs[job_id]

            # Clean failed jobs
            old_failed = [
                job_id
                for job_id, job in self.failed_jobs.items()
                if job.completed_at and job.completed_at < cutoff_date
            ]
            for job_id in old_failed:
                del self.failed_jobs[job_id]

            logging.info(
                f"Cleaned up {len(old_completed)} completed and {len(old_failed)} failed jobs"
            )

    def shutdown(self):
        """Shutdown the job queue."""
        self.running = False
        self._save_jobs()
        logging.info("Job queue shutdown complete")
