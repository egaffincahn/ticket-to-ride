# separate files
# class individual
# raise exception
# SPEED UP
    # get random weights once - should have a function that uses number_of_cluster_reps to return number of total weights
# necessary:
    # add longest road
    #

import networkx as nx
import numpy as np
from datetime import datetime as dt
from utils import *
import ticket_to_ride.game as game

# http://cs231n.github.io/python-numpy-tutorial/
# https://numpy.org/devdocs/user/numpy-for-matlab-users.html
# exec(open('ticket_to_ride.py').read())

# python3 -m cProfile -s 'cumtime' ticket_to_ride.py > profile.txt
# cProfile.run('play_game(players)')
#

players = 3
plot = True

# fobj = open('log.txt', 'w')
log = Log()
log.open()
log.write(['started at ', dt.now()])
# utils.write_log(cmd='open', file='log.txt')
# utils.write_log(lines=['started at ', dt.now()])
game_map, game_info, game_cards, game_strategies = game.play_game(players, plot)
# utils.write_log(fobj=fobj, lines=['finished at ', dt.now()])
# fobj.close()
# utils.write_log(fobj=fobj, cmd='close')
print('finished')
