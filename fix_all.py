import re

# 1. viewer.py - ensure no multiline f-strings for btn.setText
with open("cce/gui/viewer.py", "r") as f:
    cv = f.read()

# Replace any accidental literals inside btn.setText, should already be fixed but let's double check.
cv = re.sub(r'btn\.setText\(f"\{day\}\n📍"\)', 'btn.setText(f"{day}\\\\n📍")', cv)
cv = re.sub(r'btn\.setText\(f"\{day\}\n🌘"\)', 'btn.setText(f"{day}\\\\n🌘")', cv)
cv = re.sub(r'base_text \+= "\n🌘"', 'base_text += "\\\\n🌘"', cv)
cv = re.sub(r'btn\.setText\(f"\{base_text\}\n\(\{events_today\} 📌\)"\)', 'btn.setText(f"{base_text}\\\\n({events_today} 📌)")', cv)

with open("cce/gui/viewer.py", "w") as f:
    f.write(cv)

# 2. storage.py
with open("cce/core/storage.py", "r") as f:
    cs = f.read()

# Already correctly handles primitive list checks: `if dataclasses.is_dataclass(item_type):`
# but maybe it needs `is_dataclass(item_type)` on the item itself if item_type is Any?
# Let's ensure it handles primitives perfectly.
old_storage = """        # Handle lists of dataclasses
        if hasattr(ftype, '__origin__') and ftype.__origin__ is list:
            item_type = ftype.__args__[0]
            if dataclasses.is_dataclass(item_type):
                kwargs[key] = [_instantiate_dataclass(item_type, item) for item in value]
            else:
                kwargs[key] = value
        else:"""

new_storage = """        # Handle lists of dataclasses
        if hasattr(ftype, '__origin__') and ftype.__origin__ is list:
            item_type = ftype.__args__[0]
            if isinstance(item_type, type) and dataclasses.is_dataclass(item_type):
                kwargs[key] = [_instantiate_dataclass(item_type, item) for item in value]
            elif isinstance(item_type, str) and item_type == 'Event': # ForwardRef check if needed
                kwargs[key] = value
            else:
                kwargs[key] = value
        else:"""
cs = cs.replace(old_storage, new_storage)
with open("cce/core/storage.py", "w") as f:
    f.write(cs)


# 3. engine.py - get_days_in_month returns max(1, days)
with open("cce/core/engine.py", "r") as f:
    ce = f.read()

ce = ce.replace("        return days", "        return max(1, days)")

with open("cce/core/engine.py", "w") as f:
    f.write(ce)
