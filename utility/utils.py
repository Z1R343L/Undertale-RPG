from disnake.ui import Button

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

async def disable_all(msg):
    new = []

    for i in msg.components:
        for b in i.children:
            b.disabled = True
            b = Button.from_component(b)
            new.append(b)
    return new