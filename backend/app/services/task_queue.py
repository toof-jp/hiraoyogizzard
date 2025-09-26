"""Task queue utilities backed by Valkey/Redis."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from ..models.howa import HowaTaskStatus


@dataclass
class HowaTask:
    """Representation of a persisted howa generation task."""

    task_id: str
    status: HowaTaskStatus
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: int | None = None
    updated_at: int | None = None


class HowaTaskQueue:
    """Helper around Valkey/Redis primitives to manage task lifecycle."""

    def __init__(self, redis: Redis, queue_name: str, task_ttl_seconds: int = 3600) -> None:
        self._redis = redis
        self._queue_name = queue_name
        self._task_ttl_seconds = task_ttl_seconds

    async def enqueue(self, request_payload: Dict[str, Any]) -> str:
        """Persist a task and push it to the processing queue."""

        task_id = str(uuid.uuid4())
        key = self._task_key(task_id)
        now = int(time.time())

        pipe = self._redis.pipeline()
        pipe.hset(
            key,
            mapping={
                "status": HowaTaskStatus.QUEUED.value,
                "request": json.dumps(request_payload),
                "created_at": now,
                "updated_at": now,
            },
        )
        if self._task_ttl_seconds:
            pipe.expire(key, self._task_ttl_seconds)
        pipe.rpush(self._queue_name, json.dumps({"task_id": task_id}))
        await pipe.execute()
        return task_id

    async def fetch_next(self, timeout: int = 5) -> Optional[str]:
        """Block until the next task identifier is available."""

        item = await self._redis.blpop(self._queue_name, timeout=timeout)
        if not item:
            return None
        _, payload = item
        try:
            data = json.loads(payload)
            return data.get("task_id")
        except json.JSONDecodeError:
            return None

    async def load(self, task_id: str) -> Optional[HowaTask]:
        data = await self._redis.hgetall(self._task_key(task_id))
        if not data:
            return None

        request_data: Dict[str, Any]
        try:
            request_data = json.loads(data.get("request", "{}"))
        except json.JSONDecodeError:
            request_data = {}

        result_data: Optional[Dict[str, Any]] = None
        result_raw = data.get("result")
        if result_raw:
            try:
                result_data = json.loads(result_raw)
            except json.JSONDecodeError:
                result_data = None

        status_raw = data.get("status", HowaTaskStatus.FAILED.value)
        try:
            status = HowaTaskStatus(status_raw)
        except ValueError:
            status = HowaTaskStatus.FAILED
        error = data.get("error")
        created_at = self._coerce_int(data.get("created_at"))
        updated_at = self._coerce_int(data.get("updated_at"))

        return HowaTask(
            task_id=task_id,
            status=status,
            request=request_data,
            result=result_data,
            error=error,
            created_at=created_at,
            updated_at=updated_at,
        )

    async def mark_processing(self, task_id: str) -> None:
        await self._set_status(task_id, HowaTaskStatus.PROCESSING)

    async def mark_completed(self, task_id: str, result: Dict[str, Any]) -> None:
        await self._set_status(task_id, HowaTaskStatus.COMPLETED, result=result)

    async def mark_failed(self, task_id: str, error_message: str) -> None:
        await self._set_status(task_id, HowaTaskStatus.FAILED, error=error_message)

    async def _set_status(
        self,
        task_id: str,
        status: HowaTaskStatus,
        *,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        key = self._task_key(task_id)
        mapping: Dict[str, Any] = {
            "status": status.value,
            "updated_at": int(time.time()),
        }

        if result is not None:
            mapping["result"] = json.dumps(result)
        if error is not None:
            mapping["error"] = error

        pipe = self._redis.pipeline()
        pipe.hset(key, mapping=mapping)
        if self._task_ttl_seconds:
            pipe.expire(key, self._task_ttl_seconds)
        await pipe.execute()

    def _task_key(self, task_id: str) -> str:
        return f"howa:task:{task_id}"

    @staticmethod
    def _coerce_int(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
