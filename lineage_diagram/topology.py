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


def reservation_overlap_component(reservations: list[AssemblyReservation], x: float) -> list[AssemblyReservation]:
  """Return the transitive strict-overlap component active at ``x``.

  Interpolation must retain one window while a staggered reservation chain is
  active; recomputing bounds from only currently active reservations jumps at
  each inner start or end boundary.
  """
  component = [
    reservation for reservation in reservations
    if reservation.start_x < x < reservation.end_x
  ]
  if not component:
    return []

  start_x = min(reservation.start_x for reservation in component)
  end_x = max(reservation.end_x for reservation in component)
  while True:
    expanded = [
      reservation for reservation in reservations
      if reservation.start_x < end_x and start_x < reservation.end_x
    ]
    expanded_start = min(reservation.start_x for reservation in expanded)
    expanded_end = max(reservation.end_x for reservation in expanded)
    if expanded_start == start_x and expanded_end == end_x:
      return expanded
    start_x, end_x = expanded_start, expanded_end


@dataclass(frozen=True)
class ReorderTransition:
  lineage: "Lineage"
  from_x: float
  to_x: float
  new_index: int
