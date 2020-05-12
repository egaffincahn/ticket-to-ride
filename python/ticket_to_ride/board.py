import pandas as pd
import numpy.random as rd
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
import logging
from core import TicketToRide
from ticket_to_ride.data.read_files import read_adjacencies


class Cards(TicketToRide):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resources = {
            'deck': [color for color in range(self.NUM_COLORS) for _ in range(12)],  # 9 colors, 12 of each
            'faceup': [[] for _ in range(5)],
            'discards': [],
            'hands': [[] for _ in range(self.players)]
        }
        self.resources['deck'].extend([0, 0])  # 14 rainbows vs 12 of every other
        self.goals = {
            'deck': self.goals_init,
            'hands': [pd.DataFrame({'from': [], 'to': [], 'value': []}, dtype=int) for _ in
                      range(self.players)],
        }

    def initialize_game(self):
        self.shuffle_deck()
        self.shuffle_goals()
        self.init_faceup()
        self.deal_out()

    def shuffle_deck(self):
        logging.debug('shuffling deck')
        rd.shuffle(self.resources['deck'])

    def shuffle_goals(self):
        logging.debug('shuffling goal cards')
        self.goals['deck'] = self.goals['deck'].sample(frac=1)

    def init_faceup(self, number=5):
        logging.debug('placing %d faceup cards, %d in deck and %d in discards', number, len(self.resources['deck']),
                      len(self.resources['discards']))
        self.resources['faceup'] = self.resources['deck'][0:number]
        self.resources['deck'] = self.resources['deck'][number:]
        self.cards_check()

    def deal_out(self):
        logging.debug('dealing cards')
        [self.pick_deck(turn) for _ in range(4) for turn in range(self.players)]
        [self.pick_goal(turn) for _ in range(3) for turn in range(self.players)]

    def cards_check(self):
        if self.resources['faceup'].count(0) >= 3 and (
                sum(self.color_count('deck')[1:]) + sum(self.color_count('deck')[1:])) >= 3:
            logging.debug('3 rainbows, clearing faceup')
            self.resources['discards'].extend(self.resources['faceup'])
            self.resources['faceup'] = []
        if len(self.resources['deck']) < 5:
            logging.debug('deck has %d resources left, shuffling in %d discards', len(self.resources['deck']),
                          len(self.resources['discards']))
            self.resources['deck'].extend(self.resources['discards'])
            self.resources['discards'].clear()
            self.shuffle_deck()
        num_faceups_needed = 5 - len(self.resources['faceup'])
        if num_faceups_needed > 0:
            self.init_faceup(num_faceups_needed)

    def spend_card(self, turn, card_index):  # can be multiple cards, index goes up to length of hand
        logging.debug('player %d spends resource index %d', turn, card_index)
        card = self.resources['hands'][turn][card_index]
        self.resources['discards'].extend([card])
        self.resources['hands'][turn].pop(card_index)

    def pick_faceup(self, turn, card_index):
        card = self.resources['faceup'][card_index]
        logging.debug('player %d picks faceup index %d, color %d', turn, card_index, card)
        self.resources['hands'][turn].append(card)
        self.resources['faceup'].pop(card_index)
        self.resources['faceup'].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        self.cards_check()

    def pick_deck(self, turn):
        self.resources['hands'][turn].append(self.resources['deck'][0])
        self.resources['deck'].pop(0)
        logging.debug('player %d picks from deck, %d resources in hand, %d in the deck', turn,
                      len(self.resources['hands'][turn]), len(self.resources['deck']))
        self.cards_check()

    def pick_goal(self, turn):
        self.goals['hands'][turn] = self.goals['hands'][turn].append(self.goals['deck'].iloc[0,])
        self.goals['deck'] = self.goals['deck'][1:]
        logging.debug('player %d picks goal from %s to %s for %d points, %d goals in hand, %d in deck', turn,
                      self.goals['hands'][turn].iloc[-1, 0], self.goals['hands'][turn].iloc[-1, 1],
                      self.goals['hands'][turn].iloc[-1, 2], len(self.goals['hands'][turn]),
                      len(self.goals['deck']))

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
    _pandas_map = pd.read_csv('ticket_to_ride/data/map_multitrack2.txt')
    _pandas_map['turn'] = -1
    _blank_map = nx.from_pandas_edgelist(_pandas_map, 'from', 'to',
                                        edge_attr=['distance', 'color', 'parallel', 'turn'],
                                        create_using=nx.MultiGraph())
    _coordinates = pd.read_csv('ticket_to_ride/data/coordinates.txt', index_col=0).T.to_dict('list')
    _adjacent_edges_int, _adjacent_nodes_int, _adjacent_edges_tuple, _adjacent_nodes_str = read_adjacencies()

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

    def get_adjacent_nodes(self, edge, reps=0, **kwargs):  # FIX DTYPE_OUT
        dtype_in = type(edge)
        if dtype_in == tuple or dtype_in == list:
            dtype_in = str
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            nodes = self._adjacent_nodes_int[reps][edge]
        elif dtype_in == tuple:
            nodes = self._adjacent_nodes_str[reps][edge]
        else:
            raise self.Error('Invalid type(edge)' + dtype_in)
        if dtype_out == int and isinstance(nodes, str):
            nodes = self.get_node_index(nodes)
        elif dtype_out == str and isinstance(nodes[0], np.int64):
            nodes = np.array([self.get_node_name(n) for n in nodes])
        return nodes

    def get_adjacent_edges(self, node, reps=0, **kwargs): # FIX DTYPE OUT
        dtype_in = type(node)
        if 'dtype' in kwargs:
            dtype_out = kwargs['dtype']
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            edges = self._adjacent_edges_int[reps][node]
        elif dtype_in == str:
            edges = self._adjacent_edges_tuple[reps][node]
        else:
            raise self.Error('Invalid type(edge)' + dtype_in)
        return edges

    def create_player_subgraph(self, turn):
        subgraph = nx.MultiGraph()
        subgraph.add_nodes_from(self.nodes)
        subgraph.add_edges_from(self.subset_edges(feature='turn', value=turn))
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
        elif isinstance(values[0], int) or isinstance(values[0], np.int64):
            return list(np.unique(values))
        elif isinstance(values[0], str) or isinstance(values[0], tuple) or isinstance(values[0], list):
            if 'edges' in kwargs:
                return list(set([reorder_edge(e) for e in values]))
            elif 'nodes' in kwargs:
                return list(np.unique(values))
        else:
            raise self.Error('Invalid values type'+type(values))

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

    # end class Map
