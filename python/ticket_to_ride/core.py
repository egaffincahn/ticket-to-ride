import pandas as pd
import numpy.random as rd
import numpy as np
import networkx as nx
import networkx.algorithms.approximation as approx
import matplotlib.pyplot as plt
import logging
import utils


class Map:

    def __init__(self, players):
        self.pandas_map = pd.read_csv('ticket_to_ride/data/map_multitrack2.txt')
        self.pandas_map['turn'] = -1
        self.coordinates = pd.read_csv('ticket_to_ride/data/coordinates.txt', index_col=0).T.to_dict('list')
        self.map = nx.from_pandas_edgelist(self.pandas_map, 'from', 'to',
                                           edge_attr=['distance', 'color', 'parallel', 'turn'],
                                           create_using=nx.MultiGraph())
        # self.pandas_map = nx.to_pandas_edgelist(self.map) # reorder edges
        self.edges = self.map.edges
        self.nodes = self.map.nodes
        self.number_of_edges = self.map.number_of_edges()
        self.number_of_nodes = self.map.number_of_nodes()
        self.players = players

        # adjacent edges and nodes
        self.edge_tuple_to_int = dict()
        for e in range(self.number_of_edges):
            edge = list(self.edges)[e]
            self.edge_tuple_to_int[self.reorder_edge(edge)] = e
        self.node_str_to_int = dict()
        for n in range(self.number_of_nodes):
            node = list(self.nodes)[n]
            self.node_str_to_int[node] = n
        self.adjacent_edges_int, self.adjacent_nodes_int, self.adjacent_edges_tuple, self.adjacent_nodes_str = utils.read_adjacencies()

        # shortest paths
        self.shortest_path_length = dict(nx.shortest_path_length(self.map))
        shortest_path_length_int = {}
        for (n, length_dict) in self.shortest_path_length.items():
            node_dict = {}
            for (n_, length) in length_dict.items():
                node_dict[self.get_node_index(n_)] = length
            shortest_path_length_int[self.get_node_index(n)] = node_dict
        self.shortest_path_length_int = shortest_path_length_int
        self.shortest_path = dict(nx.shortest_path(self.map))

        edge_features = {
            'color': nx.get_edge_attributes(self.map, 'color'),
            'parallel': nx.get_edge_attributes(self.map, 'parallel'),
            'distance': nx.get_edge_attributes(self.map, 'distance'),
            'turn': nx.get_edge_attributes(self.map, 'turn'),
        }
        self.edge_features_int = dict()
        for key in edge_features.keys():
            self.edge_features_int[key] = np.empty(self.number_of_edges, dtype=np.int8)
            for key_, value in edge_features[key].items():
                self.edge_features_int[key][self.get_edge_index(key_)] = value

    def create_player_subgraph(self, turn):
        G = nx.MultiGraph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.subset_edges(feature='turn', value=turn))
        return G

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

    def subset_edges(self, feature, value, dtype=tuple, **kwargs):
        edges = None
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

    def extract_feature(self, edges, feature, turn=None, as_col=False):  # faster if input is int
        if isinstance(edges, list) and len(edges) == 0:
            return []
        if isinstance(edges, list) and isinstance(edges[0], tuple):
            edges = [self.get_edge_index(e) for e in edges]
        if isinstance(edges, list):
            edges = np.array(edges)
        feature_values = self.edge_features_int[feature][edges]
        if feature == 'turn' and turn is not None:
            feature_values_tmp = np.empty(feature_values.shape, dtype=np.int8)
            oppnt = -1
            for f in np.arange(-1, self.players, 1):
                if f == -1:
                    feature_values_tmp[feature_values == f] = 0
                elif f == turn:
                    feature_values_tmp[feature_values == f] = 1
                else:
                    feature_values_tmp[feature_values == f] = oppnt
                    oppnt -= 1
            feature_values = feature_values_tmp
        if as_col:
            feature_values = feature_values.ravel()
        return feature_values

    def reorder_edge(self, edge):
        edge_reorder = list(edge)[:2]
        edge_reorder.sort()
        edge_reorder.append(edge[2])
        return tuple(edge_reorder)

    def unique(self, **kwargs):

        if 'edges' in kwargs:
            values = kwargs['edges']
        elif 'nodes' in kwargs:
            values = kwargs['nodes']
        else:
            return None

        if len(values) == 0:
            return []
        elif isinstance(values[0], int) or isinstance(values[0], np.int64):
            return list(np.unique(values))
        elif isinstance(values[0], str) or isinstance(values[0], tuple) or isinstance(values[0], list):
            if 'edges' in kwargs:
                return list(set([self.reorder_edge(e) for e in values]))
            elif 'nodes' in kwargs:
                return list(np.unique(values))
        else:
            return None

    def get_edge_index(self, edge_name):
        return self.edge_tuple_to_int[self.reorder_edge(edge_name)]

    def get_node_index(self, node_name):
        return self.node_str_to_int[node_name]

    def get_edge_name(self, edge_index):
        return list(self.edges)[edge_index]

    def get_node_name(self, node_index):
        return list(self.nodes)[node_index]

    def get_adjacent_nodes_slow(self, edge, reps=0, **kwargs):

        dtype_in = type(edge)
        if dtype_in == tuple or dtype_in == list:
            dtype_in = str
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == str:
            edge = self.get_edge_index(edge)

        nodes0 = [self.get_node_index(n) for n in self.get_edge_name(edge)[:2]]
        nodes = []
        for n in range(2):
            within_reps = np.array(list(self.shortest_path_length_int[nodes0[n]].values())) <= reps
            nodes.extend(list(np.array(list(self.shortest_path_length_int[nodes0[n]].keys()))[within_reps]))
            nodes = self.unique(nodes=nodes)

        if dtype_out == str:
            nodes = [self.get_node_name(n) for n in nodes]
        else:
            nodes = np.array(nodes)
        return nodes

    def get_adjacent_nodes(self, edge, reps=0, **kwargs):  # FIX DTYPE_OUT
        dtype_in = type(edge)
        if dtype_in == tuple or dtype_in == list:
            dtype_in = str
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            nodes = self.adjacent_nodes_int[reps][edge]
        elif dtype_in == tuple:
            nodes = self.adjacent_nodes_str[reps][edge]
        else:
            dsjflsjf
        if dtype_out == int and isinstance(nodes, str):
            nodes = self.get_node_index(nodes)
        elif dtype_out == str and isinstance(nodes[0], np.int64):
            nodes = np.array([self.get_node_name(n) for n in nodes])
        return nodes

    def get_adjacent_edges_slow(self, node, reps=0, **kwargs):

        dtype_in = type(node)
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in != str:
            node = self.get_node_name(node)

        edges = []
        for e in self.edges:
            if self.shortest_path_length[e[0]][node] <= reps or self.shortest_path_length[e[1]][node] <= reps:
                edges.append(e)

        if dtype_out == int:
            edges = [self.get_edge_index(e) for e in edges]
        else:
            edges = [self.reorder_edge(e) for e in edges]
        return edges

    def get_adjacent_edges(self, node, reps=0, **kwargs):
        dtype_in = type(node)
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            edges = self.adjacent_edges_int[reps][node]
        elif dtype_in == str:
            edges = self.adjacent_edges_tuple[reps][node]
        return edges

    def plot_graph(self, turn):
        #
        edges = self.subset_edges(feature='turn', value=turn)
        nodes = self.nodes

        nx.draw_networkx(self.map, with_labels=True, pos=self.coordinates, node_size=50, nodelist=nodes, edgelist=edges)
        plt.show()

    # end class Map


class Info:

    def __init__(self, players):
        self.pieces = 45 * np.ones(players, dtype=np.int8)
        self.points = np.zeros(players, dtype=np.int8)
        self.turn = 0
        self.nrounds = 0
        self.players = players
        self.distance_points = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

    def lay_track(self, turn, distance):
        self.points[turn] += self.distance_points[distance]
        self.pieces[turn] -= distance

    def next_turn(self):
        self.turn += 1
        if self.turn == self.players:
            self.turn = 0
            self.nrounds += 1

    # end class info


class Cards:

    def __init__(self, players):
        self.resources = {
            'deck': [color for color in range(9) for _ in range(12)],  # 9 colors, 12 of each
            'faceup': [[] for _ in range(5)],
            'discards': [],
            'hands': [[] for _ in range(players)]
        }
        self.resources['deck'].extend([0, 0])  # 14 rainbows vs 12 of every other
        self.goals = {
            'deck': pd.read_csv('ticket_to_ride/data/goals.txt'),
            'hands': [pd.DataFrame({'from': [], 'to': [], 'value': []}, dtype=int) for _ in range(players)],
        }
        self.goals_init = self.goals['deck']
        self.num_goals = len(self.goals['deck'])
        self.players = players

    def initialize_game(self):
        self.shuffle_deck()
        self.shuffle_goals()
        self.init_faceup()
        self.deal_out()

    def shuffle_deck(self):
        logging.info('shuffling deck')
        rd.shuffle(self.resources['deck'])

    def shuffle_goals(self):
        logging.info('shuffling goal cards')
        self.goals['deck'] = self.goals['deck'].sample(frac=1)

    def init_faceup(self, number=5):
        logging.info('placing %d faceup cards, %d in deck and %d in discards', number, len(self.resources['deck']),
                     len(self.resources['discards']))
        self.resources['faceup'] = self.resources['deck'][0:number]
        self.resources['deck'] = self.resources['deck'][number:]
        self.cards_check()

    def deal_out(self):
        logging.info('dealing cards')
        [self.pick_deck(turn) for _ in range(4) for turn in range(self.players)]
        [self.pick_goal(turn) for _ in range(3) for turn in range(self.players)]

    def cards_check(self):
        if self.resources['faceup'].count(0) >= 3 and (
                sum(self.color_count('deck')[1:]) + sum(self.color_count('deck')[1:])) >= 3:
            logging.info('3 rainbows, clearing faceup')
            self.resources['discards'].extend(self.resources['faceup'])
            self.resources['faceup'] = []
        if len(self.resources['deck']) < 5:
            logging.info('deck has %d resources left, shuffling in %d discards', len(self.resources['deck']),
                         len(self.resources['discards']))
            self.resources['deck'].extend(self.resources['discards'])
            self.resources['discards'].clear()
            self.shuffle_deck()
        num_faceups_needed = 5 - len(self.resources['faceup'])
        if num_faceups_needed > 0:
            self.init_faceup(num_faceups_needed)

    def spend_card(self, turn, card_index):  # can be multiple cards, index goes up to length of hand
        logging.info('player %d spends resource index %d', turn, card_index)
        card = self.resources['hands'][turn][card_index]
        self.resources['discards'].extend([card])
        self.resources['hands'][turn].pop(card_index)

    def pick_faceup(self, turn, card_index):
        card = self.resources['faceup'][card_index]
        logging.info('player %d picks faceup index %d, color %d', turn, card_index, card)
        self.resources['hands'][turn].append(card)
        self.resources['faceup'].pop(card_index)
        self.resources['faceup'].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        self.cards_check()

    def pick_deck(self, turn):
        self.resources['hands'][turn].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        logging.info('player %d picks from deck, %d resources in hand, %d in the deck', turn,
                     len(self.resources['hands'][turn]), len(self.resources['deck']))
        self.cards_check()

    def pick_goal(self, turn):
        self.goals['hands'][turn] = self.goals['hands'][turn].append(self.goals['deck'].iloc[0,])
        self.goals['deck'] = self.goals['deck'][1:]
        logging.info('player %d picks goal from %s to %s for %d points, %d goals in hand, %d in deck', turn,
                     self.goals['hands'][turn].iloc[-1, 0], self.goals['hands'][turn].iloc[-1, 1],
                     self.goals['hands'][turn].iloc[-1, 2], len(self.goals['hands'][turn]), len(self.goals['deck']))

    def color_count(self, stack, **kwargs):
        if 'turn' in kwargs:
            stack = self.resources[stack][kwargs['turn']]
        else:
            stack = self.resources[stack]
        ct = [stack.count(c) for c in range(9)]
        if 'dtype' in kwargs and kwargs['dtype'] == 'array':
            # ct = [np.array(val).ravel() for _, val in enumerate(ct)]
            ct = np.array([ct])
        return ct

    # end class cards


class Strategy:

    def __init__(self, players, turn=0, seed=0):
        self.blank_map = Map(players)
        self.blank_info = Info(1)
        self.number_of_edges = self.blank_map.number_of_edges
        self.number_of_nodes = self.blank_map.number_of_nodes
        self.number_of_colors = 9
        self.number_of_parallel = 2
        self.number_of_distances = 6
        self.number_of_cluster_reps = 2
        self.number_of_goals = 30
        self.players = players
        self.turn = turn
        self.player_logical_index = np.arange(self.players) == turn
        self.reps = nx.diameter(self.blank_map.map)
        self.rng = rd.default_rng(seed=seed)
        self.init_inputs()

    def init_weights(self, parent1=None, parent2=None):

        logging.info('Building strategy')
        M0, M1, M2, M3 = utils.read_masks()

        W0 = self.rande(M0)
        W1 = [[self.rande(M1[rep][ind]) for ind in range(2)] for rep in range(self.reps)]
        W2 = self.rande(M2)
        W3 = self.rande(M3)

        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.W3 = W3

        if parent1 is not None and parent2 is not None:

            p = self.rng.beta(10, 10)

            mutation_mask = self.rng.uniform(size=M0.shape) > .01
            self.W0[mutation_mask] = p * parent1.W0[mutation_mask] + (1 - p) * parent2.W0[mutation_mask]

            for rep in range(self.reps):
                for ind in range(2):
                    mutation_mask = self.rng.uniform(size=M1[rep][ind].shape) > .01
                    self.W1[rep][ind][mutation_mask] = p * parent1.W1[rep][ind][mutation_mask] + (1 - p) * parent2.W1[rep][ind][mutation_mask]

            mutation_mask = self.rng.uniform(size=M2.shape) > .01
            self.W2[mutation_mask] = p * parent1.W2[mutation_mask] + (1 - p) * parent2.W2[mutation_mask]

            mutation_mask = self.rng.uniform(size=M3.shape) > .01
            self.W3[mutation_mask] = p * parent1.W3[mutation_mask] + (1 - p) * parent2.W3[mutation_mask]

    def init_inputs(self):

        # blank_map = Map(self.players)
        blank_info = Info(1)
        # blank_cards = Cards(1)
        #
        # self.inputs = dict()
        #
        # self.update_inputs('edges', blank_info, blank_cards, blank_map)
        # self.update_inputs('goals', blank_info, blank_cards, blank_map)
        # self.update_inputs('resources', blank_info, blank_cards, blank_map)

        self.inputs = np.concatenate(( # non-zero values in a row R of inputs map to row R of layer 1
            np.zeros(1), # bias
            np.zeros(1) + blank_info.pieces,
            np.zeros(self.players - 1) + blank_info.pieces,
            np.zeros(1),
            np.zeros(self.players - 1),
            np.zeros(self.players - 1),
            np.zeros(self.number_of_colors),
            np.zeros(self.number_of_colors),
            np.zeros(self.number_of_goals),
            np.zeros(self.number_of_edges)
        ))

        next_ind = lambda x: np.max(np.concatenate((list(x.values()))), keepdims=True) + 1
        self.next_ind = next_ind

        input_indices = dict()
        input_indices['bias'] = np.array([0])
        input_indices['turn_pieces'] = next_ind(input_indices)
        input_indices['oppnt_pieces'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['turn_points'] = next_ind(input_indices)
        input_indices['oppnt_points'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['oppnt_hand_lengths'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['faceups'] = next_ind(input_indices) + np.arange(self.number_of_colors)
        input_indices['hand_colors'] = next_ind(input_indices) + np.arange(self.number_of_colors)
        input_indices['goals'] = next_ind(input_indices) + np.arange(self.number_of_goals)
        input_indices['edges'] = next_ind(input_indices) + np.arange(self.number_of_edges)

        self.input_indices = input_indices

    def update_inputs(self, input_type, game_info, game_cards, game_map):

        turn = game_info.turn

        if input_type == 'all' or input_type == 'edges':
            self.inputs[self.input_indices['turn_pieces']] = self.zpieces(game_info.pieces[self.player_logical_index])
            self.inputs[self.input_indices['oppnt_pieces']] = self.zpieces(game_info.pieces[np.logical_not(self.player_logical_index)])
            self.inputs[self.input_indices['turn_points']] = self.zpoints(game_info.points[self.player_logical_index])
            self.inputs[self.input_indices['oppnt_points']] = self.zpoints(game_info.points[np.logical_not(self.player_logical_index)])
            self.inputs[self.input_indices['edges']] = game_map.extract_feature(range(self.number_of_edges), 'turn', turn)

        if input_type == 'all' or input_type == 'edges' or input_type == 'goal':
            goal_points = np.zeros(self.number_of_goals)
            subgraph = game_map.create_player_subgraph(turn)
            for g in range(game_cards.goals['hands'][turn].shape[0]):
            # for g in range(len(game_cards.goals['hands'][turn]))#:game_cards.goals_init.shape[0]
                ind = game_cards.goals['hands'][turn].index[g]
                frm = game_cards.goals['hands'][turn].iloc[g, 0]
                to = game_cards.goals['hands'][turn].iloc[g, 1]
                points = game_cards.goals['hands'][turn].iloc[g, 2]
                if not approx.local_node_connectivity(subgraph, frm, to):
                    points = -points
                goal_points[ind] = points
            self.inputs[self.input_indices['goals']] = self.zgoals(goal_points)

        if input_type == 'all' or input_type == 'resources':
            hand_lengths = np.array([len(game_cards.resources['hands'][trn]) for trn in range(self.players)])
            self.inputs[self.input_indices['oppnt_hand_lengths']] = self.zhand_length(hand_lengths[np.logical_not(self.player_logical_index)])
            self.inputs[self.input_indices['faceups']] = self.zfaceup(game_cards.color_count('faceup', dtype='array'))
            self.inputs[self.input_indices['hand_colors']] = self.zhand(game_cards.color_count('hands', turn=turn, dtype='array'))

    def feedforward(self):

        y = np.tanh(np.matmul(self.inputs, self.W0)) # onto Nodes, Colors, Parallel, Distances
        for rep in range(self.reps):
            y = self.relu(np.matmul(self.catbias(y), self.W1[rep][0])) # onto Edges
            y = np.tanh(np.matmul(self.catbias(y), self.W1[rep][1])) # onto Nodes, Colors, Parallel, Distances
        y = np.tanh(np.matmul(self.catbias(y), self.W2)) # onto Edges, Colors
        y = self.relu(np.matmul(self.catbias(y), self.W3)) # onto Edges, Goals, Deck, Faceups
        action_values = {
            'track': list(y[range(self.number_of_edges)]),
            'goals': [y[self.number_of_edges]],
            'deck': [y[self.number_of_edges + 1]],
            'faceup': list(y[-5:])
        }

        return action_values

    def catbias(self, x):
        return np.concatenate((np.ones(1), x))

    def rande(self, m, size=None, ismutation=False, mask=None):
        if ismutation: # this does not normalize
            sz = np.sum(m)
            w = self.rng.uniform(size=np.sum(m)) - 0.5
            w = w / sz
        else:
            w = np.zeros(m.shape)
            w[m] = self.rng.uniform(size=np.sum(m)) - 0.5
            w = w / np.tile(np.sum(m, axis=0), (m.shape[0], 1))
        return w

    def relu(self, x):
        return np.maximum(x, 0)

    def zpoints(self, x):
        return (x - 30) / 30

    def zpieces(self, x):
        return (x - 30) / 30

    def zgoals(self, x):
        return x / 11

    def zfaceup(self, x):
        return (x - .5) / .5

    def zhand(self, x):
        return (x - 3.5) / 3.5

    def zhand_length(self, x):
        return (x - 10) / 10

    def zdistance(self, x):
        return (x - 3.5) / 3.5

    # end class strategy
