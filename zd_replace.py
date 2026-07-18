import os
B = r"C:\Users\HP\Desktop\study-tracker"
with open(os.path.join(B, "templates", "base.html"), "r", encoding="utf-8") as f:
    h = f.read()
nav_end = h.index("</nav>") + len("</nav>")
main_start = h.index("<main")
script_i = h.rfind("<script>")
script_e = h.rfind("</script>") + len("</script>")
result = h[:nav_end] + "\n" + h[main_start:script_i]
new_scr = "<div class=\"md:hidden\"></div>\n<script>\ndocument.addEventListener(\"alpine:init\",()=>{Alpine.store(\"nav\",{open:false})})\nfunction toggleDark(){document.documentElement.classList.toggle(\"dark\");localStorage.setItem(\"theme\",document.documentElement.classList.contains(\"dark\")?\"dark\":\"light\")}\n</script>\n"
result += new_scr + h[script_e:]
result = result.replace("<div class=\"md:hidden h-20\"></div>", "")
with open(os.path.join(B, "templates", "base.test"), "w", encoding="utf-8") as f:
    f.write(result)
print("done")
