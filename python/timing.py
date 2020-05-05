from datetime import datetime as dt
import numpy as np
from scipy import sparse
from itertools import chain
# import timeit
#
# number = 100
# timeit.timeit(funA, number=number)
# timeit.timeit(funB, number=number)
# from ticket_to_ride.core import Map, Info, Cards, Strategy
#
# game_info = Info(3)
# game_cards = Cards(3)
# game_cards.initialize_game()
# game_map = Map(3)
# self = Strategy(3)
# self.init_weights()
# self.update_inputs("all", game_info, game_cards, game_map)
# y = np.tanh(np.matmul(self.inputs, self.W0))
# Y = self.catbias(y)
# W = self.W1[0][0]

M_sparse = sparse.random(100,100,1)
M = M_sparse.toarray()

def funA():
    np.matmul(M, M)

def funB():
    M_sparse * M_sparse

def testfun(fun):
    fun()


number = 100
funs = [funA, funB]
t = [[-1 for _ in range(number)] for _ in range(len(funs))]
for i in range(number):
    for f in range(len(funs)):
        tStart = dt.now()
        z = testfun(funs[f])
        t[f][i] = dt.now() - tStart

print("funs", [funs[f].__name__ for f in range(len(funs))])
print([np.sum(t[f]).total_seconds() for f in range(len(funs))])


# exec(open("timing.py").read())

