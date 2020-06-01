from datetime import datetime as dt
import numpy as np
from ticket.population import Population
from ticket.game import Game


num_test = 0
turn = 0
turn_ = 1
pop = Population(players=3)


def test(test_num, edges, expected_length, expected_points=[10, 0, 0], edges_=None):
    game = Game(pop.cohort)
    [game.map.lay_track(turn, game.map.get_edge_index(e)) for e in edges]
    if edges_ is not None:
        [game.map.lay_track(turn_, game.map.get_edge_index(e)) for e in edges_]
    tStart = dt.now()
    game.add_longest_track()
    tFinish = dt.now()
    if game.longest_track_length != expected_length or np.any(np.not_equal(game.points, expected_points)):
        game.map.plot_graph(turn)
        raise Exception('failed test {}:\nexpected len {}, counted {}\nexpected pts {}, counted {}'.format(
            test_num, expected_length, game.longest_track_length, expected_points, game.points))
    else:
        print('passed test {}: {}'.format(test_num, tFinish - tStart))
    return tFinish - tStart


# single track
num_test += 1
edges = [('Vancouver', 'Calgary', 0)]  # +3
test(num_test, edges, 3)

# string of tracks
num_test += 1
edges = [
    ('Seattle', 'Calgary', 0),  # +4
    ('Calgary', 'Winnipeg', 0),  # +6
    ('Winnipeg', 'Duluth', 0)  # +4
]
test(num_test, edges, 14)

# loop
num_test += 1
edges = [
    ('Boston', 'Montreal', 0),  # +2
    ('Montreal', 'New York', 0),  # +3
    ('New York', 'Boston', 0)  # +2
]
test(num_test, edges, 7)

# loop + tail
num_test += 1
edges = [
    ('Boston', 'Montreal', 0),  # +2
    ('Montreal', 'New York', 0),  # +3
    ('New York', 'Boston', 0),  # +2
    ('Sault St. Marie', 'Montreal', 0),  # +5
    ('Sault St. Marie', 'Duluth', 0),  # +3
]
test(num_test, edges, 15)

# multiple unconnected subgraphs
num_test += 1
edges = [
    ('Calgary', 'Helena', 0),  # +4
    ('Seattle', 'Helena', 0),  # +6
    ('Seattle', 'Portland', 0),  # +1
    ('Portland', 'San Francisco', 0),  # +5
    ('Seattle', 'Calgary', 0),  # +4
    ('San Francisco', 'Salt Lake City', 0),  # +5
    ('Boston', 'New York', 0),  # 2
    ('Montreal', 'Boston', 0),  # 2
    ('Washington', 'New York', 0)  # 2
]
test(num_test, edges, 25)

# one winner
num_test += 1
edges = [
    ('Seattle', 'Vancouver', 0)  # 1
]
edges_ = [
    ('Calgary', 'Helena', 0)  # +4
]
test(num_test, edges, 4, expected_points=[0, 10, 0], edges_=edges_)

# tie
num_test += 1
edges = [
    ('Calgary', 'Helena', 0)  # +4
]
edges_ = [
    ('Denver', 'Kansas City', 0)  # +4
]
test(num_test, edges, 4, expected_points=[10, 10, 0], edges_=edges_)


# 1-1 fork
num_test += 1
edges = [
    ('Calgary', 'Helena', 0),  # (+)4
    ('Helena', 'Duluth', 0),  # +6
    ('Helena', 'Denver', 0)  # (+)4
]
test(num_test, edges, 10)

# 2-1 fork
num_test += 1
edges = [
    ('Calgary', 'Helena', 0),  # 4
    ('Helena', 'Duluth', 0),  # +6
    ('Helena', 'Denver', 0),  # +4
    ('Denver', 'Omaha', 0)  # +4
]
test(num_test, edges, 14)

# three forks
num_test += 1
edges = [
    ('Vancouver', 'Seattle', 0),  # 1
    ('Seattle', 'Portland', 0),  # +1
    ('Portland', 'San Francisco', 0),  # +5
    ('San Francisco', 'Los Angeles', 0),  # 3
    ('Seattle', 'Calgary', 0),  # +4
    ('San Francisco', 'Salt Lake City', 0)  # +5
]
test(num_test, edges, 15)

# non-included fork off loop
num_test += 1
edges = [
    ('Vancouver', 'Calgary', 0),  # 3
    ('Calgary', 'Helena', 0),  # +4
    ('Seattle', 'Helena', 0),  # +6
    ('Seattle', 'Portland', 0),  # +1
    ('Portland', 'San Francisco', 0),  # +5
    ('Seattle', 'Calgary', 0),  # +4
    ('San Francisco', 'Salt Lake City', 0)  # +5
]
test(num_test, edges, 25)

# non-included loop off fork
num_test += 1
edges = [
    ('Seattle', 'Vancouver', 0),  # 1
    ('Vancouver', 'Calgary', 0),  # 3
    ('Calgary', 'Helena', 0),  # +4
    ('Duluth', 'Helena', 0),  # +6
    ('Seattle', 'Portland', 0),  # +1
    ('Portland', 'San Francisco', 0),  # +5
    ('Seattle', 'Calgary', 0),  # +4
    ('San Francisco', 'Salt Lake City', 0)  # +5
]
test(num_test, edges, 25)

# double loop
num_test += 1
edges = [
    ('Houston', 'New Orleans', 0),  # +2
    ('New Orleans', 'Atlanta', 0),  # +4
    ('Atlanta', 'Nashville', 0),  # +1
    ('Nashville', 'Little Rock', 0),  # +3
    ('Little Rock', 'Dallas', 0),  # +2
    ('Dallas', 'Houston', 0),  # +1
    ('Dallas', 'Oklahoma City', 0),  # +2
    ('Oklahoma City', 'Kansas City', 0),  # +2
    ('Kansas City', 'Saint Louis', 0),  # +2
    ('Saint Louis', 'Pittsburgh', 0),  # +5
    ('Pittsburgh', 'Nashville', 0)  # +4
]
test(num_test, edges, 28)

# double loop with fork
num_test += 1
edges = [
    ('Houston', 'New Orleans', 0),  # +2
    ('New Orleans', 'Atlanta', 0),  # +4
    ('Atlanta', 'Nashville', 0),  # +1
    ('Nashville', 'Little Rock', 0),  # +3
    ('Little Rock', 'Dallas', 0),  # +2
    ('Dallas', 'Houston', 0),  # +1
    ('Dallas', 'Oklahoma City', 0),  # +2
    ('Oklahoma City', 'Kansas City', 0),  # +2
    ('Kansas City', 'Saint Louis', 0),  # +2
    ('Saint Louis', 'Pittsburgh', 0),  # +5
    ('Pittsburgh', 'Nashville', 0),  # +4
    ('Kansas City', 'Omaha', 0)  # 1
]
test(num_test, edges, 28)

# fork with double loop, one loop unused
num_test += 1
edges = [
    ('Houston', 'New Orleans', 0),  # 2
    ('New Orleans', 'Atlanta', 0),  # +4
    ('Atlanta', 'Nashville', 0),  # +1
    ('Nashville', 'Little Rock', 0),  # +3
    ('Little Rock', 'Dallas', 0),  # +2
    ('Dallas', 'Houston', 0),  # 1
    ('Dallas', 'Oklahoma City', 0),  # +2
    ('Oklahoma City', 'Kansas City', 0),  # +2
    ('Kansas City', 'Saint Louis', 0),  # +2
    ('Saint Louis', 'Pittsburgh', 0),  # +5
    ('Pittsburgh', 'Nashville', 0),  # +4
    ('New Orleans', 'Miami', 0)  # +6
]
test(num_test, edges, 31)

# long track with forking loops, forks off loops, double loops
num_test += 1
edges = [('Seattle', 'Portland', 0), ('Portland', 'Salt Lake City', 0), ('Salt Lake City', 'San Francisco', 0),
         ('Portland', 'San Francisco', 0), ('San Francisco', 'Los Angeles', 0), ('Los Angeles', 'Phoenix', 0),
         ('Phoenix', 'Santa Fe', 0), ('Santa Fe', 'Denver', 0), ('Denver', 'Phoenix', 0),
         ('Los Angeles', 'El Paso', 0), ('El Paso', 'Houston', 0), ('Houston', 'Dallas', 0),
         ('Dallas', 'Oklahoma City', 0), ('Oklahoma City', 'Kansas City', 0), ('Kansas City', 'Omaha', 0),
         ('Omaha', 'Chicago', 0), ('Chicago', 'Pittsburgh', 0), ('Pittsburgh', 'Nashville', 0),
         ('Nashville', 'Little Rock', 0), ('Little Rock', 'Dallas', 0), ('Houston', 'New Orleans', 0),
         ('New Orleans', 'Atlanta', 0), ('Nashville', 'Atlanta', 0), ('Atlanta', 'Miami', 0)]
test(num_test, edges, 59)

# long track with forking loops, forks off loops, double loops, connected
num_test += 1
edges = [('Seattle', 'Portland', 0), ('Portland', 'Salt Lake City', 0), ('Salt Lake City', 'San Francisco', 0),
         ('Portland', 'San Francisco', 0), ('San Francisco', 'Los Angeles', 0), ('Los Angeles', 'Phoenix', 0),
         ('Phoenix', 'Santa Fe', 0), ('Santa Fe', 'Denver', 0), ('Denver', 'Phoenix', 0),
         ('Los Angeles', 'El Paso', 0), ('El Paso', 'Houston', 0), ('Houston', 'Dallas', 0),
         ('Dallas', 'Oklahoma City', 0), ('Oklahoma City', 'Kansas City', 0), ('Kansas City', 'Omaha', 0),
         ('Omaha', 'Chicago', 0), ('Chicago', 'Pittsburgh', 0), ('Pittsburgh', 'Nashville', 0),
         ('Nashville', 'Little Rock', 0), ('Little Rock', 'Dallas', 0), ('Houston', 'New Orleans', 0),
         ('New Orleans', 'Atlanta', 0), ('Nashville', 'Atlanta', 0), ('Atlanta', 'Miami', 0),
         ('Salt Lake City', 'Helena', 0), ('Helena', 'Omaha', 0)]
test(num_test, edges, 67)


print('passed all tests')
