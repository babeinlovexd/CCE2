from cce.core.models import World, Month, Planet, LeapRule
from cce.core.engine import TimeEngine

def test_leap_rule():
    w = World()
    p = Planet(day_length_ticks=10)
    w.planets = [p]
    m = Month(id="m1", days=10)
    w.months = [m]

    # Gregorian leap year rules: every 4, exclude 100, force 400
    w.leap_rules = [LeapRule(interval_years=4, days_to_add=1, month_id_to_append="m1", exclude_interval=100, force_include_interval=400)]

    e = TimeEngine(w)

    assert e.get_days_in_year(p, 1) == 10
    assert e.get_days_in_year(p, 4) == 11
    assert e.get_days_in_year(p, 100) == 10
    assert e.get_days_in_year(p, 400) == 11
    print("All leap year tests passed!")

test_leap_rule()
