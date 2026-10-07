from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    sender: str
    recipient: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)

    def serialized_size(self) -> int:
        return len(repr((self.sender, self.recipient, self.kind, self.payload)).encode("utf-8"))
