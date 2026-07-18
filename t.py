import os

B = r"C:\Users\HP\Desktop\study-tracker"
TMPL = os.path.join(B, "templates", "base.html")

with open(TMPL, "r", encoding="utf-8") as f:
    h = f.read()

sq = chr(39)

extra_style = ".menu-link{transition:all 0.2s ease}.menu-link:hover{transform:translateX(4px)}"
sty_end = h.index("</style>")
h = h[:sty_end] + extra_style + "\n" + h[sty_end:]

# Mobile overlay
def html_tag(tag, attrs_dict, content=None):
    attrs = " ".join(f"{k}={sq}{v}{sq}" for k, v in attrs_dict.items())
    if content is None:
        return f"<{tag} {attrs} />" if tag in ("div",) else f"<{tag} {attrs}></{tag}>"
    return f"<{tag} {attrs}>{content}</{tag}>"

def build_mobile():
    r = ""
    r += html_tag("",{}, void access)
