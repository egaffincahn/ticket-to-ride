# strategy - make class?
# nnet package - tf?
# add longest road
# class individual


# import plotly.graph_objects as go
import networkx as nx
from networkx.algorithms import approximation as approx
import numpy as np
import pandas as pd
import random as rd
import matplotlib.pyplot as plt

# http://cs231n.github.io/python-numpy-tutorial/
# https://numpy.org/devdocs/user/numpy-for-matlab-users.html
# exec(open("ticket_to_ride.py").read())

rd.seed(1)
players = 3
plot = True
distance_points = {1:1, 2:2, 3:4, 4:7, 5:10, 6:15}
fobj = open("log.txt", "w")

def write_log(lines):
    [fobj.write(str(lines[l])) for l in range(len(lines))]
    fobj.write("\n")

    # end write_log

class map:

    def __init__(self, players):
        G = pd.read_csv("map_multitrack2.txt")
        G["turn"] = -1
        self.coordinates = pd.read_csv("coordinates.txt", index_col=0).T.to_dict("list")
        self.map = nx.from_pandas_edgelist(G, "from", "to", edge_attr=["distance", "color", "parallel", "turn"], create_using=nx.MultiGraph())
        self.edges = self.map.edges
        self.nodes = self.map.nodes

    def lay_track(self, players, frm, to, track_index, turn):
        self.map[frm][to][track_index]["turn"] = turn
        if players > 3:
            parallel_track = [ind for ind in range(2) if not(track_index == ind)][0]
            self.map[frm][to][parallel_track]["turn"] = -2

    def tracks_by(self, turn):
        return [key[:2] for (key, value) in nx.get_edge_attributes(self.map, "turn").items() if value == turn]

    def create_new(self, edges):
        G = nx.MultiGraph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(edges)
        return G

    # end class map

class info:

    def __init__(self, players):
        self.pieces = [45 for _ in range(players)]
        self.points = [0 for _ in range(players)]
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

    def init_faceup(self):
        write_log("placing faceup cards")
        self.resources["faceup"] = self.resources["deck"][0:5]
        self.resources["deck"] = self.resources["deck"][5:]
        self.cards_check()

    def deal_out(self):
        write_log("dealing cards")
        [self.pick_deck(turn) for _ in range(4) for turn in range(players)]
        [self.pick_goal(turn) for _ in range(3) for turn in range(players)]

    def cards_check(self):
        if self.resources["faceup"].count(0) >= 3:
            write_log("3 rainbows, clearing faceup")
            self.resources["discards"].extend(self.resources["faceup"])
            self.init_faceup()
        if len(self.resources["deck"]) < 5:
            write_log(["deck has ", len(self.resources["deck"]), " resources left, shuffling in ", len(self.resources["discards"]), " discards"])
            self.resources["deck"].extend(self.resources["discards"])
            self.resources["discards"].clear()
            self.shuffle_deck()

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
        # strategy.inputs["goals"]
        # np.where(deck2.index==0)[0][0]
        write_log(["player ", turn, " picks goal from ", self.goals["hands"][turn].iloc[0,0], " to ", self.goals["hands"][turn].iloc[0,1], " for ", self.goals["hands"][turn].iloc[0,2], " points, ", len(self.goals["hands"][turn]), " goals in hand, ", len(self.goals["deck"]), " in the deck"])

    # end class cards

class strategy:

    # def __init__(self, game_cards, game_info, turn):
    def __init__(self, players):
        self.action_values = {
        "goals": [rd.random()],
        "faceup": [rd.random()*5 for _ in range(5)],
        "deck": [rd.random()*10],
        "track": [rd.random() for _ in range(map(players).map.number_of_edges())]
        }

    # end class strategy

# class individual:
#
#

def plot_graph(game_map, turn):
    #
    edges = game_map.tracks_by(turn)
    nodes = game_map.nodes

    nx.draw_networkx(game_map.map, with_labels=True, pos=game_map.coordinates, node_size=50, nodelist=nodes, edgelist=edges)
    plt.show()

    # end plot_graph

def find_best_action(action_values):
    action = None
    key = None
    value = -1
    for k in list(action_values):
        value_tmp = max(action_values[k])
        if value_tmp > value:
            key = k
            action = np.argmax(action_values[k])
            value = value_tmp
    return key, action, value

    # end find_best_action

def choose_resources(game_map, game_cards, turn, frm, to):
    # needs functionality to decide whether to use rainbows
    # needs functionality to choose which color based on color value if grey or parallel
    edge = game_map.map[frm][to]
    distance = edge[0]["distance"]
    hand_colors = game_cards.resources["hands"][turn]
    if edge[0]["color"] == 0: # grey (single or parallel)
        has_of_each = [hand_colors.count(color) for color in range(9)]
        has_enough = [color for color in range(9) if has_of_each[color] >= distance]
        track_color_choice = has_enough[-1] # this is the color we choose to use for the grey
        indices = [ind for ind, val in enumerate(hand_colors) if val == track_color_choice]
        track_index = 0
    elif len(edge) == 1: # single color
        indices = [ind for ind, val in enumerate(hand_colors) if val == edge[0]["color"]]
        track_index = 0
    else: # parallel color
        track_colors = [edge[0]["color"], edge[1]["color"]]
        has_of_each = [hand_colors.count(color) for color in track_colors] # num of resources of both colors
        has_enough = [track_colors[x] for x in range(2) if has_of_each[x] >= distance] # which colors have enough of
        has_fewest = np.argmin([hand_colors.count(val) for _, val in enumerate(has_enough)]) # which of available colors has fewest
        indices = [ind for ind, val in enumerate(hand_colors) if val == has_enough[has_fewest]]
        track_index = has_fewest
    return indices[:distance], track_index

    # end choose_resources

def lay_track(game_map, game_info, game_cards, hand_indices, frm, to, track_index):
    # to do: clear the other track if it"s parallel and there are few players
    turn = game_info.turn
    edge = game_map.map[frm][to]
    distance = edge[0]["distance"]
    write_log(["player ", turn, " lays track from ", frm, " to ", to, " with track length ", edge[track_index]["distance"], " using cards ", [game_cards.resources["hands"][turn][ind] for ind in hand_indices]])
    hand_indices.reverse()
    [game_cards.spend_card(turn, card) for card in hand_indices]
    game_cards.cards_check()
    game_map.lay_track(game_info.players, frm, to, track_index, turn)
    game_info.lay_track(turn, distance)
    write_log(["player ", turn, " now has ", game_info.points[turn], " points, with ", game_info.pieces[turn], " pieces and ", len(game_cards.resources["hands"][turn]) , " resources remaining"])

    # end lay_track

def add_goal_points(game_map, game_info, game_cards):

    points = [0 for _ in range(game_info.players)]
    completed = [0 for _ in range(game_info.players)]
    for turn in range(game_info.players):
        player_tracks = game_map.tracks_by(turn) # tracks by this player
        subgraph = game_map.create_new(player_tracks)
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

def action_values_zero(action_values, game_map, game_cards, game_info, turn, cards_taken):

    if cards_taken > 0: # then required to take a second card, set all other values to 0
        action_values["goals"] = [0]
        action_values["track"] = [0 for _ in range(game_map.map.number_of_edges())]
        for i,val in enumerate(action_values["faceup"]):
            if val == 0:
                action_values["faceup"][i] = 0

    if len(game_cards.resources["deck"]) == 0 or len(game_cards.resources["faceup"]) < 5: # not enough resources
        action_values["faceup"] = [0 for _ in range(5)]
        action_values["deck"] = [0]

    if len(game_cards.goals["deck"]) < 3:
        action_values["goals"] = [0]

    # possible edges where there aren"t enough cards of the color, or already taken, or not enough pieces
    for edge_index in range(len(list(game_map.edges()))):
        frm = list(game_map.edges())[edge_index][0]
        to = list(game_map.edges())[edge_index][1]
        edge = game_map.map[frm][to]
        for track_ind in range(len(edge)):
            if not(edge[track_ind]["turn"] == -1) or game_info.pieces[turn] < edge[track_ind]["distance"]:
                action_values["track"][edge_index] = 0
        distance = edge[0]["distance"]
        track_colors = [edge[e]["color"] for e in range(len(edge))]
        hand_colors = game_cards.resources["hands"][turn]
        has_of_each = [hand_colors.count(color) for color in track_colors] # num of resources of both colors
        for color in track_colors:
            if (color == 0 and max(has_of_each) < distance) or (hand_colors.count(color) < distance):
                action_values["track"][edge_index] = 0

    return action_values

    # end action_values_zero

def do_turn(game_map, game_info, game_cards, game_strategies):
    turn = game_info.turn
    finished = False
    cards_taken = 0
    # try_count = 0
    while not finished:
        # try_count = try_count + 1
        # if try_count > 5:
        #     break
        action_values = action_values_zero(game_strategies.action_values, game_map, game_cards, game_info, turn, cards_taken)
        move, action_index, value = find_best_action(action_values)
        if value <= 0:
            # input("no moves of value...")
            write_log("No possible moves, skipping turn")
            write_log(["cards in hand: ", len(game_cards.resources["hands"][turn])])
            write_log(["pieces remaining: ", game_info.pieces[turn]])
            write_log(["cards in deck: ", len(game_cards.resources["deck"])])
            write_log(["cards in discards: ", len(game_cards.resources["discards"])])
            write_log(["goal cards remaining: ", len(game_cards.goals["deck"])])
            move = None
            finished = True
            # change strategy

        if move == "goals":
            [game_cards.pick_goal(turn) for _ in range(3)]
            finished = True
        elif move == "faceup":
            cards_taken += 1
            if game_cards.resources["faceup"][action_index] == 0:
                cards_taken += 1 # when take rainbow, as if taken 2 cards
            game_cards.pick_faceup(turn, action_index)
        elif move == "deck": # random card from deck
            cards_taken += 1
            game_cards.pick_deck(turn)
        elif move == "track": # laying track
            frm = list(game_map.edges())[action_index][0]
            to = list(game_map.edges())[action_index][1]
            hand_indices, track_index = choose_resources(game_map, game_cards, turn, frm, to)
            lay_track(game_map, game_info, game_cards, hand_indices, frm, to, track_index)
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
    # game_strategies = [strategy(game_cards, game_info, turn) for turn in range(players)]

    while all([game_info.pieces[trn] > 2 for trn in range(players)]):
        write_log(["round ", game_info.nrounds, " player ", game_info.turn])
        do_turn(game_map, game_info, game_cards, strategy(players))
        game_info.next_turn()
        finished_randomly = rd.random() < .00 and rd.random() < .2
        if finished_randomly:
            write_log("finished randomly")
            break
    if not finished_randomly:
        write_log("finished naturally")
    for _ in range(players):
        write_log(["final round, player ", game_info.turn])
        do_turn(game_map, game_info, game_cards, strategy(players))
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
        plot_graph(game_map, winner)

    return game_map, game_info, game_cards

    # end play_game


game_map, game_info, game_cards = play_game(players)
fobj.close()
print("finished")
