from disnake.ui import Button, ActionRow


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDER = '\033[4m'


def occurance(stored, value):
    try:
        stored[value] = stored[value] + 1
    except KeyError:
        stored[value] = 1
        return
async def get_bar(health, max_health):
    bar0 = "<:0_:899376245496758343>"
    bar2 = "<:2_:899376429568000040>"
    bar3 = "<:3_:899376559700451379>"
    bar4 = "<:4_:899376608220172339>"
    bar5 = "<:5_:899376657759088750>"
    bar = None
    mix = health / max_health
    per = mix * 100
    if per == 0:
        bar = f"{bar0}{bar0}{bar0}{bar0}{bar0}"
    if 10 >= per > 0:
        bar = f"{bar2}{bar0}{bar0}{bar0}{bar0}"
    if 20 >= per > 10:
        bar = f"{bar5}{bar0}{bar0}{bar0}{bar0}"
    if 30 >= per > 20:
        bar = f"{bar5}{bar2}{bar0}{bar0}{bar0}"
    if 40 >= per > 30:
        bar = f"{bar5}{bar4}{bar0}{bar0}{bar0}"
    if 50 >= per > 40:
        bar = f"{bar5}{bar5}{bar2}{bar0}{bar0}"
    if 60 >= per > 50:
        bar = f"{bar5}{bar5}{bar4}{bar0}{bar0}"
    if 70 >= per > 60:
        bar = f"{bar5}{bar5}{bar5}{bar3}{bar0}"
    if 80 >= per > 70:
        bar = f"{bar5}{bar5}{bar5}{bar5}{bar2}"
    if 90 >= per > 80:
        bar = f"{bar5}{bar5}{bar5}{bar5}{bar4}"
    if 100 >= per > 90:
        bar = f"{bar5}{bar5}{bar5}{bar5}{bar5}"
    return bar
