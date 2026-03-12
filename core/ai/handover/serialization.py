from __future__ import annotations
import json
from typing import Any, Dict, Union, Tuple
from core.ai.handover.models import HandoverContext, ContextDiff

class ContextSerializer:
    """Handles serialization and deserialization of HandoverContext."""

    @staticmethod
    def serialize(context: HandoverContext, compact: bool = False) -> str:
        if compact:
            data = context.model_dump(exclude={"conversation_history", "snapshot"}, exclude_none=True)
        else:
            data = context.model_dump()
        return json.dumps(data, default=str, separators=(",", ":") if compact else None)

    @staticmethod
    def deserialize(data: Union[str, Dict[str, Any]]) -> HandoverContext:
        if isinstance(data, str):
            data = json.loads(data)
        return HandoverContext(**data)

    @staticmethod
    def create_diff(base: HandoverContext, updated: HandoverContext) -> ContextDiff:
        base_data = base.model_dump()
        updated_data = updated.model_dump()
        added, removed, modified, unchanged = {}, {}, {}, []
        for key, value in updated_data.items():
            if key not in base_data: added[key] = value
            elif base_data[key] != value: modified[key] = (base_data[key], value)
            else: unchanged.append(key)
        return ContextDiff(base_version=base.updated_at, compare_version=updated.updated_at, added=added, removed=removed, modified=modified, unchanged=unchanged)
