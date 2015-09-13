# -*- coding: <UTF-8> -*-
from random import *
from ffe_data import *
from ffe_combatants import *
from ffe_actions import *
import renpy.store as store
import renpy.exports as renpy


class FFEngine(object):
    """
    This is the main script of Fast Fight Engine for Mists of Eternal Rome.

    """
    def __init__(self, allies, enemies):
        self.ally = allies          # List of all combatants participating on a player side
        self.enemy = enemies        # List of all combatants participating on a players enemy side
        self.target = self.enemy[0]     # Enemy chosen by player as a current target
        self.actor = self.ally[0]       # Ally who's current action is resolving
        self.action_pool = {"ally": [], "enemy": []}    # Actions made by combatant this turn

    def start(self):
        for enemy in self.enemy:
            enemy.shuffle_actions()
            enemy.action = enemy.reserve[0]
        for ally in self.ally:
            ally.shuffle_actions()
            ally.draw(ally.potential_size)

    def actor_move(self, action):
        self.action_pool["ally"].append(action)
        self.actor.discard.append(action)
        self.actor.potential.remove(action)
        if len(self.actor.reserve) <= 0:
            self.actor.shuffle_actions()
        self.actor.potential.append(self.actor.reserve.pop(0))
        return "turn_resolution"

    def resolution_phase(self):
        for enemy in self.enemy:
            self.action_pool["enemy"].append(enemy.reserve[0])
            enemy.discard.append(enemy.reserve.pop(0))
            if len(enemy.reserve) <= 0:
                enemy.shuffle_actions()
            enemy.action = enemy.reserve[0]
        for ally in self.ally:
            if ally.active:
                ally.state = "ready"
        for enemy in self.enemy:
            if enemy.active:
                enemy.state = "ready"
        self.actions_resolution("fast")
        if self.check_fight_status() == "going on":
            self.actions_resolution("normal")
        if self.check_fight_status() == "going on":
            self.actions_resolution("slow")
        if self.check_fight_status() == "going on":
            return "new_turn"
        return self.check_fight_status()

    def check_fight_status(self):
        all_ally_dead = True
        all_enemy_dead = True
        for ally in self.ally:
            if ally.active:
                all_ally_dead = False
        for enemy in self.enemy:
            if enemy.active:
                all_enemy_dead = False
        if all_ally_dead:
            fight_status = "defeat"
        elif all_enemy_dead:
            fight_status = "victory"
        else:
            fight_status = "going on"
        return fight_status

    def actions_resolution(self, speed_rate):
        summary = {"ally": FFEAction("ally actions"), "enemy": FFEAction("enemy actions")}
        for side in summary:
            for action in self.action_pool[side]:
                if action.speed_rate == speed_rate:
                    summary[side].addup(action)
        self.resolution(summary)

    def damage_reduction(self, defender_summ, def_type, attacker_sum, atk_type):
        if defender_summ.defence[def_type] > attacker_sum.atk[atk_type]:
            defender_summ.defence[def_type] -= attacker_sum.atk[atk_type]
            attacker_sum.atk[atk_type] = 0
        elif defender_summ.defence[def_type] < attacker_sum.atk[atk_type]:
            attacker_sum.atk[atk_type] -= defender_summ.defence[def_type]
            defender_summ.defence[def_type] = 0
        else:
            attacker_sum.atk[atk_type] = 0
            defender_summ.defence[def_type] = 0

    def resolution(self, summary):
        # TODO: Add oncoming damage
        for side in summary:
            if side == "enemy":
                opposition = "ally"
            else:
                opposition = "enemy"
            for key in ("bold", "sly", "total", "subdual"):
                self.damage_reduction(summary[side], key, summary[opposition], key)      # Specific defences works
                self.damage_reduction(summary[side], key, summary[opposition], "total")  # Total defence works
                self.damage_reduction(summary[side], "bold", summary[opposition], key)   # Rest defences reduce bold atk

        damage_to = {"ally": 0, "enemy": 0}
        for side in summary:
            if side == "enemy":
                opposition = "ally"
                damaged_person = self.target
            else:
                opposition = "enemy"
                damaged_person = self.actor
            for key in ("bold", "sly", "total", "subdual"):
                damage_to[side] += summary[opposition].atk[key]
            damaged_person.hp -= damage_to[side]
            if damaged_person.hp <= 0:
                damaged_person.active = False
                damaged_person.state = "killed"
                if summary[opposition].atk["subdual"] > 0:
                    damaged_person.state = "subdued"


class FFEAction(object):
    """
    This is a class for "action cards" to form a decks and use in FaFiEn.
    """
    def __init__(self, name):
        self.name = name
        self.description = ""       # Mostly not used, but needed when action is not standard
        self.atk = {"subdual": 0, "bold": 0, "sly": 0, "total": 0}  # Three kinds of atk. Subdual bloked by any means, but can subdue enemy not kill it. Bold and sly can be blocked bu matching type of defence or by total defence
        self.oncoming = {"subdual": 0, "bold": 0, "sly": 0, "total": 0}  # Bonus atk for next atk of this type
        self.defence = {"subdual": 0, "bold": 0, "sly": 0, "total": 0}  # Four types of defence. All works good with subdual. Total works with any atk type.
        self.ongoing_dmg = 0        # Opponent get X unblokable nontyped damage / round
        self.recovery = 0           # Recovers HP
        self.regenerate = 0         # Author recovers X hp / round
        self.backlash = 0           # Author gets damage to himself
        self.tactical = 0           # if Hero: he gets additional actions up to max. if NPC: hero discards acrions up to 1
        self.trickery = False       # if Hero: choose next enemy action from two nearest actions in a row, discard other. if NPC: shuffle into Heroes deck "Confusion" action
        self.unblockable = False    # This action attacks cannot be blocked
        self.on_hit = False         # This action has special effect if and when damage successfully dealt to enemy
        self.use_up = False         # Uses some item or resource then discards permanently
        self.speed_rate = "normal"  # Actions resolved in order. Firstly "fast", then "normal", then "slow"

        # ACTIONS LIBRARY
        if self.name == "Confusion":  # This action does nothing at all
            pass
        if self.name == "Scratch":
            self.atk["subdual"] = 1
        if self.name == "Bitch-slap":
            self.atk["subdual"] = 1
        if self.name == "Bite":
            self.atk["subdual"] = 1
        if self.name == "Cover in fear":
            self.defence["total"] = 1
        if self.name == "Squawk":
            self.oncoming["subdual"] = 1
        if self.name == "Punch":
            self.atk["subdual"] = 1
        if self.name == "Kick":
            self.atk["subdual"] = 2
        if self.name == "Arm block":
            self.defence["subdual"] = 2
        if self.name == "Bull-rush":
            self.atk["subdual"] = 3
            self.backlash = 1
        if self.name == "Counterblow":
            self.defence["subdual"] = 1
            self.atk["subdual"] = 1

    def addup(self, action):
        for key in self.atk:
            self.atk[key] += action.atk[key]
        for key in self.oncoming:
            self.oncoming[key] += action.oncoming[key]
        for key in self.defence:
            self.defence[key] += action.defence[key]
        self.ongoing_dmg += action.ongoing_dmg
        self.recovery += action.recovery
        self.regenerate += action.regenerate
        self.backlash += action.backlash
        self.tactical += action.tactical
        self.trickery += action.trickery
        self.unblockable += action.unblockable
        self.speed_rate += action.speed_rate
        self.on_hit += action.on_hit
        self.use_up += action.use_up

combat_style_actions = {
    "chick": [
        FFEAction("Confusion"),
        FFEAction("Scratch"),
        FFEAction("Bitch-slap"),
        FFEAction("Bite"),
        FFEAction("Cover in fear"),
        FFEAction("Squawk"),
    ],

    "bully": [
        FFEAction("Punch"),
        FFEAction("Punch"),
        FFEAction("Kick"),
        FFEAction("Arm block"),
        FFEAction("Bull-rush"),
        FFEAction("Counterblow"),
        ],
}


class FFCombatant(object):
    """
    This class makes a characters participating in Fast Fight.
    """
    def __init__(self, person):
        self.name = person.name
        self.avatar = person.avatar
        self.max_hp = person.physique + person.spirit
        self.hp = self.max_hp
        self.active = True
        self.state = "ready"                                        # ready, subdued, wounded, killed
        self.reserve = combat_style_actions[person.ff_combat_style][:]  # List of all possible actions
        self.potential_size = max(person.agility, person.mind)      # Available actions amount on start
        self.potential = []                                         # Available actions list
        self.discard = []                                           # Discarded actions list
        self.action = None
        self.oncoming = {"total": 0, "subdual": 0, "bold": 0, "sly": 0}  # Bonus atk for next atk of this type
        self.ongoing_dmg = 0            # Damage to character per round
        self.regenerate = 0             # Hp recovery per round
        self.trickery = False           # Choose one of two enemy cards, discard other next round

    def shuffle_actions(self):
        self.reserve.extend(self.discard)
        self.discard = []
        shuffle(self.reserve)

    def draw(self, number=1):
        # Drawing no more than we have at all
        if number > len(self.reserve):
            self.shuffle_actions()
        if number > len(self.reserve):
            num = len(self.reserve)
        else:
            num = number
        for n in range(num):
            self.potential.append(self.reserve.pop(n))

