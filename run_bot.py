# run_bot.py
import sys
from sc2 import maps
from sc2.main import run_game
from sc2.data import Race
from sc2.player import Bot

# Import your bot class from your main file
from sc2_bot_starter import StarterBot

def main():
    run_game(
        maps.get(sys.argv[1]),         # Ladder passes the map name as an argument
        [
            Bot(Race.Terran, StarterBot()),
            # The opponent slot is filled in by the ladder server
        ],
        realtime=False,
    )

if __name__ == "__main__":
    main()
```

The key differences from the `__main__` block in your starter file are that the map name comes in as a command-line argument (the ladder server decides the map), there's no `Computer(...)` opponent slot (the server fills that in with the real opposing bot), and the file is named exactly `run_bot.py` so the ladder knows what to call.

When you zip your submission, the structure should look like:
```
my_bot.zip
├── run_bot.py          ← entry-point the ladder calls
├── sc2_bot_starter.py  ← your bot logic
└── sc2/                ← optional: copy of the burnysc2 library folder