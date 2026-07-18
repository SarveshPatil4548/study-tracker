import os
BASE = r"C:\Users\HP\Desktop\study-tracker"
TMPL = os.path.join(BASE, "templates", "base.html")
with open(TMPL, "r", encoding="utf-8") as f: h = f.read()
im = "<p>hi</p>"
print(im)
