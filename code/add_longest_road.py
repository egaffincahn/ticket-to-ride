import networkx as nx
import copy
import numpy as np

# We take the graph of track distances and then only keep the ones where the current player has laid the track. Then we
# take the remaining connections (the player's tracks) and build a full adjacency matrix, which is a symmetric matrix
# (# cities x # cities) where there is a 1 at each (row,column) pair where the two cities are connected. Start with a
# column that has a connection, and then look down the column for connected cities. If there's only 1, remove that
# connection, then do the same for the connected city. If there are ever 2 or more cities connected, duplicate
# everything and keep going down each path.
def add_longest_road(game):

    def compare(old=None, new=None, players=None):
        if players is not None:  # initialize
            return dict(turn=np.arange(players), length=0)
        elif new['length'] > old['length']:
            return new
        elif new['length'] == old['length'] and new['turn'] not in old['turn']:
            return dict(length=old['length'], turn=np.unique(np.concatenate((new['turn'], old['turn']))))
        else:
            return old

    def by_turn(map, players):
        best = compare(players=players)
        for turn in range(players):
            G = map.create_player_subgraph(turn, multi=False, incl_nodes=True)
            G.turn = turn
            groups = find_groups(G)
            best = by_group(G, groups, best)
        return best

    def sum_edges(edges):
        edges = [(e[0], e[1], 0) for e in edges]
        return sum(game.map.extract_feature(edges, feature='distance'))

    def by_group(G, groups, best):
        if len(groups) == 0:
            return best
        for g, nbunch in enumerate(groups):
            H = copy.deepcopy(G)
            H.remove_edges_from([e for e in H.edges if not np.any(np.isin(nbunch, e))])
            if sum_edges(H.edges) >= best['length']:  # skip if this group cannot be longer
                best = DFS(H, best)
        return best

    def find_groups(G):
        H = copy.deepcopy(G)
        groups = []
        for frm, to in dict(nx.shortest_path_length(H)).items():
            if frm in H.nodes and len(list(H.neighbors(frm))) > 0:
                grp = list(to.keys())
                groups.append(grp)
                H.remove_nodes_from(grp)
        return groups

    def extend(base, node=None, edge=None):
        if node is not None and isinstance(node, list) and len(node) == 1:
            node = node[0]
        if node is not None:
            extension = node
        elif edge is not None:
            extension = game.map.get_edge_index((game.map.get_node_name(edge[0]), game.map.get_node_name(edge[1]), 0))
        else:
            raise self.Error('argument error')
        return np.int8(np.concatenate((base, [extension])))

    def DFS(G, best):

        full_adj_mat = nx.adjacency_matrix(G).todense()  # faster than the other methods of making adj matrix
        path_nodes = []  # list of lists; each item is a route through each node index
        path_edges = []
        terminated = []  # list representing whether the path has been fully searched
        trim_adj_mat = []  # list of adjacency matrices that have edges removed
        path_dists = []  # list for this player where each index is the length of a path, only updated once terminated

        seeds = np.flatnonzero(np.array(list(dict(G.degree).values())) % 2 == 1)  # only start with nodes of odd degree
        if len(seeds) == 0:
            seeds = np.flatnonzero(np.sum(full_adj_mat, axis=0))  # use even degree nodes if we have to

        if sum(d % 2 == 1 for _, d in G.degree()) in (0, 2):  # check if semi-eulerian
            new = dict(turn=np.array([G.turn]), length=sum_edges(G.edges))
            return compare(new=new, old=best)

        for n in seeds:  # n: seed
            path_nodes.append([n])  # initialize a new path with the current city we start with
            path_edges.append([])
            terminated.append(False)  # this new path has not been finished

            trim_adj_mat.append(copy.deepcopy(full_adj_mat))

            while any(np.logical_not(terminated)):

                curr_path_index = np.flatnonzero(np.logical_not(terminated))[0]
                n_ = path_nodes[curr_path_index][-1]  # n_: current node
                connected_nodes = np.flatnonzero(trim_adj_mat[curr_path_index][:, n_])
                num_connected = len(connected_nodes)

                if num_connected == 0:

                    edges = np.int8(path_edges[curr_path_index])
                    path_dists.append(sum(game.map.extract_feature(edges, feature='distance')))
                    terminated[curr_path_index] = True  # don't need to return to this path

                elif num_connected == 1:

                    n__ = connected_nodes[0]  # n__: next node
                    path_nodes[curr_path_index] = extend(path_nodes[curr_path_index], node=n__)
                    path_edges[curr_path_index] = extend(path_edges[curr_path_index], edge=(n_, n__))

                    # remove the edge
                    trim_adj_mat[curr_path_index][n_, n__] = 0
                    trim_adj_mat[curr_path_index][n__, n_] = 0

                elif num_connected > 1:

                    for n__ in connected_nodes:  # n__: next node

                        # create a new path and add the connected city to it
                        path_nodes.append(extend(path_nodes[curr_path_index], node=n__))
                        path_edges.append(extend(path_edges[curr_path_index], edge=(n_, n__)))

                        terminated.append(False)
                        trim_adj_mat.append(copy.deepcopy(trim_adj_mat[curr_path_index]))

                        # remove edge
                        trim_adj_mat[-1][n_, n__] = 0
                        trim_adj_mat[-1][n__, n_] = 0

                    # remove the current info, replaced by the forks
                    del terminated[curr_path_index]
                    del trim_adj_mat[curr_path_index]
                    del path_nodes[curr_path_index]
                    del path_edges[curr_path_index]

        new = dict(length=0)
        if len(path_nodes) > 0:
            new = dict(turn=np.array([G.turn]), length=max(path_dists))
        return compare(new=new, old=best)

        # end DFS

    best = by_turn(game.map, game.players)
    points = np.zeros(game.players, dtype=np.int16)
    points[best['turn']] = 10  # ties go to both players
    length = best['length']
    return length, points
