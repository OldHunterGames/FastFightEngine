# Fast Fight Engine prototype for MER

init -2 python:
    import sys
    sys.path.append(renpy.loader.transfn("scripts"))
    
init -1 python:
    from random import *
    from ffe_data import *
    from ffe_combatants import *
    from ffe_actions import *
   
init python:
    fight = FFEngine([FFCombatant(Person("Witcher", "tester"))], [FFCombatant(Person("Slave", "tester"))])

# The game starts here.
label start:
    show expression "images/bg.jpg" as bg
    $ fight.start()    
    show screen ffe_battle

label user_turn:    
    $ act = fight.actor_move(ui.interact()[1])        
    call expression act
    
    return

label turn_resolution:
    $ act = fight.resolution_phase()
    call expression act
    return
    
label new_turn:
    "New Turn"
    call user_turn
    return

label defeat:
    "Defeat"
    return

label victory:
    "Victory"
    return    
    
