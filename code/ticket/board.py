import pandas as pd
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
import logging
from copy import deepcopy as copy
from ticket.core import TicketToRide
from ticket import utils


class Cards(TicketToRide):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resources = dict(
            deck=[color for color in range(self.NUM_COLORS) for _ in range(12)],  # 9 colors, 12 of each
            faceup=[[] for _ in range(5)],
            discards=[],
            hands=[[] for _ in range(self.players)]
        )
        self.resources['deck'].extend([0, 0])  # 14 rainbows vs 12 of every other
        self.goals = dict(
            deck=self.goals_init,
            discards=[],
            hands=[pd.DataFrame(data={'from': [], 'to': [], 'value': []}) for _ in range(self.players)]
        )

    def initialize_game(self):
        self.shuffle_deck()
        self.shuffle_goals()
        self.init_faceup()
        self.deal_resources()

    def shuffle_deck(self):
        logging.debug('shuffling deck')
        self.rng.shuffle(self.resources['deck'])

    def shuffle_goals(self):
        logging.debug('shuffling goal cards')
        self.goals['deck'] = self.goals_init.iloc[self.rng.permutation(self.NUM_GOALS), :]

    def init_faceup(self, number=5):
        logging.debug('placing {} faceup cards, {} in deck and {} in discards'.format(number,
                      len(self.resources['deck']), len(self.resources['discards'])))
        self.resources['faceup'] = self.resources['deck'][0:number]
        self.resources['deck'] = self.resources['deck'][number:]
        self.cards_check()

    def deal_resources(self):
        logging.debug('dealing resources')
        [self.pick_deck(turn) for _ in range(4) for turn in range(self.players)]

    def cards_check(self):
        if self.resources['faceup'].count(0) >= 3 and (
                sum(self.color_count('deck')[1:]) + sum(self.color_count('deck')[1:])) >= 3:
            logging.debug('3 rainbows, clearing faceup')
            self.resources['discards'].extend(self.resources['faceup'])
            self.resources['faceup'] = []
        if len(self.resources['deck']) < 5:
            logging.debug('deck has {} resources left, shuffling in {} discards'.format(len(self.resources['deck']),
                          len(self.resources['discards'])))
            self.resources['deck'].extend(self.resources['discards'])
            self.resources['discards'].clear()
            self.shuffle_deck()
        num_faceups_needed = 5 - len(self.resources['faceup'])
        if num_faceups_needed > 0:
            self.init_faceup(num_faceups_needed)

    def spend_card(self, turn, card_index):  # can be multiple cards, index goes up to length of hand
        logging.debug('player {} spends resource index {}'.format(turn, card_index))
        card = self.resources['hands'][turn][card_index]
        self.resources['discards'].extend([card])
        self.resources['hands'][turn].pop(card_index)

    def pick_faceup(self, turn, color):
        card_index = self.resources['faceup'].index(color)
        logging.debug('player {} picks faceup index {}, color {}'.format(turn, card_index, color))
        self.resources['hands'][turn].append(color)
        self.resources['faceup'].pop(card_index)
        self.resources['faceup'].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        self.cards_check()

    def pick_deck(self, turn):
        self.resources['hands'][turn].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        logging.debug('player {} picks from deck, {} resources in hand, {} in the deck'.format(turn,
                      len(self.resources['hands'][turn]), len(self.resources['deck'])))
        self.cards_check()

    def pick_goals(self, turn, force_keep, action_values):
        drawn = []
        for _ in range(3):  # draw 3
            drawn.append(self.goals['deck'].iloc[0, ])
            self.goals['deck'] = self.goals['deck'][1:]
        ind = [g.name for g in drawn]
        values = action_values['goals_each'][ind]
        threshold = action_values['goals_threshold']
        keep = []
        while len(keep) < force_keep:
            keep.append(drawn[np.argmax(values)])
            values[np.argmax(values)] = -np.inf
        keep.extend([drawn[i] for i in range(3) if values[i] > threshold])
        for g in keep:
            self.goals['hands'][turn] = self.goals['hands'][turn].append(g)  # pandas df append method returns the df
            logging.debug('player {} keeps goal from {} to {} for {} points, {} goals in hand'.format(
                turn, g[0], g[1], g[2], len(self.goals['hands'][turn])))
        for g in drawn:
            keep_ind = [g_.name for g_ in keep]
            if g.name not in keep_ind:
                self.goals['discards'].append(g)
                logging.debug('player {} discards goal from {} to {} for {} points'.format(turn, g[0], g[1], g[2]))

    def color_count(self, stack, **kwargs):
        if 'turn' in kwargs:
            stack = self.resources[stack][kwargs['turn']]
        else:
            stack = self.resources[stack]
        ct = [stack.count(c) for c in range(self.NUM_COLORS)]
        if 'dtype' in kwargs and kwargs['dtype'] == 'array':
            ct = np.array([ct])
        return ct

    # end class Cards


def reorder_edge(edge):
    edge_reorder = list(edge)[:2]
    edge_reorder.sort()
    edge_reorder.append(edge[2])
    return tuple(edge_reorder)


class Map(TicketToRide):
    _pandas_map = pd.read_csv(utils.map_file)
    _pandas_map['turn'] = -1
    _blank_map = nx.from_pandas_edgelist(_pandas_map, 'from', 'to', edge_attr=['distance', 'color', 'parallel', 'turn'],
                                         create_using=nx.MultiGraph())
    _coordinates = pd.read_csv(utils.coordinates_file, index_col=0).T.to_dict('list')
    _adjacent_edges_int, _adjacent_nodes_int, _adjacent_edges_tuple, _adjacent_nodes_str = utils.read_adjacencies()

    # adjacent edges and nodes
    _edge_tuple_to_int = dict()
    for e in range(100):
        edge = list(_blank_map.edges)[e]
        _edge_tuple_to_int[reorder_edge(edge)] = e
    _node_str_to_int = dict()
    for n in range(36):
        node = list(_blank_map.nodes)[n]
        _node_str_to_int[node] = n

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.map = nx.from_pandas_edgelist(self._pandas_map, 'from', 'to',
                                           edge_attr=['distance', 'color', 'parallel', 'turn'],
                                           create_using=nx.MultiGraph())
        self.edges = self.map.edges
        self.nodes = self.map.nodes

        edge_features = {
            'color': nx.get_edge_attributes(self.map, 'color'),
            'parallel': nx.get_edge_attributes(self.map, 'parallel'),
            'distance': nx.get_edge_attributes(self.map, 'distance'),
            'turn': nx.get_edge_attributes(self.map, 'turn'),
        }
        self.edge_features_int = dict()
        for key in edge_features.keys():
            self.edge_features_int[key] = np.empty(self.NUM_EDGES, dtype=np.int8)
            for key_, value in edge_features[key].items():
                self.edge_features_int[key][self.get_edge_index(key_)] = value

    def subset_edges(self, feature, value, dtype=tuple, **kwargs):
        feature_values = self.edge_features_int[feature]
        if 'op' in kwargs:
            op = kwargs['op']
        else:
            op = np.equal
        edges = np.nonzero(op(feature_values, value))[0]  # starts as tuple
        if dtype == int:
            return edges
        elif dtype == tuple:
            return [self.get_edge_name(e) for e in edges]
        else:
            return None

    def extract_feature(self, edges, feature=None, turn=None, as_col=False):  # faster if input is int
        if isinstance(edges, list) and len(edges) == 0:
            return []
        if isinstance(edges, list) and isinstance(edges[0], tuple):
            edges = [self.get_edge_index(e) for e in edges]
        if isinstance(edges, list):
            edges = np.array(edges)
        if feature is None:
            feature = 'turn'
        feature_values = self.edge_features_int[feature][edges]
        if turn is not None:
            feature_values_tmp = np.empty(feature_values.shape, dtype=np.int8)
            opponent = -1
            for f in np.arange(-1, self.players, 1):
                if f == -1:
                    feature_values_tmp[feature_values == f] = 0
                elif f == turn:
                    feature_values_tmp[feature_values == f] = 1
                else:
                    feature_values_tmp[feature_values == f] = opponent
                    opponent -= 1
            feature_values = feature_values_tmp
        if as_col:
            feature_values = feature_values.ravel()
        return feature_values

    def get_adjacent_nodes(self, edge, reps=0, **kwargs):
        dtype_in = type(edge)
        if dtype_in == tuple or dtype_in == list:
            dtype_in = str
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.integer:
            nodes = self._adjacent_nodes_int[reps][edge]
            if dtype_out == str:
                nodes = np.array([self.get_node_name(n) for n in nodes])
        elif dtype_in == tuple:
            nodes = self._adjacent_nodes_str[reps][edge]
            if dtype_out == int:
                nodes = np.array([self.get_node_index(n) for n in nodes])
        else:
            raise self.Error('Invalid type(edge) {}'.format(dtype_in))
        return nodes

    def get_adjacent_edges(self, node, reps=0, **kwargs):
        dtype_in = type(node)
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.integer:
            edges = self._adjacent_edges_int[reps][node]
            if dtype_out == tuple:
                edges = [self.get_edge_name(e) for e in edges]
        elif dtype_in == str:
            edges = self._adjacent_edges_tuple[reps][node]
            if dtype_out == int:
                edges = [self.get_edge_index(e) for e in edges]
        else:
            raise self.Error('Invalid type(edge) {}'.format(dtype_in))
        return edges

    def create_player_subgraph(self, turn, multi=True, incl_nodes=True):
        if multi:
            subgraph = nx.MultiGraph()
        else:
            subgraph = nx.Graph()
        if incl_nodes:
            subgraph.add_nodes_from(self.nodes)
        edges = self.subset_edges(feature='turn', value=turn)
        if not multi:
            edges = list(zip(*list(zip(*edges))[:2]))  # removes the parallel component
        subgraph.add_edges_from(edges)
        subgraph.turn = turn
        return subgraph

    def lay_track(self, turn, edge_index):
        edge_name = self.get_edge_name(edge_index)
        frm = edge_name[0]
        to = edge_name[1]
        parallel = edge_name[2]
        self.map[frm][to][parallel]['turn'] = turn
        self.edge_features_int['turn'][edge_index] = turn
        if self.players < 4 and self.map[frm][to][parallel]['parallel'] == 1:
            parallel = [ind for ind in range(2) if not (edge_name[2] == ind)][0]
            self.map[frm][to][parallel]['turn'] = -2
            self.edge_features_int['turn'][self.get_edge_index((frm, to, parallel))] = -2

    def unique(self, **kwargs):

        if 'edges' in kwargs:
            values = kwargs['edges']
        elif 'nodes' in kwargs:
            values = kwargs['nodes']
        else:
            return None

        if len(values) == 0:
            return []
        elif isinstance(values[0], int) or isinstance(values[0], np.integer):
            return list(np.unique(values))
        elif isinstance(values[0], str) or isinstance(values[0], tuple) or isinstance(values[0], list):
            if 'edges' in kwargs:
                return list(set([reorder_edge(e) for e in values]))
            elif 'nodes' in kwargs:
                return list(np.unique(values))
        else:
            raise self.Error('Invalid values type {}'.format(type(values)))

    def get_edge_index(self, edge_name):
        return self._edge_tuple_to_int[reorder_edge(edge_name)]

    def get_node_index(self, node_name):
        return self._node_str_to_int[node_name]

    def get_edge_name(self, edge_index):
        return list(self.edges)[edge_index]

    def get_node_name(self, node_index):
        return list(self.nodes)[node_index]

    @staticmethod
    def reorder_edge(edge):
        edge_reorder = list(edge)[:2]
        edge_reorder.sort()
        edge_reorder.append(edge[2])
        return tuple(edge_reorder)

    def plot_graph(self, turn):
        edges = self.subset_edges(feature='turn', value=turn)
        nodes = self.nodes
        nx.draw_networkx(self.map, with_labels=True, pos=self._coordinates, node_size=50, nodelist=nodes,
                         edgelist=edges)
        plt.show()

    @staticmethod
    def compare_paths(old=None, new=None, players=None):
        if old is None and new is None:  # initialize
            return dict(turn=np.arange(players), length=0)
        elif new['length'] > old['length']:
            return new
        elif new['length'] == old['length'] and new['turn'] not in old['turn']:
            return dict(length=old['length'], turn=np.unique(np.concatenate((new['turn'], old['turn']))))
        else:
            return old

    def find_longest_path(self, G, best=None):

        """Find the longest Eulerian path on the board.

        We take the graph of track distances and then only keep the ones where the current player has laid the track.
        Then we take the remaining connections (the player's tracks) and build a full adjacency matrix, which is a
        symmetric matrix (# cities x # cities) where there is a 1 at each (row,column) pair where the two cities are
        connected. Start with a column that has a connection, and then look down the column for connected cities. If
        there's only 1, remove that connection, then do the same for the connected city. If there are ever 2 or more
        cities connected, duplicate everything and keep going down each path.

        """

        def sum_edges(edges):
            edges = [(e[0], e[1], 0) for e in edges]
            return sum(self.extract_feature(edges, feature='distance'))

        def find_groups(G):
            H = copy(G)
            groups = []
            for frm, to in dict(nx.shortest_path_length(H)).items():
                if frm in H.nodes and len(list(H.neighbors(frm))) > 0:
                    grp = list(to.keys())
                    groups.append(grp)
                    H.remove_nodes_from(grp)
            return groups

        def by_group(G, best):
            if best is None:
                best = self.compare_paths(players=self.players)  # initialize
            groups = find_groups(G)
            if len(groups) == 0:
                return best
            for g, nbunch in enumerate(groups):
                H = copy(G)
                H.remove_edges_from([e for e in H.edges if not np.any(np.isin(nbunch, e))])
                if sum_edges(H.edges) >= best['length']:  # skip if this group cannot be longer
                    best = DFS(H, best)
            return best

        def extend(base, node=None, edge=None):
            if node is not None and isinstance(node, list) and len(node) == 1:
                node = node[0]
            if node is not None:
                extension = node
            elif edge is not None:
                extension = self.get_edge_index((self.get_node_name(edge[0]), self.get_node_name(edge[1]), 0))
            else:
                raise self.Error('argument error')
            return np.int8(np.concatenate((base, [extension])))

        def DFS(G, best):

            full_adj_mat = nx.adjacency_matrix(G).todense()  # faster than the other methods of making adj matrix
            path_nodes = []  # list of lists; each item is a route through each node index
            path_edges = []
            terminated = []  # list representing whether the path has been fully searched
            trim_adj_mat = []  # list of adjacency matrices that have edges removed
            path_dists = []  # each index is the length of a path, only updated once terminated

            seeds = np.flatnonzero(
                np.array(list(dict(G.degree).values())) % 2 == 1)  # only start with nodes of odd degree
            if len(seeds) == 0:
                seeds = np.flatnonzero(np.sum(full_adj_mat, axis=0))  # use even degree nodes if we have to

            if sum(d % 2 == 1 for _, d in G.degree()) in (0, 2):  # check if semi-eulerian
                new = dict(turn=np.array([G.turn]), length=sum_edges(G.edges))
                return self.compare_paths(new=new, old=best)

            for n in seeds:  # n: seed
                path_nodes.append([n])  # initialize a new path with the current city we start with
                path_edges.append([])
                terminated.append(False)  # this new path has not been finished

                trim_adj_mat.append(copy(full_adj_mat))

                while any(np.logical_not(terminated)):

                    curr_path_index = np.flatnonzero(np.logical_not(terminated))[0]
                    n_ = path_nodes[curr_path_index][-1]  # n_: current node
                    connected_nodes = np.flatnonzero(trim_adj_mat[curr_path_index][:, n_])
                    num_connected = len(connected_nodes)

                    if num_connected == 0:

                        edges = np.int8(path_edges[curr_path_index])
                        path_dists.append(sum(self.extract_feature(edges, feature='distance')))
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
                            trim_adj_mat.append(copy(trim_adj_mat[curr_path_index]))

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
            return self.compare_paths(new=new, old=best)

            # end DFS

        return by_group(G, best)

    # end class Map
