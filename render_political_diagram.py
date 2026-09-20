import datetime
from typing import List, Optional, Dict, Any

import politics_lib as db
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.bundle import Bundle
from lineage_diagram.orbit import Orbit
from lineage_diagram.paths import MembershipEventType, ScaleEvent
from lineage_diagram.region import Region, RegionStroke
from lineage_diagram.timeline import NumericTimeline

# Diagram configuration
DIAGRAM_WIDTH  = 8650*1.5
DIAGRAM_HEIGHT = 635

# Time configuration
DIAGRAM_START_DATE = db.Date(1789, 7, 14)
DIAGRAM_DATE_SCALE = 0.15 # pixels per day

# Y/Orientation configuration
DIAGRAM_ORIENTATION_SCALE = 100 # pixels per unit spectrum

# Year grid styling
YEAR_GRID_INTERVAL_YEARS    = 5
YEAR_GRID_COLOR             = "#000000"
YEAR_GRID_OPACITY           = 0.06
YEAR_GRID_STROKE_WIDTH      = 2
YEAR_LABEL_ROTATION_DEGREES = -90
YEAR_LABEL_FONT_SIZE        = "10px"
YEAR_LABEL_OPACITY          = 0.12
YEAR_LABEL_FONT_FAMILY      = "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
YEAR_LABEL_FONT_WEIGHT      = "900"
YEAR_LABEL_X_OFFSET_PX      = 0
YEAR_LABEL_Y_OFFSET_PX      = 10
YEAR_LABEL_Y_SPACING_PX     = 150
YEAR_LABEL_MARGIN_PX        = 8
YEAR_LABEL_FONT_SIZE_PX     = 10
YEAR_LABEL_CHAR_WIDTH_PX    = 6.5
YEAR_LABEL_BG_COLOR         = "#FFFFFF"
YEAR_LABEL_BG_OPACITY       = 0.95
YEAR_LABEL_BG_PADDING_PX    = 3
YEAR_LABEL_BG_RADIUS_PX     = 2


def date_to_x(date: db.Date) -> float:
  start_date       = DIAGRAM_START_DATE._to_datetime_date(default_to_start=True)
  current_date     = date._to_datetime_date(default_to_start=True)
  days_since_start = (current_date - start_date).days
  return float(days_since_start) * DIAGRAM_DATE_SCALE


def orientation_to_y(orientation: float) -> float:
  return DIAGRAM_HEIGHT / 2 - orientation * DIAGRAM_ORIENTATION_SCALE


# Transition configuration (in days) for visual merges/splits
MERGE_TRANSITION_DAYS  = 160
SECEDE_TRANSITION_DAYS = 160

# Federation and satellite configuration
FEDERATION_BUNDLE_MARGIN           = 2.0
FEDERATION_JOIN_TRANSITION_DAYS    = 160
FEDERATION_LEAVE_TRANSITION_DAYS   = 160

SATELLITE_ORBIT_MARGIN             = 2.0
SATELLITE_JOIN_TRANSITION_DAYS     = 160
SATELLITE_LEAVE_TRANSITION_DAYS    = 160

ALLIANCE_REGION_PADDING      = 4.0
ALLIANCE_REGION_OPACITY      = 0.14
ALLIANCE_REGION_CORNER       = 4.0
ALLIANCE_REGION_EVENT_CORNER = 2.0
ALLIANCE_REGION_STROKE_WIDTH = 1.0
ALLIANCE_REGION_STROKE_ALPHA = 0.65
ALLIANCE_REGION_DASHARRAY    = (5.0, 3.0)

# Relative-position decision threshold for end_at_lineage based on political orientation
ORIENTATION_EDGE_DELTA = 0.03  # If abs(source - target) <= this => center; else upper/lower

SHIFT_MIN_SEGMENT_EPS = 1e-6


def find_active_lineage(lineages: List[Lineage], x: float) -> Optional[Lineage]:
  """
  Finds the lineage active at x coordinate.
  Prefers a lineage that is active at x. If none, chooses the one ending just before x.
  If none before, chooses the one starting just after x.
  """
  # Lineage class has start_x and end_x attributes
  active = [lineage for lineage in lineages if lineage.start_x <= x <= (lineage.end_x if lineage.end_x is not None else float('inf'))]
  if active:
    # If multiple, choose the one with the latest start
    active.sort(key=lambda lineage: lineage.start_x)
    return active[-1]

  before = [lineage for lineage in lineages if (lineage.end_x is not None and lineage.end_x < x)]
  if before:
    before.sort(key=lambda lineage: (lineage.end_x if lineage.end_x is not None else 0))
    return before[-1]

  after = [lineage for lineage in lineages if lineage.start_x > x]
  if after:
    after.sort(key=lambda lineage: lineage.start_x)
    return after[0]
  return None


def determine_relative_position(source_y: float, target_y: float) -> str:
  """
  Determines relative position of source relative to target based on Y coordinates.
  """
  diff = source_y - target_y
  # In SVG coordinates, smaller Y is higher up.
  # So if source_y < target_y, source is ABOVE target.
  # But the legacy script logic was:
  # diff < -DELTA => "upper" (meaning source is above target)
  # diff > DELTA => "lower" (meaning source is below target)
  if diff < -ORIENTATION_EDGE_DELTA:
    return "upper"
  elif diff > ORIENTATION_EDGE_DELTA:
    return "lower"
  else:
    return "center"


def apply_importance_changes_to_lineage(
  lineage: Lineage,
  party: db.PoliticalParty,
  min_x: Optional[float] = None,
  max_x: Optional[float] = None,
  compose_until_x: Optional[float] = None,
) -> None:
  """
  Applies importance-based width changes to a lineage using the party's importance history.
  """
  changes = party.get_importance_changes()
  if compose_until_x is not None and min_x is not None and compose_until_x > min_x:
    overlapping_changes = [
      change for change in changes
      if date_to_x(change["from_date"]) < compose_until_x
      and date_to_x(change["to_date"]) > min_x
    ]
    if overlapping_changes:
      # A split allocates the parent's width at its start, while importance is
      # an authoritative political value. Compose them into one split target
      # instead of temporarily interrupting, then resuming, the allocation.
      importance_events = [
        ScaleEvent(
          date_to_x(change["from_date"]),
          date_to_x(change["to_date"]),
          float(change["to_importance"]),
        )
        for change in changes
      ]
      effective_target = NumericTimeline(
        importance_at(party, party.creation_date),
        importance_events,
        "to_w",
      ).value_at(compose_until_x)
      split_scale = next((
        event for event in reversed(lineage._scale_events)
        if abs(event.from_x - min_x) < 1e-6
        and abs(event.to_x - compose_until_x) < 1e-6
      ), None)
      if split_scale is not None:
        split_scale.to_w = effective_target
        min_x = compose_until_x

  for change in changes:
    change_from_x = date_to_x(change["from_date"])
    change_to_x = date_to_x(change["to_date"])
    target_w = float(change["to_importance"])

    seg_start = max(change_from_x, lineage.start_x)
    seg_end = min(change_to_x, lineage.end_x if lineage.end_x is not None else float('inf'))

    if min_x is not None: seg_start = max(seg_start, min_x)
    if max_x is not None: seg_end = min(seg_end, max_x)

    if seg_end - seg_start > 1e-6:
        lineage.scale_to(seg_start, seg_end, target_w)


def importance_at(party: db.PoliticalParty, at_date: db.Date) -> float:
  # Re-implementing based on legacy script logic which calls private methods of party
  components = party._get_component_values_at_date(at_date)
  bonus = float(party._get_prominence_bonus_at_date(at_date))
  total = (db.MINIMAL_IMPORTANCE
           + float(components.get("presidential", 0.0))
           + float(components.get("legislative",  0.0))
           + float(components.get("senatorial",   0.0))
           + float(components.get("european",     0.0))
           + bonus)
  return float(db.IMPORTANCE_MULTIPLIER * pow(total, db.IMPORTANCE_POWER))


def add_alliance_regions(
  diagram: Diagram,
  alliances: dict,
  party_lineages: dict[str, list[Lineage]],
  symbol_by_party: dict,
) -> dict[str, Region]:
  """Project political alliance intervals into post-layout engine Regions."""
  regions = {}
  for alliance_symbol in sorted(alliances):
    alliance = alliances[alliance_symbol]
    color = getattr(alliance, "color", None) or "#808080"
    region = Region(
      diagram,
      padding=ALLIANCE_REGION_PADDING,
      fill=color,
      fill_opacity=ALLIANCE_REGION_OPACITY,
      corner_radius=ALLIANCE_REGION_CORNER,
      event_corner_radius=ALLIANCE_REGION_EVENT_CORNER,
      stroke=RegionStroke(
        color,
        ALLIANCE_REGION_STROKE_WIDTH,
        ALLIANCE_REGION_STROKE_ALPHA,
        ALLIANCE_REGION_DASHARRAY,
      ),
    )
    regions[alliance_symbol] = region
    alliance_end_x = (
      date_to_x(alliance.dissolution_date)
      if getattr(alliance, "dissolution_date", None)
      else diagram.view_width
    )
    for interval in getattr(alliance, "membership_intervals", ()):
      party = interval.get("party")
      symbol = symbol_by_party.get(party)
      if symbol is None:
        continue
      interval_start = interval.get("from")
      if interval_start is None:
        continue
      interval_start_x = max(date_to_x(interval_start), date_to_x(alliance.creation_date))
      interval_end_x = min(
        date_to_x(interval["to"]) if interval.get("to") else diagram.view_width,
        alliance_end_x,
      )
      for lineage in party_lineages.get(symbol, ()):
        start_x = max(interval_start_x, lineage.start_x)
        visual_end_x = lineage.visual_end_x if lineage.visual_end_x is not None else diagram.view_width
        end_x = min(
          interval_end_x,
          lineage.end_x if lineage.end_x is not None else diagram.view_width,
          visual_end_x,
        )
        if end_x > start_x:
          region.add_member(lineage, start_x, end_x)
  return regions


class PoliticalDiagram(Diagram):
    def __init__(self, view_width: float, view_height: float, resolution: int = 1000):
        super().__init__(view_width, view_height, resolution)
        self.overlays = []

    def add_overlay(self, svg_content: str):
        self.overlays.append(svg_content)

    def generate(self, filepath: str = "diagram.svg"):
        # Generate the standard diagram first
        super().generate(filepath)

        # Now read it back and inject overlays
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            # Find the line with <svg ...>
            svg_start_index = -1
            for i, line in enumerate(lines):
                if "<svg" in line:
                    svg_start_index = i
                    break

            if svg_start_index != -1:
                # Insert overlays after the <svg> tag line to be at the back (drawn first)
                overlay_content = "\n".join(self.overlays) + "\n"
                lines.insert(svg_start_index + 1, overlay_content)

                with open(filepath, 'w') as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"Error injecting overlays: {e}")


def add_year_grid(diagram: PoliticalDiagram):
  """
  Adds a year grid overlay to the diagram.
  """
  start_date_multiple_base = DIAGRAM_START_DATE._to_datetime_date(default_to_start=True)
  first_year_multiple = ((start_date_multiple_base.year + (YEAR_GRID_INTERVAL_YEARS - 1)) // YEAR_GRID_INTERVAL_YEARS) * YEAR_GRID_INTERVAL_YEARS
  current_year = first_year_multiple
  end_year = datetime.date.today().year

  while current_year <= end_year:
    year_x = date_to_x(db.Date(current_year, 1, 1))
    # Vertical line
    diagram.add_overlay(
      f'<line x1="{year_x}" y1="0" x2="{year_x}" y2="{DIAGRAM_HEIGHT}" '
      f'stroke="{YEAR_GRID_COLOR}" stroke-width="{YEAR_GRID_STROKE_WIDTH}" stroke-opacity="{YEAR_GRID_OPACITY}"/>'
    )
    # Labels
    label_text   = f"{current_year}"
    label_x      = year_x + YEAR_LABEL_X_OFFSET_PX
    y_center     = DIAGRAM_HEIGHT / 2.0

    def add_year_label_at(y_pos: float) -> bool:
      approx_text_width = len(label_text) * YEAR_LABEL_CHAR_WIDTH_PX
      rect_width = approx_text_width + 2 * YEAR_LABEL_BG_PADDING_PX
      rect_height = YEAR_LABEL_FONT_SIZE_PX + 2 * YEAR_LABEL_BG_PADDING_PX

      if (y_pos - rect_height / 2) < YEAR_LABEL_MARGIN_PX or (y_pos + rect_height / 2) > (DIAGRAM_HEIGHT - YEAR_LABEL_MARGIN_PX):
        return False

      rect_x = label_x - rect_width / 2
      rect_y = y_pos - rect_height / 2

      diagram.add_overlay(
        f'<rect x="{rect_x}" y="{rect_y}" width="{rect_width}" height="{rect_height}" '
        f'rx="{YEAR_LABEL_BG_RADIUS_PX}" ry="{YEAR_LABEL_BG_RADIUS_PX}" '
        f'fill="{YEAR_LABEL_BG_COLOR}" fill-opacity="{YEAR_LABEL_BG_OPACITY}" '
        f'transform="rotate({YEAR_LABEL_ROTATION_DEGREES} {label_x} {y_pos})"/>'
      )
      diagram.add_overlay(
        f'<text x="{label_x}" y="{y_pos}" fill="{YEAR_GRID_COLOR}" fill-opacity="{YEAR_LABEL_OPACITY}" '
        f'font-size="{YEAR_LABEL_FONT_SIZE}" font-family="{YEAR_LABEL_FONT_FAMILY}" font-weight="{YEAR_LABEL_FONT_WEIGHT}" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'style="font-variant-numeric: tabular-nums" '
        f'transform="rotate({YEAR_LABEL_ROTATION_DEGREES} {label_x} {y_pos})">{label_text}</text>'
      )
      return True

    add_year_label_at(y_center)
    step = YEAR_LABEL_Y_SPACING_PX
    offset_multiplier = 1
    while True:
      placed_any = False
      y_up = y_center - offset_multiplier * step
      y_down = y_center + offset_multiplier * step
      if y_up >= 0:
        placed_any = add_year_label_at(y_up) or placed_any
      if y_down <= DIAGRAM_HEIGHT:
        placed_any = add_year_label_at(y_down) or placed_any
      if not placed_any:
        break
      offset_multiplier += 1
    current_year += YEAR_GRID_INTERVAL_YEARS


def get_max_importance(party: db.PoliticalParty) -> float:
  initial = importance_at(party, party.creation_date)
  changes = party.get_importance_changes()
  if not changes:
    return initial
  max_val = initial
  for change in changes:
    v1 = float(change["from_importance"])
    v2 = float(change["to_importance"])
    if v1 > max_val: max_val = v1
    if v2 > max_val: max_val = v2
  return max_val


def main():
  diagram = PoliticalDiagram(view_width=DIAGRAM_WIDTH, view_height=DIAGRAM_HEIGHT, resolution=10000)
  add_year_grid(diagram)

  system = db.load_france()
  parties = system.political_parties
  by_symbol = {sym: parties[sym] for sym in parties.keys()}
  symbol_by_party = {party: sym for sym, party in by_symbol.items()}

  # Sort by creation date to ensure dependencies (hosts/federations) are processed first
  symbols_sorted = sorted(by_symbol.keys(), key=lambda s: (by_symbol[s].creation_date, s))

  # 1. Create Federation Bundles early
  federations = system.political_federations
  federation_bundles = {}

  for federation_symbol in sorted(federations.keys()):
      federation = federations[federation_symbol]
      if int(federation.creation_date.year) < 1: continue

      start_x = date_to_x(federation.creation_date)
      start_y = orientation_to_y(float(getattr(federation, "initial_political_position", 0.0)))

      bundle = Bundle(diagram, start_x, start_y, float(FEDERATION_BUNDLE_MARGIN))

      # Shifts
      shifts = getattr(federation, "political_position_shifts", []) or []
      for shift in shifts:
          from_x = date_to_x(shift["from"])
          to_x = date_to_x(shift["to"])
          target_y = orientation_to_y(float(shift["target_position"]))
          if to_x - from_x > SHIFT_MIN_SEGMENT_EPS:
              bundle.shift_to(from_x, to_x, target_y)

      federation_bundles[federation_symbol] = bundle

  # 2. Pre-calculate Indices (REMOVED - Now dynamic)
  # federation_index_maps = {}
  # orbit_index_maps = {}

  # Collect events
  merges_by_target_date = {}
  secede_events = []
  dissolves = []
  secede_from_by_target_date = {}

  for symbol in symbols_sorted:
    party = by_symbol[symbol]
    for evt in getattr(party, "lineage_events", []):
      et = evt.get("type")
      if et == "merge_from":
        key = (symbol, evt["date"])
        ratio = float(evt.get("ratio", 1.0))
        merges_by_target_date.setdefault(key, []).append((evt.get("from"), ratio))
      elif et == "secede_into":
        secede_events.append({
          "from": symbol,
          "into": evt.get("into"),
          "date": evt.get("date"),
          "ratio": evt.get("ratio"),
          "new_pos": evt.get("new_pos"),
          "source_new_position": evt.get("source_new_position", None),
          "visual_width": evt.get("visual_width", None),
        })
      elif et == "secede_from":
        key = (symbol, evt.get("date"))
        src = evt.get("from")
        ratio = float(evt.get("ratio") or 0.0)
        secede_from_by_target_date.setdefault(key, []).append((src, ratio))
      elif et == "dissolve":
        dissolves.append((symbol, evt.get("date")))

  party_lineages = {sym: [] for sym in symbols_sorted}

  orbits_by_host = {} # Map host_lineage -> Orbit

  # Create initial lineages
  for symbol in symbols_sorted:
    party = by_symbol[symbol]
    if int(party.creation_date.year) < 1: continue
    if (symbol, party.creation_date) in merges_by_target_date: continue
    if (symbol, party.creation_date) in secede_from_by_target_date: continue

    color = getattr(party, "color", None) or "black"
    start_x = date_to_x(party.creation_date)
    start_y = orientation_to_y(party.initial_political_position)
    start_w = importance_at(party, party.creation_date)

    z_val = get_max_importance(party)

    lineage = None

    # Check inside_entity
    if party.inside_entity:
        if isinstance(party.inside_entity, db.PoliticalFederation):
             fed_symbol = party.inside_entity.symbol
             bundle = federation_bundles.get(fed_symbol)
             if bundle:
                 # Dynamic Indexing for Initial Creation
                 # Get all members active at creation date
                 fed = party.inside_entity
                 active_members = []
                 for interval in fed.membership_intervals:
                     if interval.get("from") <= party.creation_date and (interval.get("to") is None or interval.get("to") >= party.creation_date):
                         p = interval.get("party")
                         if p: active_members.append(p)

                 # Sort by current political position (Ascending: Left to Right -> Top to Bottom)
                 active_members.sort(key=lambda p: p.get_political_position_at(party.creation_date))

                 try:
                    idx = active_members.index(party)
                 except ValueError:
                    idx = -1 # Should not happen if data is consistent

                 lineage = Lineage.create_in_assembly(diagram, color, start_x, float(start_w), bundle, index=idx, z=z_val)

        elif isinstance(party.inside_entity, db.PoliticalParty):
             host_party = party.inside_entity
             host_symbol = host_party.symbol
             host_lines = party_lineages.get(host_symbol, [])
             # Find active host lineage at start_x
             host_lin = find_active_lineage(host_lines, start_x)
             if host_lin:
                 orbit = orbits_by_host.get(host_lin)
                 if not orbit:
                     orbit = Orbit(diagram, host_lin, float(SATELLITE_ORBIT_MARGIN))
                     orbits_by_host[host_lin] = orbit

                 # Dynamic Indexing for Orbit
                 sat_pos = party.get_political_position_at(party.creation_date)
                 host_pos = host_party.get_political_position_at(party.creation_date)

                 # Determine side
                 is_upper = sat_pos >= host_pos

                 # Get all satellites active at this time
                 active_sats = []
                 for m in host_party.satellite_host_memberships:
                     if m.get("from") <= party.creation_date and (m.get("to") is None or m.get("to") >= party.creation_date):
                         s = m.get("satellite")
                         if s: active_sats.append(s)

                 # Filter by side and sort by closeness (abs diff)
                 side_sats = []
                 for s in active_sats:
                     s_pos = s.get_political_position_at(party.creation_date)
                     if (s_pos >= host_pos) == is_upper:
                         side_sats.append(s)

                 # Sort by distance from host (ascending)
                 side_sats.sort(key=lambda s: abs(s.get_political_position_at(party.creation_date) - host_pos))

                 try:
                    rank = side_sats.index(party) + 1
                 except ValueError:
                    rank = 1

                 idx = rank if is_upper else -rank
                 lineage = Lineage.create_in_assembly(diagram, color, start_x, float(start_w), orbit, index=idx, z=z_val)

    if not lineage:
        lineage = Lineage(diagram, color, start_x, start_y, float(start_w), z=z_val)

    end_x = date_to_x(party.dissolution_date) if party.dissolution_date is not None else date_to_x(db.Date.today())
    lineage.terminate_at(end_x)

    party_lineages[symbol].append(lineage)

  # Apply importance changes for initial lineages
  for symbol in symbols_sorted:
    party = by_symbol[symbol]
    for lineage in party_lineages.get(symbol, []):
      apply_importance_changes_to_lineage(lineage, party)

  # Build timeline
  timeline_events = []
  for (target_symbol, merge_date) in merges_by_target_date.keys():
    timeline_events.append({
      "type": "merge",
      "date": merge_date,
      "target_symbol": target_symbol,
      "parents_symbols": merges_by_target_date[(target_symbol, merge_date)]
    })
  for evt in secede_events:
    timeline_events.append({
      "type": "split",
      "date": evt["date"],
      "source_symbol": evt["from"],
      "target_symbol": evt["into"],
      "ratio": float(evt.get("ratio") or 0.0),
      "source_new_position": evt.get("source_new_position", None),
      "visual_width": evt.get("visual_width", None)
    })
  for symbol in symbols_sorted:
    party = by_symbol[symbol]
    shifts = getattr(party, "political_position_shifts", []) or []
    for shift in shifts:
      timeline_events.append({
        "type": "y_shift",
        "symbol": symbol,
        "from_date": shift["from"],
        "to_date": shift["to"],
        "target_position": float(shift["target_position"])
      })

  timeline_events.sort(key=lambda e: (int(e["date" if "date" in e else "from_date"].year), int(e["date" if "date" in e else "from_date"].month), int(e["date" if "date" in e else "from_date"].day)))

  newly_created_lineages = []

  for evt in timeline_events:
    if evt["type"] == "merge":
      target_symbol = evt["target_symbol"]
      merge_date = evt["date"]
      parents_symbols = evt["parents_symbols"]
      to_x = date_to_x(merge_date)
      from_x = to_x - (MERGE_TRANSITION_DAYS * DIAGRAM_DATE_SCALE)

      parent_lineages = []
      micro_parent_lines = []
      zero_ratio_parent_lines = []

      existing_target_lineages = party_lineages.get(target_symbol, [])
      target_active = find_active_lineage(existing_target_lineages, to_x)
      if target_active:
          parent_lineages.append(target_active)

      for fs, merge_ratio in parents_symbols:
        flist = party_lineages.get(fs, [])
        cand = find_active_lineage(flist, to_x)
        if cand:
            src_party = by_symbol.get(fs)
            is_zero_ratio = (merge_ratio <= 0.0)
            is_micro = False
            try:
                bonus = float(src_party._get_prominence_bonus_at_date(merge_date)) if src_party else 0.0
                is_micro = abs(bonus - db.IMPORTANCE_TIER_BONUS_MICRO) < 1e-9
                if not is_micro and src_party:
                    if abs(importance_at(src_party, merge_date)) < 1e-6:
                        is_micro = True
            except: is_micro = False

            if is_zero_ratio:
                zero_ratio_parent_lines.append((cand, src_party))
            elif is_micro:
                micro_parent_lines.append((cand, src_party))
            else:
                if cand != target_active:
                    parent_lineages.append(cand)

      # Promote micro parents if target is major
      target_party = by_symbol[target_symbol]
      has_non_target_parents = any(cand != target_active for cand, _ in micro_parent_lines) or any(p != target_active for p in parent_lineages)
      if has_non_target_parents and micro_parent_lines and (not parent_lineages or (len(parent_lineages) == 1 and parent_lineages[0] == target_active)):
          try:
              target_bonus = float(target_party._get_prominence_bonus_at_date(merge_date))
              if abs(target_bonus - db.IMPORTANCE_TIER_BONUS_MICRO) > 1e-9:
                  for cand, _ in micro_parent_lines:
                      if cand != target_active:
                          parent_lineages.append(cand)
                  micro_parent_lines = []
          except: pass

      micro_parent_lines.extend(zero_ratio_parent_lines)

      if not parent_lineages:
          # Create new lineage for target
          color = getattr(target_party, "color", None) or "black"
          start_w = importance_at(target_party, merge_date)
          target_y = orientation_to_y(target_party.initial_political_position)
          z_val = get_max_importance(target_party)
          new_line = Lineage(diagram, color, to_x, target_y, float(start_w), z=z_val)
          end_x = date_to_x(target_party.dissolution_date) if target_party.dissolution_date else date_to_x(db.Date.today())
          new_line.terminate_at(end_x)
          party_lineages[target_symbol].append(new_line)
          newly_created_lineages.append((target_symbol, new_line))

          for (src_line, _) in micro_parent_lines:
              src_line.end_at_lineage(new_line, from_x, to_x)
      else:
          # Perform merge
          color = getattr(target_party, "color", None) or "black"
          start_w = importance_at(target_party, merge_date)
          z_val = get_max_importance(target_party)

          if target_active and len(parent_lineages) == 1:
              receiving_line = target_active
          else:
              target_y = target_active._get_y_at(to_x) if target_active else orientation_to_y(target_party.initial_political_position)
              merged = Lineage.create_from_merge(diagram, color, from_x, to_x, target_y, float(start_w), parent_lineages, z=z_val)
              end_x = date_to_x(target_party.dissolution_date) if target_party.dissolution_date else date_to_x(db.Date.today())
              merged.terminate_at(end_x)
              party_lineages[target_symbol].append(merged)
              newly_created_lineages.append((target_symbol, merged))
              receiving_line = merged

          if receiving_line:
              for (src_line, _) in micro_parent_lines:
                  src_line.end_at_lineage(receiving_line, from_x, to_x)

      # Apply importance changes
      for symbol, lineage in newly_created_lineages:
          apply_importance_changes_to_lineage(lineage, by_symbol[symbol])
      newly_created_lineages = []

    elif evt["type"] == "split":
        # Process Split
        source_symbol = evt["source_symbol"]
        target_symbol = evt["target_symbol"]
        ratio = evt["ratio"]
        from_x = date_to_x(evt["date"])
        to_x = from_x + (SECEDE_TRANSITION_DAYS * DIAGRAM_DATE_SCALE)

        src_list = party_lineages.get(source_symbol, [])
        source_lin = find_active_lineage(src_list, to_x)
        if not source_lin: continue

        source_party = by_symbol[source_symbol]
        target_party = by_symbol[target_symbol]

        if ratio <= 0.0:
            target_lineages = party_lineages.get(target_symbol, [])
            target_is_being_created = (target_party.creation_date == evt["date"]) and not target_lineages

            if target_is_being_created:
                target_color = getattr(target_party, "color", None) or "black"
                start_w = importance_at(target_party, target_party.creation_date)
                target_y = orientation_to_y(target_party.initial_political_position)
                z_val = get_max_importance(target_party)

                # Resolve inside_entity for target_party
                sec_in_assembly = None
                sec_index = -1

                if target_party.inside_entity:
                    if isinstance(target_party.inside_entity, db.PoliticalFederation):
                        fed_symbol = target_party.inside_entity.symbol
                        bundle = federation_bundles.get(fed_symbol)
                        if bundle:
                            sec_in_assembly = bundle
                            # Dynamic Indexing
                            fed = target_party.inside_entity
                            active_members = []
                            for interval in fed.membership_intervals:
                                if interval.get("from") <= target_party.creation_date and (interval.get("to") is None or interval.get("to") >= target_party.creation_date):
                                    p = interval.get("party")
                                    if p: active_members.append(p)
                            active_members.sort(key=lambda p: p.get_political_position_at(target_party.creation_date))
                            try:
                                sec_index = active_members.index(target_party)
                            except ValueError:
                                sec_index = -1

                    elif isinstance(target_party.inside_entity, db.PoliticalParty):
                        host_party = target_party.inside_entity
                        host_symbol = host_party.symbol
                        host_lines = party_lineages.get(host_symbol, [])
                        host_lin = find_active_lineage(host_lines, from_x)
                        if host_lin:
                            orbit = orbits_by_host.get(host_lin)
                            if not orbit:
                                orbit = Orbit(diagram, host_lin, float(SATELLITE_ORBIT_MARGIN))
                                orbits_by_host[host_lin] = orbit
                            sec_in_assembly = orbit

                            # Dynamic Indexing for Orbit
                            sat_pos = target_party.get_political_position_at(target_party.creation_date)
                            host_pos = host_party.get_political_position_at(target_party.creation_date)
                            is_upper = sat_pos >= host_pos
                            active_sats = []
                            for m in host_party.satellite_host_memberships:
                                if m.get("from") <= target_party.creation_date and (m.get("to") is None or m.get("to") >= target_party.creation_date):
                                    s = m.get("satellite")
                                    if s: active_sats.append(s)
                            side_sats = []
                            for s in active_sats:
                                s_pos = s.get_political_position_at(target_party.creation_date)
                                if (s_pos >= host_pos) == is_upper:
                                    side_sats.append(s)
                            side_sats.sort(key=lambda s: abs(s.get_political_position_at(target_party.creation_date) - host_pos))
                            try:
                                rank = side_sats.index(target_party) + 1
                            except ValueError:
                                rank = 1
                            sec_index = rank if is_upper else -rank

                new_line = Lineage.create_from_lineage(source_lin, from_x, to_x, target_color, float(start_w), target_y, z=z_val, new_in_bundle=sec_in_assembly, new_index=sec_index)
                end_x = date_to_x(target_party.dissolution_date) if target_party.dissolution_date else date_to_x(db.Date.today())
                new_line.terminate_at(end_x)

                party_lineages[target_symbol].append(new_line)
                newly_created_lineages.append((target_symbol, new_line))
            else:
                target_lin = find_active_lineage(target_lineages, from_x)
                if target_lin:
                    connect_w = float(evt.get("visual_width") or 0.1)
                    # Create temporary connecting line
                    conn = Lineage.create_from_lineage(source_lin, from_x, to_x, source_lin.color, connect_w, target_lin._get_y_at(to_x), z=source_lin.z)
                    conn.end_at_lineage(target_lin, from_x, to_x)
        else:
            # Real split
            apply_importance_changes_to_lineage(source_lin, source_party, max_x=from_x)

            cont_w = importance_at(source_party, evt["date"])
            secede_w = importance_at(target_party, target_party.creation_date)
            z_val = get_max_importance(target_party)

            parent_y = source_lin._get_y_at(from_x)
            target_color = getattr(target_party, "color", None) or "black"

            sec_target_y = orientation_to_y(float(target_party.initial_political_position))
            source_new_position = evt.get("source_new_position")
            cont_target_y = orientation_to_y(float(source_new_position)) if source_new_position is not None else parent_y

            # Resolve inside_entity for target_party
            sec_in_assembly = None
            sec_index = -1

            if target_party.inside_entity:
                if isinstance(target_party.inside_entity, db.PoliticalFederation):
                    fed_symbol = target_party.inside_entity.symbol
                    if fed_symbol == "CONV_FED":
                         print(f"DEBUG: Looking for CONV_FED. Available bundles: {list(federation_bundles.keys())}")
                    bundle = federation_bundles.get(fed_symbol)
                    if fed_symbol == "CONV_FED":
                         print(f"DEBUG: Bundle found: {bundle is not None}")
                    if bundle:
                        sec_in_assembly = bundle
                        # Dynamic Indexing
                        fed = target_party.inside_entity
                        active_members = []
                        for interval in fed.membership_intervals:
                            if interval.get("from") <= target_party.creation_date and (interval.get("to") is None or interval.get("to") >= target_party.creation_date):
                                p = interval.get("party")
                                if p: active_members.append(p)
                        active_members.sort(key=lambda p: p.get_political_position_at(target_party.creation_date))
                        try:
                            sec_index = active_members.index(target_party)
                        except ValueError:
                            sec_index = -1

                elif isinstance(target_party.inside_entity, db.PoliticalParty):
                    host_party = target_party.inside_entity
                    host_symbol = host_party.symbol
                    host_lines = party_lineages.get(host_symbol, [])
                    host_lin = find_active_lineage(host_lines, from_x)
                    if host_lin:
                        orbit = orbits_by_host.get(host_lin)
                        if not orbit:
                            orbit = Orbit(diagram, host_lin, float(SATELLITE_ORBIT_MARGIN))
                            orbits_by_host[host_lin] = orbit
                        sec_in_assembly = orbit

                        # Dynamic Indexing for Orbit
                        sat_pos = target_party.get_political_position_at(target_party.creation_date)
                        host_pos = host_party.get_political_position_at(target_party.creation_date)
                        is_upper = sat_pos >= host_pos
                        active_sats = []
                        for m in host_party.satellite_host_memberships:
                            if m.get("from") <= target_party.creation_date and (m.get("to") is None or m.get("to") >= target_party.creation_date):
                                s = m.get("satellite")
                                if s: active_sats.append(s)
                        side_sats = []
                        for s in active_sats:
                            s_pos = s.get_political_position_at(target_party.creation_date)
                            if (s_pos >= host_pos) == is_upper:
                                side_sats.append(s)
                        side_sats.sort(key=lambda s: abs(s.get_political_position_at(target_party.creation_date) - host_pos))
                        try:
                            rank = side_sats.index(target_party) + 1
                        except ValueError:
                            rank = 1
                        sec_index = rank if is_upper else -rank

            children_specs = [
                {"color": source_lin.color, "target_w": float(cont_w), "target_y": cont_target_y, "is_continuation": True, "z": source_lin.z, "in_assembly": None, "index": -1},
                {"color": target_color, "target_w": float(secede_w), "target_y": sec_target_y, "is_continuation": False, "z": z_val, "in_assembly": sec_in_assembly, "index": sec_index}
            ]

            children = source_lin.split(from_x, to_x, children_specs)

            # Identify children
            # The split method sorts specs by target_y. We need to match children to specs.
            # children list corresponds to sorted specs.
            sorted_specs = sorted(children_specs, key=lambda s: s["target_y"])

            cont_child = None
            sec_child = None

            for child, spec in zip(children, sorted_specs):
                if spec["is_continuation"]: cont_child = child
                else: sec_child = child

            if cont_child:
                party_lineages[source_symbol].append(cont_child)
                newly_created_lineages.append((source_symbol, cont_child))
                end_x = date_to_x(source_party.dissolution_date) if source_party.dissolution_date else date_to_x(db.Date.today())
                cont_child.terminate_at(end_x)

            if sec_child:
                target_lineages = party_lineages.get(target_symbol, [])
                if target_symbol == "CONV":
                    print(f"DEBUG: CONV treated as continuation. Lineages count: {len(target_lineages)}")
                target_is_being_created = (target_party.creation_date == evt["date"]) and not target_lineages

                if target_is_being_created:
                    party_lineages[target_symbol].append(sec_child)
                    newly_created_lineages.append((target_symbol, sec_child))
                    end_x = date_to_x(target_party.dissolution_date) if target_party.dissolution_date else date_to_x(db.Date.today())
                    sec_child.terminate_at(end_x)
                else:
                    # Merge into existing target
                    existing_target_lin = find_active_lineage(target_lineages, to_x)
                    if existing_target_lin:
                        sec_child.merge_into(existing_target_lin, to_x, to_x + (MERGE_TRANSITION_DAYS * DIAGRAM_DATE_SCALE), secede_w)
                    else:
                        # Fallback
                        party_lineages[target_symbol].append(sec_child)
                        newly_created_lineages.append((target_symbol, sec_child))
                        end_x = date_to_x(target_party.dissolution_date) if target_party.dissolution_date else date_to_x(db.Date.today())
                        sec_child.terminate_at(end_x)

        for symbol, lineage in newly_created_lineages:
            apply_importance_changes_to_lineage(
                lineage,
                by_symbol[symbol],
                min_x=from_x,
                compose_until_x=to_x,
            )
        newly_created_lineages = []

    elif evt["type"] == "y_shift":
        symbol = evt["symbol"]
        from_x = date_to_x(evt["from_date"])
        to_x = date_to_x(evt["to_date"])
        target_y = orientation_to_y(evt["target_position"])

        if to_x > from_x:
            lineages = party_lineages.get(symbol, [])
            for lin in lineages:
                seg_start = max(from_x, lin.start_x)
                seg_end = min(to_x, lin.end_x if lin.end_x is not None else float('inf'))
                if seg_end - seg_start > SHIFT_MIN_SEGMENT_EPS:
                    lin.shift_to(seg_start, seg_end, target_y)

  # Enforce dissolutions
  for (symbol, at_date) in dissolves:
      lines = party_lineages.get(symbol, [])
      if lines:
          lines[-1].terminate_at(date_to_x(at_date))

  # Federations
  # Federations (Created at top)
  # federations = getattr(db.PoliticalSystem(), "political_federations", {})
  # federation_bundles = {}
  # ... (Moved to top)

  # Federation Memberships
  for federation_symbol, federation in federations.items():
      bundle = federation_bundles.get(federation_symbol)
      if not bundle: continue

      membership_intervals = getattr(federation, "membership_intervals", []) or []
      member_parties = []
      for interval in membership_intervals:
          party = interval.get("party")
          if party and party not in member_parties: member_parties.append(party)

      member_parties.sort(key=lambda p: float(getattr(p, "initial_political_position", 0.0)), reverse=True)
      member_index_map = {party: i for i, party in enumerate(member_parties)}

      for interval in membership_intervals:
          party = interval.get("party")
          if not party: continue
          symbol = symbol_by_party.get(party)
          if not symbol: continue
          lineages = party_lineages.get(symbol, [])
          if not lineages: continue

          from_date = interval.get("from")
          if not from_date: continue

          base_join_to_x = date_to_x(from_date)
          join_to_x = base_join_to_x
          join_from_x = join_to_x - (FEDERATION_JOIN_TRANSITION_DAYS * DIAGRAM_DATE_SCALE)

          lineage_for_join = find_active_lineage(lineages, join_to_x)
          if lineage_for_join:
              join_from_x = max(join_from_x, lineage_for_join.start_x)
              join_to_x = min(join_to_x, lineage_for_join.end_x if lineage_for_join.end_x is not None else float('inf'))

              if join_to_x - join_from_x > SHIFT_MIN_SEGMENT_EPS:
                  # Skip if already handled by create_in_assembly
                  if lineage_for_join._initial_bundle == bundle and abs(date_to_x(from_date) - lineage_for_join.start_x) < 1e-3:
                      continue

                  # Also check if we already have a JOIN event to this bundle at this time (e.g. from split creation)
                  already_joined = False
                  for evt in lineage_for_join.membership_events:
                      if evt.type == MembershipEventType.JOIN and evt.assembly == bundle and abs(evt.from_x - join_from_x) < 1e-3:
                          already_joined = True
                          break
                  if already_joined: continue

                  # Dynamic Indexing for Federation Join
                  # Get all members active at join_to_x
                  active_members = []
                  for interval_check in membership_intervals:
                      # Check overlap with join_to_x
                      check_from = date_to_x(interval_check.get("from"))
                      check_to = date_to_x(interval_check.get("to")) if interval_check.get("to") else float('inf')

                      if check_from <= join_to_x and check_to >= join_to_x:
                          p = interval_check.get("party")
                          if p: active_members.append(p)

                  # Sort by current political position at join date (Ascending: Left to Right -> Top to Bottom)
                  join_date = interval.get("from") # Use from date for position calculation
                  active_members.sort(key=lambda p: p.get_political_position_at(join_date))

                  try:
                     index = active_members.index(party)
                  except ValueError:
                     index = 0 # Fallback

                  lineage_for_join.join(join_from_x, join_to_x, bundle, index)

                  to_date = interval.get("to")
                  if to_date:
                      leave_center_x = date_to_x(to_date)
                      leave_half_span = (FEDERATION_LEAVE_TRANSITION_DAYS * DIAGRAM_DATE_SCALE) / 2.0
                      leave_from_x = leave_center_x - leave_half_span
                      leave_to_x = leave_center_x + leave_half_span

                      lineage_for_leave = find_active_lineage(lineages, leave_center_x)
                      if lineage_for_leave:
                           leave_from_x = max(leave_from_x, lineage_for_leave.start_x)
                           leave_to_x = min(leave_to_x, lineage_for_leave.end_x if lineage_for_leave.end_x is not None else float('inf'))
                           if leave_to_x - leave_from_x > SHIFT_MIN_SEGMENT_EPS:
                               # Leave to original Y (orientation)
                               target_y = orientation_to_y(float(getattr(party, "initial_political_position", 0.0)))
                               lineage_for_leave.leave(leave_from_x, leave_to_x, bundle, target_y)

  # Satellites
  for host_symbol in symbols_sorted:
      host_party = by_symbol[host_symbol]
      host_satellites = getattr(host_party, "satellite_host_memberships", []) or []
      if not host_satellites: continue

      host_lines = party_lineages.get(host_symbol, [])
      if not host_lines: continue

      host_main_lineage = host_lines[-1]
      orbit = orbits_by_host.get(host_main_lineage)
      if not orbit:
          orbit = Orbit(diagram, host_main_lineage, float(SATELLITE_ORBIT_MARGIN))
          orbits_by_host[host_main_lineage] = orbit

      top_satellites = []
      bottom_satellites = []

      for membership in host_satellites:
          satellite_party = membership.get("satellite")
          if not satellite_party: continue
          if satellite_party in [p for p, _ in top_satellites] or satellite_party in [p for p, _ in bottom_satellites]: continue

          sat_orientation = float(getattr(satellite_party, "initial_political_position", 0.0))
          host_orientation = float(getattr(host_party, "initial_political_position", 0.0))

          if sat_orientation >= host_orientation: top_satellites.append((satellite_party, sat_orientation))
          else: bottom_satellites.append((satellite_party, sat_orientation))

      top_satellites.sort(key=lambda p: p[1], reverse=True)
      bottom_satellites.sort(key=lambda p: p[1])

      satellite_index_map = {}
      for i, (p, _) in enumerate(top_satellites, start=1): satellite_index_map[p] = i
      for i, (p, _) in enumerate(bottom_satellites, start=1): satellite_index_map[p] = -i

      for membership in host_satellites:
          satellite_party = membership.get("satellite")
          if not satellite_party: continue
          symbol = symbol_by_party.get(satellite_party)
          if not symbol: continue

          satellite_lines = party_lineages.get(symbol, [])
          if not satellite_lines: continue

          from_date = membership.get("from")
          if not from_date: continue

          join_center_x = date_to_x(from_date)
          join_half_span = (SATELLITE_JOIN_TRANSITION_DAYS * DIAGRAM_DATE_SCALE) / 2.0
          join_from_x = join_center_x - join_half_span
          join_to_x = join_center_x + join_half_span

          lineage_for_join = find_active_lineage(satellite_lines, join_center_x)
          if lineage_for_join:
              join_from_x = max(join_from_x, lineage_for_join.start_x)
              join_to_x = min(join_to_x, lineage_for_join.end_x if lineage_for_join.end_x is not None else float('inf'))

              if join_to_x - join_from_x > SHIFT_MIN_SEGMENT_EPS:
                  # Skip if already handled by create_in_assembly
                  if lineage_for_join._initial_bundle == orbit and abs(date_to_x(from_date) - lineage_for_join.start_x) < 1e-3:
                      continue

                  # Also check if we already have a JOIN event to this orbit at this time (e.g. from split creation)
                  already_joined = False
                  for evt in lineage_for_join.membership_events:
                      if evt.type == MembershipEventType.JOIN and evt.assembly == orbit and abs(evt.from_x - join_from_x) < 1e-3:
                          already_joined = True
                          break
                  if already_joined: continue

                  # Dynamic Indexing for Orbit Join
                  sat_pos = satellite_party.get_political_position_at(from_date)
                  host_pos = host_party.get_political_position_at(from_date)

                  is_upper = sat_pos >= host_pos

                  # Get all satellites active at join_to_x
                  active_sats = []
                  for m in host_party.satellite_host_memberships:
                      check_from = date_to_x(m.get("from"))
                      check_to = date_to_x(m.get("to")) if m.get("to") else float('inf')

                      if check_from <= join_to_x and check_to >= join_to_x:
                          s = m.get("satellite")
                          if s: active_sats.append(s)

                  # Filter and sort
                  side_sats = []
                  for s in active_sats:
                      s_pos = s.get_political_position_at(from_date)
                      if (s_pos >= host_pos) == is_upper:
                          side_sats.append(s)

                  side_sats.sort(key=lambda s: abs(s.get_political_position_at(from_date) - host_pos))

                  try:
                     rank = side_sats.index(satellite_party) + 1
                  except ValueError:
                     rank = 1

                  index = rank if is_upper else -rank
                  lineage_for_join.join(join_from_x, join_to_x, orbit, index)

                  to_date = membership.get("to")
                  if to_date:
                      leave_center_x = date_to_x(to_date)
                      leave_half_span = (SATELLITE_LEAVE_TRANSITION_DAYS * DIAGRAM_DATE_SCALE) / 2.0
                      leave_from_x = leave_center_x - leave_half_span
                      leave_to_x = leave_center_x + leave_half_span

                      lineage_for_leave = find_active_lineage(satellite_lines, leave_center_x)
                      if lineage_for_leave:
                          leave_from_x = max(leave_from_x, lineage_for_leave.start_x)
                          leave_to_x = min(leave_to_x, lineage_for_leave.end_x if lineage_for_leave.end_x is not None else float('inf'))

                          if leave_to_x - leave_from_x > SHIFT_MIN_SEGMENT_EPS:
                                target_y = orientation_to_y(float(satellite_party.get_political_position_at(to_date)))
                                lineage_for_leave.leave(leave_from_x, leave_to_x, orbit, target_y)

  add_alliance_regions(
    diagram,
    system.political_alliances,
    party_lineages,
    symbol_by_party,
  )

  diagram.generate("political_diagram.svg")
  return diagram

if __name__ == "__main__":
  main()
