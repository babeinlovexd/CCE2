import random
from typing import Dict

WEATHER_ICONS = {
    "Sunny": "☀️",
    "Clear": "🌤️",
    "Overcast": "☁️",
    "Rainy": "🌧️",
    "Thunderstorm": "⛈️",
    "Snowy": "🌨️",
    "Blizzard": "❄️",
    "Foggy": "🌫️",
    "Windy": "🌬️"
}

CLIMATE_PROFILES = {
    "Temperate": [
        ("Sunny", 0.4), ("Overcast", 0.3), ("Rainy", 0.2), ("Thunderstorm", 0.1)
    ],
    "Glacial": [
        ("Snowy", 0.4), ("Blizzard", 0.3), ("Overcast", 0.2), ("Sunny", 0.1)
    ],
    "Tropical": [
        ("Sunny", 0.5), ("Thunderstorm", 0.3), ("Rainy", 0.2)
    ],
    "Arid": [
        ("Sunny", 0.7), ("Windy", 0.2), ("Overcast", 0.1)
    ]
}

def generate_daily_weather(world_id: str, year: int, month_name: str, day: int, climate: str = "Temperate") -> Dict:
    """Deterministically generates daily weather for a given world, year, month, and day."""
    profile = CLIMATE_PROFILES.get(climate, CLIMATE_PROFILES["Temperate"])

    # Create a deterministic seed based on date and world ID
    seed_str = f"{world_id}_{year}_{month_name}_{day}"
    rng = random.Random(seed_str)

    rand_val = rng.random()
    cumulative = 0.0
    selected_condition = profile[0][0]

    for cond, weight in profile:
        cumulative += weight
        if rand_val <= cumulative:
            selected_condition = cond
            break

    # Temperature calculation based on condition and climate
    base_temp = 20
    if climate == "Glacial":
        base_temp = -10
    elif climate == "Tropical":
        base_temp = 30
    elif climate == "Arid":
        base_temp = 35

    temp_offset = rng.randint(-5, 5)
    temp_c = base_temp + temp_offset

    icon = WEATHER_ICONS.get(selected_condition, "🌤️")

    return {
        "condition": selected_condition,
        "icon": icon,
        "temp_c": temp_c
    }
