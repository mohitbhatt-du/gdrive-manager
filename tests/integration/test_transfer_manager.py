"""Unit tests for TransferManager job handling, status transitions, and cancellation."""

import sys
from pathlib import Path
import json
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.transfer_job import TransferJob
from app.core.transfer_manager import TransferManager

@pytest.fixture
def tm():
    return TransferManager(max_concurrent=1)

def test_initial_sample_jobs(tm):
    """TransferManager should initialize with sample jobs for demonstration."""
    jobs = tm.get_jobs()
    assert len(jobs) > 0
    assert all(j.is_sample for j in jobs)

def test_add_real_job_clears_samples(tm):
    """Adding a real transfer job should replace the sample jobs."""
    real_job = TransferJob(
        id="job_real_1",
        account_name="Personal",
        item_name="test.zip",
        operation_type="Download",
        total_bytes=1000,
        is_sample=False
    )
    tm.add_job(real_job, ["dummy_cmd"])
    jobs = tm.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "job_real_1"
    assert jobs[0].is_sample is False

def test_cancel_job(tm):
    """Test cancelling an in-progress transfer job."""
    job = TransferJob(
        id="job_cancel_test",
        account_name="Personal",
        item_name="huge_dataset.iso",
        operation_type="Download",
        total_bytes=5000000,
        status="Running"
    )
    tm.cancel_job(job)
    assert job.status == "Cancelled"

def test_pause_and_resume_job(tm):
    """Test pausing and resuming transfer job."""
    job = TransferJob(
        id="job_pause_test",
        account_name="Work",
        item_name="video.mp4",
        operation_type="Upload",
        total_bytes=2000000,
        status="Running"
    )
    tm._active_commands[job.id] = ["rclone", "copy"]

    # Pause
    tm.pause_job(job)
    assert job.status == "Paused"
    assert job.speed_bytes_per_sec == 0.0

    # Resume
    tm.resume_job(job)
    assert job.status == "Running"
