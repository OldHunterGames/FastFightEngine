# -*- coding: <UTF-8> -*-
from random import *
from ffe_engine import *
from ffe_actions import *
from ffe_data import *
import renpy.store as store
import renpy.exports as renpy


class Person(object):
    """
    This is a class for a base character, to be converted into a FFCombatant
    """
    def __init__(self, name, style):
        self.name = name
        self.avatar = "images/ava/witcher.jpg"
        self.ff_combat_style = style
        self.physique = 3
        self.agility = 3
        self.spirit = 3
        self.mind = 3
        if name == "Slave":
            self.avatar = "images/ava/slave.jpg"


