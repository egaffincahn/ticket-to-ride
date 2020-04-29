import networkx as nx
import pickle
from datetime import datetime as dt
# import ticket_to_ride.utils

class Log:

    def __init__(self):
        pass

    def open(self, file='log.txt'):
        self.fobj = open(file, 'w')
        self.write(['initialized log at ', dt.now()])

    def close(self):
        self.fobj.close()

    def write(self, lines):
        [self.fobj.write(str(lines[l])) for l in range(len(lines))]
        self.fobj.write("\n")

    # end write_log

def write_adjacencies():

    blank_map = Map(players)
    reps = nx.diameter(blank_map.map) + 1

    adjacent_edges_int = [[[] for _ in range(blank_map.number_of_nodes)] for _ in range(reps)]
    adjacent_nodes_int = [[[] for _ in range(blank_map.number_of_edges)] for _ in range(reps)]
    for rep in range(reps):
        for n in range(blank_map.number_of_nodes):
            adjacent_edges_int[rep][n] = blank_map.get_adjacent_edges_slow(n, reps=rep, dtype=int)
        for e in range(blank_map.number_of_edges):
            adjacent_nodes_int[rep][e] = blank_map.get_adjacent_nodes_slow(e, reps=rep, dtype=int)

    # adjacent_edges_tuple = [[dict() for _ in range(blank_map.number_of_nodes)] for _ in range(reps)]
    adjacent_edges_tuple = [dict() for _ in range(reps)]
    # adjacent_nodes_str = [[dict() for _ in range(blank_map.number_of_edges)] for _ in range(reps)]
    adjacent_nodes_str = [dict() for _ in range(reps)]
    for rep in range(reps):
        for node in blank_map.nodes:
            adjacent_edges_tuple[rep][node] = blank_map.get_adjacent_edges_slow(node, reps=rep, dtype=tuple)
        for edge in blank_map.edges:
            adjacent_nodes_str[rep][edge] = blank_map.get_adjacent_nodes_slow(edge, reps=rep, dtype=str)

    with open("ticket_to_ride/data/adjacent.obj", "wb") as f:
        pickle.dump(adjacent_edges_int, f)
        pickle.dump(adjacent_nodes_int, f)
        pickle.dump(adjacent_edges_tuple, f)
        pickle.dump(adjacent_nodes_str, f)

def read_adjacencies():
    with open("ticket_to_ride/data/adjacent.obj", "rb") as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str
