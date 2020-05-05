import numpy as np
import networkx as nx
import pickle
from itertools import product
from ticket_to_ride.core import Map, Cards, Strategy


def write_adjacencies(players):

    blank_map = Map(players)
    reps = nx.diameter(blank_map.map) + 1

    adjacent_edges_int = [[[] for _ in range(blank_map.number_of_nodes)] for _ in range(reps)]
    adjacent_nodes_int = [[[] for _ in range(blank_map.number_of_edges)] for _ in range(reps)]
    for rep in range(reps):
        for n in range(blank_map.number_of_nodes):
            adjacent_edges_int[rep][n] = blank_map.get_adjacent_edges_slow(n, reps=rep, dtype=int)
        for e in range(blank_map.number_of_edges):
            adjacent_nodes_int[rep][e] = blank_map.get_adjacent_nodes_slow(e, reps=rep, dtype=int)

    adjacent_edges_tuple = [dict() for _ in range(reps)]
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


def write_masks(players):

    s = Strategy(players)

    s.blank_cards = Cards(s.players)

    layer_indices = dict()
    layer_indices['nodes'] = np.arange(s.number_of_nodes * s.number_of_cluster_reps)
    layer_indices['colors'] = s.next_ind(layer_indices) + np.arange(s.number_of_colors * s.number_of_cluster_reps)
    layer_indices['parallel'] = s.next_ind(layer_indices) + np.arange(s.number_of_parallel * s.number_of_cluster_reps)
    layer_indices['distances'] = s.next_ind(layer_indices) + np.arange(s.number_of_distances * s.number_of_cluster_reps)
    layer_indices['edges'] = np.arange(s.number_of_edges * s.number_of_cluster_reps)  # start again at 0

    ind2repind = lambda ind: ind * s.number_of_cluster_reps + np.arange(s.number_of_cluster_reps, dtype=np.int8)

    # inputs onto layer 0

    nrow = 1 + s.players * 2 + (s.players - 1) + s.number_of_colors * 2 + s.number_of_goals + s.number_of_edges
    ncol = (s.number_of_nodes + s.number_of_colors + s.number_of_parallel + s.number_of_distances) * s.number_of_cluster_reps
    mask = np.zeros((nrow, ncol), dtype=bool)

    # bias
    row = np.concatenate((
        s.input_indices['bias'],
        s.input_indices['turn_pieces'],
        s.input_indices['oppnt_pieces'],
        s.input_indices['turn_points'],
        s.input_indices['oppnt_points'],
        s.input_indices['oppnt_hand_lengths']
    ))
    mask[row,] = True

    # from colors (both)
    for c in range(s.number_of_colors):
        col = layer_indices['colors'][ind2repind(c)]

        row = s.input_indices['faceups'][c]
        mask[row, col] = True

        row = s.input_indices['hand_colors'][c]
        mask[row, col] = True

    # from goals
    for g in range(s.number_of_goals):
        for n in [0, 1]:
            n_ = s.blank_map.get_node_index(s.blank_cards.goals_init.iloc[g, n])
            col = layer_indices['nodes'][ind2repind(n_)]
            row = s.input_indices['goals'][g]
            mask[row, col] = True

    # from edges
    for e in range(s.number_of_edges):
        row = s.input_indices['edges'][e]

        # onto nodes
        nodes = s.blank_map.get_adjacent_nodes(e)
        for n in nodes:
            col = layer_indices['nodes'][ind2repind(n)]
            mask[row, col] = True

        # onto colors
        ind = s.blank_map.extract_feature(e, 'color')
        col = layer_indices['colors'][ind2repind(ind)]
        mask[row, col] = True

        # onto parallel
        ind = s.blank_map.extract_feature(e, 'parallel')
        col = layer_indices['parallel'][ind2repind(ind)]
        mask[row, col] = True

        # onto distances
        ind = s.blank_map.extract_feature(e, 'distance') - 1
        col = layer_indices['distances'][ind2repind(ind)]
        mask[row, col] = True

    M0 = mask

    # REPS:

    def expand(row, col):
        return tuple(np.array(tuple(product(row, col))).T.tolist())

    M1 = [[[] for _ in range(2)] for _ in range(s.reps)]

    for rep in range(s.reps):

        nrow = (s.number_of_nodes + s.number_of_colors + s.number_of_parallel + s.number_of_distances) * s.number_of_cluster_reps
        ncol = s.number_of_edges * s.number_of_cluster_reps
        mask = np.zeros((nrow + 1, ncol), dtype=bool)

        # bias
        mask[0,] = True

        # from Nodes
        for n in range(s.number_of_nodes):
            row = layer_indices['nodes'][ind2repind(n)] + 1  # add 1 bc layer indices does not include bias
            col = np.concatenate([ind2repind(e) for e in s.blank_map.get_adjacent_edges(n, reps=rep)])
            mask[expand(row, col)] = True

        # from Colors
        for c in range(s.number_of_colors):
            row = layer_indices['colors'][ind2repind(c)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('color', c, dtype=int)])
            mask[expand(row, col)] = True

        # from Parallel
        for p in range(s.number_of_parallel):
            row = layer_indices['parallel'][ind2repind(p)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('parallel', p, dtype=int)])
            mask[expand(row, col)] = True

        # from Distances
        for d in range(s.number_of_distances):
            row = layer_indices['distances'][ind2repind(d)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('distance', d + 1, dtype=int)])
            mask[expand(row, col)] = True

        M1[rep][0] = mask

        mask = np.zeros((ncol + 1, nrow), dtype=bool)

        # bias
        mask[0,] = True

        # from Edges
        for e in range(s.number_of_edges):
            row = layer_indices['edges'][ind2repind(e)] + 1

            # onto nodes
            nodes = s.blank_map.get_adjacent_nodes(e)
            for n in nodes:
                col = layer_indices['nodes'][ind2repind(n)]
                mask[expand(row, col)] = True

            # onto colors
            ind = s.blank_map.extract_feature(e, 'color')
            col = layer_indices['colors'][ind2repind(ind)]
            mask[expand(row, col)] = True

            # onto parallel
            ind = s.blank_map.extract_feature(e, 'parallel')
            col = layer_indices['parallel'][ind2repind(ind)]
            mask[expand(row, col)] = True

            # onto distances
            ind = s.blank_map.extract_feature(e, 'distance') - 1
            col = layer_indices['distances'][ind2repind(ind)]
            mask[expand(row, col)] = True

        M1[rep][1] = mask

    # post-reps

    # from edges, colors, parallel, distance to edges, colors
    nrow = (s.number_of_nodes + s.number_of_colors + s.number_of_parallel + s.number_of_distances) * s.number_of_cluster_reps + 1
    ncol = (s.number_of_edges + s.number_of_colors) * s.number_of_cluster_reps
    M2 = np.ones((nrow, ncol), dtype=bool)

    # from edges, colors to edges, goals, deck, faceups
    nrow = ncol + 1
    ncol = s.number_of_edges + 1 + 1 + 5
    M3 = np.ones((nrow, ncol), dtype=bool)

    with open("ticket_to_ride/data/masks.obj", "wb") as f:
        pickle.dump(M0, f)
        pickle.dump(M1, f)
        pickle.dump(M2, f)
        pickle.dump(M3, f)
