import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class TimeUnit:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    abbreviation: str = ""
    ticks: int = 1  # How many universal ticks this unit represents

@dataclass
class Sun:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    twilight_dawn_ticks: int = 0
    twilight_dusk_ticks: int = 0

@dataclass
class Moon:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    cycle_days: float = 28.0
    phase_offset: float = 0.0

@dataclass
class Planet:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    day_length_ticks: int = 86400  # Number of ticks in a day
    year_length_days: int = 365
    is_primary: bool = False

@dataclass
class Era:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    abbreviation: str = ""
    start_year: int = 0  # Year relative to absolute 0
    includes_year_zero: bool = False

@dataclass
class Month:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    days: int = 30
    color: str = "#FFFFFF"

@dataclass
class Weekday:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""

@dataclass
class Holiday:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    month_id: Optional[str] = None  # If None, it might be outside months
    day_in_month: int = 1
    counts_as_weekday: bool = True

@dataclass
class LeapRule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    interval_years: int = 4
    month_id_to_append: str = ""
    days_to_add: int = 1
    exception_interval: Optional[int] = 100
    exception_days: int = -1

@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    start_tick: int = 0
    end_tick: int = 0
    characters: List[str] = field(default_factory=list)
    location: str = ""
    category: str = ""
    notes: str = ""

@dataclass
class World:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New World"
    base_tick_name: str = "Tick"
    time_units: List[TimeUnit] = field(default_factory=list)
    planets: List[Planet] = field(default_factory=list)
    eras: List[Era] = field(default_factory=list)
    months: List[Month] = field(default_factory=list)
    weekdays: List[Weekday] = field(default_factory=list)
    holidays: List[Holiday] = field(default_factory=list)
    leap_rules: List[LeapRule] = field(default_factory=list)
    suns: List[Sun] = field(default_factory=list)
    moons: List[Moon] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
