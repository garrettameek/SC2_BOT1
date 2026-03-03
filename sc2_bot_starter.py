"""
SC2 Competition Starter Bot — Terran
=====================================
Framework : BurnySc2/python-sc2  (the most actively maintained fork)
Install   : pip install burnysc2
Compete   : https://aiarena.net  |  https://sc2ai.net

Quick-start
-----------
1. Install SC2 (free starter edition works) + burnysc2
2. Download a ladder map from https://wiki.sc2ai.net and place it in
   your SC2 Maps/ folder.
3. Run:  python sc2_bot_starter.py
4. To compete: zip this file (+ a run_bot.py entry-point) and upload to aiarena.net

Bot overview (all sections are clearly labelled for easy modification)
----------------------------------------------------------------------
  SECTION 1 — Constants & tuneable parameters
  SECTION 2 — Economy   (workers + supply)
  SECTION 3 — Production (barracks + add-ons)
  SECTION 4 — Army management (attack / defend)
  SECTION 5 — Entry-point / local test runner
"""

import sc2
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Constants & tuneable parameters
#   Adjust these values to change the bot's behaviour without touching logic.
# ─────────────────────────────────────────────────────────────────────────────

MAX_WORKERS = 22          # Stop building SCVs above this number
BARRACKS_CAP = 3          # Maximum Barracks to build
SUPPLY_BUFFER = 4         # Build a Supply Depot when this many supply remain
ATTACK_AT_ARMY = 12       # Launch an attack once we have this many marines
DEFEND_DISTANCE = 25      # Pull army back to base if enemy is within this range


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Economy helpers
# ─────────────────────────────────────────────────────────────────────────────

class StarterBot(BotAI):
    """
    A simple but complete Terran bot structured for easy modification.
    Every public method corresponds to one clear responsibility.
    """

    # ------------------------------------------------------------------
    # Called once at the start of the game
    # ------------------------------------------------------------------
    async def on_start(self):
        self.attacking = False
        print(f"[Bot] Game started — playing as {self.race} on {self.game_info.map_name}")

    # ------------------------------------------------------------------
    # Main loop — called every game step (~22 times per second on Normal)
    # ------------------------------------------------------------------
    async def on_step(self, iteration: int):
        await self.manage_supply()
        await self.manage_workers()
        await self.manage_production_buildings()
        await self.manage_army_production()
        await self.manage_army()

    # ------------------------------------------------------------------
    # Build Supply Depots before we run out of supply
    # ------------------------------------------------------------------
    async def manage_supply(self):
        # Only build one depot at a time; skip if already building one
        if self.supply_left < SUPPLY_BUFFER and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                workers = self.workers.gathering
                if workers:
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=self.start_location.towards(self.game_info.map_center, 8))

        # Lower completed depots so units can pass through
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

    # ------------------------------------------------------------------
    # Train SCVs and keep them mining
    # ------------------------------------------------------------------
    async def manage_workers(self):
        # Train SCVs from all idle Command Centres
        if self.supply_workers < MAX_WORKERS:
            for cc in self.townhalls.idle:
                if self.can_afford(UnitTypeId.SCV):
                    cc.train(UnitTypeId.SCV)

        # Send idle workers back to minerals
        for worker in self.workers.idle:
            closest_cc = self.townhalls.closest_to(worker)
            mf = self.mineral_field.closest_to(closest_cc)
            worker.gather(mf)

    # ------------------------------------------------------------------
    # Build Barracks (add more building types here to expand your build)
    # ------------------------------------------------------------------
    async def manage_production_buildings(self):
        # ── Barracks ──────────────────────────────────────────────────
        barracks_count = self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS)
        if barracks_count < BARRACKS_CAP:
            if self.can_afford(UnitTypeId.BARRACKS):
                # Build near the start location but offset toward the map centre
                await self.build(
                    UnitTypeId.BARRACKS,
                    near=self.start_location.towards(self.game_info.map_center, 10),
                )

        # ── TODO: add Factories, Starports, Tech Labs, etc. here ──────

    # ------------------------------------------------------------------
    # Train units from production buildings
    # ------------------------------------------------------------------
    async def manage_army_production(self):
        # Train Marines from every idle Barracks
        for rax in self.structures(UnitTypeId.BARRACKS).idle:
            if self.can_afford(UnitTypeId.MARINE):
                rax.train(UnitTypeId.MARINE)

        # ── TODO: add Marauder, Medivac, Tank training here ───────────

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4 — Army management
    # ─────────────────────────────────────────────────────────────────────────

    async def manage_army(self):
        marines = self.units(UnitTypeId.MARINE)

        if not marines:
            return

        # ── Defend: if enemy units are near our base, fight them ──────
        enemy_near_base = self.enemy_units.filter(
            lambda u: u.distance_to(self.start_location) < DEFEND_DISTANCE
        )
        if enemy_near_base:
            for marine in marines:
                marine.attack(enemy_near_base.closest_to(marine))
            return

        # ── Attack: once we have enough marines, push toward the enemy ─
        if marines.amount >= ATTACK_AT_ARMY:
            self.attacking = True

        if self.attacking:
            target = self._pick_attack_target()
            for marine in marines.idle:
                marine.attack(target)
        else:
            # Rally idle marines near the front of our base
            rally = self.start_location.towards(self.game_info.map_center, 12)
            for marine in marines.idle:
                marine.move(rally)

    def _pick_attack_target(self) -> Point2:
        """
        Choose the best target to attack.
        Priority: known enemy structures → known enemy units → enemy start location.
        Modify this method to implement smarter targeting logic.
        """
        if self.enemy_structures:
            return self.enemy_structures.random.position
        if self.enemy_units:
            return self.enemy_units.random.position
        # Fall back to the enemy's starting location
        return self.enemy_start_locations[0]

    # ------------------------------------------------------------------
    # Optional callbacks — uncomment and implement as needed
    # ------------------------------------------------------------------

    # async def on_unit_destroyed(self, unit_tag: int):
    #     """Called when any unit (ours or theirs) is destroyed."""
    #     pass

    # async def on_building_construction_complete(self, unit):
    #     """Called when one of our buildings finishes."""
    #     pass

    # async def on_end(self, game_result):
    #     """Called at the end of the game with the result."""
    #     print(f"[Bot] Game ended: {game_result}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — Entry-point / local test runner
#   Run this file directly to start a local game against a built-in AI.
#   Change `Difficulty` and `Race` of the Computer player to practise
#   against different opponents.
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_game(
        maps.get("AcropolisLE"),          # ← change to any downloaded ladder map
        [
            Bot(Race.Terran, StarterBot()),
            Computer(Race.Zerg, Difficulty.Easy),   # ← adjust opponent here
        ],
        realtime=False,                   # False = run as fast as possible
    )
