import re

with open("cce/gui/editor.py", "r") as f:
    c = f.read()

c = c.replace("""        self.main_window.mark_unsaved()
            else:
                p.is_primary = False""", """            else:
                p.is_primary = False
        self.main_window.mark_unsaved()""")

with open("cce/gui/editor.py", "w") as f:
    f.write(c)
