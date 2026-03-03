# StarCraft II Starter Bot

A beginner-friendly StarCraft II bot written in Python using the **BurnySc2/python-sc2** framework. The bot plays as **Terran** and implements a straightforward Marines rush strategy, structured to be easy to read and extend.

---

## Repository structure

```
starcraft_2_bot/
├── sc2_bot_starter.py   # Your bot logic (the file you'll edit)
├── run_bot.py           # Ladder entry-point (called by aiarena.net)
└── sc2/                 # python-sc2 library — files must be added separately (see below)
```

---

## The `sc2/` library — attribution and setup

The `sc2/` subdirectory is sourced from the **BurnySc2/python-sc2** project, the most actively maintained fork of the python-sc2 library:

> **https://github.com/BurnySc2/python-sc2**
> Licensed under the MIT License — © BurnySc2 and contributors.

### Option A — Install via pip (recommended for local development)

The simplest approach is to install the library as a package. You do **not** need the `sc2/` folder at all when using this method:

```bash
pip install burnysc2
```

Both `sc2_bot_starter.py` and `run_bot.py` import from `sc2` by name, so once the package is installed the imports resolve automatically.

### Option B — Copy the library folder manually (required for ladder submission)

Some ladder platforms (including aiarena.net) do not run `pip install` for you, so you must bundle the library with your bot. To do this:

1. Clone the upstream repository:
   ```bash
   git clone https://github.com/BurnySc2/python-sc2.git
   ```
2. Copy the `sc2/` folder from the cloned repo into this directory so it sits alongside `run_bot.py`:
   ```
   starcraft_2_bot/
   ├── run_bot.py
   ├── sc2_bot_starter.py
   └── sc2/          ← copied from BurnySc2/python-sc2
   ```

Alternatively, if you track your bot in its own git repository, you can add python-sc2 as a **git submodule**:

```bash
git submodule add https://github.com/BurnySc2/python-sc2.git sc2_lib
# Then symlink or copy sc2_lib/sc2 → sc2/
```

---

## Prerequisites

- **StarCraft II** installed (the free [Starter Edition](https://us.battle.net/shop/en/product/starcraft-ii) is sufficient)
- **Python 3.10+**
- The `burnysc2` package (and its dependencies):
  ```bash
  pip install burnysc2
  ```
- At least one **ladder map** placed in your SC2 `Maps/` folder.
  Download current ladder maps from the [SC2AI wiki](https://wiki.sc2ai.net/Ladder_Maps).

---

## Running locally

To test your bot against the built-in AI, run the starter file directly:

```bash
python sc2_bot_starter.py
```

This launches a game on **AcropolisLE** against a Zerg opponent at Easy difficulty (both settings are at the bottom of `sc2_bot_starter.py` and can be changed freely).

To test against a specific map:

```python
# Inside sc2_bot_starter.py — SECTION 5
maps.get("YourMapName")          # must match a file in SC2/Maps/
Computer(Race.Protoss, Difficulty.Medium)
```

---

## Bot overview

All tunable parameters are in **SECTION 1** at the top of `sc2_bot_starter.py`:

| Constant | Default | What it controls |
|---|---|---|
| `MAX_WORKERS` | 22 | SCV cap |
| `BARRACKS_CAP` | 3 | Maximum Barracks to build |
| `SUPPLY_BUFFER` | 4 | Supply Depots are queued when this many supply remain |
| `ATTACK_AT_ARMY` | 12 | Marine count that triggers the attack push |
| `DEFEND_DISTANCE` | 25 | Range within which the army defends the base |

The bot's logic is split across clearly labelled sections:

- **SECTION 2** — Economy (SCV training, worker assignment)
- **SECTION 3** — Production buildings (Barracks, with TODOs for Factory/Starport)
- **SECTION 4** — Army management (attack / defend logic)
- **SECTION 5** — Local test runner

---

## Competing on aiarena.net

[aiarena.net](https://aiarena.net) is a free, community-run ladder where Python bots compete automatically. Here is how to submit this bot:

### 1. Create an account

Register at [https://aiarena.net](https://aiarena.net).

### 2. Prepare your zip file

The ladder calls `run_bot.py` as the entry-point and passes the map name as `sys.argv[1]`. Bundle everything the bot needs into a single zip:

```
my_bot.zip
├── run_bot.py           ← entry-point (do not rename)
├── sc2_bot_starter.py   ← your bot logic
└── sc2/                 ← the python-sc2 library folder (Option B above)
```

> **Note:** If you prefer not to bundle `sc2/`, some aiarena competitions allow you to list `burnysc2` in a `requirements.txt` file. Check the current competition rules on the site.

A convenient way to create the zip (from inside the `starcraft_2_bot/` directory):

```bash
zip -r my_bot.zip run_bot.py sc2_bot_starter.py sc2/
```

### 3. Upload your bot

1. Go to **My Bots → Upload Bot** on aiarena.net.
2. Set the bot type to **Python**.
3. Upload your zip file.
4. Choose a competition to enter.

The server will call:
```
python run_bot.py <MapName>
```
and will inject the opposing bot into the second player slot automatically.

### 4. Watch your replays

After matches complete, replay files are available on the match result pages. Download them and open in StarCraft II to review your bot's performance.

---

## Extending the bot

Some good first steps:

- Add a **Factory** and train **Siege Tanks** in `manage_production_buildings` / `manage_army_production`.
- Implement **scouting** with an early SCV to detect the enemy's build order.
- Add **expansion logic** to build a second Command Centre.
- Override `on_unit_destroyed` to react when key units die.
- Override `on_end` to log win/loss results.

The [python-sc2 wiki](https://github.com/BurnySc2/python-sc2/wiki) and the [SC2AI Discord](https://discord.gg/sc2ai) are excellent resources for going further.

---

## License

Your bot code (`sc2_bot_starter.py`, `run_bot.py`) is yours to license as you wish.
The `sc2/` library is © BurnySc2 and contributors, distributed under the [MIT License](https://github.com/BurnySc2/python-sc2/blob/develop/LICENSE).
