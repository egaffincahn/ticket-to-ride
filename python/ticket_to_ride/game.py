import numpy as np
from ticket_to_ride.core import Map, Info, Cards, Strategy
# import utils
from . import utils as game_utils
# from utils import Log as log

def play_game(players, plot=False):

    game_map = Map(players)
    game_info = Info(players)
    game_cards = Cards(players)
    game_cards.initialize_game()
    game_strategies = [Strategy(players, turn, seed=turn) for turn in range(players)]
    [game_strategies[turn].update_inputs('all', game_info, game_cards, game_map) for turn in range(players)]

    while all([game_info.pieces[trn] > 2 for trn in range(players)]):
        #log.write(['round ', game_info.nrounds, ' player ', game_info.turn])
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()
        if len(game_cards.resources['faceup']) < 5:
            dsjflsjlksdf
    for _ in range(players):
        #log.write(['final round, player ', game_info.turn])
        do_turn(game_map, game_info, game_cards, game_strategies)
        game_info.next_turn()

    #log.write(['played ', game_info.nrounds, ' rounds'])

    #log.write(['points for tracks: ', game_info.points])

    longest_road_winner = game_utils.add_longest_road(game_map)
    game_info.points[longest_road_winner] += 10
    #log.write(['player ', longest_road_winner, ' wins longest road (+10)'])

    goal_points = game_utils.add_goal_points(game_map, game_info, game_cards)
    game_info.points = [game_info.points[trn] + goal_points[trn] for trn in range(players)]
    #log.write(['goal points: ', goal_points])

    winner = np.argmax(game_info.points)
    winning_points = game_info.points[winner]

    #log.write(['pieces at end: ', game_info.pieces])
    #log.write(['points at end: ', game_info.points])
    #log.write(['winner: ', winner])

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

        action_values = player_strategy.feedforward(game_info, game_cards, game_map)
        action_values = game_utils.action_values_zero(action_values, game_map, game_cards, game_info, cards_taken)
        move, action_index, value = game_utils.find_best_action(action_values)

        if move is None: # change strategy?
            #log.write('\n\n\nNo possible moves, skipping turn')
            #log.write(['round, ', game_info.nrounds, ' player ', turn])
            #log.write(['\ncards in hand: ', len(game_cards.resources['hands'][turn])])
            #log.write('colors of hand cards:')
            #log.write(list(game_cards.color_count('hands', turn=turn)))
            #log.write(['\npieces remaining: ', game_info.pieces[turn]])
            edges_short_enough = game_map.subset_edges(feature='distance',value=game_info.pieces[turn],op=np.less_equal)
            #log.write('tracks short enough for pieces remaining: ')
            #log.write(list(edges_short_enough))
            #log.write('...and their taken status:')
            #log.write(game_map.extract_feature([game_map.get_edge_index(e) for e in edges_short_enough],feature='turn'))
            #log.write('...and the values of laying a track:')
            #log.write(list(action_values['track']))
            #log.write(['\ncards in deck: ', len(game_cards.resources['deck'])])
            #log.write(['value of taking from deck:', action_values['deck']])
            #log.write('values of taking from faceups:')
            #log.write(list(action_values['faceup']))
            #log.write(['cards in discards: ', len(game_cards.resources['discards'])])
            #log.write(['goal cards remaining: ', len(game_cards.goals['deck'])])
            #log.write(['value of taking new goals:', action_values['goals']])
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
            hand_indices = game_utils.choose_resources(game_map, game_cards, turn, action_index)
            game_utils.lay_track(game_map, game_info, game_cards, hand_indices, action_index)
            [game_strategies[trn].update_inputs('edges', game_info, game_cards, game_map, edge=action_index) for trn in range(game_info.players)]
            game_strategies[turn].update_inputs('goals', game_info, game_cards, game_map)
            finished = True
        else:
            pass
            #log.write('no move!')

        if cards_taken > 1:
            finished = True

    # end do_turn
