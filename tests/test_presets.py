from cce.core.presets import PRESETS

def test_presets_creation():
    for name, generator in PRESETS.items():
        world = generator()
        assert world.name != ""
        assert len(world.planets) >= 1
        assert len(world.months) >= 1
        assert len(world.time_units) >= 1
