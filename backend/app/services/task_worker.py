"""Background task worker that consumes the Valkey queue."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable

from pydantic import ValidationError

from ..models.howa import GenerateHowaRequest, HowaTaskStatus
from .howa_service import HowaGenerationService
from .task_queue import HowaTaskQueue

logger = logging.getLogger(__name__)


class HowaTaskWorker:
    """Continuously poll the queue and execute howa generation tasks."""

    def __init__(
        self,
        queue: HowaTaskQueue,
        service_factory: Callable[[], HowaGenerationService],
        poll_timeout: int = 5,
    ) -> None:
        self._queue = queue
        self._service_factory = service_factory
        self._poll_timeout = poll_timeout
        self._shutdown = asyncio.Event()

    async def start(self) -> None:
        logger.info("Starting howa task worker")
        while not self._shutdown.is_set():
            try:
                task_id = await self._queue.fetch_next(timeout=self._poll_timeout)
                if task_id is None:
                    continue

                task = await self._queue.load(task_id)
                if task is None:
                    logger.warning("Task %s disappeared before processing", task_id)
                    continue

                if task.status not in {HowaTaskStatus.QUEUED, HowaTaskStatus.PROCESSING}:
                    logger.debug("Skipping task %s with status %s", task_id, task.status)
                    continue

                await self._queue.mark_processing(task_id)
                logger.info("Processing howa task %s", task_id)

                try:
                    request_model = GenerateHowaRequest(**task.request)
                except ValidationError as exc:
                    logger.exception("Invalid payload for task %s", task_id)
                    await self._queue.mark_failed(task_id, f"Invalid request payload: {exc}")
                    continue


                service = self._service_factory()
                try:
                    result = await service.generate_full_howa(request_model)
                except Exception as exc:
                    logger.exception("Task %s failed during execution", task_id)
                    await self._queue.mark_failed(task_id, str(exc))
                    continue

                await self._queue.mark_completed(task_id, result.model_dump())
                logger.info("Task %s completed", task_id)

            except asyncio.CancelledError:
                logger.info("Howa task worker cancelled")
                raise
            except Exception as exc:
                logger.exception("Unexpected error in task worker: %s", exc)

        logger.info("Howa task worker stopped")

    def stop(self) -> None:
        self._shutdown.set()
