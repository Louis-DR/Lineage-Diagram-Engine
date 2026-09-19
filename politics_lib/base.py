import datetime
from typing import Union
from .constants import (
    IMPORTANCE_CHANGE_DURATION,
    MINIMAL_IMPORTANCE,
    IMPORTANCE_POWER,
    IMPORTANCE_MULTIPLIER,
    PRESIDENTIAL_IMPORTANCE_MULTIPLIER,
    LEGISLATIVE_IMPORTANCE_MULTIPLIER,
    SENATORIAL_IMPORTANCE_MULTIPLIER,
    EUROPEAN_IMPORTANCE_MULTIPLIER,
    PRESIDENTIAL_IMPORTANCE_VOTES_WEIGHT,
    PRESIDENTIAL_IMPORTANCE_VICTORY_WEIGHT,
    LEGISLATIVE_IMPORTANCE_VOTES_WEIGHT,
    LEGISLATIVE_IMPORTANCE_SEATS_WEIGHT,
    LEGISLATIVE_IMPORTANCE_MAJORITY_WEIGHT,
    SENATORIAL_IMPORTANCE_SEATS_WEIGHT,
    SENATORIAL_IMPORTANCE_MAJORITY_WEIGHT,
    EUROPEAN_IMPORTANCE_VOTES_WEIGHT,
    EUROPEAN_IMPORTANCE_SEATS_WEIGHT,
    IMPORTANCE_TIER_BONUS_MICRO,
    IMPORTANCE_TIER_BONUS_MINOR,
    IMPORTANCE_TIER_BONUS_MAJOR,
)

from .date import Date




class PoliticalSystem:
  _instance    = None
  _initialized = False

  def __new__(cls) -> "PoliticalSystem":
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self):
    if self._initialized: return
    self._initialized = True

    self.reset()

  def reset(self):
    """Clear loaded data so an explicit loader can rebuild deterministically."""

    self.political_regimes      = {}
    self.political_parties      = {}
    self.political_federations  = {}
    self.political_alliances    = {}
    self.presidents             = {}
    self.governments            = {}
    self.legislatures           = {}
    self.senate_compositions    = {}
    self.european_delegations   = {}
    self.entities_by_id         = {}
    self.aliases                = {}
    self.loader_warnings        = []

  def set_political_regime(
    self,
    from_date: Date,
    to_date:   Date,
    name:      str
  ):
    self.political_regimes[(from_date, to_date)] = {
      "name": name,
      "from": from_date,
      "to":   to_date,
    }

  def add_presidential_election(
    self,
    at_date: Date
  ):
    self.presidents[at_date] = {
      "date": at_date
    }

  def add_government_composition(
    self,
    at_date:          Date,
    name:             str,
    state_ministers:  int,
    ministers:        int,
    deputy_ministers: int
  ):
    self.governments[at_date] = {
      "name":             name,
      "state_ministers":  state_ministers,
      "ministers":        ministers,
      "deputy_ministers": deputy_ministers,
      "date":             at_date,
    }

  def add_legislative_election(
    self,
    at_date:      Date,
    legislature:  str,
    seats:        int,
    proportional: bool = False
  ):
    self.legislatures[at_date] = {
      "name":         legislature,
      "seats":        seats,
      "proportional": proportional,
      "date":         at_date,
    }

  def add_senatorial_election(
    self,
    at_date: Date,
    seats:   int
  ):
    self.senate_compositions[at_date] = {
      "seats": seats,
      "date":  at_date,
    }

  def add_european_election(
    self,
    at_date: Date,
    seats:   int
  ):
    self.european_delegations[at_date] = {
      "seats": seats,
      "date":  at_date,
    }

  def get_number_legislative_seats(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.legislatures.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.legislatures[latest_key]["seats"])

  def get_number_state_ministers(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.governments.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.governments[latest_key]["state_ministers"])

  def get_number_ministers(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.governments.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.governments[latest_key]["ministers"])

  def get_number_deputy_ministers(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.governments.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.governments[latest_key]["deputy_ministers"])

  def get_number_senatorial_seats(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.senate_compositions.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.senate_compositions[latest_key]["seats"])

  def get_number_european_seats(
    self,
    at_date: Date
  ) -> int:
    eligible_keys = [key for key in self.european_delegations.keys() if key <= at_date]
    if not eligible_keys:
      return 0
    latest_key = max(eligible_keys)
    return int(self.european_delegations[latest_key]["seats"])


class PoliticalParty:
  def __init__(
    self,
    symbol:                     str,
    color:                      str,
    creation_date:              Date,
    initial_name:               str,
    initial_political_position: float,
    initial_prominence_tier:    str = "micro",
    merge_from:                 dict["PoliticalParty", float] | list["PoliticalParty"] = [],  # dict for ratios, list for backward compatibility (full merge)
    secede_from:                dict["PoliticalParty", float | dict] = {},  # float for ratio only, or dict with "ratio" and optional "source_new_position"
    inside_entity:              Union["PoliticalParty","PoliticalFederation","PoliticalAlliance"] = None,
  ):
    PoliticalSystem().political_parties[symbol] = self

    self.symbol              = symbol
    self.color               = color
    self.creation_date       = creation_date
    self.dissolution_date    = None
    self.inside_entity       = inside_entity
    self.names_by_date = {
      creation_date: initial_name
    }
    self.initial_political_position = initial_political_position

    # Handle merge_from: can be list (backward compat) or dict with ratios
    if isinstance(merge_from, dict):
      self.merged_from_parties = dict(merge_from)
    else:
      self.merged_from_parties = {party: 1.0 for party in merge_from}  # Default ratio of 1.0 for list entries
    self.seceded_from_parties  = dict(secede_from)

    self.presidential_results      = {}
    self.government_participations = []
    self.legislative_results       = {}
    self.senatorial_results        = {}
    self.european_results          = {}

    # Political position shift events over time
    self.political_position_shifts = []

    # Prominence tier changes by date. Defaults to micro at creation.
    self.prominence_tier_by_date: dict[Date, str] = {}
    # Use the setter for validation/normalization.
    self.set_prominence_tier(creation_date, initial_prominence_tier)

    # Lineage event log for rendering (merge/secede/dissolve).
    # Events are dicts with keys: type, date, and counterpart symbols/ratios.
    self.lineage_events: list[dict] = []

    # Per-component additive adjustments from transfers (positive=incoming, negative=outgoing).
    # Adjustments apply from their date until the next election of that component for this party.
    self.component_adjustments = {
      "presidential": [],
      "legislative":  [],
      "senatorial":   [],
      "european":     [],
    }

    # Grouping structures
    # Satellites:
    #  - As a satellite, this party can orbit a host party.
    #  - As a host, this party can have other parties as satellites.
    # Memberships are stored as intervals with from/to dates.
    self.satellite_memberships      = []  # List[dict]: {"host": PoliticalParty, "from": Date, "to": Optional[Date]}
    self.satellite_host_memberships = []  # List[dict]: {"satellite": PoliticalParty, "from": Date, "to": Optional[Date]}

    # Federations and alliances memberships (this party as a member).
    self.federation_memberships = []  # List[dict]: {"federation": PoliticalFederation, "from": Date, "to": Optional[Date]}
    self.alliance_memberships   = []  # List[dict]: {"alliance": PoliticalAlliance,   "from": Date, "to": Optional[Date]}

    # Apply lineage at creation: perform merges/secessions now rather than storing them.
    # This transfers the four components as of the creation date.
    if self.merged_from_parties:
      for source_party, ratio in list(self.merged_from_parties.items()):
        if isinstance(source_party, PoliticalParty):
          source_party.merge_into(self.creation_date, self, float(ratio))
    if self.seceded_from_parties:
      for source_party, secede_spec in list(self.seceded_from_parties.items()):
        if isinstance(source_party, PoliticalParty):
          # secede_spec can be either a float (ratio) or a dict with "ratio" and optional "source_new_position"
          if isinstance(secede_spec, dict):
            ratio = float(secede_spec.get("ratio", 0.0))
            source_new_position = secede_spec.get("source_new_position", None)
          else:
            ratio = float(secede_spec)
            source_new_position = None
          source_party.secede_into(self.creation_date, self, ratio, source_new_position)

    if self.inside_entity:
      self.join(self.creation_date, self.inside_entity)

  def dissolve(self, at_date:Date):
    # Dissolution marks the end date of the party's existence.
    self.dissolution_date = at_date
    for membership in self.satellite_memberships:
      if membership.get("to") is None:
        self._leave_satellite(at_date, membership["host"])
    for membership in self.federation_memberships:
      if membership.get("to") is None:
        membership["to"] = at_date
        membership["federation"]._remove_member(at_date, self)
    for membership in self.alliance_memberships:
      if membership.get("to") is None:
        membership["to"] = at_date
        membership["alliance"]._remove_member(at_date, self)
    self.lineage_events.append({
      "type": "dissolve",
      "date": at_date,
    })

  def merge_into(self, at_date:Date, target_party:"PoliticalParty", ratio:float=1.0):
    # Transfer a portion (or all) of each importance component into the target and dissolve.
    if not isinstance(target_party, PoliticalParty):
      return
    ratio = max(0.0, min(1.0, float(ratio)))

    # If ratio is 0, still log lineage events but don't transfer components
    # This allows the rendering engine to show the connection visually
    if ratio <= 0.0:
      # The merging party still disappears on that date
      self.dissolve(at_date)
      # Log lineage events for rendering (visual connection only, no component transfer)
      self.lineage_events.append({
        "type": "merge_into",
        "date": at_date,
        "into": target_party.symbol,
        "ratio": 0.0,
      })
      target_party.lineage_events.append({
        "type": "merge_from",
        "date": at_date,
        "from": self.symbol,
        "ratio": 0.0,
      })
      return

    # Compute source components at the transfer date (including prior adjustments).
    source_components = self._get_component_values_at_date(at_date)
    for component_name, component_value in source_components.items():
      if component_value != 0.0:
        target_party._add_component_adjustment(component_name, at_date, float(component_value * ratio))
    # The merging party disappears on that date.
    self.dissolve(at_date)
    # Log lineage events for rendering
    self.lineage_events.append({
      "type": "merge_into",
      "date": at_date,
      "into": target_party.symbol,
      "ratio": ratio,
    })
    target_party.lineage_events.append({
      "type": "merge_from",
      "date": at_date,
      "from": self.symbol,
      "ratio": ratio,
    })

  def secede_into(self, at_date:Date, target_party:"PoliticalParty", importance_ratio:float, source_new_position:float=None, visual_width:float=None):
    # Transfer a fraction of each importance component into the target; reduce source accordingly.
    if not isinstance(target_party, PoliticalParty):
      return
    ratio = max(0.0, min(1.0, float(importance_ratio)))

    # If ratio is 0, still log lineage events but don't transfer components
    # This allows the rendering engine to show the connection visually
    if ratio <= 0.0:
      # Log lineage events for rendering (visual connection only, no component transfer)
      self.lineage_events.append({
        "type": "secede_into",
        "date": at_date,
        "into": target_party.symbol,
        "ratio": 0.0,
        "source_new_position": source_new_position,
        "visual_width": visual_width,
      })
      target_party.lineage_events.append({
        "type": "secede_from",
        "date": at_date,
        "from": self.symbol,
        "ratio": 0.0,
      })
      return
    # Compute source components at the transfer date (including prior adjustments).
    source_components = self._get_component_values_at_date(at_date)
    for component_name, component_value in source_components.items():
      if component_value == 0.0:
        continue
      delta = float(component_value) * ratio
      if delta == 0.0:
        continue
      # Target receives positive adjustment.
      target_party._add_component_adjustment(component_name, at_date, delta)
      # Source loses the same amount.
      self._add_component_adjustment(component_name, at_date, -delta)
    # Log lineage events for rendering
    self.lineage_events.append({
      "type":  "secede_into",
      "date":  at_date,
      "into":  target_party.symbol,
      "ratio": ratio,
      "source_new_position": source_new_position,  # Optional new position for continuation party
      "visual_width": visual_width,  # Optional visual width for zero-ratio connections
    })
    target_party.lineage_events.append({
      "type":  "secede_from",
      "date":  at_date,
      "from":  self.symbol,
      "ratio": ratio,
    })

  def join(self, date:Date, entity:Union["PoliticalParty","PoliticalFederation","PoliticalAlliance"]):
    # Joining a party means becoming its satellite.
    # Joining a federation means becoming a member of it.
    # Joining an alliance means becoming a member of it.
    if isinstance(entity, PoliticalParty):
      self._join_satellite(date, entity)
      return
    if isinstance(entity, PoliticalFederation):
      self._join_federation(date, entity)
      return
    if isinstance(entity, PoliticalAlliance):
      self._join_alliance(date, entity)
      return
    raise TypeError("Entity must be a PoliticalParty, PoliticalFederation or PoliticalAlliance")

  def leave(self, date:Date, entity:Union["PoliticalParty","PoliticalFederation","PoliticalAlliance"]):
    if isinstance(entity, PoliticalParty):
      self._leave_satellite(date, entity)
      return
    if isinstance(entity, PoliticalFederation):
      self._leave_federation(date, entity)
      return
    if isinstance(entity, PoliticalAlliance):
      self._leave_alliance(date, entity)
      return
    raise TypeError("Entity must be a PoliticalParty, PoliticalFederation or PoliticalAlliance")

  def set_results_presidential_election(
    self,
    at_date:                     Date,
    first_round_vote_percentage: float,
    won:                         bool = False
  ):
    self.presidential_results[at_date] = {
      "date":                         at_date,
      "first_round_vote_percentage":  first_round_vote_percentage,
      "won":                          won,
    }

  def set_gouvernment_participation(
    self,
    at_date:          Date,
    to_date:          Date,
    prime_minister:   bool = False,
    state_ministers:  int  = 0,
    ministers:        int  = 0,
    deputy_ministers: int  = 0
  ):
    self.government_participations.append({
      "from":             at_date,
      "to":               to_date,
      "prime_minister":   prime_minister,
      "state_ministers":  state_ministers,
      "ministers":        ministers,
      "deputy_ministers": deputy_ministers,
    })

  def set_results_legislative_election(
    self,
    at_date:                     Date,
    first_round_vote_percentage: float,
    seats_won:                   int  = 0,
    majority:                    bool = False
  ):
    self.legislative_results[at_date] = {
      "date":                         at_date,
      "first_round_vote_percentage":  first_round_vote_percentage,
      "seats_won":                    seats_won,
      "majority":                     majority,
    }

  def set_results_senatorial_election(
    self,
    at_date:   Date,
    seats_won: int,
    majority:  bool = False
  ):
    self.senatorial_results[at_date] = {
      "date":      at_date,
      "seats_won": seats_won,
      "majority":  majority,
    }

  def set_results_european_election(
    self,
    at_date:         Date,
    vote_percentage: float,
    seats_won:       int = 0
  ):
    self.european_results[at_date] = {
      "date":            at_date,
      "vote_percentage": vote_percentage,
      "seats_won":       seats_won,
    }

  def name_change(self, at_date:Date, new_name:str) -> "PoliticalParty":
    # Record a new official name for this party at a given date.
    self.names_by_date[at_date] = str(new_name)
    return self

  def shift_political_position(self, from_date:Date, to_date:Date, target_position:float):
    # Record a shift in political position over a period.
    self.political_position_shifts.append({
      "from":            from_date,
      "to":              to_date,
      "target_position": target_position,
    })

  def get_political_position_at(self, at_date:Date) -> float:
    # Calculate political position at a specific date, accounting for shifts.
    current_pos = self.initial_political_position

    # Sort shifts by date
    sorted_shifts = sorted(self.political_position_shifts, key=lambda s: s["from"])

    for shift in sorted_shifts:
      start_date = shift["from"]
      end_date = shift["to"]
      target = shift["target_position"]

      if at_date >= end_date:
        current_pos = target
      elif at_date > start_date:
        # Interpolate
        total_days = (end_date - start_date).days
        elapsed_days = (at_date - start_date).days
        if total_days > 0:
          ratio = elapsed_days / total_days
          # Simple linear interpolation for value (visuals use smootherstep)
          current_pos = current_pos + (target - current_pos) * ratio
        else:
          current_pos = target
      # If at_date <= start_date, this shift hasn't started yet, so we ignore it (and subsequent ones)
      # But since we iterate in order, we just keep the current_pos from previous shifts.

    return current_pos

  def _join_satellite(self, at_date:Date, host_party:"PoliticalParty"):
    # Register this party as a satellite of the host party starting at at_date.
    for membership in reversed(self.satellite_memberships):
      if membership["host"] is host_party and membership.get("to") is None:
        return
    self.satellite_memberships.append({
      "host": host_party,
      "from": at_date,
      "to":   None,
    })
    for membership in reversed(host_party.satellite_host_memberships):
      if membership["satellite"] is self and membership.get("to") is None:
        return
    host_party.satellite_host_memberships.append({
      "satellite": self,
      "from":      at_date,
      "to":        None,
    })

  def _leave_satellite(self, at_date:Date, host_party:"PoliticalParty"):
    # Close the active satellite membership interval, if any.
    for membership in reversed(self.satellite_memberships):
      if membership["host"] is host_party and membership.get("to") is None:
        membership["to"] = at_date
        break
    for membership in reversed(host_party.satellite_host_memberships):
      if membership["satellite"] is self and membership.get("to") is None:
        membership["to"] = at_date
        break

  def _join_federation(self, at_date:Date, federation:"PoliticalFederation"):
    # Register membership in a political federation.
    for membership in reversed(self.federation_memberships):
      if membership["federation"] is federation and membership.get("to") is None:
        return
    self.federation_memberships.append({
      "federation": federation,
      "from":       at_date,
      "to":         None,
    })
    federation._add_member(at_date, self)

  def _leave_federation(self, at_date:Date, federation:"PoliticalFederation"):
    # Close the active federation membership interval, if any.
    for membership in reversed(self.federation_memberships):
      if membership["federation"] is federation and membership.get("to") is None:
        membership["to"] = at_date
        break
    federation._remove_member(at_date, self)

  def _join_alliance(self, at_date:Date, alliance:"PoliticalAlliance"):
    # Register membership in a political alliance.
    for membership in reversed(self.alliance_memberships):
      if membership["alliance"] is alliance and membership.get("to") is None:
        return
    self.alliance_memberships.append({
      "alliance": alliance,
      "from":     at_date,
      "to":       None,
    })
    alliance._add_member(at_date, self)

  def _leave_alliance(self, at_date:Date, alliance:"PoliticalAlliance"):
    # Close the active alliance membership interval, if any.
    for membership in reversed(self.alliance_memberships):
      if membership["alliance"] is alliance and membership.get("to") is None:
        membership["to"] = at_date
        break
    alliance._remove_member(at_date, self)

  def set_prominence_tier(self, at_date:Date, tier:str):
    # Normalize and validate input.
    normalized = str(tier or "").strip().lower()
    if normalized not in ("micro", "minor", "major"):
      raise ValueError("Prominence tier must be one of: 'micro', 'minor', 'major'")
    self.prominence_tier_by_date[at_date] = normalized

  def _prominence_tier_to_bonus(self, tier:str) -> float:
    if tier == "major":
      return float(IMPORTANCE_TIER_BONUS_MAJOR)
    if tier == "minor":
      return float(IMPORTANCE_TIER_BONUS_MINOR)
    return float(IMPORTANCE_TIER_BONUS_MICRO)

  def _get_prominence_bonus_at_date(self, at_date:Date) -> float:
    eligible = [d for d in self.prominence_tier_by_date.keys() if d <= at_date]
    if not eligible:
      return float(IMPORTANCE_TIER_BONUS_MICRO)
    last_date = max(eligible)
    return self._prominence_tier_to_bonus(self.prominence_tier_by_date.get(last_date, "micro"))

  def _add_component_adjustment(self, component_name:str, at_date:Date, delta:float):
    if component_name not in self.component_adjustments:
      self.component_adjustments[component_name] = []
    self.component_adjustments[component_name].append({
      "date":  at_date,
      "delta": float(delta),
    })

  def _get_component_values_at_date(self, at_date:Date) -> dict[str, float]:
    # Build election calendars (system preferred, else fallback to party dates)
    presidential_dates = sorted([d for d in PoliticalSystem().presidents.keys() if d <= at_date])
    if not presidential_dates:
      presidential_dates = sorted([d for d in self.presidential_results.keys() if d <= at_date])
    legislative_dates = sorted([d for d in PoliticalSystem().legislatures.keys() if d <= at_date])
    if not legislative_dates:
      legislative_dates = sorted([d for d in self.legislative_results.keys() if d <= at_date])
    senatorial_dates = sorted([d for d in PoliticalSystem().senate_compositions.keys() if d <= at_date])
    if not senatorial_dates:
      senatorial_dates = sorted([d for d in self.senatorial_results.keys() if d <= at_date])
    european_dates = sorted([d for d in PoliticalSystem().european_delegations.keys() if d <= at_date])
    if not european_dates:
      european_dates = sorted([d for d in self.european_results.keys() if d <= at_date])

    # Helpers to find a result keyed in the same year as a date
    def find_result_same_year(results: dict, target_date: Date):
      exact_value = results.get(target_date)
      if exact_value is not None:
        return exact_value
      year_candidates = [(result_date, result_value) for result_date, result_value in results.items() if int(result_date.year) == int(target_date.year)]
      if not year_candidates:
        return None
      if int(target_date.month) > 0:
        same_month = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == int(target_date.month)]
        if same_month:
          if int(target_date.day) > 0:
            for result_date, result_value in same_month:
              if int(result_date.day) == int(target_date.day):
                return result_value
          same_month.sort(key=lambda pair: (0 if int(pair[0].day) == 0 else 1, int(pair[0].day)))
          return same_month[0][1]
        year_only = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == 0]
        if year_only:
          return year_only[0][1]
        year_candidates.sort(key=lambda pair: (int(pair[0].month), int(pair[0].day)))
        return year_candidates[0][1]
      year_only = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == 0]
      if year_only:
        return year_only[0][1]
      year_candidates.sort(key=lambda pair: (int(pair[0].month), int(pair[0].day)))
      return year_candidates[0][1]

    # Build last-known base values as of at_date (only elections update base values)
    presidential_base = 0.0
    for date_iter in presidential_dates:
      data = find_result_same_year(self.presidential_results, date_iter)
      if data is None:
        presidential_base = 0.0
      else:
        vote_percentage = float(data.get("first_round_vote_percentage") or 0.0)
        won = bool(data.get("won") or False)
        votes_score = PRESIDENTIAL_IMPORTANCE_VOTES_WEIGHT * vote_percentage
        victory_score = PRESIDENTIAL_IMPORTANCE_VICTORY_WEIGHT * (1.0 if won else 0.0)
        presidential_base = PRESIDENTIAL_IMPORTANCE_MULTIPLIER * (votes_score + victory_score)

    legislative_base = 0.0
    for date_iter in legislative_dates:
      data = find_result_same_year(self.legislative_results, date_iter)
      if data is None:
        legislative_base = 0.0
      else:
        vote_percentage = float(data.get("first_round_vote_percentage") or 0.0)
        seats_won = int(data.get("seats_won") or 0)
        total_seats = PoliticalSystem().get_number_legislative_seats(date_iter)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        majority = bool(data.get("majority") or False)
        score = (LEGISLATIVE_IMPORTANCE_VOTES_WEIGHT * vote_percentage) + (LEGISLATIVE_IMPORTANCE_SEATS_WEIGHT * representation) + (LEGISLATIVE_IMPORTANCE_MAJORITY_WEIGHT * (100.0 if majority else 0.0))
        legislative_base = LEGISLATIVE_IMPORTANCE_MULTIPLIER * score

    senatorial_base = 0.0
    for date_iter in senatorial_dates:
      data = find_result_same_year(self.senatorial_results, date_iter)
      if data is None:
        senatorial_base = 0.0
      else:
        total_seats = PoliticalSystem().get_number_senatorial_seats(date_iter)
        seats_won = int(data.get("seats_won") or 0)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        majority = bool(data.get("majority") or False)
        score = (SENATORIAL_IMPORTANCE_SEATS_WEIGHT * representation) + (SENATORIAL_IMPORTANCE_MAJORITY_WEIGHT * (100.0 if majority else 0.0))
        senatorial_base = SENATORIAL_IMPORTANCE_MULTIPLIER * score

    european_base = 0.0
    for date_iter in european_dates:
      data = find_result_same_year(self.european_results, date_iter)
      if data is None:
        european_base = 0.0
      else:
        vote_percentage = float(data.get("vote_percentage") or 0.0)
        total_seats = PoliticalSystem().get_number_european_seats(date_iter)
        seats_won = int(data.get("seats_won") or 0)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        score = (EUROPEAN_IMPORTANCE_VOTES_WEIGHT * vote_percentage) + (EUROPEAN_IMPORTANCE_SEATS_WEIGHT * representation)
        european_base = EUROPEAN_IMPORTANCE_MULTIPLIER * score

    # Helper to find the next election date (strictly after) for expiry
    def next_after(dates: list[Date], pivot: Date) -> Date|None:
      for candidate in dates:
        if candidate > pivot:
          return candidate
      return None

    # Sum active adjustments for each component
    presidential_adj = 0.0
    legislative_adj  = 0.0
    senatorial_adj   = 0.0
    european_adj     = 0.0
    for event in self.component_adjustments.get("presidential", []):
      start_date = event["date"]
      if start_date <= at_date:
        expiry = next_after(sorted([d for d in PoliticalSystem().presidents.keys()]), start_date)
        if expiry is None or at_date < expiry:
          presidential_adj += float(event["delta"])
    for event in self.component_adjustments.get("legislative", []):
      start_date = event["date"]
      if start_date <= at_date:
        expiry = next_after(sorted([d for d in PoliticalSystem().legislatures.keys()]), start_date)
        if expiry is None or at_date < expiry:
          legislative_adj += float(event["delta"])
    for event in self.component_adjustments.get("senatorial", []):
      start_date = event["date"]
      if start_date <= at_date:
        expiry = next_after(sorted([d for d in PoliticalSystem().senate_compositions.keys()]), start_date)
        if expiry is None or at_date < expiry:
          senatorial_adj += float(event["delta"])
    for event in self.component_adjustments.get("european", []):
      start_date = event["date"]
      if start_date <= at_date:
        expiry = next_after(sorted([d for d in PoliticalSystem().european_delegations.keys()]), start_date)
        if expiry is None or at_date < expiry:
          european_adj += float(event["delta"])

    return {
      "presidential": float(presidential_base + presidential_adj),
      "legislative":  float(legislative_base  + legislative_adj),
      "senatorial":   float(senatorial_base   + senatorial_adj),
      "european":     float(european_base     + european_adj),
    }

  def get_importance_changes(self) -> list[dict]:
    # Utility: find a party result keyed in the same year as target_date.
    def find_result_same_year(results: dict, target_date: Date):
      # 1) Prefer exact (year, month, day) key match.
      exact_value = results.get(target_date)
      if exact_value is not None:
        return exact_value

      # 2) Collect candidates with the same year.
      year_candidates = [(result_date, result_value) for result_date, result_value in results.items() if int(result_date.year) == int(target_date.year)]
      if not year_candidates:
        return None

      # 3) If month is specified on the target, search for exact month.
      if int(target_date.month) > 0:
        same_month = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == int(target_date.month)]
        if same_month:
          # If day is specified, try exact day; otherwise pick a deterministic candidate in that month.
          if int(target_date.day) > 0:
            for result_date, result_value in same_month:
              if int(result_date.day) == int(target_date.day):
                return result_value
          # Pick a deterministic candidate in that month (prefer day==0, else earliest day).
          same_month.sort(key=lambda pair: (0 if int(pair[0].day) == 0 else 1, int(pair[0].day)))
          return same_month[0][1]
        # No exact month match; prefer a year-only entry if present, else a deterministic month from that year.
        year_only = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == 0]
        if year_only:
          return year_only[0][1]
        year_candidates.sort(key=lambda pair: (int(pair[0].month), int(pair[0].day)))
        return year_candidates[0][1]

      # 4) Month is not specified on the target; prefer a year-only result if it exists.
      year_only = [(result_date, result_value) for result_date, result_value in year_candidates if int(result_date.month) == 0]
      if year_only:
        return year_only[0][1]

      # 5) Otherwise, pick a deterministic candidate within the year (earliest month, then earliest day).
      year_candidates.sort(key=lambda pair: (int(pair[0].month), int(pair[0].day)))
      return year_candidates[0][1]

    # Build per-body election calendars (system first; fall back to party dates if system is empty).
    presidential_dates = sorted([d for d in PoliticalSystem().presidents.keys() if d >= self.creation_date])
    if not presidential_dates:
      presidential_dates = sorted([d for d in self.presidential_results.keys() if d >= self.creation_date])

    legislative_dates = sorted([d for d in PoliticalSystem().legislatures.keys() if d >= self.creation_date])
    if not legislative_dates:
      legislative_dates = sorted([d for d in self.legislative_results.keys() if d >= self.creation_date])

    senatorial_dates = sorted([d for d in PoliticalSystem().senate_compositions.keys() if d >= self.creation_date])
    if not senatorial_dates:
      senatorial_dates = sorted([d for d in self.senatorial_results.keys() if d >= self.creation_date])

    european_dates = sorted([d for d in PoliticalSystem().european_delegations.keys() if d >= self.creation_date])
    if not european_dates:
      european_dates = sorted([d for d in self.european_results.keys() if d >= self.creation_date])

    # Prominence tier change dates and updates
    tier_dates = sorted([d for d in self.prominence_tier_by_date.keys() if d >= self.creation_date])
    tier_updates: dict[Date, float] = {d: self._prominence_tier_to_bonus(self.prominence_tier_by_date[d]) for d in tier_dates}

    # Include adjustment start and expiry dates in the timeline for each component.
    def next_after(dates: list[Date], pivot: Date) -> Date|None:
      for candidate in dates:
        if candidate > pivot:
          return candidate
      return None

    # Collect component-specific adjustment start and expiry dates
    presidential_adjustment_events = self.component_adjustments.get("presidential", [])
    legislative_adjustment_events  = self.component_adjustments.get("legislative",  [])
    senatorial_adjustment_events   = self.component_adjustments.get("senatorial",   [])
    european_adjustment_events     = self.component_adjustments.get("european",     [])

    presidential_event_dates = [ev["date"] for ev in presidential_adjustment_events]
    presidential_expiry_dates = [d for d in [next_after(presidential_dates, ev["date"]) for ev in presidential_adjustment_events] if d is not None]

    legislative_event_dates = [ev["date"] for ev in legislative_adjustment_events]
    legislative_expiry_dates = [d for d in [next_after(legislative_dates, ev["date"]) for ev in legislative_adjustment_events] if d is not None]

    senatorial_event_dates = [ev["date"] for ev in senatorial_adjustment_events]
    senatorial_expiry_dates = [d for d in [next_after(senatorial_dates, ev["date"]) for ev in senatorial_adjustment_events] if d is not None]

    european_event_dates = [ev["date"] for ev in european_adjustment_events]
    european_expiry_dates = [d for d in [next_after(european_dates, ev["date"]) for ev in european_adjustment_events] if d is not None]

    # Compute per-body component updates only on that body's election dates.
    presidential_updates: dict[Date, float] = {}
    for election_date in presidential_dates:
      data = find_result_same_year(self.presidential_results, election_date)
      if data is None:
        presidential_updates[election_date] = 0.0
      else:
        vote_percentage = float(data.get("first_round_vote_percentage") or 0.0)
        won = bool(data.get("won") or False)
        votes_score = PRESIDENTIAL_IMPORTANCE_VOTES_WEIGHT * vote_percentage
        victory_score = PRESIDENTIAL_IMPORTANCE_VICTORY_WEIGHT * (1.0 if won else 0.0)
        presidential_updates[election_date] = PRESIDENTIAL_IMPORTANCE_MULTIPLIER * (votes_score + victory_score)

    legislative_updates: dict[Date, float] = {}
    for election_date in legislative_dates:
      data = find_result_same_year(self.legislative_results, election_date)
      if data is None:
        legislative_updates[election_date] = 0.0
      else:
        vote_percentage = float(data.get("first_round_vote_percentage") or 0.0)
        seats_won = int(data.get("seats_won") or 0)
        total_seats = PoliticalSystem().get_number_legislative_seats(election_date)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        majority = bool(data.get("majority") or False)
        score = (LEGISLATIVE_IMPORTANCE_VOTES_WEIGHT * vote_percentage) + (LEGISLATIVE_IMPORTANCE_SEATS_WEIGHT * representation) + (LEGISLATIVE_IMPORTANCE_MAJORITY_WEIGHT * (100.0 if majority else 0.0))
        legislative_updates[election_date] = LEGISLATIVE_IMPORTANCE_MULTIPLIER * score

    senatorial_updates: dict[Date, float] = {}
    for election_date in senatorial_dates:
      data = find_result_same_year(self.senatorial_results, election_date)
      if data is None:
        senatorial_updates[election_date] = 0.0
      else:
        total_seats = PoliticalSystem().get_number_senatorial_seats(election_date)
        seats_won = int(data.get("seats_won") or 0)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        majority = bool(data.get("majority") or False)
        score = (SENATORIAL_IMPORTANCE_SEATS_WEIGHT * representation) + (SENATORIAL_IMPORTANCE_MAJORITY_WEIGHT * (100.0 if majority else 0.0))
        senatorial_updates[election_date] = SENATORIAL_IMPORTANCE_MULTIPLIER * score

    european_updates: dict[Date, float] = {}
    for election_date in european_dates:
      data = find_result_same_year(self.european_results, election_date)
      if data is None:
        european_updates[election_date] = 0.0
      else:
        vote_percentage = float(data.get("vote_percentage") or 0.0)
        total_seats = PoliticalSystem().get_number_european_seats(election_date)
        seats_won = int(data.get("seats_won") or 0)
        representation = (seats_won / float(total_seats)) * 100.0 if total_seats > 0 else 0.0
        score = (EUROPEAN_IMPORTANCE_VOTES_WEIGHT * vote_percentage) + (EUROPEAN_IMPORTANCE_SEATS_WEIGHT * representation)
        european_updates[election_date] = EUROPEAN_IMPORTANCE_MULTIPLIER * score

    # Debug: trace updates for a specific party if needed
    # (disabled)
    pass

    # Global timeline of change dates across all bodies (system + party dates) filtered after creation.
    all_dates = set()
    all_dates.update(presidential_dates)
    all_dates.update(legislative_dates)
    all_dates.update(senatorial_dates)
    all_dates.update(european_dates)
    all_dates.update([d for d in self.presidential_results.keys() if d >= self.creation_date])
    all_dates.update([d for d in self.legislative_results.keys()  if d >= self.creation_date])
    all_dates.update([d for d in self.senatorial_results.keys()   if d >= self.creation_date])
    all_dates.update([d for d in self.european_results.keys()     if d >= self.creation_date])
    # Include prominence tier change dates
    all_dates.update(tier_dates)
    # Add transfer start/expiry dates so step changes are reflected
    all_dates.update([d for d in presidential_event_dates if d >= self.creation_date])
    all_dates.update([d for d in presidential_expiry_dates if d >= self.creation_date])
    all_dates.update([d for d in legislative_event_dates if d >= self.creation_date])
    all_dates.update([d for d in legislative_expiry_dates if d >= self.creation_date])
    all_dates.update([d for d in senatorial_event_dates if d >= self.creation_date])
    all_dates.update([d for d in senatorial_expiry_dates if d >= self.creation_date])
    all_dates.update([d for d in european_event_dates if d >= self.creation_date])
    all_dates.update([d for d in european_expiry_dates if d >= self.creation_date])

    timeline = sorted(all_dates)

    # Carry-forward the last known component for each body.
    changes: list[dict] = []
    last_presidential = 0.0
    last_legislative  = 0.0
    last_senatorial   = 0.0
    last_european     = 0.0
    last_tier_bonus   = float(self._get_prominence_bonus_at_date(self.creation_date))

    # Establish the initial total importance at creation (baseline before any change events).
    initial_components = self._get_component_values_at_date(self.creation_date)
    initial_total_importance = IMPORTANCE_MULTIPLIER * pow(
      MINIMAL_IMPORTANCE
      + float(initial_components["presidential"])
      + float(initial_components["legislative"])
      + float(initial_components["senatorial"])
      + float(initial_components["european"])
      + float(self._get_prominence_bonus_at_date(self.creation_date)),
      IMPORTANCE_POWER
    )
    last_total_importance = float(initial_total_importance)

    EPS = 1e-9

    for date_iter in timeline:
      # Update base values at election dates
      if date_iter in presidential_updates:
        last_presidential = presidential_updates[date_iter]
      if date_iter in legislative_updates:
        last_legislative = legislative_updates[date_iter]
      if date_iter in senatorial_updates:
        last_senatorial = senatorial_updates[date_iter]
      if date_iter in european_updates:
        last_european = european_updates[date_iter]
      if date_iter in tier_updates:
        last_tier_bonus = float(tier_updates[date_iter])

      # Compute active adjustments for each component at this date
      presidential_adj = 0.0
      legislative_adj  = 0.0
      senatorial_adj   = 0.0
      european_adj     = 0.0

      for event in presidential_adjustment_events:
        start_date = event["date"]
        if start_date <= date_iter:
          expiry = next_after(presidential_dates, start_date)
          if expiry is None or date_iter < expiry:
            presidential_adj += float(event["delta"])
      for event in legislative_adjustment_events:
        start_date = event["date"]
        if start_date <= date_iter:
          expiry = next_after(legislative_dates, start_date)
          if expiry is None or date_iter < expiry:
            legislative_adj += float(event["delta"])
      for event in senatorial_adjustment_events:
        start_date = event["date"]
        if start_date <= date_iter:
          expiry = next_after(senatorial_dates, start_date)
          if expiry is None or date_iter < expiry:
            senatorial_adj += float(event["delta"])
      for event in european_adjustment_events:
        start_date = event["date"]
        if start_date <= date_iter:
          expiry = next_after(european_dates, start_date)
          if expiry is None or date_iter < expiry:
            european_adj += float(event["delta"])

      presidential_effective = last_presidential + presidential_adj
      legislative_effective  = last_legislative  + legislative_adj
      senatorial_effective   = last_senatorial   + senatorial_adj
      european_effective     = last_european     + european_adj

      total_importance = IMPORTANCE_MULTIPLIER * pow(
        MINIMAL_IMPORTANCE + presidential_effective + legislative_effective + senatorial_effective + european_effective + last_tier_bonus,
        IMPORTANCE_POWER
      )

      # Debug output disabled
      pass

      # Only record an event if the total importance actually changes (beyond epsilon).
      if len(changes) == 0:
        # Compare to initial total before any events.
        if abs(total_importance - last_total_importance) > EPS:
          changes.append({"date": date_iter, "importance": float(total_importance), "prev_importance": float(last_total_importance)})
          last_total_importance = float(total_importance)
      else:
        # Compare to the last recorded change importance
        if abs(total_importance - float(changes[-1]["importance"])) > EPS:
          changes.append({"date": date_iter, "importance": float(total_importance), "prev_importance": float(changes[-1]["importance"])})
          last_total_importance = float(total_importance)

    # Smooth step changes into envelopes of half IMPORTANCE_CHANGE_DURATION around each change date,
    # merging overlapping envelopes. Each merged envelope goes from half-duration before the earliest
    # date to half-duration after the latest date in the group.
    def add_years_months_days(base: datetime.date, years: int, months: int, days: int) -> datetime.date:
      total_months = (base.month - 1) + (years * 12) + months
      new_year     = base.year + (total_months // 12)
      new_month    = (total_months % 12) + 1
      # Clamp day to last day of new month
      try:
        shifted = datetime.date(new_year, new_month, base.day)
      except ValueError:
        if new_month == 12:
          next_month = datetime.date(new_year + 1, 1, 1)
        else:
          next_month = datetime.date(new_year, new_month + 1, 1)
        shifted = next_month - datetime.timedelta(days=1)
      return shifted + datetime.timedelta(days=int(days))

    def half_duration_days(center: Date) -> int:
      center_date = center._to_datetime_date(default_to_start=True)
      years     = int(IMPORTANCE_CHANGE_DURATION.year)
      months    = int(IMPORTANCE_CHANGE_DURATION.month)
      days      = int(IMPORTANCE_CHANGE_DURATION.day)
      end_date  = add_years_months_days(center_date, years, months, days)
      full_days = (end_date - center_date).days
      return max(1, int(full_days // 2))

    # Build event envelopes around each change date
    event_envelopes = []
    for idx, item in enumerate(changes):
      date_obj  = item["date"]
      value     = float(item["importance"])
      half_days = half_duration_days(date_obj)
      center_date = date_obj._to_datetime_date(default_to_start=True)
      start_date  = center_date - datetime.timedelta(days=half_days)
      end_date    = center_date + datetime.timedelta(days=half_days)
      # Clamp start to creation date if needed
      creation_date = self.creation_date._to_datetime_date(default_to_start=True)
      if start_date < creation_date:
        start_date = creation_date
      event_envelopes.append({
        "index":    idx,
        "date":     date_obj,
        "value":    value,
        "start_dt": start_date,
        "end_dt":   end_date,
      })

    # Merge overlapping envelopes into grouped windows
    smoothed: list[dict] = []
    if event_envelopes:
      # Events are already sorted by date, but ensure envelopes are sorted by center date
      event_envelopes.sort(key=lambda e: e["date"])
      group_start_idx = event_envelopes[0]["index"]
      group_end_idx   = event_envelopes[0]["index"]
      group_start_date  = event_envelopes[0]["start_dt"]
      group_end_date    = event_envelopes[0]["end_dt"]

      for env in event_envelopes[1:]:
        start_date = env["start_dt"]
        end_date   = env["end_dt"]
        idx      = env["index"]
        # Overlap if the start of this envelope is on or before the current group's end
        if start_date <= group_end_date:
          # Extend current group
          group_end_date = max(group_end_date, end_date)
          group_end_idx = idx
        else:
          # Finalize previous group
          prev_value = float(changes[group_start_idx - 1]["importance"]) if group_start_idx > 0 else float(changes[group_start_idx].get("prev_importance", changes[group_start_idx]["importance"]))
          end_value = float(changes[group_end_idx]["importance"])
          smoothed.append({
            "from_date":       Date.from_datetime_date(group_start_date),
            "from_importance": prev_value,
            "to_date":         Date.from_datetime_date(group_end_date),
            "to_importance":   end_value,
          })
          # Start new group
          group_start_idx = idx
          group_end_idx   = idx
          group_start_date  = start_date
          group_end_date    = end_date

      # Finalize last group
      prev_value = float(changes[group_start_idx - 1]["importance"]) if group_start_idx > 0 else float(changes[group_start_idx].get("prev_importance", changes[group_start_idx]["importance"]))
      end_value  = float(changes[group_end_idx]["importance"])
      smoothed.append({
        "from_date":       Date.from_datetime_date(group_start_date),
        "from_importance": prev_value,
        "to_date":         Date.from_datetime_date(group_end_date),
        "to_importance":   end_value,
      })

    return smoothed


class PoliticalFederation:
  def __init__(
    self,
    symbol:                     str,
    color:                      str,
    creation_date:              Date,
    initial_name:               str,
    initial_political_position: float,
    initial_members:            list[PoliticalParty] = []
  ):
    PoliticalSystem().political_federations[symbol] = self

    self.symbol              = symbol
    self.color               = color
    self.creation_date       = creation_date
    self.dissolution_date    = None

    self.names_by_date = {
      creation_date: initial_name
    }

    self.initial_political_position = float(initial_political_position)

    # Political position shifts over time for the federation as a whole.
    self.political_position_shifts = []

    # Membership intervals.
    self.membership_intervals = []  # List[dict]: {"party": PoliticalParty, "from": Date, "to": Optional[Date]}

    for member_party in list(initial_members or []):
      if isinstance(member_party, PoliticalParty):
        member_party.join(creation_date, self)

  def dissolve(self, at_date:Date):
    # Mark the end of the federation.
    self.dissolution_date = at_date

  def name_change(self, at_date:Date, new_name:str):
    # Record a name change at a given date.
    self.names_by_date[at_date] = str(new_name)

  def shift_political_position(self, from_date:Date, to_date:Date, target_position:float):
    # Record a shift in political position over a period.
    self.political_position_shifts.append({
      "from":            from_date,
      "to":              to_date,
      "target_position": target_position,
    })

  def get_political_position_at(self, at_date:Date) -> float:
    # Calculate political position at a specific date, accounting for shifts.
    current_pos = self.initial_political_position

    # Sort shifts by date
    sorted_shifts = sorted(self.political_position_shifts, key=lambda s: s["from"])

    for shift in sorted_shifts:
      start_date = shift["from"]
      end_date = shift["to"]
      target = shift["target_position"]

      if at_date >= end_date:
        current_pos = target
      elif at_date > start_date:
        # Interpolate
        total_days = (end_date._to_datetime_date() - start_date._to_datetime_date()).days
        elapsed_days = (at_date._to_datetime_date() - start_date._to_datetime_date()).days
        if total_days > 0:
          ratio = elapsed_days / total_days
          # Simple linear interpolation for value (visuals use smootherstep)
          current_pos = current_pos + (target - current_pos) * ratio
        else:
          current_pos = target
      # If at_date <= start_date, this shift hasn't started yet, so we ignore it (and subsequent ones)
      # But since we iterate in order, we just keep the current_pos from previous shifts.

    return current_pos

  def _add_member(self, at_date:Date, party:PoliticalParty):
    # Internal helper called from PoliticalParty._join_federation.
    for interval in reversed(self.membership_intervals):
      if interval["party"] is party and interval.get("to") is None:
        return
    self.membership_intervals.append({
      "party": party,
      "from":  at_date,
      "to":    None,
    })

  def _remove_member(self, at_date:Date, party:PoliticalParty):
    # Internal helper called from PoliticalParty._leave_federation.
    for interval in reversed(self.membership_intervals):
      if interval["party"] is party and interval.get("to") is None:
        interval["to"] = at_date
        break



class PoliticalAlliance:
  def __init__(
    self,
    symbol:          str,
    color:           str,
    creation_date:   Date,
    initial_name:    str,
    initial_members: list[PoliticalParty] = []
  ):
    PoliticalSystem().political_alliances[symbol] = self

    self.symbol              = symbol
    self.color               = color
    self.creation_date       = creation_date
    self.dissolution_date    = None

    self.names_by_date = {
      creation_date: initial_name
    }

    # Membership intervals.
    self.membership_intervals = []  # List[dict]: {"party": PoliticalParty, "from": Date, "to": Optional[Date]}

    for member_party in list(initial_members or []):
      if isinstance(member_party, PoliticalParty):
        member_party.join(creation_date, self)

  def dissolve(self, at_date:Date):
    # Mark the end of the alliance.
    self.dissolution_date = at_date

  def name_change(self, at_date:Date, new_name:str):
    # Record a name change at a given date.
    self.names_by_date[at_date] = str(new_name)

  def _add_member(self, at_date:Date, party:PoliticalParty):
    # Internal helper called from PoliticalParty._join_alliance.
    for interval in reversed(self.membership_intervals):
      if interval["party"] is party and interval.get("to") is None:
        return
    self.membership_intervals.append({
      "party": party,
      "from":  at_date,
      "to":    None,
    })

  def _remove_member(self, at_date:Date, party:PoliticalParty):
    # Internal helper called from PoliticalParty._leave_alliance.
    for interval in reversed(self.membership_intervals):
      if interval["party"] is party and interval.get("to") is None:
        interval["to"] = at_date
        break
