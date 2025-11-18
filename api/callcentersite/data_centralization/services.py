"""Domain services and strategies for data_centralization queries."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol, Sequence

from django.utils import timezone


class InvalidQueryTypeError(Exception):
    """Raised when an unsupported query type is requested."""


class QueryExecutionError(Exception):
    """Raised when a strategy cannot complete its execution."""


class DataQueryStrategy(Protocol):
    """Contract for data query strategies."""

    query_type: str

    def execute(self, days: int, limit: int) -> dict[str, Any]:
        """Execute the query for the given time window and limit."""


@dataclass
class DataQueryResult:
    """Typed container for strategy responses."""

    query_type: str
    source: str
    days: int
    count: int
    data: Any
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the result."""

        payload: dict[str, Any] = {
            "query_type": self.query_type,
            "source": self.source,
            "days": self.days,
            "count": self.count,
            "data": self.data,
        }
        if self.note:
            payload["note"] = self.note
        return payload


class DataQueryService:
    """Coordinates available strategies for the data query API."""

    def __init__(self, strategies: Sequence[DataQueryStrategy]):
        self._strategies = {strategy.query_type: strategy for strategy in strategies}

    @property
    def valid_types(self) -> list[str]:
        """Return the supported query types."""

        return list(self._strategies.keys())

    def run(self, query_type: str, days: int, limit: int) -> dict[str, Any]:
        """Execute the strategy that matches the requested query type."""

        strategy = self._strategies.get(query_type)
        if strategy is None:
            raise InvalidQueryTypeError(f"Unsupported query type: {query_type}")

        return strategy.execute(days=days, limit=limit)


class MetricsQueryStrategy:
    """Simple in-memory metrics provider used for API responses."""

    query_type = "metrics"

    def __init__(
        self,
        dataset: Sequence[dict[str, Any]] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._dataset = list(dataset) if dataset is not None else []
        self._clock = clock or timezone.now

    def execute(self, days: int, limit: int) -> dict[str, Any]:
        cutoff = self._clock() - timedelta(days=days)
        filtered: list[dict[str, Any]] = []

        for entry in self._dataset:
            created_at = self._coerce_datetime(entry.get("created_at"))
            if created_at is None or created_at < cutoff:
                continue

            serialized = {
                **entry,
                "created_at": created_at.isoformat(),
            }
            filtered.append(serialized)
            if len(filtered) >= limit:
                break

        result = DataQueryResult(
            query_type=self.query_type,
            source="in-memory",
            days=days,
            count=len(filtered),
            data=filtered,
        )
        return result.to_dict()

    @staticmethod
    def _coerce_datetime(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                normalized = value.replace("Z", "+00:00")
                return datetime.fromisoformat(normalized)
            except ValueError:
                return None
        return None


class LogsQueryStrategy:
    """Reads JSON lines logs from disk for centralized access."""

    query_type = "logs"

    def __init__(
        self,
        log_path: Path,
        reader: Callable[[Path], Iterable[str]] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._log_path = log_path
        self._reader = reader or self._read_lines
        self._clock = clock or datetime.utcnow

    def execute(self, days: int, limit: int) -> dict[str, Any]:
        if not self._log_path.exists():
            return DataQueryResult(
                query_type=self.query_type,
                source=str(self._log_path),
                days=days,
                count=0,
                data=[],
                note="Log file not found.",
            ).to_dict()

        cutoff = self._clock() - timedelta(days=days)
        records: list[dict[str, Any]] = []

        for raw_line in self._reader(self._log_path):
            if len(records) >= limit:
                break

            try:
                payload = json.loads(raw_line.strip())
            except json.JSONDecodeError:
                continue

            timestamp = self._coerce_datetime(payload.get("timestamp"))
            if timestamp is None or timestamp < cutoff:
                continue

            records.append(payload)

        return DataQueryResult(
            query_type=self.query_type,
            source=str(self._log_path),
            days=days,
            count=len(records),
            data=records,
        ).to_dict()

    @staticmethod
    def _read_lines(path: Path) -> Iterable[str]:
        with path.open("r", encoding="utf-8") as log_file:
            yield from log_file

    @staticmethod
    def _coerce_datetime(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                normalized = value.replace("Z", "+00:00")
                return datetime.fromisoformat(normalized)
            except ValueError:
                return None
        return None


class HealthQueryStrategy:
    """Executes a local health script and returns its JSON output."""

    query_type = "health"

    def __init__(
        self,
        script_path: Path,
        executor: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self._script_path = script_path
        self._executor = executor or self._default_executor

    def execute(self, days: int, limit: int) -> dict[str, Any]:  # noqa: ARG002
        if not self._script_path.exists():
            return DataQueryResult(
                query_type=self.query_type,
                source=str(self._script_path),
                days=0,
                count=0,
                data={"status": "missing_script"},
                note="Health check script not found",
            ).to_dict()

        result = self._executor([str(self._script_path)])
        if result.returncode != 0:
            raise QueryExecutionError(
                f"Health script failed with code {result.returncode}: {result.stderr}"
            )

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"raw_output": result.stdout.strip()}

        return DataQueryResult(
            query_type=self.query_type,
            source=str(self._script_path),
            days=0,
            count=1,
            data=payload,
        ).to_dict()

    @staticmethod
    def _default_executor(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603,S607
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
