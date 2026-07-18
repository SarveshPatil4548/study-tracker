
def make_desktop_nav_section():
    return dedent('''
<nav class="bg-white dark-bg-gray-800 shadow sticky top-0 z-30 transition">
<div class="max-w-6xl mx-auto px-4 sm:px-6">
<div class="flex items-center justify-between h-16 gap-2">
DIVISION
MAIN
END
''').replace('DIVISION','').replace('MAIN','').replace('END','')

