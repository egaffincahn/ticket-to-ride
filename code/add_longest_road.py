import networkx as nx
import copy
import numpy as np


def add_longest_road(game):
    player_dists = np.zeros(game.players, dtype=np.int16)
    player_paths = [[] for _ in range(game.players)]

    for turn in range(game.players):

        H = game.map.create_player_subgraph(turn, multi=True, incl_nodes=True)
        full_adj_mat = nx.adjacency_matrix(H).todense()  # faster than the other methods of making adj matrix
        path = []  # list of lists; each item is a route through each node index
        terminated = []  # list representing whether the path has been fully searched
        trim_adj_mat = []  # list of adjacency matrices that have edges removed
        path_dists = []  # list for this player where each index is the length of a path, only updated once terminated
        found_global_best = False  # tells us if there's a path that has used every connection - allows us to quit early

        for n in np.flatnonzero(np.sum(full_adj_mat, axis=0)):  # only look at the cities that have connections
            path.append([n])  # initialize a new path with the current city we start with
            terminated.append(False)  # this new path has not been finished

            trim_adj_mat.append(copy.deepcopy(full_adj_mat))

            while any(np.logical_not(terminated)) and not found_global_best:

                curr_path_index = np.flatnonzero(np.logical_not(terminated))[0]  # indexes the current index of the path (and others lists)
                n_ = path[curr_path_index][-1]
                connected_nodes = np.flatnonzero(trim_adj_mat[curr_path_index][:, n_])
                num_connected = len(connected_nodes)

                if num_connected == 1:
                    n__ = connected_nodes
                    path[curr_path_index] = np.concatenate((path[curr_path_index], n__))  # add the connected to the path vector

                    # remove the edge
                    trim_adj_mat[curr_path_index][n_, n__] = 0
                    trim_adj_mat[curr_path_index][n__, n_] = 0
                elif num_connected > 1:
                    # remove the current info (terminated, path, trim_adj_mat) in lieu of the forks
                    terminated = [t for i, t in enumerate(terminated) if i != curr_path_index]
                    for n__ in connected_nodes:
                        # create a new path and add the connected city to it
                        path.append(np.concatenate((path[curr_path_index], [n__])))
                        terminated.append(False)
                        trim_adj_mat.append(copy.deepcopy(trim_adj_mat[curr_path_index]))

                        # remove edge
                        trim_adj_mat[-1][n_, n__] = 0
                        trim_adj_mat[-1][n__, n_] = 0
                    trim_adj_mat = [t for i, t in enumerate(trim_adj_mat) if i != curr_path_index]
                    path = [p for i, p in enumerate(path) if i != curr_path_index]  # this path is replaced with the forks
                elif num_connected == 0:  # when there are no more connected cities on this path
                    edges = []
                    # gets the edge indices for the cities in the path
                    for i in range(len(path[curr_path_index]) - 1):
                        n0 = game.map.get_node_name(path[curr_path_index][i])
                        n1 = game.map.get_node_name(path[curr_path_index][i + 1])
                        edges.append(game.map.get_edge_index((n0, n1, 0)))
                    n0 = game.map.get_node_name(path[curr_path_index][0])
                    n1 = game.map.get_node_name(path[curr_path_index][-1])
                    if len(path[curr_path_index]) > 2 and n0 in nx.neighbors(H, n1) and game.map.get_edge_index((n0, n1, 0)) not in edges:
                        edges.append(game.map.get_edge_index((n0, n1, 0)))
                    path_dists.append(sum(game.map.extract_feature(edges, feature='distance')))
                    if np.all(np.logical_not(trim_adj_mat[curr_path_index])):  # all cities have been connected on this path
                        found_global_best = True
                    else:
                        terminated[curr_path_index] = True  # don't need to return to this path

            if found_global_best:
                break

        if len(path_dists) < 1:
            path_dists.append(0)
        else:
            best = np.argmax(path_dists)
            player_dists[turn] = path_dists[best]
            player_paths[turn] = [game.map.get_node_name(n) for n in path[best]]

    return player_dists, player_paths
