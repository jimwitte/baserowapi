"""Small records that retain Baserow IDs and raw value metadata."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class SelectOption:
    """A Baserow select option, including its stable option ID."""

    id: Optional[int]
    value: Optional[str]
    color: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


@dataclass(slots=True)
class LinkedRow:
    """A reference to a row selected through a Baserow link-row field."""

    table_id: int
    id: Optional[int]
    value: Any = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


@dataclass(slots=True)
class BaserowFile:
    """A Baserow user file that can be assigned to a file field."""

    name: str
    visible_name: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    original_name: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


@dataclass(slots=True)
class Collaborator:
    """A Baserow collaborator value with its stable user ID."""

    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


@dataclass(slots=True)
class LookupEntry:
    """One Baserow lookup result and its related row ID, when supplied."""

    row_id: Optional[int]
    value: Any
    raw: Any = field(default=None, repr=False, compare=False)
