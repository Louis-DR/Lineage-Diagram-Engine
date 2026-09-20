from dataclasses import dataclass
from typing import TYPE_CHECKING

from .timeline import BoundarySide

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


@dataclass(frozen=True)
class CompiledRibbonSample:
  """One paired rendered-edge sample at an authoritative timeline X."""

  source_x: float
  upper: complex
  lower: complex
  side: BoundarySide = BoundarySide.RIGHT
