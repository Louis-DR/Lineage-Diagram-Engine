import datetime

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
