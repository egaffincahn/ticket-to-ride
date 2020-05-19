import logging
import pickle
import bz2
import gzip
import os
from os.path import join


data_location = join('ticket', 'data')

goals_file = join(data_location, 'goals.txt')
coordinates_file = join(data_location, 'coordinates.txt')
map_file = join(data_location, 'map.txt')

adjacency_file = join(data_location, 'adjacent.obj')
masks_file = join(data_location, 'masks.obj')

log_file = join(data_location, 'log.txt')


def get_output_file(filename=None):
    if filename is not None:
        return filename
    _external = join(os.sep, 'Volumes', 'EGs WD')
    if os.path.exists(_external):
        return join(_external, 'data.obj')
    else:
        return join(data_location, 'data.obj')


def read_adjacencies():
    with bz2.open(adjacency_file, 'rb') as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str


def read_masks():
    with bz2.open(masks_file, 'rb') as f:
        mask = pickle.load(f)
        number_of_cluster_reps = pickle.load(f)
    return mask, number_of_cluster_reps


def extract_cluster_reps():
    _, number_of_cluster_reps = read_masks()
    return number_of_cluster_reps


def read_population():
    with gzip.open(get_output_file(), 'rb') as f:
        logging.critical('reading from {}'.format(get_output_file()))
        return pickle.load(f)
