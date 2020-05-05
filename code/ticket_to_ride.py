# separate files
# class individual
# raise exception
# SPEED UP
    # get random weights once - should have a function that uses number_of_cluster_reps to return number of total weights
# necessary:
    # add longest road
    #

# import plotly.graph_objects as go
import networkx as nx
from networkx.algorithms import approximation as approx
import numpy as np
import numpy.random as rd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
from itertools import chain
import pickle

# http://cs231n.github.io/python-numpy-tutorial/
# https://numpy.org/devdocs/user/numpy-for-matlab-users.html
# exec(open("ticket_to_ride.py").read())

# python3 -m cProfile -s 'cumtime' ticket_to_ride.py > profile.txt
# cProfile.run('play_game(players)')
#
num_weights = 0
rng = rd.default_rng(seed=0)

players = 3
plot = False
distance_points = {1:1, 2:2, 3:4, 4:7, 5:10, 6:15}
fobj = open("log.txt", "w")

# global ncolors = 9
# global

def write_log(lines):
    if not fobj.closed:
        [fobj.write(str(lines[l])) for l in range(len(lines))]
        fobj.write("\n")

    # end write_log

class map:

    def __init__(self, players):
        self.pandas_map = pd.read_csv("map_multitrack2.txt")
        self.pandas_map["turn"] = -1
        self.coordinates = pd.read_csv("coordinates.txt", index_col=0).T.to_dict("list")
        self.map = nx.from_pandas_edgelist(self.pandas_map, "from", "to", edge_attr=["distance", "color", "parallel", "turn"], create_using=nx.MultiGraph())
        self.pandas_map = nx.to_pandas_edgelist(self.map) # reorder edges
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
        self.adjacent_edges_int, self.adjacent_nodes_int, self.adjacent_edges_tuple, self.adjacent_nodes_str = read_adjacencies()

        # shortest paths
        self.shortest_path_length = dict(nx.shortest_path_length(self.map))
        shortest_path_length_int = {}
        for (n,length_dict) in self.shortest_path_length.items():
            node_dict = {}
            for (n_,length) in length_dict.items():
                node_dict[self.get_node_index(n_)] = length
            shortest_path_length_int[self.get_node_index(n)] = node_dict
        self.shortest_path_length_int = shortest_path_length_int
        self.shortest_path = dict(nx.shortest_path(self.map))

        edge_features = {
        "color": nx.get_edge_attributes(self.map, "color"),
        "parallel": nx.get_edge_attributes(self.map, "parallel"),
        "distance": nx.get_edge_attributes(self.map, "distance"),
        "turn": nx.get_edge_attributes(self.map, "turn"),
        }
        self.edge_features_int = dict()
        for key in edge_features.keys():
            self.edge_features_int[key] = np.empty(self.number_of_edges, dtype=np.int8)
            for key_,value in edge_features[key].items():
                self.edge_features_int[key][self.get_edge_index(key_)] = value

    def create_player_subgraph(self, turn):
        G = nx.MultiGraph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.subset_edges(feature="turn", value=turn))
        return G

    def lay_track(self, turn, edge_index):
        edge_name = self.get_edge_name(edge_index)
        frm = edge_name[0]
        to = edge_name[1]
        parallel = edge_name[2]
        self.map[frm][to][parallel]["turn"] = turn
        self.edge_features_int["turn"][edge_index] = turn
        if self.players < 4 and self.map[frm][to][parallel]["parallel"] == 1:
            parallel = [ind for ind in range(2) if not(edge_name[2] == ind)][0]
            self.map[frm][to][parallel]["turn"] = -2
            self.edge_features_int["turn"][self.get_edge_index((frm, to, parallel))] = -2

    def subset_edges(self, feature, value, dtype=tuple, **kwargs):
        edges = None
        feature_values = self.edge_features_int[feature]
        if "op" in kwargs:
            op = kwargs["op"]
        else:
            op = np.equal
        edges = np.nonzero(op(feature_values, value))[0] # 0 reduces down to 1D
        if dtype == int:
            return edges
        elif dtype == tuple:
            return [self.get_edge_name(e) for e in edges]
        else:
            return None

    def extract_feature(self, edges, feature, turn=None, as_col=False): # faster if input is int
        if isinstance(edges, list) and len(edges) == 0:
            return []
        if isinstance(edges, list) and isinstance(edges[0], tuple):
            edges = [self.get_edge_index(e) for e in edges]
        if isinstance(edges, list):
            edges = np.array(edges)
        feature_values = self.edge_features_int[feature][edges]
        if feature == "turn" and turn is not None:
            feature_values_tmp = np.empty(feature_values.shape, dtype=np.int8)
            oppnt = -1
            for f in np.arange(-1, players, 1):
                if f == -1:
                    feature_values_tmp[feature_values == f] = 0
                elif f == turn:
                    feature_values_tmp[feature_values == f] = 1
                else:
                    feature_values_tmp[feature_values == f] = oppnt
                    oppnt -= 1
            feature_values = feature_values_tmp
        if as_col:
            feature_values = feature_values.flatten()
        return feature_values

    def reorder_edge(self, edge):
        edge_reorder = list(edge)[:2]
        edge_reorder.sort()
        edge_reorder.append(edge[2])
        return tuple(edge_reorder)

    def unique(self, **kwargs):

        if "edges" in kwargs:
            values = kwargs["edges"]
        elif "nodes" in kwargs:
            values = kwargs["nodes"]
        else:
            return None

        if len(values) == 0:
            return []
        elif isinstance(values[0], int) or isinstance(values[0], np.int64):
            return list(np.unique(values))
        elif isinstance(values[0], str) or isinstance(values[0], tuple) or isinstance(values[0], list):
            if "edges" in kwargs:
                return list(set([self.reorder_edge(e) for e in values]))
            elif "nodes" in kwargs:
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
        if "dtype" in kwargs:
            dtype_out = kwargs["dtype"]
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
        return nodes

    def get_adjacent_nodes(self, edge, reps=0, **kwargs): # FIX DTYPE_OUT
        dtype_in = type(edge)
        if dtype_in == tuple or dtype_in == list:
            dtype_in = str
        if "dtype" in kwargs:
            dtype_out = kwargs["dtype"]
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            nodes = self.adjacent_nodes_int[reps][edge]
        elif dtype_in == tuple:
            nodes = self.adjacent_nodes_str[reps][edge]
        if dtype_out == int and isinstance(nodes, str):
            nodes = self.get_node_index(nodes)
        elif dtype_out == str and isinstance(nodes[0], np.int64):
            nodes = np.array([self.get_node_name(n) for n in nodes])
        return nodes

    def get_adjacent_edges_slow(self, node, reps=0, **kwargs):

        dtype_in = type(node)
        if "dtype" in kwargs:
            dtype_out = kwargs["dtype"]
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
        if "dtype" in kwargs:
            dtype_out = kwargs["dtype"]
        else:
            dtype_out = dtype_in
        if dtype_in == int or dtype_in == np.int64:
            edges = self.adjacent_edges_int[reps][node]
        elif dtype_in == str:
            edges = self.adjacent_edges_tuple[reps][node]
        return edges

    def plot_graph(self, turn):
        #
        edges = self.subset_edges(feature="turn", value=turn)
        nodes = self.nodes

        nx.draw_networkx(self.map, with_labels=True, pos=self.coordinates, node_size=50, nodelist=nodes, edgelist=edges)
        plt.show()

    # end class map

class info:

    def __init__(self, players):
        self.pieces = 45 * np.ones(players, dtype=np.int8)
        self.points = np.zeros(players, dtype=np.int8)
        self.turn = 0
        self.nrounds = 0
        self.players = players

    def lay_track(self, turn, distance):
        self.points[turn] += distance_points[distance]
        self.pieces[turn] -= distance

    def next_turn(self):
        self.turn += 1
        if self.turn == players:
            self.turn = 0
            self.nrounds += 1

    # end class info

class cards:

    def __init__(self, players):
        self.resources = {
            "deck": [color for color in range(9) for _ in range(12)], # 9 colors, 12 of each
            "faceup": [[] for _ in range(5)],
            "discards": [],
            "hands": [[] for _ in range(players)]
        }
        self.resources["deck"].extend([0, 0]) # 14 rainbows vs 12 of every other
        self.goals = {
            "deck": pd.read_csv("goals.txt"),
            "hands": [pd.DataFrame({"from":[],"to":[],"value":[]}, dtype=int) for _ in range(players)],
        }
        self.goals_init = self.goals["deck"]
        self.num_goals = len(self.goals["deck"])

    def initialize_game(self):
        self.shuffle_deck()
        self.shuffle_goals()
        self.init_faceup()
        self.deal_out()

    def shuffle_deck(self):
        write_log("shuffling deck")
        rd.shuffle(self.resources["deck"])

    def shuffle_goals(self):
        write_log("shuffling goal cards")
        self.goals["deck"] = self.goals["deck"].sample(frac=1)

    def init_faceup(self, number=5):
        write_log(["placing ", number, " faceup cards, ", len(self.resources["deck"]), " in deck and ", len(self.resources["discards"]), " in discards"])
        self.resources["faceup"] = self.resources["deck"][0:number]
        self.resources["deck"] = self.resources["deck"][number:]
        self.cards_check()

    def deal_out(self):
        write_log("dealing cards")
        [self.pick_deck(turn) for _ in range(4) for turn in range(players)]
        [self.pick_goal(turn) for _ in range(3) for turn in range(players)]

    def cards_check(self):
        # if self.resources["faceup"].count(0) >= 3 and (len(self.resources["deck"]) + len(self.resources["discards"]) >= 5):
        if self.resources["faceup"].count(0) >= 3 and (sum(self.color_count("deck")[1:]) + sum(self.color_count("deck")[1:])) >=3:
            write_log("3 rainbows, clearing faceup")
            self.resources["discards"].extend(self.resources["faceup"])
            self.resources["faceup"] = []
            # self.init_faceup()
        if len(self.resources["deck"]) < 5:
            write_log(["deck has ", len(self.resources["deck"]), " resources left, shuffling in ", len(self.resources["discards"]), " discards"])
            self.resources["deck"].extend(self.resources["discards"])
            self.resources["discards"].clear()
            self.shuffle_deck()
        num_faceups_needed = 5 - len(self.resources["faceup"])
        if num_faceups_needed > 0:
            self.init_faceup(num_faceups_needed)

    def spend_card(self, turn, card_index): # can be multiple cards, index goes up to length of hand
        write_log(["player ", turn, " spends resource index ", card_index])
        card = self.resources["hands"][turn][card_index]
        self.resources["discards"].extend([card])
        self.resources["hands"][turn].pop(card_index)

    def pick_faceup(self, turn, card_index):
        card = self.resources["faceup"][card_index]
        write_log(["player ", turn, " picks faceup index ", card_index, " color ", card])
        self.resources["hands"][turn].append(card)
        self.resources["faceup"].pop(card_index)
        self.resources["faceup"].append(self.resources["deck"][0])
        self.resources["deck"].pop(0)
        self.cards_check()

    def pick_deck(self, turn):
        self.resources["hands"][turn].append(self.resources["deck"][0])
        self.resources["deck"].pop(0)
        write_log(["player ", turn, " picks from deck, ", len(self.resources["hands"][turn]), " resources in hand, ", len(self.resources["deck"])," in the deck"])
        self.cards_check()

    def pick_goal(self, turn):
        self.goals["hands"][turn] = self.goals["hands"][turn].append(self.goals["deck"].iloc[0,])
        self.goals["deck"] = self.goals["deck"][1:]
        write_log(["player ", turn, " picks goal from ", self.goals["hands"][turn].iloc[-1,0], " to ", self.goals["hands"][turn].iloc[-1,1], " for ", self.goals["hands"][turn].iloc[-1,2], " points, ", len(self.goals["hands"][turn]), " goals in hand, ", len(self.goals["deck"]), " in the deck"])

    def color_count(self, stack, **kwargs):
        if "turn" in kwargs:
            stack = self.resources[stack][kwargs["turn"]]
        else:
            stack = self.resources[stack]
        ct = [stack.count(c) for c in range(9)]
        if "dtype" in kwargs and kwargs["dtype"] == "array":
            ct = [np.array(val).flatten() for _, val in enumerate(ct)]
        return ct

    # end class cards

class strategy:

    def __init__(self, players, turn):
        self.blank_map = map(players)
        self.number_of_edges = self.blank_map.number_of_edges
        self.number_of_nodes = self.blank_map.number_of_nodes
        self.number_of_colors = 9
        self.number_of_parallel = 2
        self.number_of_distances = 6
        self.number_of_cluster_reps = 2
        self.players = players
        self.turn = turn
        self.player_logical_index = np.arange(self.players) == turn
        self.reps = nx.diameter(self.blank_map.map)
        self.init_inputs()
        self.weights = self.init_weights()

    def init_weights(self):

        write_log("Building strategy")

        weights = {
        "nodes": [[[] for _ in range(self.number_of_nodes)] for _ in range(self.reps)],
        "colors": [[[] for _ in range(self.number_of_colors)] for _ in range(self.reps+1)],
        "parallel": [[[] for _ in range(self.number_of_parallel)] for _ in range(self.reps)],
        "distances": [[[] for _ in range(self.number_of_distances)] for _ in range(self.reps)],
        "edges": [[[] for _ in range(self.number_of_edges)] for _ in range(self.reps+1)],
        "action_values": {
        "edges": [],
        "goals": [],
        "decks": [],
        "faceups": []
        }
        }

        for rep in range(self.reps):

            for n in range(self.number_of_nodes):
                edges = self.blank_map.adjacent_edges_int[rep][n]
                M = 1 + len(edges)
                if rep == 0:
                    M += len(self.inputs["goal_points"][n])
                else:
                    M *= self.number_of_cluster_reps
                weights["nodes"][rep][n] = self.rande(M, self.number_of_cluster_reps)

            for c in range(self.number_of_colors):
                edges = self.blank_map.subset_edges(feature="color", value=c, dtype=int)
                M = 1 + len(edges)
                if rep == 0:
                    M += 2 # add extra for hands, faceups
                else:
                    M *= self.number_of_cluster_reps
                weights["colors"][rep][c] = self.rande(M, self.number_of_cluster_reps)

            for p in range(self.number_of_parallel):
                edges = self.blank_map.subset_edges(feature="parallel", value=p, dtype=int)
                M = 1 + len(edges)
                if rep > 0:
                    M *= self.number_of_cluster_reps
                weights["parallel"][rep][p] = self.rande(M, self.number_of_cluster_reps)

            for d in range(self.number_of_distances):
                edges = self.blank_map.subset_edges(feature="distance", value=d+1, dtype=int)
                M = 1 + len(edges)
                if rep > 0:
                    M *= self.number_of_cluster_reps
                weights["distances"][rep][d] = self.rande(M, self.number_of_cluster_reps)

            for e in range(self.number_of_edges):
                nodes = self.blank_map.adjacent_nodes_int[rep][e]
                M = (4 + len(nodes)) * self.number_of_cluster_reps # bias, color, parallel, distance
                weights["edges"][rep][e] = self.rande(M, self.number_of_cluster_reps)

        # end for rep in range(self.reps)

        M = (1 + self.number_of_edges) * self.number_of_cluster_reps
        for e in range(self.number_of_edges):
            weights["edges"][rep+1][e] = self.rande(M, self.number_of_cluster_reps)
        for c in range(self.number_of_colors):
            weights["colors"][rep+1][c] = self.rande(M, self.number_of_cluster_reps)

        M = (10 + self.number_of_edges) * self.number_of_cluster_reps
        weights["action_values"]["edges"] = self.rande(M, self.number_of_edges)
        weights["action_values"]["goals"] = self.rande(M, 1)
        weights["action_values"]["deck"] = self.rande(M, 1)
        weights["action_values"]["faceup"] = self.rande(M, 5)

        return weights

    def init_inputs(self):

        blank_map = map(self.players)
        blank_info = info(self.players)
        blank_cards = cards(self.players)

        self.inputs = dict()

        self.update_inputs("edges", blank_info, blank_cards, blank_map)
        self.update_inputs("goals", blank_info, blank_cards, blank_map)
        self.update_inputs("resources", blank_info, blank_cards, blank_map)

    def update_inputs(self, input_type, game_info, game_cards, game_map, edge=None):

        turn = self.turn

        if input_type == "all" or input_type == "edges": # laid track

            self.inputs["pieces_player"] = game_info.pieces[self.player_logical_index] # 1
            self.inputs["pieces_oppnts"] = game_info.pieces[np.logical_not(self.player_logical_index)] # players - 1
            self.inputs["points_player"] = game_info.points[self.player_logical_index] # 1
            self.inputs["points_oppnts"] = game_info.points[np.logical_not(self.player_logical_index)] # players - 1

            if edge is not None:

                input_value = game_map.extract_feature(edge, "turn", turn=turn)

                nodes = game_map.get_adjacent_nodes(edge)
                for n in nodes: # have to update the values in both inputs I think
                    node_edge_index = edge == np.array(self.blank_map.get_adjacent_edges(n))
                    self.inputs["edges"]["nodes"][n][node_edge_index] = input_value

                c = game_map.extract_feature(edge, "color")
                color_edge_index = edge == self.blank_map.subset_edges(feature="color", value=c, dtype=int)
                self.inputs["edges"]["colors"][c][color_edge_index] = input_value

                p = game_map.extract_feature(edge, "parallel")
                parallel_edge_index = edge == self.blank_map.subset_edges(feature="parallel", value=p, dtype=int)
                self.inputs["edges"]["parallel"][p][parallel_edge_index] = input_value

                d = game_map.extract_feature(edge, "distance")
                distance_edge_index = edge == self.blank_map.subset_edges(feature="distance", value=d, dtype=int)
                self.inputs["edges"]["distances"][d-1][distance_edge_index] = input_value

            else:
                self.inputs["edges"] = {
                "nodes": [game_map.extract_feature(self.blank_map.get_adjacent_edges(n, dtype=int), "turn", turn=turn) for n in self.blank_map.nodes],
                "colors": [game_map.extract_feature(self.blank_map.subset_edges(feature="color", value=c, dtype=int), "turn", turn=turn) for c in range(self.number_of_colors)],
                "parallel": [game_map.extract_feature(self.blank_map.subset_edges(feature="parallel", value=p, dtype=int), "turn", turn=turn) for p in range(self.number_of_parallel)],
                "distances": [game_map.extract_feature(self.blank_map.subset_edges(feature="distance", value=d+1, dtype=int), "turn", turn=turn) for d in range(self.number_of_distances)]
                }

        if input_type == "all" or input_type == "goals":

            if edge is not None:
                goal_points = self.inputs["goal_points"]
            else:
                goals_init = np.array(game_cards.goals_init.iloc[:,:2]).flatten()
                goal_points = [np.zeros(sum(n == goals_init)) for n in game_map.nodes]

            subgraph = game_map.create_player_subgraph(turn)
            goal_hand_indices = game_cards.goals["hands"][turn].index.values
            for g in range(len(game_cards.goals["hands"][turn])):
                frm = game_cards.goals["hands"][turn].iloc[g,0]
                to = game_cards.goals["hands"][turn].iloc[g,1]
                points = game_cards.goals["hands"][turn].iloc[g,2]
                if not approx.local_node_connectivity(subgraph, frm, to):
                    points = -points
                for n in [frm, to]:
                    goal_init_indices = np.array(game_cards.goals_init["from"].str.contains(n) | game_cards.goals_init["to"].str.contains(n)).nonzero()[0]
                    goal_index = np.where(np.isin(goal_init_indices, goal_hand_indices))[0]
                    goal_points[self.blank_map.get_node_index(n)][goal_index] += points

            self.inputs["goal_points"] = goal_points

        if input_type == "all" or input_type == "resources": # movement of resource cards

            hand_lengths = np.array([len(game_cards.resources["hands"][trn]) for trn in range(self.players)]) # players
            self.inputs["num_resources_player"] = hand_lengths[self.player_logical_index] # 1
            self.inputs["num_resources_oppnts"] = hand_lengths[np.logical_not(self.player_logical_index)] # players - 1

            self.inputs["resources_faceup"] = game_cards.color_count("faceup", dtype="array") # faceups to colors
            self.inputs["hand_colors"] = game_cards.color_count("hands", turn=turn, dtype="array") # hand to colors

    def feedforward(self, game_info, game_cards, game_map):

        Y = {
        "nodes": [[[] for _ in range(self.number_of_nodes)] for _ in range(self.reps)],
        "colors": [[[] for _ in range(self.number_of_colors)] for _ in range(self.reps+1)],
        "parallel": [[[] for _ in range(self.number_of_parallel)] for _ in range(self.reps)],
        "distances": [[[] for _ in range(self.number_of_distances)] for _ in range(self.reps)],
        "edges": [[[] for _ in range(self.number_of_edges)] for _ in range(self.reps+1)]
        }

        rep = 0

        bias1 = np.ones(1)
        biasR = np.ones([1,self.number_of_cluster_reps])

        # inputs onto Nodes
        Y["nodes"][rep] = np.empty((self.number_of_nodes, self.number_of_cluster_reps))
        for n in range(self.number_of_nodes):
            X = np.concatenate((
            bias1, # 1
            self.zgoals(self.inputs["goal_points"][n]), # len = number of goal cards with this node
            self.inputs["edges"]["nodes"][n] # len = number of edges connected to this node
            ))
            W = self.weights["nodes"][rep][n]
            Y["nodes"][rep][n,:] = np.tanh(np.matmul(X.T, W))

        # inputs onto Colors
        Y["colors"][rep] = np.empty((self.number_of_colors, self.number_of_cluster_reps))
        for c in range(self.number_of_colors):
            X = np.concatenate((
            bias1, # 1
            self.zfaceup(self.inputs["resources_faceup"][c]), # 1
            self.zhand(self.inputs["hand_colors"][c]), # 1
            self.inputs["edges"]["colors"][c] # number of edges with this color
            ))
            W = self.weights["colors"][rep][c]
            Y["colors"][rep][c,:] = np.tanh(np.matmul(X.T, W))

        # inputs onto Parallel
        Y["parallel"][rep] = np.empty((self.number_of_parallel, self.number_of_cluster_reps))
        for p in range(self.number_of_parallel):
            X = np.concatenate((
            bias1, # 1
            self.inputs["edges"]["parallel"][p] # number of parallel edges
            ))
            W = self.weights["parallel"][rep][p]
            Y["parallel"][rep][p,:] = np.tanh(np.matmul(X.T, W))

        # inputs onto Distance
        Y["distances"][rep] = np.empty((self.number_of_distances, self.number_of_cluster_reps))
        for d in range(self.number_of_distances):
            X = np.concatenate((
            bias1, # 1
            self.zdistance(self.inputs["edges"]["distances"][d]) # number of edges of this distance
            ))
            W = self.weights["distances"][rep][d]
            Y["distances"][rep][d,:] = np.tanh(np.matmul(X.T, W))


        # Nodes, Colors, Parallel, Distances onto Edges
        nodes = np.array(self.blank_map.adjacent_nodes_int[rep])
        Y["edges"][rep] = np.empty((self.number_of_edges, self.number_of_cluster_reps))
        for e in range(self.number_of_edges):
            c = game_map.extract_feature(e, "color", as_col=True) # should be 0 - returns a list of len 1
            p = game_map.extract_feature(e, "parallel", as_col=True)
            d = game_map.extract_feature(e, "distance", as_col=True)-1
            X = np.concatenate((
            biasR,
            Y["nodes"][rep][nodes[e,:]],
            Y["colors"][rep][c,:],
            Y["parallel"][rep][p,:],
            Y["distances"][rep][d,:],
            ))
            W = self.weights["edges"][rep][e]
            Y["edges"][rep][e,:] = self.relu(np.matmul(X.flatten(), W))


        for rep in np.arange(1,self.reps,1):

            # Edges onto Nodes
            Y["nodes"][rep] = np.empty((self.number_of_nodes, self.number_of_cluster_reps))
            for n in range(self.number_of_nodes):
                edges = self.blank_map.get_adjacent_edges(n, rep)
                X = np.concatenate((biasR, Y["edges"][rep-1][np.array(edges)]))
                W = self.weights["nodes"][rep][n]
                Y["nodes"][rep][n,:] = np.tanh(np.matmul(X.flatten(), W))

            # Edges onto Colors
            Y["colors"][rep] = np.empty((self.number_of_colors, self.number_of_cluster_reps))
            for c in range(self.number_of_colors):
                edges = self.blank_map.subset_edges(feature="color", value=c, dtype=int)
                X = np.concatenate((biasR, Y["edges"][rep-1][np.array(edges)]))
                W = self.weights["colors"][rep][c]
                Y["colors"][rep][c,:] = np.tanh(np.matmul(X.flatten(), W))

            # Edges onto Parallel
            Y["parallel"][rep] = np.empty((self.number_of_parallel, self.number_of_cluster_reps))
            for p in range(self.number_of_parallel):
                edges = game_map.subset_edges(feature="parallel", value=p, dtype=int)
                X = np.concatenate((biasR, Y["edges"][rep-1][np.array(edges)]))
                W = self.weights["parallel"][rep][p]
                Y["parallel"][rep][p,:] = np.tanh(np.matmul(X.flatten(), W))

            # Edges onto Distances
            Y["distances"][rep] = np.empty((self.number_of_distances, self.number_of_cluster_reps))
            for d in range(self.number_of_distances):
                edges = game_map.subset_edges(feature="distance", value=d+1, dtype=int)
                X = np.concatenate((biasR, Y["edges"][rep-1][np.array(edges)]))
                W = self.weights["distances"][rep][d]
                Y["distances"][rep][d,:] = np.tanh(np.matmul(X.flatten(), W))

            # Nodes, Colors, Parallel, Distances onto Edges
            Y["edges"][rep] = np.empty((self.number_of_edges, self.number_of_cluster_reps))
            for e in range(self.number_of_edges):
                nodes = self.blank_map.get_adjacent_nodes(e,rep)
                c = game_map.extract_feature(e, "color", as_col=True)
                p = game_map.extract_feature(e, "parallel", as_col=True)
                d = game_map.extract_feature(e, "distance", as_col=True)-1
                X = np.concatenate((
                biasR,
                Y["nodes"][rep][np.array(nodes)],
                Y["colors"][rep][c,:],
                Y["parallel"][rep][p,:],
                Y["distances"][rep][d,:],
                ))
                W = self.weights["edges"][rep][e]
                Y["edges"][rep][e,] = self.relu(np.matmul(X.flatten(), W))

            # end for rep in np.arange(1,self.reps,1)

        X = np.concatenate((biasR, Y["edges"][rep])) # fully connected

        # Edges onto Edges
        Y["edges"][rep+1] = np.empty((self.number_of_edges, self.number_of_cluster_reps))
        for e in range(self.number_of_edges):
            W = self.weights["edges"][rep+1][e]
            Y["edges"][rep+1][e,] = np.tanh(np.matmul(X.flatten(), W))

        # Edges onto Colors
        Y["colors"][rep+1] = np.empty((self.number_of_colors, self.number_of_cluster_reps))
        for c in range(self.number_of_colors):
            W = self.weights["colors"][rep+1][c]
            Y["colors"][rep+1][c,] = np.tanh(np.matmul(X.flatten(), W))

        # Values: Edges, Colors onto Edges, Goals, Deck, Faceup (share same inputs)
        X = np.concatenate((
        biasR,
        Y["edges"][rep+1],
        Y["colors"][rep+1]
        ))

        action_values = {
        "track": list(self.relu(np.matmul(X.flatten(), self.weights["action_values"]["edges"]))),
        "goals": list(self.relu(np.matmul(X.flatten(), self.weights["action_values"]["goals"]))),
        "deck": list(self.relu(np.matmul(X.flatten(), self.weights["action_values"]["deck"]))),
        "faceup": list(self.relu(np.matmul(X.flatten(), self.weights["action_values"]["faceup"])))
        }

        return action_values

        # end feedforward

    def rande(self, x, y):
        global num_weights
        num_weights += np.prod((x, y))
        return rng.uniform(size=(x,y)) / (x * y)

    def relu(self, x):
        return np.maximum(x, 0)

    def zgoals(self, x):
        return x / 11

    def zfaceup(self, x):
        return (x - .5) / .5

    def zhand(self, x):
        return (x - 3.5) / 3.5

    def zdistance(self, x):
        return (x - 3.5) / 3.5

    # end class strategy

def find_best_action(action_values):
    action_index = None
    move = None
    value = -np.inf
    for k in list(action_values):
        value_tmp = max(action_values[k])
        if value_tmp > value:
            move = k
            action_index = np.argmax(action_values[k])
            value = value_tmp
    return move, action_index, value

    # end find_best_action

def choose_resources(game_map, game_cards, turn, edge_index):
    edge_color = game_map.extract_feature(edge_index, "color")
    edge_length = game_map.extract_feature(edge_index, "distance")
    hand_colors = game_cards.color_count("hands", turn=turn)
    if edge_color == 0:
        possible_colors = []
        nrainbow = 0
        while len(possible_colors) == 0:
            possible_colors = [c for c in np.arange(1,9,1) if hand_colors[c]+nrainbow >= edge_length]
            nrainbow += 1
        edge_color = np.random.choice(possible_colors)
    possible_indices = [ind for ind, val in enumerate(game_cards.resources["hands"][turn]) if val == edge_color]
    possible_indices.extend([ind for ind, val in enumerate(game_cards.resources["hands"][turn]) if val == 0])
    indices = possible_indices[:edge_length]
    # raise exception if length of indices is less than edge length
    return indices

    # end choose_resources

def lay_track(game_map, game_info, game_cards, hand_indices, edge_index):
    turn = game_info.turn
    edge_name = game_map.get_edge_name(edge_index)
    edge_length = game_map.extract_feature(edge_index, "distance")
    write_log(["player ", turn, " lays track from ", edge_name[0], " to ", edge_name[1], " with track length ", edge_length, " using cards ", [game_cards.resources["hands"][turn][ind] for ind in hand_indices]])
    hand_indices.sort(reverse=True)
    [game_cards.spend_card(turn, card) for card in hand_indices]
    game_cards.cards_check()
    game_map.lay_track(turn, edge_index)
    game_info.lay_track(turn, edge_length)
    game_cards.cards_check()
    write_log(["player ", turn, " now has ", game_info.points[turn], " points, with ", game_info.pieces[turn], " pieces and ", len(game_cards.resources["hands"][turn]) , " resources remaining"])

    # end lay_track

def add_goal_points(game_map, game_info, game_cards):

    points = [0 for _ in range(game_info.players)]
    completed = [0 for _ in range(game_info.players)]
    for turn in range(game_info.players):
        subgraph = game_map.create_player_subgraph(turn)
        goals = game_cards.goals["hands"][turn]
        for _, row in goals.iterrows():
            if approx.local_node_connectivity(subgraph, row[0], row[1]) == 1:
                write_log(["goal for player ", turn, ": from ", row[0], ", to ", row[1], ", +", row[2]])
                points[turn] += row[2]
            else:
                write_log(["goal for player ", turn, ": from ", row[0], ", to ", row[1], ", -", row[2]])
                points[turn] -= row[2]
    return points

    # end add_goal_points

def add_longest_road(game_map):
    # addlongestroad.m
    return rd.randint(0, players-1)

    # end add_longest_road

def action_values_zero(action_values_init, game_map, game_cards, game_info, cards_taken):

    turn = game_info.turn

    action_values = {
    "goals": [-np.inf],
    "faceup": [-np.inf for _ in range(5)],
    "deck": [-np.inf],
    "track": [-np.inf for _ in range(game_map.number_of_edges)]
    }

    if cards_taken > 0: # then required to take a second card, set all other values to 0
        action_values["deck"] = action_values_init["deck"]
        action_values["faceup"] = action_values_init["faceup"]
        return action_values

    if len(game_cards.resources["faceup"]) >= 5 and (cards_taken + len(game_cards.resources["deck"]) + len(game_cards.resources["discards"]) >= 2):
        action_values["deck"] = action_values_init["deck"]
        action_values["faceup"] = action_values_init["faceup"]

    if len(game_cards.goals["deck"]) >= 3:
        action_values["goals"] = action_values_init["goals"]

    # possible edges where there aren't enough cards of the color, or already taken, or not enough pieces
    edges_unavailable = game_map.subset_edges(feature="turn", value=-1, op=np.not_equal, dtype=int)
    if game_info.pieces[turn] >= 6:
        edges_not_short_enough = []
    else:
        edges_not_short_enough = game_map.subset_edges(feature="distance", value=game_info.pieces[turn], op=np.greater, dtype=int)
    hand_colors = game_cards.color_count("hands", turn=turn)
    not_enough_color = [[] for _ in range(9)]
    for c in range(9):
        if c == 0:
            edges = [e for e in range(game_map.number_of_edges)]
            value = game_map.extract_feature(edges=edges, feature="distance")
            not_enough_color[c] = [edges[e] for e,val in enumerate(value) if val > hand_colors[c]+max(hand_colors[1:])]
        else:
            edges = game_map.subset_edges(feature="color", value=c, dtype=int)
            value = game_map.extract_feature(edges=edges, feature="distance")
            not_enough_color[c] = [edges[e] for e,val in enumerate(value) if val > hand_colors[c]+hand_colors[0]]
    cannot_lay_track = game_map.unique(edges=list(chain(*[edges_unavailable, edges_not_short_enough, list(chain(*not_enough_color))])))
    for e in range(game_map.number_of_edges):
        if e not in cannot_lay_track:
            action_values["track"][e] = action_values_init["track"][e]

    return action_values

    # end action_values_zero

def do_turn(game_map, game_info, game_cards, game_strategies):
    turn = game_info.turn
    player_strategy = game_strategies[turn]
    finished = False
    cards_taken = 0
    while not finished:

        action_values = player_strategy.feedforward(game_info, game_cards, game_map)
        action_values = action_values_zero(action_values, game_map, game_cards, game_info, cards_taken)
        move, action_index, value = find_best_action(action_values)

        if move is None: # change strategy?
            write_log("\n\n\nNo possible moves, skipping turn")
            write_log(["round, ", game_info.nrounds, " player ", turn])
            write_log(["\ncards in hand: ", len(game_cards.resources["hands"][turn])])
            write_log("colors of hand cards:")
            write_log(list(game_cards.color_count("hands", turn=turn)))
            write_log(["\npieces remaining: ", game_info.pieces[turn]])
            edges_short_enough = game_map.subset_edges(feature="distance",value=game_info.pieces[turn],op=np.less_equal)
            write_log("tracks short enough for pieces remaining: ")
            write_log(list(edges_short_enough))
            write_log("...and their taken status:")
            write_log(game_map.extract_feature([game_map.get_edge_index(e) for e in edges_short_enough],feature="turn"))
            write_log("...and the values of laying a track:")
            write_log(list(action_values["track"]))
            write_log(["\ncards in deck: ", len(game_cards.resources["deck"])])
            write_log(["value of taking from deck:", action_values["deck"]])
            write_log("values of taking from faceups:")
            write_log(list(action_values["faceup"]))
            write_log(["cards in discards: ", len(game_cards.resources["discards"])])
            write_log(["goal cards remaining: ", len(game_cards.goals["deck"])])
            write_log(["value of taking new goals:", action_values["goals"]])
            finished = True
            # djflksjfls # should return error

        if move == "goals":
            [game_cards.pick_goal(turn) for _ in range(3)]
            game_strategies[turn].update_inputs("goals", game_info, game_cards, game_map)
            finished = True
        elif move == "faceup":
            cards_taken += 1
            if game_cards.resources["faceup"][action_index] == 0:
                cards_taken += 1 # when take rainbow, as if taken 2 cards
            game_cards.pick_faceup(turn, action_index)
            [game_strategies[trn].update_inputs("resources", game_info, game_cards, game_map) for trn in range(players)]
        elif move == "deck": # random card from deck
            cards_taken += 1
            game_cards.pick_deck(turn)
            [game_strategies[trn].update_inputs("resources", game_info, game_cards, game_map) for trn in range(players)]
        elif move == "track": # laying track
            hand_indices = choose_resources(game_map, game_cards, turn, action_index)
            lay_track(game_map, game_info, game_cards, hand_indices, action_index)
            [game_strategies[trn].update_inputs("edges", game_info, game_cards, game_map, edge=action_index) for trn in range(players)]
            game_strategies[turn].update_inputs("goals", game_info, game_cards, game_map)
            finished = True
        else:
            write_log("no move!")

        if cards_taken > 1:
            finished = True

    # end do_turn

def play_game(players):

    game_map = map(players)
    game_info = info(players)
    game_cards = cards(players)
    game_cards.initialize_game()
    game_strategies = [strategy(players, turn) for turn in range(players)]
    [game_strategies[turn].update_inputs("all", game_info, game_cards, game_map) for turn in range(players)]

    while all([game_info.pieces[trn] > 2 for trn in range(players)]):
        write_log(["round ", game_info.nrounds, " player ", game_info.turn])
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()
        if len(game_cards.resources["faceup"]) < 5:
            dsjflsjlksdf
    for _ in range(players):
        write_log(["final round, player ", game_info.turn])
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()

    write_log(["played ", game_info.nrounds, " rounds"])

    write_log(["points for tracks: ", game_info.points])

    longest_road_winner = add_longest_road(game_map)
    game_info.points[longest_road_winner] += 10
    write_log(["player ", longest_road_winner, " wins longest road (+10)"])

    goal_points = add_goal_points(game_map, game_info, game_cards)
    game_info.points = [game_info.points[trn] + goal_points[trn] for trn in range(players)]
    write_log(["goal points: ", goal_points])

    winner = np.argmax(game_info.points)
    winning_points = game_info.points[winner]

    write_log(["pieces at end: ", game_info.pieces])
    write_log(["points at end: ", game_info.points])
    write_log(["winner: ", winner])

    if plot:
        game_map.plot_graph(winner)

    return game_map, game_info, game_cards, game_strategies

    # end play_game

def write_adjacencies():

    blank_map = map(players)
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

    with open("adjacent.obj", "wb") as f:
        pickle.dump(adjacent_edges_int, f)
        pickle.dump(adjacent_nodes_int, f)
        pickle.dump(adjacent_edges_tuple, f)
        pickle.dump(adjacent_nodes_str, f)

def read_adjacencies():
    with open("adjacent.obj", "rb") as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str

write_log(["started at ", dt.now()])

game_map, game_info, game_cards, game_strategies = play_game(players)
write_log(["finished at ", dt.now()])
fobj.close()
print("finished")
