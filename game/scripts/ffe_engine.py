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
        self.ally_action_pool = []  # Actions made by allied combatants this turn
        self.enemy_action_pool = []  # Actions made by enemy combatants this turn

    def start(self):
        for enemy in self.enemy:
            enemy.shuffle_actions()
            enemy.action = enemy.reserve[0]
        for ally in self.ally:
            ally.shuffle_actions()
            ally.draw(ally.potential_size)

    def actor_move(self, action):
        self.ally_action_pool.append(action)
        return "turn_resolution"

    def resolution_phase(self):
        for ally in self.ally:
            if ally.active:
                ally.state = "ready"
        for enemy in self.enemy:
            if enemy.active:
                enemy.state = "ready"
        self.fast_actions()
        if self.check_fight_status() == "going on":
            self.normal_actions()
        if self.check_fight_status() == "going on":
            self.slow_actions()
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
        elif not all_enemy_dead:
            fight_status = "victory"
        else:
            fight_status = "going on"
        return fight_status


    def fast_actions(self):
        ally_summ = FFEAction("ally actions")
        enemy_summ = FFEAction("ally actions")
        for action in self.ally_action_pool:
            if action.fast:
                ally_summ.addup(action)
        for action in self.enemy_action_pool:
            if action.fast:
                enemy_summ.addup(action)
        self.resolution(ally_summ, enemy_summ)

    def normal_actions(self):
        ally_summ = FFEAction("ally actions")
        enemy_summ = FFEAction("ally actions")
        for action in self.ally_action_pool:
            if not action.fast and not action.slow:
                ally_summ.addup(action)
        for action in self.enemy_action_pool:
            if not action.fast and not action.slow:
                enemy_summ.addup(action)
        self.resolution(ally_summ, enemy_summ)

    def slow_actions(self):
        ally_summ = FFEAction("ally actions")
        enemy_summ = FFEAction("ally actions")
        for action in self.ally_action_pool:
            if action.slow:
                ally_summ.addup(action)
        for action in self.enemy_action_pool:
            if action.slow:
                enemy_summ.addup(action)
        self.resolution(ally_summ, enemy_summ)

    def resolution(self, ally_summ, enemy_summ):
        for ally in self.ally:
            if ally_summ.subdual_atk > 0:
                ally_summ.subdual_atk += ally.oncoming_subdual
                ally.oncoming_subdual = 0
            if ally_summ.bold_atk > 0:
                ally_summ.bold_atk += ally.oncoming_bold
                ally.oncoming_bold = 0
            if ally_summ.sly_atk > 0:
                ally_summ.sly_atk += ally.oncoming_sly
                ally.oncoming_sly = 0

        if enemy_summ.bold_def > ally_summ.bold_atk:
            enemy_summ.bold_def -= ally_summ.bold_atk
            ally_summ.bold_atk = 0
        elif enemy_summ.bold_def < ally_summ.bold_atk:
            ally_summ.bold_atk -= ally_summ.bold_def
            enemy_summ.bold_def = 0
        else:
            ally_summ.bold_atk = 0
            enemy_summ.bold_def = 0

        if enemy_summ.sly_def > ally_summ.sly_atk:
            enemy_summ.sly_def -= ally_summ.sly_atk
            ally_summ.sly_atk = 0
        elif enemy_summ.sly_def < ally_summ.sly_atk:
            ally_summ.sly_atk -= ally_summ.sly_def
            enemy_summ.sly_def = 0
        else:
            ally_summ.sly_atk = 0
            enemy_summ.sly_def = 0

        if enemy_summ.subdual_def > ally_summ.subdual_atk:
            enemy_summ.subdual_def -= ally_summ.subdual_atk
            ally_summ.subdual_atk = 0
        elif enemy_summ.subdual_def < ally_summ.subdual_atk:
            ally_summ.subdual_atk -= ally_summ.subdual_def
            enemy_summ.subdual_def = 0
        else:
            ally_summ.subdual_atk = 0
            enemy_summ.subdual_def = 0

        if enemy_summ.total_def > ally_summ.bold_atk:
            enemy_summ.total_def -= ally_summ.bold_atk
            ally_summ.bold_atk = 0
        elif enemy_summ.total_def < ally_summ.bold_atk:
            ally_summ.bold_atk -= ally_summ.total_def
            enemy_summ.total_def = 0
        else:
            ally_summ.bold_atk = 0
            enemy_summ.total_def = 0

        if enemy_summ.total_def > ally_summ.sly_atk:
            enemy_summ.total_def -= ally_summ.sly_atk
            ally_summ.sly_atk = 0
        elif enemy_summ.total_def < ally_summ.sly_atk:
            ally_summ.sly_atk -= ally_summ.total_def
            enemy_summ.total_def = 0
        else:
            ally_summ.sly_atk = 0
            enemy_summ.total_def = 0

        if enemy_summ.total_def > ally_summ.subdual_atk:
            enemy_summ.total_def -= ally_summ.subdual_atk
            ally_summ.subdual_atk = 0
        elif enemy_summ.total_def < ally_summ.subdual_atk:
            ally_summ.subdual_atk -= ally_summ.total_def
            enemy_summ.total_def = 0
        else:
            ally_summ.subdual_atk = 0
            enemy_summ.total_def = 0

        if enemy_summ.bold_def > ally_summ.subdual_atk:
            enemy_summ.bold_def -= ally_summ.subdual_atk
            ally_summ.subdual_atk = 0
        elif enemy_summ.bold_def < ally_summ.subdual_atk:
            ally_summ.subdual_atk -= ally_summ.bold_def
            enemy_summ.bold_def = 0
        else:
            ally_summ.subdual_atk = 0
            enemy_summ.bold_def = 0

        if enemy_summ.sly_def > ally_summ.subdual_atk:
            enemy_summ.sly_def -= ally_summ.subdual_atk
            ally_summ.subdual_atk = 0
        elif enemy_summ.sly_def < ally_summ.subdual_atk:
            ally_summ.subdual_atk -= ally_summ.sly_def
            enemy_summ.sly_def = 0
        else:
            ally_summ.subdual_atk = 0
            enemy_summ.sly_def = 0

        damage_to_enemy = ally_summ.bold_atk + ally_summ.sly_atk + ally_summ.subdual_atk
        self.target.hp -= damage_to_enemy
        if self.target.hp <= 0:
            self.target.active = False
            self.target.state = "killed"
            if ally_summ.subdual_atk > 0:
                self.target.state = "subdued"

        for enemy in self.enemy:
            if enemy_summ.subdual_atk > 0:
                enemy_summ.subdual_atk += enemy.oncoming_subdual
                enemy.oncoming_subdual = 0
            if enemy_summ.bold_atk > 0:
                enemy_summ.bold_atk += enemy.oncoming_bold
                enemy.oncoming_bold = 0
            if enemy_summ.sly_atk > 0:
                enemy_summ.sly_atk += enemy.oncoming_sly
                enemy.oncoming_sly = 0

        if ally_summ.bold_def > enemy_summ.bold_atk:
            ally_summ.bold_def -= enemy_summ.bold_atk
            enemy_summ.bold_atk = 0
        elif ally_summ.bold_def < enemy_summ.bold_atk:
            enemy_summ.bold_atk -= enemy_summ.bold_def
            ally_summ.bold_def = 0
        else:
            enemy_summ.bold_atk = 0
            ally_summ.bold_def = 0

        if ally_summ.sly_def > enemy_summ.sly_atk:
            ally_summ.sly_def -= enemy_summ.sly_atk
            enemy_summ.sly_atk = 0
        elif ally_summ.sly_def < enemy_summ.sly_atk:
            enemy_summ.sly_atk -= enemy_summ.sly_def
            ally_summ.sly_def = 0
        else:
            enemy_summ.sly_atk = 0
            ally_summ.sly_def = 0

        if ally_summ.subdual_def > enemy_summ.subdual_atk:
            ally_summ.subdual_def -= enemy_summ.subdual_atk
            enemy_summ.subdual_atk = 0
        elif ally_summ.subdual_def < enemy_summ.subdual_atk:
            enemy_summ.subdual_atk -= enemy_summ.subdual_def
            enemy_summ.subdual_def = 0
        else:
            enemy_summ.subdual_atk = 0
            ally_summ.subdual_def = 0

        if ally_summ.total_def > enemy_summ.bold_atk:
            ally_summ.total_def -= enemy_summ.bold_atk
            enemy_summ.bold_atk = 0
        elif ally_summ.total_def < enemy_summ.bold_atk:
            enemy_summ.bold_atk -= enemy_summ.total_def
            ally_summ.total_def = 0
        else:
            enemy_summ.bold_atk = 0
            ally_summ.total_def = 0

        if ally_summ.total_def > enemy_summ.sly_atk:
            ally_summ.total_def -= enemy_summ.sly_atk
            enemy_summ.sly_atk = 0
        elif ally_summ.total_def < enemy_summ.sly_atk:
            enemy_summ.sly_atk -= enemy_summ.total_def
            ally_summ.total_def = 0
        else:
            enemy_summ.sly_atk = 0
            ally_summ.total_def = 0

        if ally_summ.total_def > enemy_summ.subdual_atk:
            ally_summ.total_def -= enemy_summ.subdual_atk
            enemy_summ.subdual_atk = 0
        elif ally_summ.total_def < enemy_summ.subdual_atk:
            enemy_summ.subdual_atk -= enemy_summ.total_def
            ally_summ.total_def = 0
        else:
            enemy_summ.subdual_atk = 0
            ally_summ.total_def = 0

        if ally_summ.bold_def > enemy_summ.subdual_atk:
            ally_summ.bold_def -= enemy_summ.subdual_atk
            enemy_summ.subdual_atk = 0
        elif ally_summ.bold_def < enemy_summ.subdual_atk:
            enemy_summ.subdual_atk -= enemy_summ.bold_def
            ally_summ.bold_def = 0
        else:
            enemy_summ.subdual_atk = 0
            ally_summ.bold_def = 0

        if ally_summ.sly_def > enemy_summ.subdual_atk:
            ally_summ.sly_def -= enemy_summ.subdual_atk
            enemy_summ.subdual_atk = 0
        elif ally_summ.sly_def < enemy_summ.subdual_atk:
            enemy_summ.subdual_atk -= enemy_summ.sly_def
            ally_summ.sly_def = 0
        else:
            enemy_summ.subdual_atk = 0
            ally_summ.sly_def = 0

        damage_to_ally = enemy_summ.bold_atk + enemy_summ.sly_atk + enemy_summ.subdual_atk
        self.actor.hp -= damage_to_ally
        if self.actor.hp <= 0:
            self.actor.active = False
            self.actor.state = "wounded"
            if enemy_summ.subdual_atk > 0:
                self.actor.state = "subdued"



class FFEAction(object):
    """
    This is a class for "action cards" to form a decks and use in FaFiEn.
    """
    def __init__(self, name):
        self.name = name
        self.description = ""       # Mostly not used, but needed when action is not standard
        self.subdual_atk = 0        # Soft type of attack, can be blocked by anything but do not kill opponent
        self.bold_atk = 0           # First type of lethal damage attack
        self.sly_atk = 0            # Second type of lethal damage attack
        self.ongoing_dmg = 0        # Opponent get X damage / round
        self.oncoming_subdual = 0   # Next action with subdual_atk gains additional oncoming_subdual attack
        self.oncoming_bold = 0      # Next action with bold_atk gains additional bold_subdual attack
        self.oncoming_sly = 0       # Next action with sly_atk gains additional sly_subdual attack
        self.subdual_def = 0        # Tis type of defence protects fom subdual_atk
        self.bold_def = 0           # Tis type of defence protects fom subdual_atk and bold_atk
        self.sly_def = 0            # Tis type of defence protects fom subdual_atk and sly_atk
        self.total_def = 0          # Tis type of defence protects fom every type of atk
        self.recovery = 0           # Recovers HP
        self.regenerate = 0         # Author recovers X hp / round
        self.backlash = 0           # Author gets damage to himself
        self.tactical = 0           # if Hero: he gets additional actions up to max. if NPC: hero discards acrions up to 1
        self.trickery = False       # if Hero: choose next enemy action from two nearest actions in a row, discard other. if NPC: shuffle into Heroes deck "Confusion" action
        self.unblockable = False    # This action attacks cannot be blocked
        self.fast = False           # This action resolves before main action resolve phase
        self.slow = False           # This action resolves after main action resolve phase
        self.on_hit = False         # This action has special effect if and when damage successfully dealt to enemy
        self.use_up = False         # Uses some item or resource then discards permanently

        if self.name == "Confusion":  # This action does nothing at all
            pass
        if self.name == "Scratch":
            self.subdual_atk = 1
        if self.name == "Bitch-slap":
            self.subdual_atk = 1
        if self.name == "Bite":
            self.subdual_atk = 1
        if self.name == "Cover in fear":
            self.total_def = 1
        if self.name == "Squawk":
            self.oncoming_subdual = 1
        if self.name == "Punch":
            self.subdual_atk = 1
        if self.name == "Kick":
            self.subdual_atk = 2
        if self.name == "Arm block":
            self.subdual_def = 2
        if self.name == "Bull-rush":
            self.subdual_atk = 3
            self.backlash = 1
        if self.name == "Counterblow":
            self.subdual_def = 1
            self.subdual_atk = 1

    def addup(self, action):
        self.subdual_atk += action.subdual_atk
        self.bold_atk += action.bold_atk
        self.sly_atk += action.sly_atk
        self.ongoing_dmg += action.ongoing_dmg
        self.oncoming_subdual += action.oncoming_subdual
        self.oncoming_bold += action.oncoming_bold
        self.oncoming_sly += action.oncoming_sly
        self.subdual_def += action.subdual_def
        self.bold_def += action.bold_def
        self.sly_def += action.sly_def
        self.total_def += action.total_def
        self.recovery += action.recovery
        self.regenerate += action.regenerate
        self.backlash += action.backlash
        self.tactical += action.tactical
        self.trickery += action.trickery
        self.unblockable += action.unblockable
        self.fast += action.fast
        self.slow += action.slow
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
        self.oncoming_subdual = 0       # Bonus damage to next subdual
        self.oncoming_bold = 0          # Bonus damage to next bold
        self.oncoming_sly = 0           # Bonus damage to next sly
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

