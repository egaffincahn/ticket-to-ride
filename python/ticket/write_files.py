import numpy as np
import networkx as nx
import pickle
from itertools import product
from ticket import utils
from ticket.board import Map, Cards
from ticket.strategy import Strategy


def write_adjacencies():
    blank_map = Map()
    reps = nx.diameter(blank_map.map) + 1

    adjacent_edges_int = [[[] for _ in range(blank_map.NUM_NODES)] for _ in range(reps)]
    adjacent_nodes_int = [[[] for _ in range(blank_map.NUM_EDGES)] for _ in range(reps)]
    for rep in range(reps):
        for n in range(blank_map.NUM_NODES):
            adjacent_edges_int[rep][n] = get_adjacent_edges_slow(blank_map, n, reps=rep, dtype=int)
        for e in range(blank_map.NUM_EDGES):
            adjacent_nodes_int[rep][e] = get_adjacent_nodes_slow(blank_map, e, reps=rep, dtype=int)

    adjacent_edges_tuple = [dict() for _ in range(reps)]
    adjacent_nodes_str = [dict() for _ in range(reps)]
    for rep in range(reps):
        for node in blank_map.nodes:
            adjacent_edges_tuple[rep][node] = get_adjacent_edges_slow(blank_map, node, reps=rep, dtype=tuple)
        for edge in blank_map.edges:
            adjacent_nodes_str[rep][edge] = get_adjacent_nodes_slow(blank_map, edge, reps=rep, dtype=str)

    with open(utils.adjacency_file, 'wb') as f:
        pickle.dump(adjacent_edges_int, f)
        pickle.dump(adjacent_nodes_int, f)
        pickle.dump(adjacent_edges_tuple, f)
        pickle.dump(adjacent_nodes_str, f)


def get_adjacent_nodes_slow(edge, reps=0, **kwargs):
    blank_map = Map()
    dtype_in = type(edge)
    if dtype_in == tuple or dtype_in == list:
        dtype_in = str
    if 'dtype' in kwargs:
        dtype_out = kwargs['dtype']
    else:
        dtype_out = dtype_in
    if dtype_in == str:
        edge = blank_map.get_edge_index(edge)

    _, shortest_path_length_int = get_shortest_paths()

    nodes0 = [blank_map.get_node_index(n) for n in blank_map.get_edge_name(edge)[:2]]
    nodes = []
    for n in range(2):
        within_reps = np.array(list(shortest_path_length_int[nodes0[n]].values())) <= reps
        nodes.extend(list(np.array(list(shortest_path_length_int[nodes0[n]].keys()))[within_reps]))
        nodes = blank_map.unique(nodes=nodes)

    if dtype_out == str:
        nodes = [blank_map.get_node_name(n) for n in nodes]
    else:
        nodes = np.array(nodes)
    return nodes


def get_adjacent_edges_slow(blank_map, node, reps=0, **kwargs):
    dtype_in = type(node)
    if 'dtype' in kwargs:
        dtype_out = kwargs['dtype']
    else:
        dtype_out = dtype_in
    if dtype_in != str:
        node = blank_map.get_node_name(node)

    shortest_path_length, _ = get_shortest_paths()

    edges = []
    for e in blank_map.edges:
        if shortest_path_length[e[0]][node] <= reps or shortest_path_length[e[1]][node] <= reps:
            edges.append(e)

    if dtype_out == int:
        edges = [blank_map.get_edge_index(e) for e in edges]
    else:
        edges = [blank_map.reorder_edge(e) for e in edges]
    return edges


def get_shortest_paths():
    blank_map = Map()
    spl = dict(nx.shortest_path_length(blank_map.map))
    spl_int = {}
    for (n, length_dict) in spl.items():
        node_dict = {}
        for (n_, length) in length_dict.items():
            node_dict[blank_map.get_node_index(n_)] = length
        spl_int[blank_map.get_node_index(n)] = node_dict
    spl_int = spl_int
    shortest_path = dict(nx.shortest_path(blank_map.map))
    return spl, spl_int


def write_masks(number_of_cluster_reps=50):

    fun = lambda x: .03 * x + .09 * x ** 2
    print("Predicted size of masks.obj:", fun(number_of_cluster_reps), "mb")

    s = Strategy()
    s.blank_cards = Cards()
    s.blank_map = Map()

    if number_of_cluster_reps is not None:
        s.number_of_cluster_reps = number_of_cluster_reps

    next_ind = lambda x: np.max(np.concatenate((list(x.values()))), keepdims=True) + 1

    layer_indices = dict()
    layer_indices['nodes'] = np.arange(s.NUM_NODES * s.number_of_cluster_reps)
    layer_indices['colors'] = next_ind(layer_indices) + np.arange(s.NUM_COLORS * s.number_of_cluster_reps)
    layer_indices['parallel'] = next_ind(layer_indices) + np.arange(s.NUM_PARALLEL * s.number_of_cluster_reps)
    layer_indices['distances'] = next_ind(layer_indices) + np.arange(s.NUM_DISTANCES * s.number_of_cluster_reps)
    layer_indices['edges'] = np.arange(s.NUM_EDGES * s.number_of_cluster_reps)  # start again at 0

    ind2repind = lambda ind: ind * s.number_of_cluster_reps + np.arange(s.number_of_cluster_reps, dtype=np.int32)
    expand = lambda row, col: tuple(np.array(tuple(product(row, col))).T.tolist())

    M = [[[] for _ in range(2)] for _ in range(s.reps+1)]

    for rep in range(s.reps):

        # ONTO NODES, COLORS, PARALLEL, DISTANCES

        nrow = 1 + s.NUM_EDGES * s.number_of_cluster_reps
        if rep == 0:  # inputs onto layer 0
            nrow = 1 + s.players * 2 + (s.players - 1) + s.NUM_COLORS * 2 + s.NUM_GOALS + s.NUM_EDGES

        ncol = (s.NUM_NODES + s.NUM_COLORS + s.NUM_PARALLEL + s.NUM_DISTANCES) * s.number_of_cluster_reps
        mask = np.zeros((nrow, ncol), dtype=bool)

        mask[0,] = True  # bias

        if rep == 0:
            row = np.concatenate((  # input indices already have bias included
                s.input_indices['turn_pieces'],
                s.input_indices['oppnt_pieces'],
                s.input_indices['turn_points'],
                s.input_indices['oppnt_points'],
                s.input_indices['oppnt_hand_lengths']
            ))
            mask[row,] = True  # inputs that are fully connected

            # from colors (both)
            for c in range(s.NUM_COLORS):
                col = layer_indices['colors'][ind2repind(c)]

                row = s.input_indices['faceups'][c]
                mask[row, col] = True

                row = s.input_indices['hand_colors'][c]
                mask[row, col] = True

            # from goals
            for g in range(s.NUM_GOALS):
                for n in [0, 1]:
                    n_ = s.blank_map.get_node_index(s.blank_cards.goals_init.iloc[g, n])
                    col = layer_indices['nodes'][ind2repind(n_)]
                    row = s.input_indices['goals'][g]
                    mask[row, col] = True

        # end if rep == 0

        # from edges
        for e in range(s.NUM_EDGES):

            if rep == 0:
                row = [s.input_indices['edges'][e]]
            else:
                row = layer_indices['edges'][ind2repind(e)] + 1

            # onto nodes
            nodes = s.blank_map.get_adjacent_nodes(e, reps=rep)
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

        # end for e in edges

        M[rep][0] = mask

        # ONTO EDGES

        nrow = (s.NUM_NODES + s.NUM_COLORS + s.NUM_PARALLEL + s.NUM_DISTANCES) * s.number_of_cluster_reps
        ncol = s.NUM_EDGES * s.number_of_cluster_reps
        mask = np.zeros((nrow + 1, ncol), dtype=bool)

        mask[0,] = True

        # from Nodes
        for n in range(s.NUM_NODES):
            row = layer_indices['nodes'][ind2repind(n)] + 1  # layer_indices does not yet have bias included
            col = np.concatenate([ind2repind(e) for e in s.blank_map.get_adjacent_edges(n, reps=rep)])
            mask[expand(row, col)] = True

        # from Colors
        for c in range(s.NUM_COLORS):
            row = layer_indices['colors'][ind2repind(c)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('color', c, dtype=int)])
            mask[expand(row, col)] = True

        # from Parallel
        for p in range(s.NUM_PARALLEL):
            row = layer_indices['parallel'][ind2repind(p)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('parallel', p, dtype=int)])
            mask[expand(row, col)] = True

        # from Distances
        for d in range(s.NUM_DISTANCES):
            row = layer_indices['distances'][ind2repind(d)] + 1
            col = np.concatenate([ind2repind(e) for e in s.blank_map.subset_edges('distance', d + 1, dtype=int)])
            mask[expand(row, col)] = True

        M[rep][1] = mask

    # end for rep in range(s.reps)

    # from Edges onto Edges, Colors
    nrow = 1 + s.NUM_EDGES * s.number_of_cluster_reps
    ncol = (s.NUM_EDGES + s.NUM_COLORS) * s.number_of_cluster_reps
    mask = np.zeros((nrow, ncol), dtype=bool)

    mask[0,] = True

    for e in range(s.NUM_EDGES):

        row = layer_indices['edges'][ind2repind(e)] + 1  # add 1 bc layer indices does not include bias
        col = layer_indices['edges'][ind2repind(e)]
        mask[expand(row, col)] = True

        ind = s.blank_map.extract_feature(e, 'color')
        col = s.NUM_EDGES * s.number_of_cluster_reps + ind2repind(ind)
        mask[expand(row, col)] = True

    M[rep + 1][0] = mask

    # from edges, colors to edges, goals, deck, faceups
    nrow = ncol + 1
    ncol = s.NUM_EDGES + 1 + 1 + 5
    mask = np.zeros((nrow, ncol), dtype=bool)

    mask[0,] = True  # bias

    # from edges
    for e in range(s.NUM_EDGES):

        # onto edges
        row = layer_indices['edges'][ind2repind(e)] + 1
        col = e
        mask[row,col] = True

        # onto goals
        col = s.NUM_EDGES
        mask[row,col] = True

        # onto colors (skip deck)
        ind = s.blank_map.extract_feature(e, 'color')
        col = s.NUM_EDGES + 2
        mask[row,col] = True

    # from colors
    for c in range(s.NUM_COLORS):

        # onto edges
        row = ind2repind(c) + s.NUM_EDGES * s.number_of_cluster_reps + 1
        col = s.blank_map.subset_edges('color', c, dtype=int)
        mask[expand(row, col)] = True

        # onto deck (skip goals)
        col = s.NUM_EDGES + 1
        mask[row,col] = True

        # onto faceups
        col = np.arange(5) + s.NUM_EDGES + 2
        mask[expand(row,col)] = True


    M[rep + 1][1] = mask

    with open(utils.masks_location, 'wb') as f:
        pickle.dump(M, f)
        pickle.dump(s.number_of_cluster_reps, f)