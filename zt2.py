import os
sq = chr(39)
TMPL = "C:\\Users\\HP\\Desktop\\study-tracker\\templates\\base.html"
with open(TMPL, "r", encoding="utf-8") as f: h = f.read()

extra = '.menu-link{transition:all 0.2s ease}.menu-link:hover{transform:translateX(4px)}'
sty_end = h.index('</style>')
h = h[:sty_end] + extra + chr(10) + "new styles for mobile panel" + chr(10) + h[sty_end:]

# Build the COMPLETE replacement area:
# 1. <div class='mobile-overlay'>... 2. <div class='mobile-panel'>... 3. <nav>...

nav_st = h.index('<!-- Desktop').index('<nav')  # start of nav tag
nav_end = h.index('</nav>') + len('</nav>')  # end of nav tag
