# Distributed Package

The `distributed` package provides job queue and distributed processing capabilities.

## Modules

### 1. Job Queue (`job_queue.py`)
Thread-safe job queue for distributed scraping operations.

**Key Classes:**
- **`JobStatus`**: Enum for job states (pending, running, completed, failed, etc.)
- **`JobPriority`**: Priority levels (low, normal, high, urgent)
- **`ScrapingJob`**: Dataclass representing a scraping job
- **`JobQueue`**: Main queue manager
  - **Features:**
    - Priority-based job scheduling
    - Job persistence to disk
    - Timeout management
    - Job retry with backoff
    - Statistics tracking
    - Background tasks for cleanup

### 2. Worker (`worker.py`)
Worker implementation for processing jobs from queue.

## Usage

The distributed package enables multi-worker scraping with job management, allowing scalable data collection across multiple processes or machines.
