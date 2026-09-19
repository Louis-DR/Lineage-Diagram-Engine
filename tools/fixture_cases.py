from dataclasses import dataclass
from typing import Callable

from lineage_diagram.bundle import Bundle
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.orbit import Orbit


BLUE = "#4682b4"
RED = "#cd5c5c"
GREEN = "#2e8b57"
GOLD = "#daa520"


@dataclass
class EngineFixture:
  name: str
  description: str
  diagram: Diagram
  lineages: dict[str, Lineage]
  event_xs: tuple[float, ...]


def _diagram(height: float = 160) -> Diagram:
  return Diagram(
    view_width=360,
    view_height=height,
    resolution=240,
    lineage_stroke_width=0.25,
    color_transition_duration=0.25,
  )


def independent_transform() -> EngineFixture:
  diagram = _diagram()
  lineage = Lineage(diagram, BLUE, 0, 80, 12)
  lineage.shift_to(60, 140, 40)
  lineage.scale_to(180, 240, 30)
  lineage.shift_to(260, 320, 100)
  return EngineFixture(
    "independent-transform",
    "Independent position and width transitions.",
    diagram,
    {"lineage": lineage},
    (60, 140, 180, 240, 260, 320),
  )


def overlapping_shifts() -> EngineFixture:
  diagram = _diagram()
  lineage = Lineage(diagram, RED, 0, 80, 14)
  lineage.shift_to(60, 260, 120)
  lineage.shift_to(120, 190, 35)
  return EngineFixture(
    "overlapping-shifts",
    "A short position transition interrupts a longer transition.",
    diagram,
    {"lineage": lineage},
    (60, 120, 190, 260),
  )


def branch_edges() -> EngineFixture:
  diagram = _diagram()
  parent = Lineage(diagram, GREEN, 0, 75, 28)
  parent.shift_to(150, 220, 95)
  branch = Lineage.create_from_lineage(
    parent=parent,
    start_x=60,
    transition_to_x=110,
    new_color=GOLD,
    new_target_w=10,
    new_target_y=30,
  )
  branch.end_at_lineage(parent, 250, 310)
  return EngineFixture(
    "branch-edges",
    "A branch starts and ends against the edge of a continuing lineage.",
    diagram,
    {"parent": parent, "branch": branch},
    (60, 110, 150, 220, 250, 310),
  )


def split_merge() -> EngineFixture:
  diagram = _diagram()
  parent = Lineage(diagram, BLUE, 0, 80, 32)
  upper, lower = parent.split(70, 120, [
    {"color": RED, "target_w": 14, "target_y": 42},
    {"color": GREEN, "target_w": 18, "target_y": 112},
  ])
  child = Lineage.create_from_merge(
    diagram=diagram,
    color=GOLD,
    merge_from_x=230,
    start_x=280,
    start_y=80,
    start_w=30,
    parents=[upper, lower],
  )
  return EngineFixture(
    "split-merge",
    "An independent lineage splits into two and merges again.",
    diagram,
    {"parent": parent, "upper": upper, "lower": lower, "merged": child},
    (70, 120, 230, 280),
  )


def bundle_join_leave() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 5)
  resident = Lineage.create_in_assembly(diagram, GREEN, 0, 18, bundle)
  visitor = Lineage(diagram, RED, 0, 25, 12)
  visitor.join(70, 120, bundle, 0)
  visitor.leave(230, 280, bundle, 130)
  bundle.shift_to(150, 210, 65)
  return EngineFixture(
    "bundle-join-leave",
    "A lineage joins and later leaves a moving bundle.",
    diagram,
    {"resident": resident, "visitor": visitor},
    (70, 120, 150, 210, 230, 280),
  )


def bundle_split() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 4)
  neighbor = Lineage.create_in_assembly(diagram, GOLD, 0, 12, bundle)
  parent = Lineage.create_in_assembly(diagram, BLUE, 0, 28, bundle)
  first, second = parent.split(100, 150, [
    {"color": RED, "target_w": 12, "in_assembly": bundle, "index": 1},
    {"color": GREEN, "target_w": 16, "in_assembly": bundle, "index": 2},
  ])
  return EngineFixture(
    "bundle-split",
    "A bundle member splits into two members while a neighbor remains.",
    diagram,
    {"neighbor": neighbor, "parent": parent, "first": first, "second": second},
    (100, 150),
  )


def bundle_merge_replacement() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 3)
  blue = Lineage.create_in_assembly(diagram, BLUE, 0, 10, bundle)
  red = Lineage.create_in_assembly(diagram, RED, 0, 10, bundle)
  green = Lineage.create_in_assembly(diagram, GREEN, 0, 10, bundle)
  yellow = Lineage.create_in_assembly(diagram, GOLD, 0, 10, bundle)
  merged = Lineage.create_in_assembly_from_merge(
    diagram, "white", 100, 150, 20, [blue, red], bundle, index=0,
  )
  return EngineFixture(
    "bundle-merge-replacement",
    "Two bundle members merge without reordering unaffected neighbors.",
    diagram,
    {"blue": blue, "red": red, "green": green, "yellow": yellow, "merged": merged},
    (100, 150),
  )


def continuing_merge_boundary() -> EngineFixture:
  diagram = _diagram()
  source = Lineage(diagram, "white", 0, 80, 10)
  incoming = Lineage(diagram, GREEN, 0, 94, 10)
  incoming.merge_into(source, 100, 150, 20)
  return EngineFixture(
    "continuing-merge-boundary",
    "A continuing merge ends with an exact right-side center step.",
    diagram,
    {"source": source, "incoming": incoming},
    (100, 150),
  )


def simultaneous_bundle_join_leave() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 3)
  yellow = Lineage.create_in_assembly(diagram, GOLD, 0, 10, bundle)
  green = Lineage.create_in_assembly(diagram, GREEN, 0, 10, bundle)
  blue = Lineage(diagram, BLUE, 0, 35, 10)
  green.leave(100, 150, bundle, 30)
  blue.join(100, 150, bundle, index=0)
  return EngineFixture(
    "simultaneous-bundle-join-leave",
    "An incoming member and outgoing member share one bundle transition window.",
    diagram,
    {"yellow": yellow, "green": green, "blue": blue},
    (100, 150),
  )


def orbit_merge_split() -> EngineFixture:
  diagram = _diagram()
  main = Lineage(diagram, "white", 0, 80, 20)
  orbit = Orbit(diagram, main, 3)
  blue = Lineage.create_in_assembly(diagram, BLUE, 0, 5, orbit, -1)
  red = Lineage.create_in_assembly(diagram, RED, 0, 5, orbit, -1)
  merged = Lineage.create_in_assembly_from_merge(
    diagram, "gray", 100, 150, 10, [blue, red], orbit, index=-1,
  )
  split_blue, split_red = merged.split(200, 250, [
    {"color": BLUE, "target_w": 5, "in_assembly": orbit, "index": -1},
    {"color": RED, "target_w": 5, "in_assembly": orbit, "index": -1},
  ])
  return EngineFixture(
    "orbit-merge-split",
    "Equal-index lower orbit members merge and split without crossing sides.",
    diagram,
    {"main": main, "blue": blue, "red": red, "merged": merged, "split-blue": split_blue, "split-red": split_red},
    (100, 150, 200, 250),
  )


def bundle_reorder() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 5)
  first = Lineage.create_in_assembly(diagram, BLUE, 0, 12, bundle)
  second = Lineage.create_in_assembly(diagram, RED, 0, 12, bundle)
  third = Lineage.create_in_assembly(diagram, GREEN, 0, 12, bundle)
  first.reorder(100, 160, bundle, 2)
  return EngineFixture(
    "bundle-reorder",
    "A bundle member moves from the first slot to the last slot.",
    diagram,
    {"first": first, "second": second, "third": third},
    (100, 160),
  )


def bundle_transfer() -> EngineFixture:
  diagram = _diagram()
  upper_bundle = Bundle(diagram, 0, 45, 4)
  lower_bundle = Bundle(diagram, 0, 115, 4)
  moving = Lineage.create_in_assembly(diagram, BLUE, 0, 12, upper_bundle)
  upper_resident = Lineage.create_in_assembly(diagram, RED, 0, 12, upper_bundle)
  lower_resident = Lineage.create_in_assembly(diagram, GREEN, 0, 12, lower_bundle)
  moving.transfer(120, 190, upper_bundle, lower_bundle, 1)
  return EngineFixture(
    "bundle-transfer",
    "A lineage transfers between two bundles.",
    diagram,
    {
      "moving": moving,
      "upper-resident": upper_resident,
      "lower-resident": lower_resident,
    },
    (120, 190),
  )


def orbit_join_leave() -> EngineFixture:
  diagram = _diagram()
  main = Lineage(diagram, GREEN, 0, 80, 26)
  orbit = Orbit(diagram, main, 5)
  satellite = Lineage(diagram, RED, 0, 25, 10)
  satellite.join(70, 120, orbit, 1)
  satellite.leave(230, 280, orbit, 135)
  return EngineFixture(
    "orbit-join-leave",
    "A satellite joins and leaves the upper side of an orbit.",
    diagram,
    {"main": main, "satellite": satellite},
    (70, 120, 230, 280),
  )


def orbit_reorder() -> EngineFixture:
  diagram = _diagram()
  main = Lineage(diagram, GREEN, 0, 80, 24)
  orbit = Orbit(diagram, main, 4)
  moving = Lineage.create_in_assembly(diagram, BLUE, 0, 10, orbit, -1)
  other = Lineage.create_in_assembly(diagram, RED, 0, 10, orbit, 1)
  moving.reorder(100, 160, orbit, 1)
  return EngineFixture(
    "orbit-reorder",
    "A satellite crosses from the lower to the upper orbit side.",
    diagram,
    {"main": main, "moving": moving, "other": other},
    (100, 160),
  )


def moving_orbit() -> EngineFixture:
  diagram = _diagram()
  main = Lineage(diagram, GREEN, 0, 105, 28)
  main.shift_to(80, 180, 50)
  main.scale_to(210, 280, 16)
  orbit = Orbit(diagram, main, 5)
  upper = Lineage.create_in_assembly(diagram, BLUE, 0, 10, orbit, 1)
  lower = Lineage.create_in_assembly(diagram, RED, 0, 12, orbit, -1)
  return EngineFixture(
    "moving-orbit",
    "Satellites follow a main lineage while it moves and changes width.",
    diagram,
    {"main": main, "upper": upper, "lower": lower},
    (80, 180, 210, 280),
  )


def assembled_termination() -> EngineFixture:
  diagram = _diagram()
  bundle = Bundle(diagram, 0, 80, 6)
  ending = Lineage.create_in_assembly(diagram, RED, 0, 14, bundle)
  survivor = Lineage.create_in_assembly(diagram, BLUE, 0, 14, bundle)
  ending.terminate_at(160)
  return EngineFixture(
    "assembled-termination",
    "A lineage terminates without an explicit assembly leave.",
    diagram,
    {"ending": ending, "survivor": survivor},
    (160,),
  )


def color_transition() -> EngineFixture:
  diagram = _diagram()
  lineage = Lineage(diagram, BLUE, 0, 80, 24)
  lineage.shade(80, 140, RED)
  lineage.shade(220, 280, GREEN)
  return EngineFixture(
    "color-transition",
    "Two successive horizontal color transitions.",
    diagram,
    {"lineage": lineage},
    (80, 140, 220, 280),
  )


FIXTURE_BUILDERS: tuple[Callable[[], EngineFixture], ...] = (
  independent_transform,
  overlapping_shifts,
  branch_edges,
  split_merge,
  bundle_join_leave,
  bundle_split,
  bundle_reorder,
  bundle_transfer,
  orbit_join_leave,
  orbit_reorder,
  moving_orbit,
  assembled_termination,
  color_transition,
  bundle_merge_replacement,
  continuing_merge_boundary,
  simultaneous_bundle_join_leave,
  orbit_merge_split,
)


def build_all_fixtures() -> list[EngineFixture]:
  return [builder() for builder in FIXTURE_BUILDERS]
