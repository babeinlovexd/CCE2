import json
import dataclasses
from typing import Any
from .models import World, TimeUnit, Planet, Era, Month, Weekday, Holiday, LeapRule, Sun, Moon, Event

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def save_world(world: World, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(world, f, cls=EnhancedJSONEncoder, indent=2)

def _instantiate_dataclass(cls, data: dict) -> Any:
    if not isinstance(data, dict):
        return data

    field_types = {f.name: f.type for f in dataclasses.fields(cls)}
    kwargs = {}
    for key, value in data.items():
        if key not in field_types:
            continue

        ftype = field_types[key]

        # Handle lists of dataclasses
        if hasattr(ftype, '__origin__') and ftype.__origin__ is list:
            item_type = ftype.__args__[0]
            if isinstance(item_type, type) and dataclasses.is_dataclass(item_type):
                kwargs[key] = [_instantiate_dataclass(item_type, item) for item in value]
            elif isinstance(item_type, str) and item_type == 'Event': # ForwardRef check if needed
                kwargs[key] = value
            else:
                kwargs[key] = value
        else:
            # Handle single dataclass
            if dataclasses.is_dataclass(ftype) and isinstance(value, dict):
                kwargs[key] = _instantiate_dataclass(ftype, value)
            else:
                kwargs[key] = value

    return cls(**kwargs)

def load_world(filepath: str) -> World:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return _instantiate_dataclass(World, data)
