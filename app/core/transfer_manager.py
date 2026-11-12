"""Transfer Manager tracking active, queued, and completed jobs with live rclone telemetry."""

import json
import subprocess
import threading
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from app.models.transfer_job import TransferJob, get_sample_transfers
from app.utils.logger import get_logger

logger = get_logger("TransferManager")

class TransferManager:
    """Manages background transfer subprocesses, telemetry parsing, and lifecycle controls."""

    def __init__(self, max_concurrent: int = 2):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent, thread_name_prefix="TransferWorker")
        self.jobs: List[TransferJob] = []
        self._active_processes: Dict[str, subprocess.Popen] = {}
        self._active_commands: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[TransferJob], None]] = []

        # Start with sample transfers for UI preview if no jobs exist
        self._load_initial_jobs()

    def _load_initial_jobs(self):
        self.jobs = get_sample_transfers()

    def register_callback(self, cb: Callable[[TransferJob], None]):
        """Register callback for real-time job progress updates."""
        self._callbacks.append(cb)

    def _notify(self, job: TransferJob):
        for cb in self._callbacks:
            try:
                cb(job)
            except Exception as e:
                logger.error(f"Error in transfer update callback: {e}")

    def get_jobs(self) -> List[TransferJob]:
        """Return all transfer jobs."""
        with self._lock:
            return list(self.jobs)

    def add_job(self, job: TransferJob, cmd_args: List[str]):
        """Submit and start a new transfer job with its associated rclone command."""
        with self._lock:
            # If current jobs are all samples, clear samples
            if all(j.is_sample for j in self.jobs):
                self.jobs = []

            self.jobs.insert(0, job)
            self._active_commands[job.id] = cmd_args

        self.executor.submit(self._run_job_process, job, cmd_args)
        self._notify(job)

    def _run_job_process(self, job: TransferJob, cmd_args: List[str]):
        """Execute rclone subprocess and parse live JSON telemetry on stderr."""
        logger.info(f"Starting transfer job {job.id} ({job.operation_type}): {' '.join(cmd_args)}")
        job.status = "Running"
        self._notify(job)

        try:
            # Execute with --use-json-log --stats 1s
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            with self._lock:
                self._active_processes[job.id] = process

            # Read stderr line-by-line for live JSON stats
            for line in iter(process.stderr.readline, ''):
                line = line.strip()
                if not line:
                    continue

                if line.startswith("{") and line.endswith("}"):
                    try:
                        record = json.loads(line)
                        stats = record.get("stats")
                        if stats:
                            job.transferred_bytes = stats.get("bytes", job.transferred_bytes)
                            total = stats.get("totalBytes", job.total_bytes)
                            if total > 0:
                                job.total_bytes = total
                            job.speed_bytes_per_sec = float(stats.get("speed", 0.0))
                            job.eta_seconds = stats.get("eta")
                            self._notify(job)
                    except Exception:
                        pass

            process.wait()
            ret = process.returncode

            with self._lock:
                self._active_processes.pop(job.id, None)

            if job.status == "Cancelled":
                logger.info(f"Job {job.id} was cancelled by user.")
            elif job.status == "Paused":
                logger.info(f"Job {job.id} was paused.")
            elif ret == 0:
                job.status = "Completed"
                job.transferred_bytes = job.total_bytes
                job.speed_bytes_per_sec = 0.0
                job.eta_seconds = 0
                logger.info(f"Transfer job {job.id} completed successfully.")
            else:
                job.status = "Failed"
                err_detail = ""
                try:
                    err_detail = process.stderr.read()
                except Exception:
                    pass
                job.error_message = err_detail.strip() or f"Process exited with code {ret}"
                logger.warning(f"Transfer job {job.id} failed: {job.error_message}")

        except Exception as e:
            job.status = "Failed"
            job.error_message = str(e)
            logger.error(f"Error executing transfer job {job.id}: {e}", exc_info=True)

        finally:
            self._notify(job)

    def cancel_job(self, job: TransferJob):
        """Cancel an in-progress transfer job."""
        job.status = "Cancelled"
        with self._lock:
            proc = self._active_processes.get(job.id)
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
        self._notify(job)

    def pause_job(self, job: TransferJob):
        """Pause transfer by terminating current process (rclone resumes on restart)."""
        job.status = "Paused"
        job.speed_bytes_per_sec = 0.0
        with self._lock:
            proc = self._active_processes.get(job.id)
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
        self._notify(job)

    def resume_job(self, job: TransferJob):
        """Resume paused transfer job."""
        with self._lock:
            cmd = self._active_commands.get(job.id)

        if cmd:
            job.status = "Running"
            self.executor.submit(self._run_job_process, job, cmd)
            self._notify(job)

    def retry_job(self, job: TransferJob):
        """Retry a failed transfer job."""
        with self._lock:
            cmd = self._active_commands.get(job.id)

        if cmd:
            job.status = "Running"
            job.error_message = ""
            self.executor.submit(self._run_job_process, job, cmd)
            self._notify(job)
