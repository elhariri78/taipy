import logging
import uuid
from typing import Callable, Iterable, List

from taipy.common.alias import JobId
from taipy.exceptions import JobNotDeletedException, ModelNotFound, NonExistingJob
from taipy.job.job import Job
from taipy.job.repository import JobRepository
from taipy.task.task import Task


class JobManager:
    """
    The Job Manager is responsible for managing all the job-related capabilities.

    This class provides methods for creating, storing, updating, retrieving and deleting jobs.
    """

    repository = JobRepository()

    @classmethod
    def create(cls, task: Task, callbacks: Iterable[Callable]) -> Job:
        """Returns a new job representing a unique execution of the provided task.

        Args:
            task (Task): The task to execute.
            callbacks (Iterable[Callable]): Iterable of callable to be executed on job status change.

        Returns:
            A new job, that is created for executing given task.
        """
        job = Job(id=JobId(f"JOB_{uuid.uuid4()}"), task=task)
        cls.set(job)
        job.on_status_change(*callbacks)
        return job

    @classmethod
    def set(cls, job: Job):
        """
        Saves or updates a job.

        Parameters:
            job (Job): The job to save.
        """
        cls.repository.save(job)

    @classmethod
    def get(cls, job_id: JobId) -> Job:
        """Gets the job from the job id given as parameter.

        Returns:
            The Job corresponding to the id.

        Raises:
            NonExistingJob: if not found.
        """
        try:
            return cls.repository.load(job_id)
        except ModelNotFound:
            logging.error(f"Job: {job_id} does not exist.")
            raise NonExistingJob(job_id)

    @classmethod
    def get_all(cls) -> List[Job]:
        """Gets all the existing jobs.

        Returns:
            List of all jobs.
        """
        return cls.repository.load_all()

    @classmethod
    def delete(cls, job: Job, force=False):
        """Deletes the job if it is finished.

        Raises:
            JobNotDeletedException: if the job is not finished.
        """
        if job.is_finished() or force:
            cls.repository.delete(job.id)
        else:
            err = JobNotDeletedException(job.id)
            logging.warning(err)
            raise err

    @classmethod
    def delete_all(cls):
        """Deletes all jobs."""
        cls.repository.delete_all()

    @classmethod
    def get_latest_job(cls, task: Task) -> Job:
        """Allows to retrieve the latest computed job of a task.

        Returns:
            The latest computed job of the task.
        """
        return max(filter(lambda job: task in job, cls.get_all()))
