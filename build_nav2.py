import os, sys
BASE = r"C:\Users\HP\Desktop\study-tracker"
TMPL = os.path.join(BASE, "templates", "base.html")

NAV_HTML = r"""    <div class="mobile-overlay fixed inset-0 bg-black/50 z-40 md:hidden" x-data x-show="$store.nav.open" x-cloak x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100" x-transition:leave-start="opacity-100" x-transition:leave-end="opacity-0" @click="$store.nav.open = false"></div>
    <div class="mobile-panel fixed top-0 left-0 h-full w-72 max-w-[85vw] bg-white dark:bg-gray-800 z-30 shadow-2xl md:hidden overflow-y-auto" x-data x-show="$store.nav.open" x-cloak x-transition:enter-start="-translate-x-full" x-transition:enter-end="translate-x-0" x-transition:leave-start="translate-x-0" x-transition:leave-end="-translate-x-full">
        <div class="flex items-center justify-between px-4 h-16 border-b border-gray-200 dark:border-gray-700">
            <span class="font-bold text-brand-600 dark:text-brand-400 text-lg">Menu</span>
            <button @click="$store.nav.open = false" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" aria-label="Close menu">
                <svg class="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/></svg>
            </button>
        </div>
        <div class="py-4 px-3 space-y-1">
'''

with open(TMPL, "r", encoding="utf-8") as f:
    html = f.read()

head_end = html.index("</head>")
head = html[:head_end] + "</head><body " + html[html.index("<body ")+6:].split(">")[0] + ">"

result = head + "\n" + NAV_HTML
result += """


PERFECT NONSENSE SENTINEL
"""

with open(TMPL + ".test_out", "w", encoding="utf-8") as blah:
    pass
print("done")