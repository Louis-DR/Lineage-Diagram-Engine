from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .lineage import Lineage


@dataclass
class AssemblyReservation:
  lineage: "Lineage"
  start_x: float
  end_x: float
  fade_in_duration: float = 0.0
  fade_out_duration: float = 0.0
  index: int = -1


@dataclass(frozen=True)
class ReorderTransition:
  lineage: "Lineage"
  from_x: float
  to_x: float
  new_index: int
