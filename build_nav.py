import os
import sys
BASE = r'C:\Users\HP\Desktop\study-tracker'
TMPL = os.path.join(BASE, 'templates', 'base.html')
NAV_PART = os.path.join(BASE, 'templates', 'new_nav.html')
with open(NAV_PART, 'r', encoding='utf-8') as f:
    panel_html = f.read()
with open(TMPL, 'r', encoding='utf-8') as f:
    html = f.read()
head_end = html.index('</head>')
head = html[:head_end] + '</head>'
main_idx = html.index('<main')
after_main = html[main_idx:]
# Remove old bottom tab
tab_marker = 'Mobile Bottom Tab Bar'
if tab_marker in after_main:
    lines = after_main.splitlines(True)
    kept = []
    skip = 0
    for i, line in enumerate(lines):
        if tab_marker in line:
            skip += 2
            continue
        if skip > 0:
            skip -= 1
            continue
        kept.append(line)
    after_main = ''.join(kept)
# Remove bottom padding div
after_main = after_main.replace('<div class="md:hidden h-20"></div>', '')
# Replace script block
script_start = after_main.rfind('<script>')
script_end = after_main.rfind('</script>') + len('</script>')
new_script = '''<div class="md:hidden h-4"></div>
<script>
document.addEventListener("alpine:init", () => {
    Alpine.store("nav", { open: false });
});
function toggleDark() {
    document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", document.documentElement.classList.contains("dark") ? "dark" : "light");
}
</script>'''
after_main = after_main[:script_start] + new_script + after_main[script_end:]
result = head + '\n' + panel_html + '\n' + after_main
with open(TMPL, 'w', encoding='utf-8') as f:
    f.write(result)
print('OK')