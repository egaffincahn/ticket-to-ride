import numpy as np
import numpy.random as rd
import logging
from itertools import chain
from networkx.algorithms import approximation as approx
from ticket_to_ride.core import Map, Info, Cards, Strategy


def play_game(players, game_strategies, plot=False):

    game_map = Map(players)
    game_info = Info(players)
    game_cards = Cards(players)
    game_cards.initialize_game()
    # game_strategies = [Strategy(players, turn, seed=turn) for turn in range(players)]
    # [game_strategies[turn].init_weights() for turn in range(players)]
    for turn in range(players):
        game_strategies[turn].update_inputs('all', game_info, game_cards, game_map)
        game_strategies[turn].turn = turn

    while all([game_info.pieces[trn] > 2 for trn in range(players)]):
        logging.info('round %d, player %d', game_info.nrounds, game_info.turn)
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()
        if len(game_cards.resources['faceup']) < 5:
            dsjflsjlksdf
    for _ in range(players):
        logging.info('final round, player %d', game_info.turn)
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()

    logging.info('played %d rounds', game_info.nrounds)

    logging.info('points for tracks: %s', ','.join(map(str, game_info.points)))

    longest_road_winner = add_longest_road(game_map)
    game_info.points[longest_road_winner] += 10
    # logging.info('player %d wins longest road (+10)', longest_road_winner)
    logging.info('...not adding longest road...')

    goal_points = add_goal_points(game_map, game_info, game_cards)
    game_info.points += np.array([goal_points[trn] for trn in range(players)])
    logging.info('goal points: %s', ','.join(map(str, goal_points)))

    winner = np.argmax(game_info.points)
    winning_points = game_info.points[winner]

    logging.info('pieces at end: %s', ','.join(map(str, game_info.pieces)))
    logging.info('points at end: %s', ','.join(map(str, game_info.points)))
    logging.info('winner: %d', winner)

    if plot:
        game_map.plot_graph(winner)

    return game_map, game_info, game_cards, game_strategies

    # end play_game


def do_turn(game_map, game_info, game_cards, game_strategies):
    turn = game_info.turn
    player_strategy = game_strategies[turn]
    finished = False
    cards_taken = 0
    while not finished:

        action_values = player_strategy.feedforward()
        action_values = action_values_zero(action_values, game_map, game_cards, game_info, cards_taken)
        move, action_index, value = find_best_action(action_values)

        if move is None: # change strategy?
            logging.warning('\n\n\nNo possible moves, skipping turn')
            logging.warning('round %d, player %d', game_info.nrounds, turn)
            logging.warning('\ncards in hand: %d', len(game_cards.resources['hands'][turn]))
            logging.warning('colors of hand cards: %s', ','.join(map(str, game_cards.color_count('hands', turn=turn))))
            logging.warning('\npieces remaining: %d', game_info.pieces[turn])
            edges_short_enough = game_map.subset_edges(feature='distance',value=game_info.pieces[turn],op=np.less_equal)
            logging.warning('tracks short enough for pieces remaining: ')
            logging.warning(list(edges_short_enough))
            logging.warning('...and their taken status:')
            logging.warning(game_map.extract_feature([game_map.get_edge_index(e) for e in edges_short_enough],feature='turn'))
            logging.warning('...and the values of laying a track:')
            logging.warning(list(action_values['track']))
            logging.warning('\ncards in deck: %d', len(game_cards.resources['deck']))
            logging.warning('value of taking from deck: %s', ''.join(map(str, action_values['deck'])))
            logging.warning('values of taking from faceups: %s', ','.join(map(str, action_values['faceup'])))
            logging.warning('cards in discards: %d', len(game_cards.resources['discards']))
            logging.warning('goal cards remaining: %d', len(game_cards.goals['deck']))
            logging.warning('value of taking new goals: %s', ''.join(map(str, action_values['goals'])))
            finished = True
            # djflksjfls # should return error

        if move == 'goals':
            [game_cards.pick_goal(turn) for _ in range(3)]
            game_strategies[turn].update_inputs('goals', game_info, game_cards, game_map)
            finished = True
        elif move == 'faceup':
            cards_taken += 1
            if game_cards.resources['faceup'][action_index] == 0:
                cards_taken += 1 # when take rainbow, as if taken 2 cards
            game_cards.pick_faceup(turn, action_index)
            [game_strategies[trn].update_inputs('resources', game_info, game_cards, game_map) for trn in range(game_info.players)]
        elif move == 'deck': # random card from deck
            cards_taken += 1
            game_cards.pick_deck(turn)
            [game_strategies[trn].update_inputs('resources', game_info, game_cards, game_map) for trn in range(game_info.players)]
        elif move == 'track': # laying track
            hand_indices = choose_resources(game_map, game_cards, turn, action_index)
            lay_track(game_map, game_info, game_cards, hand_indices, action_index)
            [game_strategies[trn].update_inputs('edges', game_info, game_cards, game_map) for trn in range(game_info.players)]
            [game_strategies[trn].update_inputs('resources', game_info, game_cards, game_map) for trn in range(game_info.players)]
            game_strategies[turn].update_inputs('goals', game_info, game_cards, game_map)
            finished = True
        else:
            logging.warning('No move')

        if cards_taken > 1:
            finished = True

    # end do_turn


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
    edge_color = game_map.extract_feature(edge_index, 'color')
    edge_length = game_map.extract_feature(edge_index, 'distance')
    hand_colors = game_cards.color_count('hands', turn=turn)
    if edge_color == 0:
        possible_colors = []
        nrainbow = 0
        while len(possible_colors) == 0:
            possible_colors = [c for c in np.arange(1,9,1) if hand_colors[c]+nrainbow >= edge_length]
            nrainbow += 1
        edge_color = np.random.choice(possible_colors)
    possible_indices = [ind for ind, val in enumerate(game_cards.resources['hands'][turn]) if val == edge_color]
    possible_indices.extend([ind for ind, val in enumerate(game_cards.resources['hands'][turn]) if val == 0])
    indices = possible_indices[:edge_length]
    # raise exception if length of indices is less than edge length
    return indices

    # end choose_resources


def lay_track(game_map, game_info, game_cards, hand_indices, edge_index):
    turn = game_info.turn
    edge_name = game_map.get_edge_name(edge_index)
    edge_length = game_map.extract_feature(edge_index, 'distance')
    logging.info('player %d lays track from %s to %s with track length %d using cards %s', turn, edge_name[0], edge_name[1], edge_length, ','.join(map(str, [game_cards.resources['hands'][turn][ind] for ind in hand_indices])))
    hand_indices.sort(reverse=True)
    [game_cards.spend_card(turn, card) for card in hand_indices]
    game_cards.cards_check()
    game_map.lay_track(turn, edge_index)
    game_info.lay_track(turn, edge_length)
    game_cards.cards_check()
    logging.info('player %d now has %d points, with %d pieces and %d resources remaining', turn, game_info.points[turn], game_info.pieces[turn], len(game_cards.resources['hands'][turn]))

    # end lay_track


def add_goal_points(game_map, game_info, game_cards):

    points = [0 for _ in range(game_info.players)]
    completed = [0 for _ in range(game_info.players)]
    for turn in range(game_info.players):
        subgraph = game_map.create_player_subgraph(turn)
        goals = game_cards.goals['hands'][turn]
        for _, row in goals.iterrows():
            if approx.local_node_connectivity(subgraph, row[0], row[1]) == 1:
                logging.info('goal for player %d: from %s to %s, +%d', turn, row[0], row[1], row[2])
                points[turn] += row[2]
            else:
                logging.info('goal for player %d: from %s to %s, -%d', turn, row[0], row[1], row[2])
                points[turn] -= row[2]
    return points


def action_values_zero(action_values_init, game_map, game_cards, game_info, cards_taken):

    turn = game_info.turn

    action_values = {
    'goals': [-np.inf],
    'faceup': [-np.inf for _ in range(5)],
    'deck': [-np.inf],
    'track': [-np.inf for _ in range(game_map.number_of_edges)]
    }

    if cards_taken > 0: # then required to take a second card, set all other values to 0
        action_values['deck'] = action_values_init['deck']
        for ind,val in enumerate(game_cards.resources['faceup']):
            if val > 0:
                action_values['faceup'][ind] = action_values_init['faceup'][ind]
        return action_values

    if len(game_cards.resources['faceup']) >= 5 and (cards_taken + len(game_cards.resources['deck']) + len(game_cards.resources['discards']) >= 2):
        action_values['deck'] = action_values_init['deck']
        action_values['faceup'] = action_values_init['faceup']

    if len(game_cards.goals['deck']) >= 3:
        action_values['goals'] = action_values_init['goals']

    # possible edges where there aren't enough cards of the color, or already taken, or not enough pieces
    edges_unavailable = game_map.subset_edges(feature='turn', value=-1, op=np.not_equal, dtype=int)
    if game_info.pieces[turn] >= 6:
        edges_not_short_enough = []
    else:
        edges_not_short_enough = game_map.subset_edges(feature='distance', value=game_info.pieces[turn], op=np.greater, dtype=int)
    hand_colors = game_cards.color_count('hands', turn=turn)
    not_enough_color = [[] for _ in range(9)]
    for c in range(9):
        if c == 0:
            edges = [e for e in range(game_map.number_of_edges)]
            value = game_map.extract_feature(edges=edges, feature='distance')
            not_enough_color[c] = [edges[e] for e,val in enumerate(value) if val > hand_colors[c]+max(hand_colors[1:])]
        else:
            edges = game_map.subset_edges(feature='color', value=c, dtype=int)
            value = game_map.extract_feature(edges=edges, feature='distance')
            not_enough_color[c] = [edges[e] for e,val in enumerate(value) if val > hand_colors[c]+hand_colors[0]]
    cannot_lay_track = game_map.unique(edges=list(chain(*[edges_unavailable, edges_not_short_enough, list(chain(*not_enough_color))])))
    for e in range(game_map.number_of_edges):
        if e not in cannot_lay_track:
            action_values['track'][e] = action_values_init['track'][e]

    return action_values

def add_longest_road(game_map):
    # addlongestroad.m
    return np.zeros(3, dtype=np.bool)#rd.randint(0, game_map.players-1)

