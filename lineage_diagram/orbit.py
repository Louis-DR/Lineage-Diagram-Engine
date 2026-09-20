import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .utils import smootherstep, find_t_at_x
from .sampling import diagram_event_xs
from .topology import AssemblyReservation, ReorderTransition, reservation_overlap_component
from .layout import CompiledRibbonSample
from .timeline import BoundarySide

if TYPE_CHECKING:
    from .lineage import Lineage
    from .diagram import Diagram
    from .region import Region, RegionMembership

@dataclass
class OrbitMembership:
    """
    Represents the membership of a lineage in an orbit.
    """
    lineage:          "Lineage"
    start_x:           float
    end_x:             float
    index:             int
    fade_in_duration:  float = 0.0
    fade_out_duration: float = 0.0

class Orbit:
    """
    Represents an orbit around a main lineage.
    Satellites are stacked outwards from the main lineage based on their index.
    """
    def __init__(self, diagram:"Diagram", main_lineage:"Lineage", margin:float=0.0):
        diagram.add_orbit(self)
        self.diagram      = diagram
        self.main_lineage = main_lineage
        self.margin       = margin
        self._memberships: list[OrbitMembership] = []
        self._reservations: list[AssemblyReservation] = []
        self._reorder_events: list[ReorderTransition] = []

        # Computed points for members
        self._compiled_member_points: dict["Lineage",tuple[list[complex],list[complex]]] = {}
        self._compiled_member_samples: dict["Lineage",list[CompiledRibbonSample]] = {}

    @property
    def memberships(self) -> list[OrbitMembership]:
        return self._memberships

    @staticmethod
    def validate_member_index(index: int, *, allow_append: bool = False):
        if not isinstance(index, int) or index == 0:
            raise ValueError("Orbit index must be a nonzero integer. Use positive for upper side and negative for lower side.")

    def add_member(
        self,
        lineage:         "Lineage",
        start_x:          float,
        end_x:            float,
        index:            int,
        fade_in_duration: float = 0.0,
    ):
        """Add a satellite lineage to the orbit."""
        self.validate_member_index(index)

        new_membership = OrbitMembership(
            lineage           = lineage,
            start_x           = start_x,
            end_x             = end_x,
            index             = index,
            fade_in_duration  = fade_in_duration,
            fade_out_duration = 0.0
        )
        self._memberships.append(new_membership)

    def join_region(self, region: "Region", x: float) -> "RegionMembership":
        """Join a post-layout Region without changing orbit layout."""
        return region.join(self, x)

    def leave_region(self, region: "Region", x: float) -> None:
        """Leave a post-layout Region without changing orbit layout."""
        region.leave(self, x)

    def get_memberships_at(self, x:float) -> list[OrbitMembership]:
        """Return memberships active at X."""
        return [membership for membership in self._memberships if membership.start_x <= x + 1e-5 and x <= membership.end_x + 1e-5]

    def reserve_member(self, lineage:"Lineage", start_x:float, end_x:float, *, fade_in:bool, index:int=-1):
        self.validate_member_index(index)
        self._reservations.append(AssemblyReservation(
            lineage=lineage,
            start_x=start_x,
            end_x=end_x,
            fade_in_duration=end_x - start_x if fade_in else 0.0,
            fade_out_duration=0.0 if fade_in else end_x - start_x,
            index=index,
        ))

    def reorder_member(self, lineage:"Lineage", from_x:float, to_x:float, new_index:int):
        self.validate_member_index(new_index)
        self._reorder_events.append(ReorderTransition(lineage, from_x, to_x, new_index))

    def effective_index_of(self, lineage:"Lineage", x:float) -> int:
        """Return a member's signed index after every completed reorder."""
        membership = next((
            item for item in self.get_memberships_at(x)
            if item.lineage is lineage
        ), None)
        if membership is None:
            raise ValueError("Lineage is not an active Orbit member")
        return self._index_at(membership, x)

    def _get_layout_memberships_at(self, x:float):
        memberships = list(self.get_memberships_at(x))
        memberships.extend(
            reservation for reservation in self._reservations
            if reservation.start_x < x < reservation.end_x
            and not any(membership.lineage is reservation.lineage for membership in memberships)
        )
        return memberships

    def _index_at(self, membership, x:float) -> int:
        index = membership.index
        for event in sorted(self._reorder_events, key=lambda item: (item.to_x, item.from_x)):
            if event.lineage is membership.lineage and x + 1e-5 >= event.to_x:
                index = event.new_index
        return index

    def _get_factor(self, membership:OrbitMembership, x:float) -> float:
        """Calculate the presence factor (0 to 1) of a member at position X."""
        # Fade In
        if x < membership.start_x + membership.fade_in_duration:
            if membership.fade_in_duration <= 1e-5: return 1.0
            ratio = (x - membership.start_x) / membership.fade_in_duration
            return smootherstep(ratio)
        # Fade Out
        elif x > membership.end_x - membership.fade_out_duration:
            if membership.fade_out_duration <= 1e-5: return 1.0
            start_fade_out = membership.end_x - membership.fade_out_duration
            ratio = (x - start_fade_out) / membership.fade_out_duration
            return 1.0 - smootherstep(ratio)
        # Stable
        return 1.0

    def _calculate_layout(self, memberships:list[OrbitMembership], x:float, index_overrides=None) -> dict["Lineage",float]:
        """
        Calculate the offset from the main lineage center for each member at X.
        Returns a dict mapping lineage to its center offset.
        """
        # We need to respect insertion order for ties (LIFO: Newest = Inner).
        # We reverse the list first, then use Python's stable sort.
        reversed_memberships = list(reversed(memberships))

        # Group by side (positive/negative index) and sort

        # Upper: index > 0. Sort by index (ascending).
        # Stable sort preserves the reversed order for ties (Newest first).
        index_overrides = index_overrides or {}
        get_index = lambda membership: index_overrides.get(membership.lineage, self._index_at(membership, x))
        upper_memberships = sorted(
            [membership for membership in reversed_memberships if get_index(membership) > 0],
            key=get_index
        )

        # Lower: index < 0. Sort by abs(index) (ascending).
        lower_memberships = sorted(
            [membership for membership in reversed_memberships if get_index(membership) < 0],
            key=lambda membership: abs(get_index(membership))
        )
        # We need the main lineage width at X to know where the surface is.
        main_width = self.main_lineage.get_width_at(x)
        half_main  = main_width / 2

        offsets = {}

        # Process Upper Side
        current_offset = half_main

        for upper_membership in upper_memberships:
            factor = self._get_factor(upper_membership, x)
            width  = upper_membership.lineage.get_width_at(x) * factor

            # Scale margin by factor
            gap = self.margin * factor

            # The center of the new member:
            # Current surface + gap + half_width
            center_offset = current_offset + gap + width / 2
            # Advance surface
            current_offset += gap + width
            offsets[upper_membership.lineage] = center_offset

        # Process Lower Side
        current_offset = -half_main

        for lower_membership in lower_memberships:
            factor = self._get_factor(lower_membership, x)
            width  = lower_membership.lineage.get_width_at(x) * factor
            gap    = self.margin * factor

            # The center of the new member (going down):
            # Current surface - gap - half_width
            center_offset = current_offset - gap - width / 2
            offsets[lower_membership.lineage] = center_offset

            # Advance surface
            current_offset -= gap + width

        return offsets

    def _layout_at(self, x:float):
        memberships = self._get_layout_memberships_at(x)
        offsets = self._calculate_layout(memberships, x)
        component = reservation_overlap_component(self._reservations, x)
        if component:
            window_start = min(reservation.start_x for reservation in component)
            window_end = max(reservation.end_x for reservation in component)
            before_offsets = self._calculate_layout(self.get_memberships_at(window_start - 1e-7), x)
            after_offsets = self._calculate_layout(self.get_memberships_at(window_end + 1e-7), x)
            factor = smootherstep((x - window_start) / (window_end - window_start))
            for lineage in set(before_offsets) & set(after_offsets):
                offsets[lineage] = before_offsets[lineage] + (after_offsets[lineage] - before_offsets[lineage]) * factor

        active_event = next((event for event in self._reorder_events if event.from_x < x < event.to_x), None)
        if active_event is None:
            return memberships, offsets
        after_offsets = self._calculate_layout(
            memberships,
            x,
            {active_event.lineage: active_event.new_index},
        )
        factor = smootherstep((x - active_event.from_x) / (active_event.to_x - active_event.from_x))
        return memberships, {
            lineage: offset + (after_offsets.get(lineage, offset) - offset) * factor
            for lineage, offset in offsets.items()
        }

    def get_compiled_points_for(self, lineage:"Lineage", start_x:float, end_x:float) -> tuple[list[complex],list[complex]]:
        """Retrieve pre-calculated points."""
        samples = self.get_compiled_samples_for(lineage, start_x, end_x)
        return [sample.upper for sample in samples], [sample.lower for sample in samples]

    def get_compiled_samples_for(
        self,
        lineage:"Lineage",
        start_x:float,
        end_x:float,
    ) -> list[CompiledRibbonSample]:
        """Retrieve paired rendered samples by authoritative timeline X."""
        if lineage not in self._compiled_member_samples:
            return []
        samples = [
            sample for sample in self._compiled_member_samples[lineage]
            if start_x <= sample.source_x <= end_x
        ]
        if not samples or samples[0].source_x > start_x + 1e-5:
            upper, lower = self._get_member_geometry_at(start_x, lineage)
            samples.insert(0, CompiledRibbonSample(start_x, upper, lower, BoundarySide.RIGHT))
        if not samples or samples[-1].source_x < end_x - 1e-5:
            upper, lower = self._get_member_geometry_at(end_x, lineage)
            samples.append(CompiledRibbonSample(end_x, upper, lower, BoundarySide.LEFT))
        return samples

    def solve_geometry(self):
        """Pre-calculate geometry."""
        # Initialize
        self._compiled_member_points = {m.lineage: ([], []) for m in self._memberships}
        self._compiled_member_samples = {m.lineage: [] for m in self._memberships}

        diagram = self.main_lineage.diagram
        steps   = diagram.resolution

        # We iterate X from 0 to width
        xs = sorted({*np.linspace(0, diagram.view_width, steps), *diagram_event_xs(diagram)})
        discontinuity_xs = {
            event.from_x
            for lineage in (self.main_lineage, *(membership.lineage for membership in self._memberships))
            for event in lineage._scale_events
            if event.from_x == event.to_x
        }
        discontinuity_xs.update(
            event.from_x for event in self.main_lineage._shift_events
            if event.from_x == event.to_x
        )
        discontinuity_xs.update(
            event.from_x for event in self._reorder_events
            if event.from_x == event.to_x
        )

        for x in xs:
            queries = [(x, BoundarySide.RIGHT)]
            if any(abs(x - event_x) <= 1e-9 for event_x in discontinuity_xs):
                queries = [
                    (x - 2e-5, BoundarySide.LEFT),
                    (x + 2e-5, BoundarySide.RIGHT),
                ]
            for query_x, side in queries:
                memberships, offsets = self._layout_at(query_x)
                if not memberships:
                    continue
                main_upper, main_lower = self.main_lineage.get_geometry_at(query_x)
                main_center = (main_upper + main_lower) / 2
                diff = main_upper - main_lower
                normal = 1j if abs(diff) < 1e-9 else diff / abs(diff)
                for membership in memberships:
                    offset = offsets[membership.lineage]
                    width = membership.lineage.get_width_at(query_x) * self._get_factor(membership, query_x)
                    center = main_center + normal * offset
                    upper = center + normal * (width / 2)
                    lower = center - normal * (width / 2)
                    self._compiled_member_points[membership.lineage][0].append(upper)
                    self._compiled_member_points[membership.lineage][1].append(lower)
                    self._compiled_member_samples[membership.lineage].append(
                        CompiledRibbonSample(x, upper, lower, side)
                    )

    def _get_member_geometry_at(self, x:float, lineage:"Lineage") -> tuple[complex,complex]:
        """Calculate the upper and lower points of a member at a specific X."""
        memberships, offsets = self._layout_at(x)
        target_membership = next((m for m in memberships if m.lineage == lineage), None)
        if not target_membership:
            # Fallback
            return complex(x, 0), complex(x, 0)

        main_upper, main_lower = self.main_lineage.get_geometry_at(x)
        main_center = (main_upper + main_lower) / 2

        diff = main_upper - main_lower
        if abs(diff) < 1e-9:
            normal = 1j
        else:
            normal = diff / abs(diff)

        offset  = offsets[lineage]
        width   = lineage.get_width_at(x) * self._get_factor(target_membership, x)

        center = main_center + normal * offset
        upper  = center + normal * (width / 2)
        lower  = center - normal * (width / 2)

        return upper, lower

    def get_center_point_of_member_at(self, x:float, lineage:"Lineage") -> complex:
        """Finds the geometric center of the lineage within the orbit at position X."""
        memberships, offsets = self._layout_at(x)
        target_m = next((m for m in memberships if m.lineage == lineage), None)
        if not target_m:
            # Fallback
            return complex(x, 0)

        main_upper, main_lower = self.main_lineage.get_geometry_at(x)
        main_center = (main_upper + main_lower) / 2

        diff = main_upper - main_lower
        if abs(diff) < 1e-9:
            normal = 1j
        else:
            normal = diff / abs(diff)

        offset  = offsets[lineage]

        return main_center + normal * offset
