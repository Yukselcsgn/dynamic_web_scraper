#!/usr/bin/env python3
"""
Distributed Worker System

This module provides a worker system for distributed scraping operations,
allowing multiple workers to process scraping jobs in parallel.
"""

import logging
import signal
import sys
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from ..config import load_config
from .job_queue import JobQueue, JobStatus, ScrapingJob


class Worker:
    """
    A worker that processes scraping jobs from the job queue.
    """

    def __init__(
        self,
        worker_id: str = None,
        job_queue: JobQueue = None,
        config: Dict[str, Any] = None,
        max_jobs: int = 100,
    ):
        """
        Initialize the worker.

        Args:
            worker_id: Unique worker ID
            job_queue: Job queue instance
            config: Worker configuration
            max_jobs: Maximum number of jobs to process before stopping
        """
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.job_queue = job_queue
        self.config = config or load_config()
        self.max_jobs = max_jobs
        self.jobs_processed = 0

        # Worker state
        self.running = False
        self.current_job: Optional[ScrapingJob] = None
        self.worker_thread: Optional[threading.Thread] = None

        # Statistics
        self.stats = {
            "jobs_processed": 0,
            "jobs_succeeded": 0,
            "jobs_failed": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0,
            "start_time": None,
            "last_job_time": None,
        }

        # Setup signal handlers for graceful shutdown (only in main thread)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError:
            # Signal handlers can only be set in the main thread
            logging.warning(
                f"Worker {self.worker_id} cannot set signal handlers (not in main thread)"
            )

        logging.info(f"Worker {self.worker_id} initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logging.info(
            f"Worker {self.worker_id} received signal {signum}, shutting down..."
        )
        self.stop()

    def start(self):
        """Start the worker."""
        if self.running:
            logging.warning(f"Worker {self.worker_id} is already running")
            return

        self.running = True
        self.stats["start_time"] = datetime.now()

        self.worker_thread = threading.Thread(target=self._work_loop, daemon=True)
        self.worker_thread.start()

        logging.info(f"Worker {self.worker_id} started")

    def stop(self):
        """Stop the worker."""
        if not self.running:
            return

        self.running = False

        if self.worker_thread:
            self.worker_thread.join(timeout=10)

        logging.info(f"Worker {self.worker_id} stopped")

    def _work_loop(self):
        """Main work loop for processing jobs in background."""
        while self.running and self.jobs_processed < self.max_jobs:
            try:
                # Get next job
                job = self.job_queue.get_job(self.worker_id)

                if job is None:
                    # No jobs available, wait a bit longer to reduce CPU usage
                    time.sleep(10)
                    continue

                # Process the job in background thread to avoid blocking
                self._process_job_background(job)
                self.jobs_processed += 1

                # Check if we've reached max jobs
                if self.jobs_processed >= self.max_jobs:
                    logging.info(
                        f"Worker {self.worker_id} reached max jobs limit ({self.max_jobs})"
                    )
                    break

            except Exception as e:
                logging.error(f"Worker {self.worker_id} error in work loop: {e}")
                time.sleep(15)  # Longer wait on error

    def _process_job_background(self, job: ScrapingJob):
        """Process job in a separate background thread to avoid blocking."""

        def background_worker():
            try:
                self._process_job(job)
            except Exception as e:
                logging.error(f"Background job processing failed for job {job.id}: {e}")

        # Start background thread
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()

        # Wait for completion with timeout
        thread.join(timeout=job.timeout)

        if thread.is_alive():
            logging.warning(f"Job {job.id} timed out in background processing")
            # Mark job as failed due to timeout
            self.job_queue.mark_job_failed(job.id, "Background processing timeout")

    def _process_job(self, job: ScrapingJob):
        """Process a single scraping job."""
        # Import Scraper locally to avoid circular import
        from ..core.scraper import Scraper

        start_time = time.time()
        self.current_job = job

        logging.info(f"Worker {self.worker_id} processing job {job.id}: {job.url}")

        try:
            # Create scraper instance
            with Scraper(job.url, job.config) as scraper:
                # Run the scraping workflow
                result = scraper.fetch_data(
                    enable_smart_detection=True,
                    enable_enrichment=True,
                    enable_analysis=True,
                )

                # Calculate processing time
                processing_time = time.time() - start_time
                self._update_stats(processing_time, success=True)

                # Mark job as completed
                self.job_queue.complete_job(job.id, result)

                logging.info(
                    f"Worker {self.worker_id} completed job {job.id} in {processing_time:.2f}s"
                )

        except Exception as e:
            # Calculate processing time
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)

            # Mark job as failed
            error_msg = str(e)
            self.job_queue.fail_job(job.id, error_msg)

            logging.error(f"Worker {self.worker_id} failed job {job.id}: {error_msg}")

        finally:
            self.current_job = None
            self.stats["last_job_time"] = datetime.now()

    def _update_stats(self, processing_time: float, success: bool):
        """Update worker statistics."""
        self.stats["total_processing_time"] += processing_time

        if success:
            self.stats["jobs_succeeded"] += 1
        else:
            self.stats["jobs_failed"] += 1

        # Update average processing time
        total_jobs = self.stats["jobs_succeeded"] + self.stats["jobs_failed"]
        if total_jobs > 0:
            self.stats["avg_processing_time"] = (
                self.stats["total_processing_time"] / total_jobs
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        stats = self.stats.copy()

        # Add current status
        stats["running"] = self.running
        stats["current_job"] = self.current_job.id if self.current_job else None
        stats["uptime"] = (
            (datetime.now() - self.stats["start_time"]).total_seconds()
            if self.stats["start_time"]
            else 0
        )

        return stats

    def is_idle(self) -> bool:
        """Check if worker is idle (not processing a job)."""
        return self.current_job is None


class WorkerPool:
    """
    A pool of workers for distributed scraping.
    """

    def __init__(
        self, job_queue: JobQueue, num_workers: int = 4, config: Dict[str, Any] = None
    ):
        """
        Initialize the worker pool.

        Args:
            job_queue: Job queue instance
            num_workers: Number of workers to create
            config: Worker configuration
        """
        self.job_queue = job_queue
        self.num_workers = num_workers
        self.config = config or load_config()

        self.workers: Dict[str, Worker] = {}
        self.running = False

        logging.info(f"Worker pool initialized with {num_workers} workers")

    def start(self):
        """Start all workers in the pool."""
        if self.running:
            logging.warning("Worker pool is already running")
            return

        self.running = True

        for i in range(self.num_workers):
            worker_id = f"worker-{i+1:02d}"
            worker = Worker(worker_id, self.job_queue, self.config)
            worker.start()
            self.workers[worker_id] = worker

        logging.info(f"Started {self.num_workers} workers")

    def stop(self):
        """Stop all workers in the pool."""
        if not self.running:
            return

        self.running = False

        for worker in self.workers.values():
            worker.stop()

        self.workers.clear()
        logging.info("All workers stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all workers."""
        stats = {
            "num_workers": len(self.workers),
            "running": self.running,
            "workers": {},
        }

        for worker_id, worker in self.workers.items():
            stats["workers"][worker_id] = worker.get_stats()

        return stats

    def get_idle_workers(self) -> int:
        """Get number of idle workers."""
        return sum(1 for worker in self.workers.values() if worker.is_idle())

    def get_busy_workers(self) -> int:
        """Get number of busy workers."""
        return sum(1 for worker in self.workers.values() if not worker.is_idle())


class DistributedScraper:
    """
    High-level interface for distributed scraping operations.
    """

    def __init__(self, num_workers: int = 4, storage_path: str = "data/job_queue"):
        """
        Initialize the distributed scraper.

        Args:
            num_workers: Number of workers to use
            storage_path: Path for job queue storage
        """
        self.job_queue = JobQueue(storage_path)
        self.worker_pool = WorkerPool(self.job_queue, num_workers)
        self.config = load_config()

        logging.info(f"Distributed scraper initialized with {num_workers} workers")

    def add_jobs(
        self,
        urls: list,
        config: Dict[str, Any] = None,
        priority: str = "normal",
        tags: list = None,
    ) -> list:
        """
        Add multiple scraping jobs to the queue.

        Args:
            urls: List of URLs to scrape
            config: Scraping configuration
            priority: Job priority (low, normal, high, urgent)
            tags: Job tags

        Returns:
            List of job IDs
        """
        from .job_queue import JobPriority

        priority_map = {
            "low": JobPriority.LOW,
            "normal": JobPriority.NORMAL,
            "high": JobPriority.HIGH,
            "urgent": JobPriority.URGENT,
        }

        job_priority = priority_map.get(priority.lower(), JobPriority.NORMAL)
        job_config = config or self.config

        job_ids = []
        for url in urls:
            job_id = self.job_queue.add_job(
                url=url, config=job_config, priority=job_priority, tags=tags or []
            )
            job_ids.append(job_id)

        logging.info(f"Added {len(job_ids)} jobs to queue")
        return job_ids

    def start_workers(self):
        """Start the worker pool."""
        self.worker_pool.start()

    def stop_workers(self):
        """Stop the worker pool."""
        self.worker_pool.stop()

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get job queue statistics."""
        return self.job_queue.get_stats()

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        return self.worker_pool.get_stats()

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        job = self.job_queue.get_job_status(job_id)
        if job:
            return job.to_dict()
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        return self.job_queue.cancel_job(job_id)

    def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed and failed jobs."""
        self.job_queue.cleanup_old_jobs(days)

    def shutdown(self):
        """Shutdown the distributed scraper."""
        self.stop_workers()
        self.job_queue.shutdown()
        logging.info("Distributed scraper shutdown complete")


def run_worker(worker_id: str, job_queue: JobQueue, config: Dict[str, Any] = None):
    """
    Run a single worker (for standalone worker processes).

    Args:
        worker_id: Worker ID
        job_queue: Job queue instance
        config: Worker configuration
    """
    worker = Worker(worker_id, job_queue, config)

    try:
        worker.start()

        # Keep the worker running
        while worker.running:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info(f"Worker {worker_id} received interrupt signal")
    finally:
        worker.stop()


if __name__ == "__main__":
    # Example usage for standalone worker
    import argparse

    parser = argparse.ArgumentParser(description="Run a distributed scraping worker")
    parser.add_argument("--worker-id", required=True, help="Worker ID")
    parser.add_argument(
        "--storage-path", default="data/job_queue", help="Job queue storage path"
    )
    parser.add_argument("--config", help="Path to config file")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        # Load from specific config file
        import json

        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = load_config()

    # Create job queue
    job_queue = JobQueue(args.storage_path)

    # Run worker
    run_worker(args.worker_id, job_queue, config)
