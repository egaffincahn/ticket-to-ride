import numpy as np
import numpy.random as rd
from ticket_to_ride.core import Strategy
from ticket_to_ride.game import play_game


def run_all(generations=1, individuals=3, players=3):
    strategies = [Strategy(players, seed=i) for i in range(individuals)]
    [strategies[i].init_weights() for i in range(individuals)]
    points = np.empty((generations, individuals), dtype=np.int8)
    for g in range(generations):
        strategies, pts = run_generation(strategies, players)
        strategies = recombine(strategies, players)
        points[g,:] = pts.ravel()
    return points

def run_generation(strategies, players):
    individuals = len(strategies)
    sets = np.int8(individuals/players)
    order = rd.permutation(individuals).reshape(players, sets)
    losers = np.empty(sets, dtype=np.int8)
    points = np.empty((players,sets), dtype=np.int8)
    for s in range(sets):
        _,game_info,_,_ = play_game(players, [strategies[order[turn, s]] for turn in range(players)])
        losers[s] = order[np.argmin(game_info.points), s]
        points[:,s] = game_info.points
    strategies = np.delete(strategies, losers)
    return strategies, points


def recombine(parents, players):
    individuals = len(parents)
    pairs = np.int8(individuals / 2)
    order = rd.permutation(individuals).reshape(2, pairs)
    children = [Strategy(players, seed=p) for p in range(pairs)]
    for p in range(pairs):
        children[p].init_weights(parents[order[0,p]], parents[order[1,p]])
    return np.concatenate((parents, children))


