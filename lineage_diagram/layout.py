from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .bundle import Bundle
  from .orbit import Orbit


@dataclass(frozen=True)
class LineageFrame:
  x: float
  center: complex
  tangent: complex
  normal: complex
  width: float
  upper: complex
  lower: complex


@dataclass(frozen=True)
class LineageState:
  lineage_id: str
  x: float
  y: float
  width: float
  color: str
  assembly_id: str | None
