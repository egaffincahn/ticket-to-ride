# import numpy as np
# import networkx as nx
import pickle
from os.path import join
# from itertools import product
# from ticket.board import Map, Cards
# from ticket.strategy import Strategy


data_location = join('ticket', 'data')

goals_file = join(data_location, 'goals.txt')
coordinates_file = join(data_location, 'coordinates.txt')
map_file = join(data_location, 'map.txt')

adjacency_file = join(data_location, 'adjacent.obj')
masks_file = join(data_location, 'masks.obj')

log_file = join(data_location, 'log.txt')
output_file = join(data_location, 'data.obj')


def read_adjacencies():
    with open(adjacency_file, 'rb') as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str


def read_masks():
    with open(masks_file, 'rb') as f:
        M = pickle.load(f)
        number_of_cluster_reps = pickle.load(f)
    return M, number_of_cluster_reps


def extract_cluster_reps():
    _, number_of_cluster_reps = read_masks()
    return number_of_cluster_reps

