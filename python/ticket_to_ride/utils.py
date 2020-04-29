import numpy as np
from networkx.algorithms import approximation as approx
from itertools import chain
import numpy.random as rd

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
    #log.write(["player ", turn, " lays track from ", edge_name[0], " to ", edge_name[1], " with track length ", edge_length, " using cards ", [game_cards.resources["hands"][turn][ind] for ind in hand_indices]])
    hand_indices.sort(reverse=True)
    [game_cards.spend_card(turn, card) for card in hand_indices]
    game_cards.cards_check()
    game_map.lay_track(turn, edge_index)
    game_info.lay_track(turn, edge_length)
    game_cards.cards_check()
    #log.write(["player ", turn, " now has ", game_info.points[turn], " points, with ", game_info.pieces[turn], " pieces and ", len(game_cards.resources["hands"][turn]) , " resources remaining"])

    # end lay_track

def add_goal_points(game_map, game_info, game_cards):

    points = [0 for _ in range(game_info.players)]
    completed = [0 for _ in range(game_info.players)]
    for turn in range(game_info.players):
        subgraph = game_map.create_player_subgraph(turn)
        goals = game_cards.goals["hands"][turn]
        for _, row in goals.iterrows():
            if approx.local_node_connectivity(subgraph, row[0], row[1]) == 1:
                #log.write(["goal for player ", turn, ": from ", row[0], ", to ", row[1], ", +", row[2]])
                points[turn] += row[2]
            else:
                #log.write(["goal for player ", turn, ": from ", row[0], ", to ", row[1], ", -", row[2]])
                points[turn] -= row[2]
    return points

    # end add_goal_points

def add_longest_road(game_map):
    # addlongestroad.m
    return rd.randint(0, game_map.players-1)

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
