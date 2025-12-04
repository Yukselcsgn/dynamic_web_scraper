# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
