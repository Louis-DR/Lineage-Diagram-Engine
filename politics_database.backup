import datetime
from typing import Union



class Date:
  def __init__(self, year:int, month:int=0, day:int=0):
    self.year  = year
    self.month = month
    self.day   = day

  @classmethod
  def today(cls) -> "Date":
    today = datetime.date.today()
    return cls(today.year, today.month, today.day)

  def __repr__(self) -> str:
    return f"Date(year={self.year}, month={self.month}, day={self.day})"

  def __str__(self) -> str:
    return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

  def _key_tuple(self) -> tuple[int,int,int]:
    return (int(self.year), int(self.month), int(self.day))

  def _ensure_valid_for_datetime(self):
    if self.year < 1:
      raise ValueError("Date arithmetic requires year >= 1")

  def _to_datetime_date(self, default_to_start: bool = True) -> datetime.date:
    self._ensure_valid_for_datetime()
    year = int(self.year)
    month = int(self.month) if self.month > 0 else (1 if default_to_start else 12)
    if int(self.day) > 0:
      day = int(self.day)
    else:
      if default_to_start:
        day = 1
      else:
        if month == 12:
          next_month = datetime.date(year + 1, 1, 1)
        else:
          next_month = datetime.date(year, month + 1, 1)
        day = (next_month - datetime.timedelta(days=1)).day
    return datetime.date(year, month, day)

  @classmethod
  def from_datetime_date(cls, value: datetime.date) -> "Date":
    return cls(value.year, value.month, value.day)

  def __hash__(self) -> int:
    return hash(self._key_tuple())

  def __eq__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() == other._key_tuple()
    return NotImplemented

  def __lt__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() < other._key_tuple()
    return NotImplemented

  def __le__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() <= other._key_tuple()
    return NotImplemented

  def __gt__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() > other._key_tuple()
    return NotImplemented

  def __ge__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() >= other._key_tuple()
    return NotImplemented

  def __ne__(self, other) -> bool:
    if isinstance(other, Date):
      return self._key_tuple() != other._key_tuple()
    return NotImplemented

  def __add__(self, other):
    if isinstance(other, datetime.timedelta):
      base = self._to_datetime_date(default_to_start=True)
      return Date.from_datetime_date(base + other)
    if isinstance(other, int):
      base = self._to_datetime_date(default_to_start=True)
      return Date.from_datetime_date(base + datetime.timedelta(days=int(other)))
    return NotImplemented

  def __radd__(self, other):
    return self.__add__(other)

  def __sub__(self, other):
    if isinstance(other, datetime.timedelta):
      base = self._to_datetime_date(default_to_start=True)
      return Date.from_datetime_date(base - other)
    if isinstance(other, int):
      base = self._to_datetime_date(default_to_start=True)
      return Date.from_datetime_date(base - datetime.timedelta(days=int(other)))
    if isinstance(other, Date):
      a = self._to_datetime_date(default_to_start=True)
      b = other._to_datetime_date(default_to_start=True)
      return a - b
    return NotImplemented

  def __iadd__(self, other):
    result = self + other
    if isinstance(result, Date):
      return result
    return NotImplemented

  def __isub__(self, other):
    result = self - other
    if isinstance(result, Date):
      return result
    return NotImplemented




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

    self.political_regimes      = {}
    self.political_parties      = {}
    self.political_federations  = {}
    self.political_alliances    = {}
    self.presidents             = {}
    self.governments            = {}
    self.legislatures           = {}
    self.senate_compositions    = {}
    self.european_delegations   = {}

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



IMPORTANCE_CHANGE_DURATION = Date(0,9,0)
MINIMAL_IMPORTANCE                     = 1.00
IMPORTANCE_POWER                       = 1.00 # Exponentiation of the total importance
IMPORTANCE_MULTIPLIER                  = 1.00 # Multiplier on the total importance
PRESIDENTIAL_IMPORTANCE_MULTIPLIER     = 0.20 # Multiplier on the presidential importance
LEGISLATIVE_IMPORTANCE_MULTIPLIER      = 0.60 # Multiplier on the legislative importance
SENATORIAL_IMPORTANCE_MULTIPLIER       = 0.10 # Multiplier on the senatorial importance
EUROPEAN_IMPORTANCE_MULTIPLIER         = 0.10 # Multiplier on the european importance
PRESIDENTIAL_IMPORTANCE_VOTES_WEIGHT   = 0.50 # Weight of the first turn votes on presidential importance
PRESIDENTIAL_IMPORTANCE_VICTORY_WEIGHT = 0.50 # Weight of the victory on the presidential importance
LEGISLATIVE_IMPORTANCE_VOTES_WEIGHT    = 0.40 # Weight of the votes in first turn on legislative importance
LEGISLATIVE_IMPORTANCE_SEATS_WEIGHT    = 0.40 # Weight of the seat representation on legislative importance
LEGISLATIVE_IMPORTANCE_MAJORITY_WEIGHT = 0.20 # Weight of the majority on legislative importance
SENATORIAL_IMPORTANCE_SEATS_WEIGHT     = 0.80 # Weight of the seat representation on senatorial importance
SENATORIAL_IMPORTANCE_MAJORITY_WEIGHT  = 0.20 # Weight of the majority on senatorial importance
EUROPEAN_IMPORTANCE_VOTES_WEIGHT       = 0.40 # Weight of the votes in first turn on european importance
EUROPEAN_IMPORTANCE_SEATS_WEIGHT       = 0.60 # Weight of the seat representation on european importance

# Prominence tier bonuses (additive before exponentiation)
IMPORTANCE_TIER_BONUS_MICRO = 1.0
IMPORTANCE_TIER_BONUS_MINOR = 2.0
IMPORTANCE_TIER_BONUS_MAJOR = 5.0



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

  def get_presidential_result(self, at_date:Date):
    data = self.presidential_results.get(at_date)
    if data is None:
      return None
    return {
      "date":            at_date,
      "vote_percentage": data.get("first_round_vote_percentage"),
      "won":             data.get("won"),
    }

  def get_legislative_result(self, at_date:Date):
    data = self.legislative_results.get(at_date)
    if data is None:
      return None
    total_seats = PoliticalSystem().get_number_legislative_seats(at_date)
    seats_won = data.get("seats_won")
    relative_representation = (seats_won / float(total_seats)) * 100.0
    return {
      "date":            at_date,
      "vote_percentage": data.get("first_round_vote_percentage"),
      "seats_won":       seats_won,
      "majority":        data.get("majority"),
      "representation":  relative_representation,
    }

  def get_senatorial_result(self, at_date:Date):
    data = self.senatorial_results.get(at_date)
    if data is None:
      return None
    total_seats = PoliticalSystem().get_number_senatorial_seats(at_date)
    seats_won = data.get("seats_won")
    relative_representation = (seats_won / float(total_seats)) * 100.0
    return {
      "date":           at_date,
      "seats_won":      seats_won,
      "majority":       data.get("majority"),
      "representation": relative_representation,
    }

  def get_european_result(self, at_date:Date):
    data = self.european_results.get(at_date)
    if data is None:
      return None
    total_seats = PoliticalSystem().get_number_european_seats(at_date)
    seats_won = data.get("seats_won")
    relative_representation = (seats_won / float(total_seats)) * 100.0
    return {
      "date":            at_date,
      "vote_percentage": data.get("vote_percentage"),
      "seats_won":       seats_won,
      "representation":  relative_representation,
    }

  def shift_political_position(
    self,
    from_date:          Date,
    to_date:            Date,
    target_position:    float
  ):
    # Record a time-bounded shift in political position (orientation).
    # Rendering code will translate these into Y shifts independently of width.
    self.political_position_shifts.append({
      "from":            from_date,
      "to":              to_date,
      "target_position": float(target_position),
    })

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
        total_days = (end_date.to_datetime() - start_date.to_datetime()).days
        elapsed_days = (at_date.to_datetime() - start_date.to_datetime()).days
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





#region[political_system]

PoliticalSystem().set_political_regime(Date(1792, 9,21), Date(1804, 5,18), "Première République")
PoliticalSystem().set_political_regime(Date(1804, 5,18), Date(1814, 4, 6), "Premier Empire")
PoliticalSystem().set_political_regime(Date(1814, 4, 6), Date(1815, 3,20), "Première Restauration")
PoliticalSystem().set_political_regime(Date(1815, 3,20), Date(1815, 7, 7), "Cent-Jours")
PoliticalSystem().set_political_regime(Date(1815, 7, 7), Date(1830, 8, 2), "Seconde Restauration")
PoliticalSystem().set_political_regime(Date(1830, 8, 9), Date(1848, 2,24), "Monarchie de Juillet")
PoliticalSystem().set_political_regime(Date(1848, 2,24), Date(1852,12, 2), "Deuxième République")
PoliticalSystem().set_political_regime(Date(1852,12, 2), Date(1870, 9, 4), "Second Empire")
PoliticalSystem().set_political_regime(Date(1870, 9, 4), Date(1940, 7,10), "Troisième République")
PoliticalSystem().set_political_regime(Date(1940, 7,10), Date(1944, 8,20), "Régime de Vichy")
PoliticalSystem().set_political_regime(Date(1946,10,27), Date(1958,10, 4), "Quatrième République")
PoliticalSystem().set_political_regime(Date(1958,10, 4), Date.today(),     "Cinquième République")

PoliticalSystem().add_presidential_election(Date(1848,12,11))
PoliticalSystem().add_presidential_election(Date(1873, 5,24))
PoliticalSystem().add_presidential_election(Date(1879, 1,30))
PoliticalSystem().add_presidential_election(Date(1885,12,28))
PoliticalSystem().add_presidential_election(Date(1887,12, 3))
PoliticalSystem().add_presidential_election(Date(1894, 6,27))
PoliticalSystem().add_presidential_election(Date(1895, 1,17))
PoliticalSystem().add_presidential_election(Date(1899, 2,18))
PoliticalSystem().add_presidential_election(Date(1906, 1,17))
PoliticalSystem().add_presidential_election(Date(1913, 1,17))
PoliticalSystem().add_presidential_election(Date(1920, 1,17))
PoliticalSystem().add_presidential_election(Date(1920, 9,23))
PoliticalSystem().add_presidential_election(Date(1924, 6,13))
PoliticalSystem().add_presidential_election(Date(1931, 5,13))
PoliticalSystem().add_presidential_election(Date(1932, 5,10))
PoliticalSystem().add_presidential_election(Date(1939, 4, 5))
PoliticalSystem().add_presidential_election(Date(1947, 1,16))
PoliticalSystem().add_presidential_election(Date(1953,12,23))
PoliticalSystem().add_presidential_election(Date(1958,12,21))
PoliticalSystem().add_presidential_election(Date(1965,12,19))
PoliticalSystem().add_presidential_election(Date(1969, 6,15))
PoliticalSystem().add_presidential_election(Date(1974, 5,19))
PoliticalSystem().add_presidential_election(Date(1981, 5,10))
PoliticalSystem().add_presidential_election(Date(1988, 5, 8))
PoliticalSystem().add_presidential_election(Date(1995, 5, 7))
PoliticalSystem().add_presidential_election(Date(2002, 5, 5))
PoliticalSystem().add_presidential_election(Date(2007, 5, 6))
PoliticalSystem().add_presidential_election(Date(2012, 5, 6))
PoliticalSystem().add_presidential_election(Date(2017, 5, 7))
PoliticalSystem().add_presidential_election(Date(2022, 4,20))

PoliticalSystem().add_legislative_election(Date(1789, 5, 5), "États Généraux",                  1139)
PoliticalSystem().add_legislative_election(Date(1791, 9,13), "Assemblée Législative",            745)
PoliticalSystem().add_legislative_election(Date(1792, 9,20), "Convention Nationale",             749)
PoliticalSystem().add_legislative_election(Date(1795,10,21), "Conseil des Cinq-Cents",           500)
PoliticalSystem().add_legislative_election(Date(1797, 4,20), "Renouvellement",                   250)
PoliticalSystem().add_legislative_election(Date(1798, 4, 9), "Renouvellement",                   250)
PoliticalSystem().add_legislative_election(Date(1799, 4, 9), "Renouvellement",                   250)
PoliticalSystem().add_legislative_election(Date(1815, 5,22), "Chambre des Représentants",        629)

PoliticalSystem().add_legislative_election(Date(1815, 8,22), "Ie Législature",                   402)
PoliticalSystem().add_legislative_election(Date(1816,10, 4), "IIe Législature",                  258)
PoliticalSystem().add_legislative_election(Date(1820,11,13), "IIIe Législature",                 430)
PoliticalSystem().add_legislative_election(Date(1824, 3, 6), "IVe Législature",                  430)
PoliticalSystem().add_legislative_election(Date(1827,11,24), "Ve Législature",                   430)

PoliticalSystem().add_legislative_election(Date(1830, 7,19), "Ie Législature",                   430)
PoliticalSystem().add_legislative_election(Date(1831, 7, 5), "IIe Législature",                  459)
PoliticalSystem().add_legislative_election(Date(1834, 6,21), "IIIe Législature",                 459)
PoliticalSystem().add_legislative_election(Date(1837,11, 4), "IVe Législature",                  459)
PoliticalSystem().add_legislative_election(Date(1839, 3, 6), "Ve Législature",                   459)
PoliticalSystem().add_legislative_election(Date(1842, 7, 9), "VIe Législature",                  459)
PoliticalSystem().add_legislative_election(Date(1846, 8, 1), "VIIe Législature",                 459)

PoliticalSystem().add_legislative_election(Date(1848, 4,24), "Assemblée Nationale Constituante", 900)
PoliticalSystem().add_legislative_election(Date(1849, 5,13), "Assemblée Nationale Législative",  750)

PoliticalSystem().add_legislative_election(Date(1852, 3, 1), "Ie Législature",                   261)
PoliticalSystem().add_legislative_election(Date(1857, 6,22), "IIe Législature",                  267)
PoliticalSystem().add_legislative_election(Date(1863, 6, 1), "IIIe Législature",                 283)
PoliticalSystem().add_legislative_election(Date(1869, 5,24), "IVe Législature",                  292)

PoliticalSystem().add_legislative_election(Date(1871, 2, 8), "Assemblée Nationale",              768)
PoliticalSystem().add_legislative_election(Date(1876, 3, 5), "Ie Législature",                   533)
PoliticalSystem().add_legislative_election(Date(1877,10,28), "IIe Législature",                  533)
PoliticalSystem().add_legislative_election(Date(1881, 9, 4), "IIIe Législature",                 557)
PoliticalSystem().add_legislative_election(Date(1885,10,18), "IVe Législature",                  584)
PoliticalSystem().add_legislative_election(Date(1889,10, 6), "Ve Législature",                   576)
PoliticalSystem().add_legislative_election(Date(1893, 9, 3), "VIe Législature",                  581)
PoliticalSystem().add_legislative_election(Date(1898, 5,22), "VIIe Législature",                 585)
PoliticalSystem().add_legislative_election(Date(1902, 5,11), "VIIIe Législature",                589)
PoliticalSystem().add_legislative_election(Date(1906, 5,20), "IXe Législature",                  588)
PoliticalSystem().add_legislative_election(Date(1910, 5, 8), "Xe Législature",                   590)
PoliticalSystem().add_legislative_election(Date(1914, 5,10), "XIe Législature",                  602)
PoliticalSystem().add_legislative_election(Date(1919,11,16), "XIIe Législature",                 613)
PoliticalSystem().add_legislative_election(Date(1924, 5,11), "XIIIe Législature",                584)
PoliticalSystem().add_legislative_election(Date(1928, 4,29), "XIVe Législature",                 612)
PoliticalSystem().add_legislative_election(Date(1932, 5, 8), "XVe Législature",                  615)
PoliticalSystem().add_legislative_election(Date(1936, 5, 3), "XVIe Législature",                 618)

PoliticalSystem().add_legislative_election(Date(1945,10,21), "Ire Assemblée constituante",       586)
PoliticalSystem().add_legislative_election(Date(1946, 6, 2), "IIe Assemblée constituante",       586)
PoliticalSystem().add_legislative_election(Date(1946,11,10), "Ire Législature",                  627)
PoliticalSystem().add_legislative_election(Date(1951, 6,17), "IIe Législature",                  627)
PoliticalSystem().add_legislative_election(Date(1956, 1, 2), "IIIe Législature",                 626)

PoliticalSystem().add_legislative_election(Date(1958,11,30), "Ie Législature",                   579)
PoliticalSystem().add_legislative_election(Date(1962,11,25), "IIe Législature",                  482)
PoliticalSystem().add_legislative_election(Date(1967, 3,12), "IIIe Législature",                 487)
PoliticalSystem().add_legislative_election(Date(1968, 6,30), "IVe Législature",                  487)
PoliticalSystem().add_legislative_election(Date(1973, 3,11), "Ve Législature",                   490)
PoliticalSystem().add_legislative_election(Date(1978, 3,19), "VIe Législature",                  491)
PoliticalSystem().add_legislative_election(Date(1981, 6,21), "VIIe Législature",                 491)
PoliticalSystem().add_legislative_election(Date(1986, 3,16), "VIIIe Législature",                577, True)
PoliticalSystem().add_legislative_election(Date(1988, 6,12), "IXe Législature",                  577)
PoliticalSystem().add_legislative_election(Date(1993, 3,28), "Xe Législature",                   577)
PoliticalSystem().add_legislative_election(Date(1997, 6, 1), "XIe Législature",                  577)
PoliticalSystem().add_legislative_election(Date(2002, 6,16), "XIIe Législature",                 577)
PoliticalSystem().add_legislative_election(Date(2007, 6,17), "XIIIe Législature",                577)
PoliticalSystem().add_legislative_election(Date(2012, 6,17), "XIVe Législature",                 577)
PoliticalSystem().add_legislative_election(Date(2017, 6,18), "XVe Législature",                  577)
PoliticalSystem().add_legislative_election(Date(2022, 6,19), "XVIe Législature",                 577)
PoliticalSystem().add_legislative_election(Date(2024, 7, 7), "XVIIe Législature",                577)

PoliticalSystem().add_senatorial_election(Date(1876, 1,30), 300)
PoliticalSystem().add_senatorial_election(Date(1879, 1, 5), 300)
PoliticalSystem().add_senatorial_election(Date(1882, 1, 8), 300)
PoliticalSystem().add_senatorial_election(Date(1885, 1,25), 300)
PoliticalSystem().add_senatorial_election(Date(1888, 1, 5), 300)
PoliticalSystem().add_senatorial_election(Date(1891, 1, 4), 300)
PoliticalSystem().add_senatorial_election(Date(1894, 1, 7), 300)
PoliticalSystem().add_senatorial_election(Date(1897, 1, 3), 300)
PoliticalSystem().add_senatorial_election(Date(1900, 1,28), 300)
PoliticalSystem().add_senatorial_election(Date(1903, 1, 4), 300)
PoliticalSystem().add_senatorial_election(Date(1906, 1, 7), 300)
PoliticalSystem().add_senatorial_election(Date(1909, 1, 3), 300)
PoliticalSystem().add_senatorial_election(Date(1912, 1, 7), 300)
PoliticalSystem().add_senatorial_election(Date(1920, 1,11), 314)
PoliticalSystem().add_senatorial_election(Date(1921, 1, 9), 314)
PoliticalSystem().add_senatorial_election(Date(1924, 1, 6), 314)
PoliticalSystem().add_senatorial_election(Date(1927, 1, 9), 314)
PoliticalSystem().add_senatorial_election(Date(1929,10,20), 314)
PoliticalSystem().add_senatorial_election(Date(1932,10,16), 314)
PoliticalSystem().add_senatorial_election(Date(1935,10,20), 314)
PoliticalSystem().add_senatorial_election(Date(1938,10,23), 314)

PoliticalSystem().add_senatorial_election(Date(1946,12, 8), 315)
PoliticalSystem().add_senatorial_election(Date(1948,11, 7), 320)
PoliticalSystem().add_senatorial_election(Date(1952, 5,18), 320)
PoliticalSystem().add_senatorial_election(Date(1955, 6,19), 320)
PoliticalSystem().add_senatorial_election(Date(1958, 6, 8), 320)

PoliticalSystem().add_senatorial_election(Date(1959, 4,26), 309)
PoliticalSystem().add_senatorial_election(Date(1962, 9,23), 283)
PoliticalSystem().add_senatorial_election(Date(1965, 9,26), 283)
PoliticalSystem().add_senatorial_election(Date(1968, 9,22), 283)
PoliticalSystem().add_senatorial_election(Date(1971, 9,26), 283)
PoliticalSystem().add_senatorial_election(Date(1974, 9,22), 283)
PoliticalSystem().add_senatorial_election(Date(1977, 9,25), 304)
PoliticalSystem().add_senatorial_election(Date(1980, 9,28), 316)
PoliticalSystem().add_senatorial_election(Date(1983, 9,25), 317)
PoliticalSystem().add_senatorial_election(Date(1986, 9,28), 321)
PoliticalSystem().add_senatorial_election(Date(1989, 9,24), 321)
PoliticalSystem().add_senatorial_election(Date(1992, 9,27), 321)
PoliticalSystem().add_senatorial_election(Date(1995, 9,24), 321)
PoliticalSystem().add_senatorial_election(Date(1998, 9,27), 321)
PoliticalSystem().add_senatorial_election(Date(2001, 9,23), 321)
PoliticalSystem().add_senatorial_election(Date(2004, 9,26), 331)
PoliticalSystem().add_senatorial_election(Date(2008, 9,21), 343)
PoliticalSystem().add_senatorial_election(Date(2011, 9,25), 348)
PoliticalSystem().add_senatorial_election(Date(2014, 9,28), 348)
PoliticalSystem().add_senatorial_election(Date(2017, 9,24), 348)
PoliticalSystem().add_senatorial_election(Date(2020, 9,27), 348)
PoliticalSystem().add_senatorial_election(Date(2023, 9,24), 348)

PoliticalSystem().add_european_election(Date(1979,6,10), 81)
PoliticalSystem().add_european_election(Date(1984,6,17), 81)
PoliticalSystem().add_european_election(Date(1989,6,18), 81)
PoliticalSystem().add_european_election(Date(1994,6,12), 87)
PoliticalSystem().add_european_election(Date(1999,6,13), 87)
PoliticalSystem().add_european_election(Date(2004,6,13), 74)
PoliticalSystem().add_european_election(Date(2009,6, 7), 74)
PoliticalSystem().add_european_election(Date(2014,5,25), 74)
PoliticalSystem().add_european_election(Date(2019,5,26), 79)
PoliticalSystem().add_european_election(Date(2024,6, 9), 81)

#endregion




extreme_gauche_offset = +0.5
gauche_offset         = +0.3
centre_offset         = +0.1
droite_offset         =  0.0
extreme_droite_offset = +0.1





#region[anarchisme]
#endregion







#region[trotskisme]

lutte_ouvriere = PoliticalParty(
  symbol        = "LO",
  color         = "#770000",
  creation_date = Date(1956,11,26),
  initial_name  = "Voix Ouvrière",
  initial_prominence_tier    = "minor",
  initial_political_position = +2.30+extreme_gauche_offset,
)

lutte_ouvriere.set_results_presidential_election(Date(1974), 2.33)
lutte_ouvriere.set_results_presidential_election(Date(1981), 2.30)
lutte_ouvriere.set_results_presidential_election(Date(1988), 1.99)
lutte_ouvriere.set_results_presidential_election(Date(1995), 5.30)
lutte_ouvriere.set_results_presidential_election(Date(2002), 5.72)
lutte_ouvriere.set_results_presidential_election(Date(2007), 1.33)
lutte_ouvriere.set_results_presidential_election(Date(2012), 0.56)
lutte_ouvriere.set_results_presidential_election(Date(2017), 0.64)
lutte_ouvriere.set_results_presidential_election(Date(2022), 0.56)

lutte_ouvriere.set_results_legislative_election(Date(1973), 2.29)
lutte_ouvriere.set_results_legislative_election(Date(1978), 1.70)
lutte_ouvriere.set_results_legislative_election(Date(1981), 1.11)
lutte_ouvriere.set_results_legislative_election(Date(1986), 0.63)
lutte_ouvriere.set_results_legislative_election(Date(1993), 2.15)
lutte_ouvriere.set_results_legislative_election(Date(1997), 3.86)
lutte_ouvriere.set_results_legislative_election(Date(2002), 1.20)
lutte_ouvriere.set_results_legislative_election(Date(2007), 0.86)
lutte_ouvriere.set_results_legislative_election(Date(2012), 0.51)
lutte_ouvriere.set_results_legislative_election(Date(2017), 0.72)
lutte_ouvriere.set_results_legislative_election(Date(2022), 1.01)
lutte_ouvriere.set_results_legislative_election(Date(2024), 1.09)

lutte_ouvriere.set_results_european_election(Date(1979), 3.08, 0)
lutte_ouvriere.set_results_european_election(Date(1984), 2.07, 0)
lutte_ouvriere.set_results_european_election(Date(1989), 1.43, 0)
lutte_ouvriere.set_results_european_election(Date(1994), 2.27, 0)
lutte_ouvriere.set_results_european_election(Date(1999), 5.18, 3)
lutte_ouvriere.set_results_european_election(Date(2004), 2.60, 0)
lutte_ouvriere.set_results_european_election(Date(2009), 1.20, 0)
lutte_ouvriere.set_results_european_election(Date(2014), 1.17, 0)
lutte_ouvriere.set_results_european_election(Date(2019), 0.78, 0)
lutte_ouvriere.set_results_european_election(Date(2024), 0.49, 0)

#endregion







#region[communisme]


federation_des_travailleurs_socialistes_de_france = PoliticalParty(
  symbol        = "FTSF",
  color         = "#FF0000",
  creation_date = Date(1879,4,30),
  initial_name  = "Fédération du Parti des Travailleurs Socialistes de France",
  initial_prominence_tier    = "major",
  initial_political_position = +1.20+gauche_offset,
)
federation_des_travailleurs_socialistes_de_france.name_change(Date(1883,10,7), "Fédération des Travailleurs Socialistes de France")

federation_des_groupes_socialistes_revolutionnaires_independants = PoliticalParty(
  symbol        = "FGSRI",
  color         = "#FF0000",
  creation_date = Date(1898,12,4),
  initial_name  = "Fédération des Groupes Socialistes Révolutionnaires Indépendants",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.85+gauche_offset,
)
federation_des_socialistes_revolutionnaires_independants_de_france = PoliticalParty(
  symbol        = "FSRI",
  color         = "#FF0000",
  creation_date = Date(1899,1,1),
  initial_name  = "Fédération des Socialistes Indépendants de France",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.75+gauche_offset,
)
federation_des_socialistes_revolutionnaires_independants_de_france.name_change(Date(1900,3,27), "Fédération des Socialistes Révolutionnaires Indépendants de France")

federation_socialiste_revolutionnaire_de_france = PoliticalParty(
  symbol        = "FSR",
  color         = "#FF0000",
  creation_date = Date(1901,8,5),
  initial_name  = "Fédération Socialiste Révolutionnaire de France",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.80+gauche_offset,
  merge_from = [
    federation_des_socialistes_revolutionnaires_independants_de_france,
    federation_des_groupes_socialistes_revolutionnaires_independants,
  ],
)

parti_socialiste_francais = PoliticalParty(
  symbol        = "PSF",
  color         = "#FF0000",
  creation_date = Date(1902,3,4),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "major",
  initial_political_position = +1.00+gauche_offset,
  merge_from = [
    federation_socialiste_revolutionnaire_de_france,
    federation_des_travailleurs_socialistes_de_france,
  ],
)


parti_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "PSR",
  color         = "#FF0000",
  creation_date = Date(1881,6,26),
  initial_name  = "Comité Révolutionnaire Central",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.70+gauche_offset,
)
parti_socialiste_revolutionnaire.name_change(Date(1898,7,1), "Parti Socialiste Révolutionnaire")

comite_central_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "CCSR",
  color         = "#FF0000",
  creation_date = Date(1889,8,20),
  initial_name  = "Comité Central Socialiste Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.00+gauche_offset, # boulangistes, rejoint le nationalisme
  secede_from = {
    parti_socialiste_revolutionnaire: {
      "ratio": 0,
    }
  }
)
comite_central_socialiste_revolutionnaire.dissolve(Date(1896,12))

parti_ouvrier_francais = PoliticalParty(
  symbol        = "POF",
  color         = "#FF0000",
  creation_date = Date(1882,9,30),
  initial_name  = "Parti Ouvrier",
  initial_prominence_tier    = "major",
  initial_political_position = +1.60+gauche_offset,
  secede_from = {
    federation_des_travailleurs_socialistes_de_france: {
      "ratio": 0,
      "source_new_position": +0.60+gauche_offset
    }
  }
)
parti_ouvrier_francais.name_change(Date(1893,9,19), "Parti Ouvrier Français")

parti_socialiste_de_france = PoliticalParty(
  symbol        = "PSdF",
  color         = "#FF0000",
  creation_date = Date(1901,6,30),
  initial_name  = "Unité Socialiste Révolutionnaire",
  initial_prominence_tier    = "major",
  initial_political_position = +1.65+gauche_offset,
  merge_from = [
    parti_socialiste_revolutionnaire,
    parti_ouvrier_francais,
  ],
)
parti_socialiste_de_france.name_change(Date(1901,11,3), "Parti Socialiste de France")



parti_ouvrier_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "POSR",
  color         = "#FF0000",
  creation_date = Date(1890,10,15),
  initial_name  = "Parti Ouvrier Socialiste Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.45+gauche_offset,
  secede_from = {
    federation_des_travailleurs_socialistes_de_france: {
      "ratio": 0,
    }
  }
)

alliance_communiste_revolutionnaire = PoliticalParty(
  symbol        = "ACR",
  color         = "#FF0000",
  creation_date = Date(1896,9,25),
  initial_name  = "Alliance Communiste Révolutionnaire",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.52+gauche_offset,
  secede_from = {
    parti_ouvrier_socialiste_revolutionnaire: {
      "ratio": 0,
    }
  }
)
alliance_communiste_revolutionnaire.merge_into(Date(1897,9), parti_socialiste_revolutionnaire, 0)



section_francaise_de_linternationale_ouvriere = PoliticalParty(
  symbol        = "SFIO",
  color         = "#FF0000",
  creation_date = Date(1905,4,25),
  initial_name  = "Section Française de 'Internationale Ouvrière",
  initial_prominence_tier    = "major",
  initial_political_position = +1.40+gauche_offset,
  merge_from = [
    parti_socialiste_de_france,
    parti_socialiste_francais,
    parti_ouvrier_socialiste_revolutionnaire,
  ],
)

section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1906),   7.26)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1920,9), 8.78)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1932),  14.67)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1939),  16.70)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1947),  51.19, True)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1953),  37.77)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1969),   5.01)

section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1906),    10.0,  54)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1910),    12.9,  75)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1914),    16.8, 102)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1919),    21.2,  68)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1924),    20.1, 104, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1928),    18.0, 100)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1932),    20.5, 132)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1936),    19.2, 149, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1945),    23.4, 134, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1946,6),  21.1, 128, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1946,11), 17.9, 102, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1951),    14.5, 107, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1956),    14.9,  95, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1958),    17.2,  47)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1962),    12.4,  66)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1967),    18.8,  76)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1968),    16.5,  40)

section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1959), 61)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1952), 52)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1965), 52)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1968), 52)


parti_ouvrier_1914 = PoliticalParty(
  symbol        = "PO-1914",
  color         = "#FF0000",
  creation_date = Date(1914,1,28),
  initial_name  = "Parti Ouvrier",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.50+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0,
    }
  }
)
parti_ouvrier_1914.merge_into(Date(1917,11), section_francaise_de_linternationale_ouvriere, 0)


parti_republicain_socialiste_1907 = PoliticalParty(
  symbol        = "PRS-1907",
  color         = "#FF0000",
  creation_date = Date(1907,3,31),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.40+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.3
    }
  },
)
parti_republicain_socialiste_1907.name_change(Date(1910,10,8), "Parti Républicain Socialiste")
parti_republicain_socialiste_1907.name_change(Date(1914,2,8),  "Parti Républicain Socialiste (briandiste)")
parti_republicain_socialiste_1914 = PoliticalParty(
  symbol        = "PRS-1914",
  color         = "#FF0000",
  creation_date = Date(1914,2,8),
  initial_name  = "Parti Républicain Socialiste (augagneuriste)",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    parti_republicain_socialiste_1907: {
      "ratio": 0.3
    }
  },
)
parti_republicain_socialiste_1907.dissolve(Date(1915))
parti_republicain_socialiste_1914.dissolve(Date(1915))
parti_socialiste_national = PoliticalParty(
  symbol        = "PSN",
  color         = "#FF0000",
  creation_date = Date(1917,12,23),
  initial_name  = "Parti Socialiste National",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.10+gauche_offset,
)
parti_socialiste_national.dissolve(Date(1921))
parti_republicain_socialiste_1923 = PoliticalParty(
  symbol        = "PRS-1923",
  color         = "#FF0000",
  creation_date = Date(1923,4,15),
  initial_name  = "Parti Républicain Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.40+gauche_offset,
)

parti_republicain_socialiste_1928 = PoliticalParty(
  symbol        = "PRS-1928",
  color         = "#FF0000",
  creation_date = Date(1928,5,20),
  initial_name  = "Parti Républicain Socialiste",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.40+gauche_offset,
)

parti_socialiste_francais_1920 = PoliticalParty(
  symbol        = "PSF-1920",
  color         = "#FF0000",
  creation_date = Date(1920,3,13),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.60+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  },
)
parti_socialiste_francais_1929 = PoliticalParty(
  symbol        = "PSF-1929",
  color         = "#FF0000",
  creation_date = Date(1926,5,30),
  initial_name  = "Parti Républicain Socialiste et Socialiste Français",
  initial_prominence_tier    = "major",
  initial_political_position = +0.50+gauche_offset,
  merge_from = [
    parti_socialiste_francais_1920,
    parti_republicain_socialiste_1923,
  ],
)
parti_socialiste_francais_1929.name_change(Date(1929,12,8), "Parti Socialiste Français")

parti_socialiste_de_france_union_jean_jaures = PoliticalParty(
  symbol        = "PSdF-UJJ",
  color         = "#FF0000",
  creation_date = Date(1933,11,5),
  initial_name  = "Parti Socialiste de France - Union Jean Jaurès",
  initial_prominence_tier    = "major",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.4
    }
  },
)

union_socialiste_républicaine = PoliticalParty(
  symbol        = "USR",
  color         = "#FF0000",
  creation_date = Date(1935,11,3),
  initial_name  = "Union Socialiste Républicaine",
  initial_prominence_tier    = "major",
  initial_political_position = +0.40+gauche_offset,
  merge_from = [
    parti_socialiste_francais_1929,
    parti_republicain_socialiste_1928,
    parti_socialiste_de_france_union_jean_jaures,
  ],
)
union_socialiste_républicaine.dissolve(Date(1940,7,10)) # Dissolution pendant la guerre





parti_communiste_francais = PoliticalParty(
  symbol        = "PCF",
  color         = "#FF0000",
  creation_date = Date(1920,12,30),
  initial_name  = "Section Française de l'Internationale Communiste",
  initial_prominence_tier    = "major",
  initial_political_position = +1.8+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.2,
      "source_new_position": +1.00+gauche_offset
    }
  },
)

parti_communiste_francais.set_results_presidential_election(Date(1924),  2.5)
parti_communiste_francais.set_results_presidential_election(Date(1931),  1.1)
parti_communiste_francais.set_results_presidential_election(Date(1932),  1.0)
parti_communiste_francais.set_results_presidential_election(Date(1939),  8.2)
parti_communiste_francais.set_results_presidential_election(Date(1953), 12.2)
parti_communiste_francais.set_results_presidential_election(Date(1958), 13.03)
parti_communiste_francais.set_results_presidential_election(Date(1969), 21.27)
parti_communiste_francais.set_results_presidential_election(Date(1981), 15.35)
parti_communiste_francais.set_results_presidential_election(Date(1988),  6.76)
parti_communiste_francais.set_results_presidential_election(Date(1995),  8.64)
parti_communiste_francais.set_results_presidential_election(Date(2002),  3.37)
parti_communiste_francais.set_results_presidential_election(Date(2007),  1.93)
parti_communiste_francais.set_results_presidential_election(Date(2012), 11.10) # Jean-Luc Mélanchon
parti_communiste_francais.set_results_presidential_election(Date(2022),  2.28)

parti_communiste_francais.set_results_legislative_election(Date(1924),     9.82,  26)
parti_communiste_francais.set_results_legislative_election(Date(1928),    11.26,  12)
parti_communiste_francais.set_results_legislative_election(Date(1932),     8.32,  23)
parti_communiste_francais.set_results_legislative_election(Date(1936),    15.23,  72, True)
parti_communiste_francais.set_results_legislative_election(Date(1945),    26.23, 159, True)
parti_communiste_francais.set_results_legislative_election(Date(1946,6),  25.98, 153, True)
parti_communiste_francais.set_results_legislative_election(Date(1946,11), 28.26, 182, True)
parti_communiste_francais.set_results_legislative_election(Date(1951),    25.90, 103)
parti_communiste_francais.set_results_legislative_election(Date(1956),    25.36, 150)
parti_communiste_francais.set_results_legislative_election(Date(1958),    18.90,  10)
parti_communiste_francais.set_results_legislative_election(Date(1962),    21.84,  41)
parti_communiste_francais.set_results_legislative_election(Date(1967),    22.51,  73)
parti_communiste_francais.set_results_legislative_election(Date(1968),    20.02,  34)
parti_communiste_francais.set_results_legislative_election(Date(1973),    21.41,  73)
parti_communiste_francais.set_results_legislative_election(Date(1978),    20.61,  86)
parti_communiste_francais.set_results_legislative_election(Date(1981),    16.17,  44, True)
parti_communiste_francais.set_results_legislative_election(Date(1986),     9.78,  35)
parti_communiste_francais.set_results_legislative_election(Date(1988),    11.32,  27, True)
parti_communiste_francais.set_results_legislative_election(Date(1993),     9.30,  24)
parti_communiste_francais.set_results_legislative_election(Date(1997),     9.92,  35, True)
parti_communiste_francais.set_results_legislative_election(Date(2002),     4.82,  21)
parti_communiste_francais.set_results_legislative_election(Date(2007),     4.29,  15)
parti_communiste_francais.set_results_legislative_election(Date(2012),     6.91,   7)
parti_communiste_francais.set_results_legislative_election(Date(2017),     2.72,  11)
parti_communiste_francais.set_results_legislative_election(Date(2022),     2.29,  12)
parti_communiste_francais.set_results_legislative_election(Date(2024),     2.35,   8)

parti_communiste_francais.set_results_senatorial_election(Date(1995), 14)
parti_communiste_francais.set_results_senatorial_election(Date(1998), 14)
parti_communiste_francais.set_results_senatorial_election(Date(2001), 18)
parti_communiste_francais.set_results_senatorial_election(Date(2004), 20)
parti_communiste_francais.set_results_senatorial_election(Date(2008), 21)
parti_communiste_francais.set_results_senatorial_election(Date(2011), 19)
parti_communiste_francais.set_results_senatorial_election(Date(2014), 16)
parti_communiste_francais.set_results_senatorial_election(Date(2017), 12)
parti_communiste_francais.set_results_senatorial_election(Date(2020), 14)
parti_communiste_francais.set_results_senatorial_election(Date(2023), 14)

parti_communiste_francais.set_results_european_election(Date(1979), 20.52, 19)
parti_communiste_francais.set_results_european_election(Date(1984), 11.21, 10)
parti_communiste_francais.set_results_european_election(Date(1989),  7.72,  7)
parti_communiste_francais.set_results_european_election(Date(1994),  6.89,  7)
parti_communiste_francais.set_results_european_election(Date(1999),  6.78,  6)
parti_communiste_francais.set_results_european_election(Date(2004),  5.88,  2)
parti_communiste_francais.set_results_european_election(Date(2009),  6.48,  2) # Front de Gauche
parti_communiste_francais.set_results_european_election(Date(2014),  6.61,  1) # Front de Gauche
parti_communiste_francais.set_results_european_election(Date(2019),  2.49,  0)
parti_communiste_francais.set_results_european_election(Date(2024),  2.36,  0)




union_federative_socialiste = PoliticalParty(
  symbol        = "UFS",
  color         = "#FF0000",
  creation_date = Date(1922,10,19),
  initial_name  = "Union Fédérative Socialiste",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.40+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_communiste_unitaire = PoliticalParty(
  symbol        = "PCU",
  color         = "#FF0000",
  creation_date = Date(1923,1,3),
  initial_name  = "Comité de Défense Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.40+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_communiste_unitaire.name_change(Date(1923,1,10), "Comité d'Unité Communiste")
parti_communiste_unitaire.name_change(Date(1923,1,17), "Parti Communiste Unitaire")
parti_socialiste_communiste = PoliticalParty(
  symbol        = "PSC",
  color         = "#FF0000",
  creation_date = Date(1923,4,30),
  initial_name  = "Parti Socialiste Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.40+gauche_offset,
  merge_from = [
    union_federative_socialiste,
    parti_communiste_unitaire,
  ],
)
parti_socialiste_communiste.secede_into(Date(1927,10), section_francaise_de_linternationale_ouvriere, 0, visual_width=2)
parti_ouvrier_et_paysan = PoliticalParty(
  symbol        = "POP",
  color         = "#FF0000",
  creation_date = Date(1929,11,24),
  initial_name  = "Parti Ouvrier et Paysan",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.50+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_de_lunite_proletarienne = PoliticalParty(
  symbol        = "PUP",
  color         = "#FF0000",
  creation_date = Date(1930,12,21),
  initial_name  = "Parti de l'Unité Prolétarienne",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.45+gauche_offset,
  merge_from = [
    parti_socialiste_communiste,
    parti_ouvrier_et_paysan,
  ],
)
parti_de_lunite_proletarienne.shift_political_position(Date(1934), Date(1936), +1.30+gauche_offset) # Front Populaire
parti_de_lunite_proletarienne.merge_into(Date(1937,1,31), section_francaise_de_linternationale_ouvriere, 0)



parti_socialiste_ouvrier_et_paysan = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Socialiste_Ouvrier_et_Paysan_(PSOP)
  symbol        = "PSOP",
  color         = "#FF0000",
  creation_date = Date(1938,6,8),
  initial_name  = "Parti Socialiste Ouvrier et Paysan",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.20+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  }
)
parti_socialiste_ouvrier_et_paysan.dissolve(Date(1940))

groupe_bolchevik_leniniste = PoliticalParty(
  # https://www.france-politique.fr/wiki/Groupe_Bolchevik-L%C3%A9niniste_(GBL)
  symbol        = "GBL",
  color         = "#770000",
  creation_date = Date(1930,12,21),
  initial_name  = "Ligue Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  }
)
groupe_bolchevik_leniniste.name_change(Date(1934,8,24), "Groupe Bolchevik-Léniniste")
jeunesses_socialistes_revolutionnaires = PoliticalParty(
  # https://www.france-politique.fr/wiki/Jeunesses_Socialistes_R%C3%A9volutionnaires_(JSR)
  symbol        = "JSR",
  color         = "#770000",
  creation_date = Date(1935,7,30),
  initial_name  = "Jeunesses Socialistes Révolutionnaires",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  }
)
parti_ouvrier_revolutionnaire = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Ouvrier_R%C3%A9volutionnaire_(POR)
  symbol        = "POR",
  color         = "#770000",
  creation_date = Date(1936,4,12),
  initial_name  = "Parti de l'Unité Prolétarienne",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  merge_from = [
    groupe_bolchevik_leniniste,
    jeunesses_socialistes_revolutionnaires,
  ],
)
# parti_communiste_internationaliste_1936 = PoliticalParty(
#   # https://www.france-politique.fr/wiki/Comit%C3%A9_Communiste_Internationaliste_pour_la_Construction_de_la_Quatri%C3%A8me_Internationale_(CCI)
#   symbol        = "PCI-1936",
#   color         = "#770000",
#   creation_date = Date(1936,1,16),
#   initial_name  = "Comité pour la Quatrième Internationale",
#   initial_prominence_tier    = "minor",
#   initial_political_position = +2.05+extreme_gauche_offset,
#   secede_from = {
#     section_francaise_de_linternationale_ouvriere: {
#       "ratio": 0
#     }
#   }
# )
# parti_communiste_internationaliste_1936.name_change(Date(1936,3,8), "Parti Communiste Internationaliste")
parti_ouvrier_internationaliste = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Ouvrier_Internationaliste_(POI)_1936
  symbol        = "POI",
  color         = "#770000",
  creation_date = Date(1936,6,2),
  initial_name  = "Parti Ouvrier Internationaliste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  # merge_from = [
  #   parti_ouvrier_revolutionnaire,
  #   parti_communiste_internationaliste_1936,
  # ],
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      # This is the PCI-1936
      "ratio": 0
    }
  }
)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale = PoliticalParty(
  # https://www.france-politique.fr/wiki/Comit%C3%A9_Communiste_Internationaliste_pour_la_Construction_de_la_Quatri%C3%A8me_Internationale_(CCI)
  symbol        = "CCI",
  color         = "#770000",
  creation_date = Date(1936,10,12),
  initial_name  = "Parti Communiste Internationaliste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  # secede_from = {
  #   parti_ouvrier_internationaliste: {
  #     "ratio": 0
  #   }
  # }
)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale.shift_political_position(Date(1936,10,12), Date(1936,10,12)+160, +1.95+extreme_gauche_offset)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale.name_change(Date(1943,4,1), "Comité Communiste Internationaliste pour la Construction de la Quatrième Internationale")
groupe_octobre = PoliticalParty(
  # https://www.france-politique.fr/wiki/Octobre
  symbol        = "GO",
  color         = "#770000",
  creation_date = Date(1942),
  initial_name  = "Groupe Octobre",
  initial_prominence_tier    = "micro",
  initial_political_position = +2.05+extreme_gauche_offset,
  secede_from = {
    comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale: {
      "ratio": 0
    }
  }
)
parti_communiste_internationaliste_1944 = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Communiste_Internationaliste_(PCI)_1944
  symbol        = "PCI-1944",
  color         = "#770000",
  creation_date = Date(1944,3),
  initial_name  = "Comité pour la Quatrième Internationale",
  initial_prominence_tier    = "minor",
  initial_political_position = +2.10+extreme_gauche_offset,
  merge_from = [
    parti_ouvrier_internationaliste,
    comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale,
    groupe_octobre,
  ],
)

#endregion







#region[socialisme]

union_des_clubs_pour_le_renouveau_de_la_gauche = PoliticalParty(
  symbol        = "UCRG",
  color         = "#FF0000",
  creation_date = Date(1966,2),
  initial_name  = "Union des Clubs pour le Renouveau de la Gauche",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.45+gauche_offset,
)

union_des_groupes_et_clubs_socialistes = PoliticalParty(
  symbol        = "UGCS",
  color         = "#FF0000",
  creation_date = Date(1967),
  initial_name  = "Union des Groupes et Clubs Socialistes",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.40+gauche_offset,
)

parti_socialiste = PoliticalParty(
  symbol        = "PS",
  color         = "#E3265B",
  creation_date = Date(1969,8,4),
  initial_name  = "Parti Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.80+gauche_offset,
  merge_from = [
    section_francaise_de_linternationale_ouvriere,
    union_des_clubs_pour_le_renouveau_de_la_gauche,
    union_des_groupes_et_clubs_socialistes,
  ],
)

convention_des_institutions_republicaines = PoliticalParty(
  symbol        = "CIR",
  color         = "#FF0000",
  creation_date = Date(1964,6,11),
  initial_name  = "Convention des Institutions Républicaines",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.30+gauche_offset,
)
convention_des_institutions_republicaines.merge_into(Date(1971,6,13), parti_socialiste, 0)

parti_socialiste.set_results_presidential_election(Date(1969),  5.01)
parti_socialiste.set_results_presidential_election(Date(1974), 43.25)
parti_socialiste.set_results_presidential_election(Date(1981), 25.85, True)
parti_socialiste.set_results_presidential_election(Date(1988), 34.10, True)
parti_socialiste.set_results_presidential_election(Date(1995), 23.30)
parti_socialiste.set_results_presidential_election(Date(2002), 16.18)
parti_socialiste.set_results_presidential_election(Date(2007), 25.87)
parti_socialiste.set_results_presidential_election(Date(2012), 28.63, True)
parti_socialiste.set_results_presidential_election(Date(2017),  6.36)
parti_socialiste.set_results_presidential_election(Date(2022),  1.75)

parti_socialiste.set_results_legislative_election(Date(1973), 18.9,   89)
parti_socialiste.set_results_legislative_election(Date(1978), 22.8,  104)
parti_socialiste.set_results_legislative_election(Date(1981), 36.0,  267, True)
parti_socialiste.set_results_legislative_election(Date(1986), 31.0,  203)
parti_socialiste.set_results_legislative_election(Date(1988), 34.8,  275, True)
parti_socialiste.set_results_legislative_election(Date(1993), 17.6,   59)
parti_socialiste.set_results_legislative_election(Date(1997), 23.53, 255, True)
parti_socialiste.set_results_legislative_election(Date(2002), 24.11, 140)
parti_socialiste.set_results_legislative_election(Date(2007), 24.73, 186)
parti_socialiste.set_results_legislative_election(Date(2012), 29.35, 280, True)
parti_socialiste.set_results_legislative_election(Date(2017),  7.44,  30)
parti_socialiste.set_results_legislative_election(Date(2022),  3.86,  28)
parti_socialiste.set_results_legislative_election(Date(2024),  8.65,  65)

parti_socialiste.set_results_senatorial_election(Date(1971),  49)
parti_socialiste.set_results_senatorial_election(Date(1974),  51)
parti_socialiste.set_results_senatorial_election(Date(1977),  62)
parti_socialiste.set_results_senatorial_election(Date(1980),  69)
parti_socialiste.set_results_senatorial_election(Date(1983),  70)
parti_socialiste.set_results_senatorial_election(Date(1986),  64)
parti_socialiste.set_results_senatorial_election(Date(1989),  66)
parti_socialiste.set_results_senatorial_election(Date(1992),  70)
parti_socialiste.set_results_senatorial_election(Date(1995),  75)
parti_socialiste.set_results_senatorial_election(Date(1998),  78)
parti_socialiste.set_results_senatorial_election(Date(2001),  83)
parti_socialiste.set_results_senatorial_election(Date(2004),  97)
parti_socialiste.set_results_senatorial_election(Date(2008), 116)
parti_socialiste.set_results_senatorial_election(Date(2011), 140, True)
parti_socialiste.set_results_senatorial_election(Date(2014), 111)
parti_socialiste.set_results_senatorial_election(Date(2017),  78)
parti_socialiste.set_results_senatorial_election(Date(2020),  64)
parti_socialiste.set_results_senatorial_election(Date(2023),  64)

parti_socialiste.set_results_european_election(Date(1979), 23.53, 20)
parti_socialiste.set_results_european_election(Date(1984), 20.75, 20)
parti_socialiste.set_results_european_election(Date(1989), 23.61, 17)
parti_socialiste.set_results_european_election(Date(1994), 14.49, 15)
parti_socialiste.set_results_european_election(Date(1999), 21.95, 18)
parti_socialiste.set_results_european_election(Date(2004), 28.90, 31)
parti_socialiste.set_results_european_election(Date(2009), 16.48, 14)
parti_socialiste.set_results_european_election(Date(2014), 13.98, 12)
parti_socialiste.set_results_european_election(Date(2019),  6.19,  3)
parti_socialiste.set_results_european_election(Date(2024), 13.83, 10)

# section_francaise_de_linternationale_ouvriere                        Date(1905,4,25)         +1.40+gauche_offset  # Création
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1914), Date(1915), +1.10+gauche_offset) # L'Union Sacrée et gouvernement, nationalisme pour la guerre
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1918), Date(1920), +1.40+gauche_offset) # Fin de la guerre et de l'Union Sacrée
# section_francaise_de_linternationale_ouvriere                        Date(1920,12,30)        +1.00+gauche_offset  # Scission de la SFIC/PCF, le reste est social-démocratie réformiste
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1934), Date(1936), +0.90+gauche_offset) # Front Populaire, modération stratégique
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1944), Date(1945), +0.80+gauche_offset) # Libération, refondation

# parti_communiste_francais                        Date(1920,12,30)        +1.80+gauche_offset  # Scission depuis la SFIO
parti_communiste_francais.shift_political_position(Date(1934), Date(1936), +1.60+gauche_offset) # Front Populaire, soutien sans participation
parti_communiste_francais.shift_political_position(Date(1939), Date(1941), +1.80+gauche_offset) # Pacte germano-soviétique, fin du Front Populaire
parti_communiste_francais.shift_political_position(Date(1970), Date(1972), +1.60+gauche_offset) # Négociation du Programme Commun, Eurocommunisme
parti_communiste_francais.shift_political_position(Date(1981), Date(1984), +1.50+gauche_offset) # Participation au gouvernement Mauroy, sortie avec le tournant de la rigueur
parti_communiste_francais.shift_political_position(Date(1991), Date(1997), +1.00+gauche_offset) # Chute de l'URSS jusqu'à la Gauche Plurielle, abandon Léninisme, changement symboles
parti_communiste_francais.shift_political_position(Date(2015), Date(2018), +0.80+gauche_offset) # Fin du Front de Gauche, Rousselisation jusqu'à la NUPES

# parti_socialiste                        Date(1969,8,4)              +0.80+gauche_offset  # Création
parti_socialiste.shift_political_position(Date(1969,8,4), Date(1972), +0.90+gauche_offset) # De Épinay au Programme Commun
parti_socialiste.shift_political_position(Date(1983),     Date(1984), +0.40+gauche_offset) # Tournant de la rigueur
parti_socialiste.shift_political_position(Date(1995),     Date(1997), +0.20+gauche_offset) # Troisième voie
parti_socialiste.shift_political_position(Date(2013),     Date(2015),  0.00+gauche_offset) # Virage social libéral
parti_socialiste.shift_political_position(Date(2017),     Date(2022), +0.30+gauche_offset) # Retour à gauche

nouvelle_donne = PoliticalParty(
  symbol        = "ND",
  color         = "#C23089",
  creation_date = Date(2013,11,28),
  initial_name  = "Nouvelle Donne",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.42+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

generations = PoliticalParty(
  symbol        = "G·s",
  color         = "#D9185D",
  creation_date = Date(2017,7,1),
  initial_name  = "Génération·s",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.50+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

gauche_democratique_et_sociale = PoliticalParty(
  symbol        = "GDS",
  color         = "#EE3437",
  creation_date = Date(2017,11,21),
  initial_name  = "Gauche Démocratique et Sociale",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.00+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

place_publique = PoliticalParty(
  symbol        = "PP",
  color         = "#FEF10A",
  creation_date = Date(2018,11,6),
  initial_name  = "Place Publique",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.05+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
  inside_entity = parti_socialiste,
)

territoires_de_progres = PoliticalParty(
  # https://fr.wikipedia.org/wiki/D%C3%A9mocrates_et_progressistes
  symbol        = "TdP",
  color         = "#E1435E",
  creation_date = Date(2020,2,1),
  initial_name  = "Territoires de Progrès",
  initial_prominence_tier    = "minor",
  initial_political_position = -0.70+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

collectif_des_sociaux_democrates_reformateurs = PoliticalParty(
  # https://fr.wikipedia.org/wiki/D%C3%A9mocrates_et_progressistes
  symbol        = "CSDR",
  color         = "#8307BD",
  # creation_date = Date(2022,12,1),
  creation_date = Date(2022,12,1)-160,
  initial_name  = "Collectif des Sociaux-Démocrates Réformateurs",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.70+centre_offset,
  secede_from = {
    territoires_de_progres: {
      "ratio": 0
    }
  },
)

federation_progressiste = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Fran%C3%A7ois_Rebsamen#F%C3%A9d%C3%A9ration_progressiste_et_retour_au_gouvernement
  symbol        = "FP",
  color         = "#FB0057",
  creation_date = Date(2022,5,19),
  initial_name  = "La Convention",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.60+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

la_convention_federation = PoliticalFederation(
  # https://fr.wikipedia.org/wiki/Bernard_Cazeneuve#Retour_actif_en_politique_et_La_Convention_(depuis_2022)
  # Virtual for the federation around La Convention
  symbol        = "CONV_FED",
  color         = "#5D1354",
  creation_date = Date(2022), # Virtual for transitions
  initial_name  = "La Convention",
  initial_political_position = -0.20+centre_offset,
)
la_convention = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Bernard_Cazeneuve#Retour_actif_en_politique_et_La_Convention_(depuis_2022)
  symbol        = "CONV",
  color         = "#5D1354",
  creation_date = Date(2023,2,1),
  initial_name  = "La Convention",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.20+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
  inside_entity = la_convention_federation
)

collectif_des_sociaux_democrates_reformateurs.join(Date(2023,3,14), la_convention_federation)
federation_progressiste.join(Date(2025,6), la_convention_federation)

#endregion







#region[insoumission]

la_france_insoumise = PoliticalParty(
  symbol        = "LFI",
  color         = "#CC2443",
  creation_date = Date(2008,11,29),
  initial_name  = "Parti de Gauche",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.80+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

la_france_insoumise.set_prominence_tier(Date(2016,2,10), "major")
la_france_insoumise.shift_political_position(Date(2015), Date(2018), +1.20+gauche_offset) # Fin du Front de Gauche

la_france_insoumise.set_results_presidential_election(Date(2012), 11.10) # Jean-Luc Mélanchon investi par le PCF
la_france_insoumise.set_results_presidential_election(Date(2017), 19,58)
la_france_insoumise.set_results_presidential_election(Date(2022), 21,95)

la_france_insoumise.set_results_legislative_election(Date(2012), 6.91*102/577, 1)
la_france_insoumise.set_results_legislative_election(Date(2017), 11.03, 17)
la_france_insoumise.set_results_legislative_election(Date(2022), 14.22, 75)
la_france_insoumise.set_results_legislative_election(Date(2024), 10.49, 71)

la_france_insoumise.set_results_senatorial_election(Date(2014), 0)
la_france_insoumise.set_results_senatorial_election(Date(2017), 0)
la_france_insoumise.set_results_senatorial_election(Date(2020), 0)
la_france_insoumise.set_results_senatorial_election(Date(2023), 0)

la_france_insoumise.set_results_european_election(Date(2009), 6.48, 2) # Front de Gauche
la_france_insoumise.set_results_european_election(Date(2014), 6.61, 4) # Front de Gauche
la_france_insoumise.set_results_european_election(Date(2019), 6.31, 6)
la_france_insoumise.set_results_european_election(Date(2024), 9.89, 9)

lapres = PoliticalParty(
  symbol        = "L'A",
  color         = "#F39E36",
  creation_date = Date(2024,5,21),
  initial_name  = "L'Après",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.05+gauche_offset,
  secede_from = {
    la_france_insoumise: {
      "ratio": 0
    }
  },
)

gauche_democratique_et_sociale.merge_into(Date(2025,2,1), lapres, 0.0)

#endregion







#region[ecosocialiste]

mouvement_decologie_politique = PoliticalParty(
  symbol        = "MÉP",
  color         = "#66C52C",
  creation_date = Date(1974,11,9),
  initial_name  = "Mouvement Écologique",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.03+gauche_offset,
)

mouvement_decologie_politique.name_change(Date(1978, 7, 1), "Coordination Interrégionale des Mouvements Écologistes")
mouvement_decologie_politique.name_change(Date(1980, 1,16), "Mouvement d'Écologie Politique")
mouvement_decologie_politique.name_change(Date(1982,11, 1), "Verts, Parti Écologiste")

confederation_ecologiste = PoliticalParty(
  symbol        = "CÉ",
  color         = "#66C52C",
  creation_date = Date(1977,5,22),
  initial_name  = "Réseau des Amis de la Terre",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.03+gauche_offset,
)

confederation_ecologiste.name_change(Date(1981,12,13), "Confédération Écologiste")
confederation_ecologiste.name_change(Date(1983, 5,23), "Les Verts - Confédération Écologiste")

les_ecologistes = PoliticalParty(
  symbol        = "LÉ",
  color         = "#66C52C",
  creation_date = Date(1984,1,29),
  initial_name  = "Les Verts - Confédération Écologiste, Parti Écologiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.00+gauche_offset,
  merge_from = [
    mouvement_decologie_politique,
    confederation_ecologiste,
  ]
)

les_ecologistes.name_change(Date(2010,11,13), "Europe Écologistes Les Verts")
les_ecologistes.name_change(Date(2024, 6,30), "Les Écologistes")

les_ecologistes.shift_political_position(Date(1994), Date(1995), +0.60+gauche_offset) # Fin du "ni-ni"

generations.join(Date(2020,8), les_ecologistes)

#endregion







#region[radicalisme]

parti_radical = PoliticalParty(
  symbol        = "PRAD",
  color         = "#C71982",
  creation_date = Date(1901,6,21),
  initial_name  = "Parti Radical et Radical-Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.20,
)

parti_radical.set_results_presidential_election(Date(1906),   43.8)
parti_radical.set_results_presidential_election(Date(1913),   37.7)
parti_radical.set_results_presidential_election(Date(1920,1),  0.0)
parti_radical.set_results_presidential_election(Date(1920,9),  0.0)
parti_radical.set_results_presidential_election(Date(1924),   60.4, True)
parti_radical.set_results_presidential_election(Date(1931),   49.3, True)
parti_radical.set_results_presidential_election(Date(1932),    0.0)
parti_radical.set_results_presidential_election(Date(1939),    5.5)
parti_radical.set_results_presidential_election(Date(1947),   13.8)
parti_radical.set_results_presidential_election(Date(1953),   13.9)
parti_radical.set_results_presidential_election(Date(1958),    0.0)
parti_radical.set_results_presidential_election(Date(1965),    0.0) # Soutien à François Mitterrand
parti_radical.set_results_presidential_election(Date(1969),    0.0) # Soutien à Alain Poher
parti_radical.set_results_presidential_election(Date(1974),    0.0) # Soutien à Valéry Giscard d'Estaing
parti_radical.set_results_presidential_election(Date(1981),    0.0) # Soutien à Valéry Giscard d'Estaing
parti_radical.set_results_presidential_election(Date(1988),    0.0) # Soutien à Raymond Barre
parti_radical.set_results_presidential_election(Date(1995),    0.0) # Soutien à Édouard Balladur
parti_radical.set_results_presidential_election(Date(2002),    0.0) # Soutien à Jacques Chirac
parti_radical.set_results_presidential_election(Date(2007),    0.0) # Soutien à Nicolas Sarkozy
parti_radical.set_results_presidential_election(Date(2012),    0.0) # Soutien à Nicolas Sarkozy
parti_radical.set_results_presidential_election(Date(2017),    0.0) # Soutien à François Fillon
parti_radical.set_results_presidential_election(Date(2022),    0.0) # Soutien à Emmanuel Macron

parti_radical.set_results_legislative_election(Date(1902),        17.7,      104, True)
parti_radical.set_results_legislative_election(Date(1906),        28.53,     132, True)
parti_radical.set_results_legislative_election(Date(1910),        39.17,     261, True)
parti_radical.set_results_legislative_election(Date(1914),        18.15,     192, True)
parti_radical.set_results_legislative_election(Date(1919),        17.47,      86, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1924),        17.86,     139, True)
parti_radical.set_results_legislative_election(Date(1928),        17.77,     125, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1932),        19.18,     160, True)
parti_radical.set_results_legislative_election(Date(1936),        15.17,     115, True)
parti_radical.set_results_legislative_election(Date(1945),        10.54,      60)       # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1946,6),      11.61,      32)       # Coalition du RGR, résultat partagé, opposition
parti_radical.set_results_legislative_election(Date(1946,11),     11.12,      42, True) # Coalition du RGR, résultat partagé
parti_radical.set_results_legislative_election(Date(1951),        11.13,      90, True) # Coalition du RGR, résultat partagé
parti_radical.set_results_legislative_election(Date(1956),        10.99,      54, True) # Coalition du FR, résultat partagé avec l'UDSR
parti_radical.set_results_legislative_election(Date(1958),         8.40,      57, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1962),         7.42,      41)
parti_radical.set_results_legislative_election(Date(1967), 75/429*18.90,      24) # Coalition de la FGDS, 75 circonscriptions sur 429
parti_radical.set_results_legislative_election(Date(1968), 77/442*16.54+0.36, 15) # Coalition de la FGDS, 77 circonscriptions sur 442, plus non-coalisés
parti_radical.set_results_legislative_election(Date(1973),   4/31*13.26,       4) # Coalition du MR, 4 sièges sur 31
parti_radical.set_results_legislative_election(Date(1978),  9/128*21.5,        9) # Composante de l'UDF,  9 sièges sur 128
parti_radical.set_results_legislative_election(Date(1981),   2/65*19.2,        2) # Composante de l'UDF,  2 sièges sur  65
parti_radical.set_results_legislative_election(Date(1986),  7/127*21.4,        7) # Composante de l'UDF,  7 sièges sur 127
parti_radical.set_results_legislative_election(Date(1988),  3/129*18.5,        3) # Composante de l'UDF,  3 sièges sur 129
parti_radical.set_results_legislative_election(Date(1993), 14/215*18.6,       14) # Composante de l'UDF, 14 sièges sur 215
parti_radical.set_results_legislative_election(Date(1997),  3/114*14.2,        3) # Composante de l'UDF,  3 sièges sur 114
parti_radical.set_results_legislative_election(Date(2002),  9/358*33.30,       9) # Composante de l'UMP,  9 sièges sur 358
parti_radical.set_results_legislative_election(Date(2007), 16/313*39.54,      16) # Composante de l'UMP, 16 sièges sur 313
parti_radical.set_results_legislative_election(Date(2012),         1.24,       6)
parti_radical.set_results_legislative_election(Date(2017),    3/18*3.03,       3) # Composante de l'UDI
parti_radical.set_results_legislative_election(Date(2022),         0.52,       5)
parti_radical.set_results_legislative_election(Date(2024),         0.54,       2)

# parti_radical.set_results_senatorial_election(Date(1903), )
# parti_radical.set_results_senatorial_election(Date(1906), )
# parti_radical.set_results_senatorial_election(Date(1909), )
# parti_radical.set_results_senatorial_election(Date(1912), )
# parti_radical.set_results_senatorial_election(Date(1920), )
# parti_radical.set_results_senatorial_election(Date(1921), )
# parti_radical.set_results_senatorial_election(Date(1924), )
# parti_radical.set_results_senatorial_election(Date(1927), )
# parti_radical.set_results_senatorial_election(Date(1929), )
# parti_radical.set_results_senatorial_election(Date(1932), )
# parti_radical.set_results_senatorial_election(Date(1935), )
# parti_radical.set_results_senatorial_election(Date(1938), )
# parti_radical.set_results_senatorial_election(Date(1946), )
# parti_radical.set_results_senatorial_election(Date(1948), )
# parti_radical.set_results_senatorial_election(Date(1952), )
# parti_radical.set_results_senatorial_election(Date(1955), )
# parti_radical.set_results_senatorial_election(Date(1958), )
# parti_radical.set_results_senatorial_election(Date(1959), )
# parti_radical.set_results_senatorial_election(Date(1962), )
# parti_radical.set_results_senatorial_election(Date(1965), )
# parti_radical.set_results_senatorial_election(Date(1968), )
# parti_radical.set_results_senatorial_election(Date(1971), )
# parti_radical.set_results_senatorial_election(Date(1974), )
# parti_radical.set_results_senatorial_election(Date(1977), )
# parti_radical.set_results_senatorial_election(Date(1980), )
# parti_radical.set_results_senatorial_election(Date(1983), )
# parti_radical.set_results_senatorial_election(Date(1986), )
# parti_radical.set_results_senatorial_election(Date(1989), )
# parti_radical.set_results_senatorial_election(Date(1992), )
# parti_radical.set_results_senatorial_election(Date(1995), )
# parti_radical.set_results_senatorial_election(Date(1998), )
# parti_radical.set_results_senatorial_election(Date(2001), )
# parti_radical.set_results_senatorial_election(Date(2004), )
# parti_radical.set_results_senatorial_election(Date(2008), )
# parti_radical.set_results_senatorial_election(Date(2011), )
# parti_radical.set_results_senatorial_election(Date(2014), )
# parti_radical.set_results_senatorial_election(Date(2017), )
# parti_radical.set_results_senatorial_election(Date(2020), )
# parti_radical.set_results_senatorial_election(Date(2023), )

# parti_radical.set_results_european_election(Date(1979), )
# parti_radical.set_results_european_election(Date(1984), )
# parti_radical.set_results_european_election(Date(1989), )
# parti_radical.set_results_european_election(Date(1994), )
# parti_radical.set_results_european_election(Date(1999), )
# parti_radical.set_results_european_election(Date(2004), )
# parti_radical.set_results_european_election(Date(2009), )
# parti_radical.set_results_european_election(Date(2014), )
# parti_radical.set_results_european_election(Date(2019), )
# parti_radical.set_results_european_election(Date(2024), )

# parti_radical                        Date(1901,6,21)              +0.20  # Création
parti_radical.shift_political_position(Date(1946), Date(1958),      +0.05) # Glissement pendant la IVe
parti_radical.shift_political_position(Date(1958), Date(1972),      -0.10) # Glissement du début de la Ve
# parti_radical                        Date(1971,11,17)             -0.50  # Scission de l'aile gauche
parti_radical.shift_political_position(Date(2017), Date(2017,12,9), -1.10+centre_offset) # Mouvement Radical

parti_radical.set_prominence_tier(Date(1967), "minor")
parti_radical.set_prominence_tier(Date(2019), "micro")

parti_radical.name_change(Date(2017,12, 9), "Mouvement Radical")
parti_radical.name_change(Date(2021, 9,12), "Parti Radical")

parti_radical.shift_political_position(Date(1972), Date(1973), -0.50) # Scission de l'aile gauche

parti_radical_de_gauche_1971 = PoliticalParty(
  symbol        = "PRG-1971",
  color         = "#C71982",
  creation_date = Date(1971,11,17),
  initial_name  = "Groupe d'Études et d'Action Radical-Socialiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    parti_radical: {
      "ratio": 0.5, # 7 députés sur 15
      "source_new_position": -0.50
    }
  }
)
parti_radical_de_gauche_1971.name_change(Date(1972,10, 4), "Mouvement de la Gauche Radicale-Socialiste")
parti_radical_de_gauche_1971.name_change(Date(1973, 1),    "Mouvement des Radicaux de Gauche")
parti_radical_de_gauche_1971.name_change(Date(1994,11, 5), "Radical")
parti_radical_de_gauche_1971.name_change(Date(1996, 8, 6), "Parti Radical Socialiste")
parti_radical_de_gauche_1971.name_change(Date(1998, 1,13), "Parti Radical de Gauche")

# parti_radical_de_gauche_1971                        Date(1971,11,17)        +0.30+gauche_offset  # Creation
parti_radical_de_gauche_1971.shift_political_position(Date(1981), Date(1984), +0.10+gauche_offset) # Tournant de la rigueur
parti_radical_de_gauche_1971.shift_political_position(Date(1995), Date(1997), -0.10+gauche_offset) # Troisième voie du PS
parti_radical_de_gauche_1971.shift_political_position(Date(2012), Date(2017), -0.30+gauche_offset) # Quinquennat Hollande

parti_radical_de_gauche_1971.merge_into(Date(2017,12,9), parti_radical, 0.5) # Mouvement Radical

parti_radical_de_gauche_2019 = PoliticalParty(
  symbol        = "PRG-2019",
  color         = "#C71982",
  creation_date = Date(2019,2,6),
  initial_name  = "Parti Radical de Gauche",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.10+gauche_offset,
  secede_from = {
    parti_radical: {
      "ratio": 0.5,
      "source_new_position": -1.57+centre_offset,
    }
  }
)
parti_radical_de_gauche_2019.join(Date(2023,2,1), la_convention_federation)

#endregion







#region[centralisme]

republicains_independants = PoliticalParty(
  symbol        = "RI",
  color         = "#002153",
  creation_date = Date(1962,12,2),
  initial_name  = "Républicains Indépendants",
  initial_prominence_tier    = "minor",
  initial_political_position = -0.50+centre_offset,
  secede_from = {
    centre_national_des_independants_et_paysans: {
      "ratio": 0.2, # TBD
    }
  }
)
federation_nationale_des_republicains_independants = republicains_independants.name_change(Date(1966,6,1),  "Fédération Nationale des Républicains Indépendants")
parti_republicain         = federation_nationale_des_republicains_independants.name_change(Date(1977,5,20), "Parti Républicain")

union_pour_la_democratie_francaise = PoliticalFederation(
  symbol        = "UDF",
  color         = "#00FFFF",
  creation_date = Date(1978,2,1),
  initial_name  = "Union pour la Démocratie Française",
  initial_political_position = -0.50+centre_offset,
  initial_members = [
    republicains_independants,
  ],
)

nouvelle_union_pour_la_democratie_francaise = PoliticalParty(
  symbol        = "NUDF",
  color         = "#F07400",
  creation_date = Date(1998,11,29),
  initial_name  = "Union pour la Démocratie Française",
  initial_prominence_tier    = "major",
  initial_political_position = -0.50+centre_offset,
)

nouvelle_union_pour_la_democratie_francaise.set_results_presidential_election(Date(2002),  6.84)
nouvelle_union_pour_la_democratie_francaise.set_results_presidential_election(Date(2007), 18.57)

nouvelle_union_pour_la_democratie_francaise.set_results_legislative_election(Date(2002), 4.86, 27)

nouvelle_union_pour_la_democratie_francaise.set_results_european_election(Date(2004), 11.96, 11)

mouvement_democrate = PoliticalParty(
  symbol        = "MoDem",
  color         = "#EF5222",
  creation_date = Date(2007,5,10),
  initial_name  = "Union pour un Mouvement Populaire",
  initial_prominence_tier    = "major",
  initial_political_position = -0.90+centre_offset,
  merge_from = [
    nouvelle_union_pour_la_democratie_francaise
  ]
)

mouvement_democrate.set_results_presidential_election(Date(2012), 9.13)

mouvement_democrate.set_results_legislative_election(Date(2007), 7.61,  3)
mouvement_democrate.set_results_legislative_election(Date(2012), 1.77,  2)
mouvement_democrate.set_results_legislative_election(Date(2017), 4.11, 42, True)
mouvement_democrate.set_results_legislative_election(Date(2022), 4.62, 46, True)
mouvement_democrate.set_results_legislative_election(Date(2024), 3.80, 36, True)

mouvement_democrate.set_results_european_election(Date(2009),  8.46, 6)
mouvement_democrate.set_results_european_election(Date(2014),  9.94, 4) # Au sein de L'Alternative avec l'Union des démocrates et indépendants (3 sièges).
mouvement_democrate.set_results_european_election(Date(2019), 22.42, 5) # Liste commune avec La République en marche (11 sièges), Agir (1 siège), le Mouvement radical, social et libéral (1 siège) et Alliance centriste, avec 3 élus sans étiquette.
mouvement_democrate.set_results_european_election(Date(2024), 14.60, 4) # Liste commune avec Renaissance (5 sièges), Horizons (2 sièges), l'UDI (1 siège) et le Parti radical avec 1 élu sans étiquette.

renaissance = PoliticalParty(
  symbol        = "RE",
  color         = "#FFD600",
  creation_date = Date(2016,4,6),
  initial_name  = "En Marche",
  initial_prominence_tier    = "major",
  initial_political_position = -0.50+centre_offset,
)
renaissance.name_change(Date(2017,8, 4), "La République En Marche")
renaissance.name_change(Date(2022,9,17), "Renaissance")

renaissance.set_results_presidential_election(Date(2017), 24.01, True)
renaissance.set_results_presidential_election(Date(2022), 27.85, True)

renaissance.set_results_legislative_election(Date(2017), 28.21, 308, True)
renaissance.set_results_legislative_election(Date(2022), 16.52, 157, True)
renaissance.set_results_legislative_election(Date(2024), 12.32,  92, True)

renaissance.set_results_senatorial_election(Date(2017), 21)
renaissance.set_results_senatorial_election(Date(2020), 21)
renaissance.set_results_senatorial_election(Date(2023), 22)

renaissance.set_results_european_election(Date(2019), 22.42, 12)
renaissance.set_results_european_election(Date(2024), 14.60,  5)

renaissance.shift_political_position(Date(2018), Date(2022), -1.30+centre_offset)

en_commun = PoliticalParty(
  symbol        = "EC",
  color         = "#DC6863",
  creation_date = Date(2020,10,14),
  initial_name  = "En Commun",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.35+centre_offset,
  secede_from = {
    renaissance: {
      "ratio": 0.0,
    }
  }
)
en_commun.join(Date(2025,4), la_convention_federation)

territoires_de_progres.join(Date(2022,9,17), renaissance)

#endregion







#region[gaullisme]

rassemblement_pour_la_republique = PoliticalParty(
  symbol        = "RPF",
  color         = "#021A6F",
  creation_date = Date(1976,12,5),
  initial_name  = "Rassemblement Pour la République",
  initial_prominence_tier    = "major",
  initial_political_position = -1.45+droite_offset,
)

rassemblement_pour_la_republique.set_results_presidential_election(Date(1981), 18.00)
rassemblement_pour_la_republique.set_results_presidential_election(Date(1988), 19.94)
rassemblement_pour_la_republique.set_results_presidential_election(Date(1995), 20.84 + 18.58, True) # Chirac et Balladur au premier tour
rassemblement_pour_la_republique.set_results_presidential_election(Date(2002), 19.88, True)

rassemblement_pour_la_republique.set_results_legislative_election(Date(1978), 22.5, 150, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1981), 20.8,  85)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1986), 11.2, 147, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1988), 19.2, 127)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1993), 19.8, 245, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1997), 15.7, 139)

# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1977), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1980), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1983), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1986), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1989), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1992), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1995), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1998), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(2001), )

rassemblement_pour_la_republique.set_results_european_election(Date(1979), 16.3, 15)
rassemblement_pour_la_republique.set_results_european_election(Date(1984), 43.0, 20)
rassemblement_pour_la_republique.set_results_european_election(Date(1989), 28.9, 13)
rassemblement_pour_la_republique.set_results_european_election(Date(1994), 25.6, 14)
rassemblement_pour_la_republique.set_results_european_election(Date(1999), 12.8, 12)

union_pour_un_mouvement_populaire = PoliticalParty(
  symbol        = "LR",
  color         = "#0045B0",
  creation_date = Date(2002,4,23),
  initial_name  = "Union pour un Mouvement Populaire",
  initial_prominence_tier    = "major",
  initial_political_position = -1.45+droite_offset,
  merge_from = [
    rassemblement_pour_la_republique
  ]
)
les_republicains = union_pour_un_mouvement_populaire.name_change(Date(2015,5,30), "Les Républicains")

union_pour_un_mouvement_populaire.set_results_presidential_election(Date(2007), 31.18, True)
union_pour_un_mouvement_populaire.set_results_presidential_election(Date(2012), 27.18)
les_republicains                 .set_results_presidential_election(Date(2017), 20.01)
les_republicains                 .set_results_presidential_election(Date(2022),  4.78)

union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2002), 33.30, 358, True)
union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2007), 39.54, 313, True)
union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2012), 27.12, 194)
les_republicains                 .set_results_legislative_election(Date(2017), 15.77, 112)
les_republicains                 .set_results_legislative_election(Date(2022), 10.55,  61)
les_republicains                 .set_results_legislative_election(Date(2024),  7.55,  48)

union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2004), 156, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2008), 151, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2011), 132, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2014), 143, True)
les_republicains                 .set_results_senatorial_election(Date(2017), 146, True)
les_republicains                 .set_results_senatorial_election(Date(2020), 148, True)
les_republicains                 .set_results_senatorial_election(Date(2023), 139, True)

union_pour_un_mouvement_populaire.set_results_european_election(Date(2004), 16.64, 17)
union_pour_un_mouvement_populaire.set_results_european_election(Date(2009), 27.88, 24) # Liste commune avec le NC (trois sièges) et la GM (deux sièges).
union_pour_un_mouvement_populaire.set_results_european_election(Date(2014), 20.80, 20)
les_republicains                 .set_results_european_election(Date(2019),  8.48,  7)
les_republicains                 .set_results_european_election(Date(2024),  7.25,  6)

# union_pour_un_mouvement_populaire                        Date(2002,4,23)                     -1.45+droite_offset  # Creation UMP
union_pour_un_mouvement_populaire.shift_political_position(Date(2006),       Date(2009),       -1.80+droite_offset) # Sarkozisme
les_republicains                 .shift_political_position(Date(2017, 6,18), Date(2022, 6,19), -1.95+droite_offset) # Macronisme

parti_radical.join (Date(2002,4,23), union_pour_un_mouvement_populaire)
parti_radical.leave(Date(2011,5,14), union_pour_un_mouvement_populaire)

agir = PoliticalParty(
  symbol        = "Agir",
  color         = "#43519E",
  creation_date = Date(2017,11,26),
  initial_name  = "En Commun",
  initial_prominence_tier    = "minor",
  initial_political_position = -1.62+centre_offset,
  secede_from = {
    les_republicains: {
      "ratio": 0.0,
    }
  }
)

agir.join(Date(2022,9,17), renaissance)

horizon = PoliticalParty(
  symbol        = "HOR",
  color         = "#0000BA",
  creation_date = Date(2021,10,9),
  initial_name  = "Horizon",
  initial_prominence_tier    = "major",
  initial_political_position = -1.68+centre_offset,
  secede_from = {
    renaissance: {
      "ratio": 0.0,
    },
    agir: {
      "ratio": 0.0,
    }
  }
)



parti_agraire_et_paysan_francais = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_agraire_et_paysan_fran%C3%A7ais
  # https://www.france-politique.fr/wiki/Parti_Agraire_et_Paysan_Fran%C3%A7ais_(PAPF)
  symbol        = "PAPF",
  color         = "#255D32",
  creation_date = Date(1927,11,26),
  initial_name  = "Parti Agraire et Paysan Français",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
)

parti_republicain_agraire_et_social = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_r%C3%A9publicain_agraire_et_social
  # https://www.france-politique.fr/wiki/Parti_R%C3%A9publicain_Agraire_et_Social_(PRAS)
  symbol        = "PRAS",
  color         = "#255D32",
  creation_date = Date(1936,2,5),
  initial_name  = "Parti Républicain Agraire et Social",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
  secede_from = {
    parti_agraire_et_paysan_francais: {
      "ratio": 0
    }
  },
)
parti_republicain_agraire_et_social.dissolve(Date(1940))

parti_paysan_dunion_sociale = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_paysan_d%27union_sociale
  # https://www.france-politique.fr/wiki/Mouvement_D%C3%A9mocrate_et_Paysan_(MDP)
  symbol        = "PPUS",
  color         = "#255D32",
  creation_date = Date(1945,3,12),
  initial_name  = "Parti Paysan d'Union Sociale",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
  merge_from = [
    parti_agraire_et_paysan_francais,
  ]
)

comites_de_defense_paysane = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Comit%C3%A9s_de_d%C3%A9fense_paysanne
  # https://www.france-politique.fr/wiki/Comit%C3%A9s_de_D%C3%A9fense_Paysanne_(DP)
  symbol        = "DP",
  color         = "#013502",
  creation_date = Date(1948,10,10),
  initial_name  = "Comités de Défense Paysanne",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
)

# https://www.france-politique.fr/wiki/Rassemblement_Paysan_(RP)

centre_national_des_independants_et_paysans = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Centre_national_des_ind%C3%A9pendants_et_paysans
  # https://www.france-politique.fr/chronologie-cnip.htm
  symbol        = "CNIP",
  color         = "#255D32",
  creation_date = Date(1949,1,6),
  initial_name  = "Centre National des Indépendants",
  initial_prominence_tier    = "major",
  initial_political_position = -1.20+droite_offset,
)
parti_paysan_dunion_sociale.merge_into(Date(1951,2,15), centre_national_des_independants_et_paysans)
centre_national_des_independants_et_paysans.name_change(Date(1951,2,15), "Centre National des Indépendants et Paysans")

#endregion







#region[nationalisme]

front_national = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Rassemblement_national
  # https://www.france-politique.fr/chronologie-fn.htm
  symbol        = "RN",
  color         = "#8A5928",
  creation_date = Date(1972,10,5),
  initial_name  = "Front National",
  initial_prominence_tier    = "major",
  initial_political_position = -2.80+extreme_droite_offset,
)
rassemblement_national = front_national.name_change(Date(2018,6,1), "Rassemblement National")

front_national        .set_results_presidential_election(Date(1974),  0.75)
front_national        .set_results_presidential_election(Date(1988), 14.39)
front_national        .set_results_presidential_election(Date(1995), 15.00)
front_national        .set_results_presidential_election(Date(2002), 16.86)
front_national        .set_results_presidential_election(Date(2007), 10.44)
front_national        .set_results_presidential_election(Date(2012), 17.90)
front_national        .set_results_presidential_election(Date(2017), 21.30)
rassemblement_national.set_results_presidential_election(Date(2022), 23.15)

front_national        .set_results_legislative_election(Date(1973),  1.33,   0)
front_national        .set_results_legislative_election(Date(1978),  0.29,   0)
front_national        .set_results_legislative_election(Date(1981),  0.18,   0)
front_national        .set_results_legislative_election(Date(1986),  9.65,  35)
front_national        .set_results_legislative_election(Date(1988),  9.66,   1)
front_national        .set_results_legislative_election(Date(1993), 12.42,   0)
front_national        .set_results_legislative_election(Date(1997), 14.94,   1)
front_national        .set_results_legislative_election(Date(2002), 11.34,   0)
front_national        .set_results_legislative_election(Date(2007),  4.29,   0)
front_national        .set_results_legislative_election(Date(2012), 13.60,   1)
front_national        .set_results_legislative_election(Date(2017), 13.20,   7)
rassemblement_national.set_results_legislative_election(Date(2022), 18.61,  82)
rassemblement_national.set_results_legislative_election(Date(2024), 28.05, 119)

front_national        .set_results_senatorial_election(Date(2014), 2)
front_national        .set_results_senatorial_election(Date(2017), 2)
rassemblement_national.set_results_senatorial_election(Date(2020), 1)
rassemblement_national.set_results_senatorial_election(Date(2023), 3)

front_national        .set_results_european_election(Date(1984), 11.95, 10)
front_national        .set_results_european_election(Date(1989), 11.73, 10)
front_national        .set_results_european_election(Date(1994), 10.52, 11)
front_national        .set_results_european_election(Date(1999),  5.69,  5)
front_national        .set_results_european_election(Date(2004),  9.81,  7)
front_national        .set_results_european_election(Date(2009),  6.34,  4)
front_national        .set_results_european_election(Date(2014), 24.86, 24)
rassemblement_national.set_results_european_election(Date(2019), 23.34, 21)
rassemblement_national.set_results_european_election(Date(2024), 31.37, 30)

# rassemblement_national                        Date(1972,10,5)         -2.80+extreme_droite_offset  # Creation
rassemblement_national.shift_political_position(Date(1982), Date(1986), -2.75+extreme_droite_offset) #
rassemblement_national.shift_political_position(Date(2013), Date(2017), -2.60+extreme_droite_offset) # Marine LePen, changement de nom
rassemblement_national.shift_political_position(Date(2018), Date(2023), -2.50+extreme_droite_offset) # Dédiablisation

union_des_droites_pour_la_republique = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Union_des_droites_pour_la_R%C3%A9publique
  # https://www.france-politique.fr/wiki/Union_des_Droites_pour_la_R%C3%A9publique_(UDR)
  symbol        = "UDR",
  color         = "#0045B0",
  creation_date = Date(2024,6,30),
  initial_name  = "Union des Droites pour la République",
  initial_prominence_tier    = "minor",
  initial_political_position = -2.50+extreme_droite_offset,
  secede_from = {
    les_republicains: {
      "ratio": 0.3
    }
  },
  inside_entity = rassemblement_national,
)

#endregion
