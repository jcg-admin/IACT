"""Context session utilities for multi-LLM agents."""

from __future__ import annotations

import asyncio
from collections import deque
from typing import Any, Deque, Dict, Iterable, List, Optional, Tuple

ROLE_USER = "user"
ALLOWED_MSG_KEYS = {"role", "content", "name"}


def _is_user_msg(item: Dict[str, Any]) -> bool:
    """Return ``True`` if the payload represents a user authored message."""
    if not isinstance(item, dict):
        role = getattr(item, "role", None)
        return role == ROLE_USER

    role = item.get("role")
    if role is not None:
        return role == ROLE_USER

    if item.get("type") == "message":
        return item.get("role") == ROLE_USER

    return False


class TrimmingSession:
    """Maintain only the last ``max_turns`` user turns in memory."""

    def __init__(self, session_id: str, max_turns: int = 8):
        self.session_id = session_id
        self.max_turns = max(1, int(max_turns))
        self._items: Deque[Dict[str, Any]] = deque()
        self._lock = asyncio.Lock()

    async def get_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            trimmed = self._trim_to_last_turns(list(self._items))
            if limit is not None and limit >= 0:
                return trimmed[-limit:]
            return trimmed

    async def add_items(self, items: Iterable[Dict[str, Any]]) -> None:
        payload = list(items)
        if not payload:
            return
        async with self._lock:
            self._items.extend(payload)
            trimmed = self._trim_to_last_turns(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)

    async def pop_item(self) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if not self._items:
                return None
            return self._items.pop()

    async def clear_session(self) -> None:
        async with self._lock:
            self._items.clear()

    async def set_max_turns(self, max_turns: int) -> None:
        async with self._lock:
            self.max_turns = max(1, int(max_turns))
            trimmed = self._trim_to_last_turns(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)

    async def raw_items(self) -> List[Dict[str, Any]]:
        async with self._lock:
            return list(self._items)

    def _trim_to_last_turns(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return items

        count = 0
        start_idx = 0
        for index in range(len(items) - 1, -1, -1):
            if _is_user_msg(items[index]):
                count += 1
                if count == self.max_turns:
                    start_idx = index
                    break

        return items[start_idx:]


class SummarizingSession:
    """Session that summarizes older turns once the context limit is exceeded."""

    def __init__(
        self,
        keep_last_n_turns: int = 3,
        context_limit: int = 3,
        summarizer: Optional[Any] = None,
        session_id: Optional[str] = None,
    ):
        if context_limit < 1:
            raise ValueError("context_limit must be >= 1")
        if keep_last_n_turns < 0:
            raise ValueError("keep_last_n_turns must be >= 0")
        if keep_last_n_turns > context_limit:
            raise ValueError("keep_last_n_turns cannot exceed context_limit")

        self.keep_last_n_turns = keep_last_n_turns
        self.context_limit = context_limit
        self.summarizer = summarizer
        self.session_id = session_id or "default"

        self._records: Deque[Dict[str, Dict[str, Any]]] = deque()
        self._lock = asyncio.Lock()

    async def get_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            data = [dict(record["msg"]) for record in self._records]
        return self._apply_limit([self._sanitize_for_model(msg) for msg in data], limit)

    async def add_items(self, items: Iterable[Dict[str, Any]]) -> None:
        payload = list(items)
        if not payload:
            return

        async with self._lock:
            for item in payload:
                msg, metadata = self._split_msg_and_meta(item)
                self._records.append({"msg": msg, "metadata": metadata})
            need_summary, boundary = self._summarize_decision_locked()

        if not need_summary:
            async with self._lock:
                self._normalize_synthetic_flags_locked()
            return

        async with self._lock:
            snapshot = list(self._records)
            prefix_msgs = [record["msg"] for record in snapshot[:boundary]]

        shadow, summary = await self._summarize(prefix_msgs)

        async with self._lock:
            still_need, new_boundary = self._summarize_decision_locked()
            if not still_need:
                self._normalize_synthetic_flags_locked()
                return

            snapshot = list(self._records)
            suffix = snapshot[new_boundary:]

            self._records.clear()
            self._records.extend(
                [
                    {
                        "msg": {"role": ROLE_USER, "content": shadow},
                        "metadata": {
                            "synthetic": True,
                            "kind": "history_summary_prompt",
                            "summary_for_turns": f"< all before idx {new_boundary} >",
                        },
                    },
                    {
                        "msg": {"role": "assistant", "content": summary},
                        "metadata": {
                            "synthetic": True,
                            "kind": "history_summary",
                            "summary_for_turns": f"< all before idx {new_boundary} >",
                        },
                    },
                ]
            )
            self._records.extend(suffix)
            self._normalize_synthetic_flags_locked()

    async def pop_item(self) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if not self._records:
                return None
            record = self._records.pop()
            return dict(record["msg"])

    async def clear_session(self) -> None:
        async with self._lock:
            self._records.clear()

    def set_max_turns(self, n: int) -> None:
        if n < 1:
            raise ValueError("n must be >= 1")
        self.context_limit = n
        if self.keep_last_n_turns > self.context_limit:
            self.keep_last_n_turns = self.context_limit

    async def get_full_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            data = [
                {"message": dict(record["msg"]), "metadata": dict(record["metadata"])}
                for record in self._records
            ]
        return self._apply_limit(data, limit)

    async def get_items_with_metadata(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return await self.get_full_history(limit)

    def _apply_limit(self, items: List[Dict[str, Any]], limit: Optional[int]) -> List[Dict[str, Any]]:
        if limit is not None and limit >= 0:
            return items[-limit:]
        return items

    def _split_msg_and_meta(self, item: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        msg = {k: item.get(k) for k in ALLOWED_MSG_KEYS if k in item}
        extra = {k: v for k, v in item.items() if k not in ALLOWED_MSG_KEYS}
        metadata = dict(extra.pop("metadata", {}))
        metadata.update(extra)

        msg.setdefault("role", ROLE_USER)
        msg.setdefault("content", str(item))

        role = msg.get("role")
        if role in (ROLE_USER, "assistant") and "synthetic" not in metadata:
            metadata["synthetic"] = False
        return msg, metadata

    def _sanitize_for_model(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in msg.items() if k in ALLOWED_MSG_KEYS}

    def _is_real_user_turn_start(self, record: Dict[str, Dict[str, Any]]) -> bool:
        return (
            record["msg"].get("role") == ROLE_USER
            and not record["metadata"].get("synthetic", False)
        )

    def _summarize_decision_locked(self) -> Tuple[bool, int]:
        user_starts = [i for i, rec in enumerate(self._records) if self._is_real_user_turn_start(rec)]
        real_turns = len(user_starts)

        if real_turns <= self.context_limit:
            return False, -1

        if self.keep_last_n_turns == 0:
            return True, len(self._records)

        if len(user_starts) < self.keep_last_n_turns:
            return False, -1

        boundary = user_starts[-self.keep_last_n_turns]
        if boundary <= 0:
            return False, -1

        return True, boundary

    def _normalize_synthetic_flags_locked(self) -> None:
        for record in self._records:
            role = record["msg"].get("role")
            if role in (ROLE_USER, "assistant") and "synthetic" not in record["metadata"]:
                record["metadata"]["synthetic"] = False

    async def _summarize(self, prefix_msgs: List[Dict[str, Any]]) -> Tuple[str, str]:
        if not self.summarizer:
            return "Summarize the conversation we had so far.", "Summary unavailable."

        clean_prefix = [self._sanitize_for_model(msg) for msg in prefix_msgs]
        result = await self.summarizer.summarize(clean_prefix)
        if not isinstance(result, tuple) or len(result) != 2:
            return "Summarize the conversation we had so far.", str(result)
        return result


__all__ = ["TrimmingSession", "SummarizingSession"]
