import re

with open("cce/gui/viewer.py", "r") as f:
    c = f.read()

# Replace any literal newlines inside strings with \\n
c = re.sub(r'btn\.setText\(f"\{day\}\n📍"\)', 'btn.setText(f"{day}\\\\n📍")', c)
c = re.sub(r'moon_tooltip \+= f"\{p_info\[\'moon\'\]\.name\}: \{p_info\[\'phase_name\'\]\} \(\{int\(p_info\[\'phase_percent\'\]\*100\)\}\%\)\n"', 'moon_tooltip += f"{p_info[\'moon\'].name}: {p_info[\'phase_name\']} ({int(p_info[\'phase_percent\']*100)}%)\\\\n"', c)
c = re.sub(r'btn\.setText\(f"\{day\}\n🌘"\)', 'btn.setText(f"{day}\\\\n🌘")', c)
c = re.sub(r'base_text \+= "\n🌘"', 'base_text += "\\\\n🌘"', c)
c = re.sub(r'btn\.setText\(f"\{base_text\}\n\(\{events_today\} 📌\)"\)', 'btn.setText(f"{base_text}\\\\n({events_today} 📌)")', c)


with open("cce/gui/viewer.py", "w") as f:
    f.write(c)
