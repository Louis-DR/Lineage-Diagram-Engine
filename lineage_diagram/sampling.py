from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .diagram import Diagram


def diagram_event_xs(diagram: "Diagram") -> tuple[float, ...]:
  """Return every x-coordinate at which authored state can change."""
  values = {0.0, float(diagram.view_width)}
  for lineage in diagram._lineages:
    values.add(float(lineage.start_x))
    for end_x in (lineage.end_x, lineage.visual_end_x):
      if end_x is not None:
        values.add(float(end_x))
    for event in (*lineage._shift_events, *lineage._scale_events, *lineage._shade_events, *lineage.membership_events):
      values.add(float(event.from_x))
      values.add(float(event.to_x))

  for assembly in (*diagram._bundles, *diagram._orbits):
    for event in getattr(assembly, "_shift_events", ()):
      values.add(float(event.from_x))
      values.add(float(event.to_x))
    for membership in assembly.memberships:
      values.add(float(membership.start_x))
      values.add(float(membership.end_x))
      values.add(float(membership.start_x + membership.fade_in_duration))
      values.add(float(membership.end_x - membership.fade_out_duration))
    for event in (*assembly._reservations, *assembly._reorder_events):
      values.add(float(event.start_x if hasattr(event, "start_x") else event.from_x))
      values.add(float(event.end_x if hasattr(event, "end_x") else event.to_x))
  return tuple(sorted(value for value in values if 0 <= value <= diagram.view_width))
