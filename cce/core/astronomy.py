import math
from .models import World, Planet, Moon, Sun

class AstronomyModel:
    def __init__(self, world: World):
        self.world = world

    def get_moon_phase(self, moon: Moon, total_days: int) -> dict:
        """
        Calculate the phase of a moon for a given absolute day.
        Returns a dict with 'phase_name', 'illumination_percent', 'age_days'
        """
        if moon.cycle_days <= 0:
            return {"phase_name": "Unknown", "illumination": 0.0, "age": 0.0}

        # Calculate days into the cycle
        # phase_offset is the phase at day 0 (in days)
        current_cycle_day = (total_days + moon.phase_offset) % moon.cycle_days

        # Calculate illumination percentage (0.0 to 1.0)
        # using a simple cosine function for visible area
        # 0 = New Moon, cycle_days/2 = Full Moon
        cycle_progress = current_cycle_day / moon.cycle_days
        illumination = (1.0 - math.cos(cycle_progress * 2 * math.pi)) / 2.0

        # Determine phase name based on progress
        if cycle_progress < 0.03 or cycle_progress > 0.97:
            phase = "New Moon"
        elif cycle_progress < 0.22:
            phase = "Waxing Crescent"
        elif cycle_progress < 0.28:
            phase = "First Quarter"
        elif cycle_progress < 0.47:
            phase = "Waxing Gibbous"
        elif cycle_progress < 0.53:
            phase = "Full Moon"
        elif cycle_progress < 0.72:
            phase = "Waning Gibbous"
        elif cycle_progress < 0.78:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"

        return {
            "phase_name": phase,
            "illumination": illumination,
            "age": current_cycle_day
        }
