import numpy as np
import logging
from itertools import chain
from networkx.algorithms import approximation as approx
from core import TicketToRide
from ticket_to_ride.strategy import Strategy
from ticket_to_ride.board import Map, Cards


class Game(TicketToRide):

    def __init__(self, strategies=None, plot=False, **kwargs):
        super().__init__(**kwargs)
        self.map = Map(**kwargs)
        self.cards = Cards(**kwargs)
        if strategies is None:
            strategies = [Strategy(**kwargs) for _ in range(self.players)]
        self.strategies = strategies
        self.pieces = self.pieces_init * np.ones(self.players, dtype=np.int8)
        self.points = np.zeros(self.players, dtype=np.int16)
        self.turn = 0
        self.round = 0
        self.goals_completed = np.zeros(self.players, dtype=np.int8)
        self.plot = plot

    def play_game(self):

        players = self.players
        self.cards.initialize_game()

        for turn in range(players):
            self.strategies[turn].set_game_turn(turn)
            self.strategies[turn].update_inputs('all', self)

        while all([self.pieces[trn] > 2 for trn in range(players)]):
            logging.debug('round %d, player %d', self.round, self.turn)
            self.do_turn()
            self.next_turn()
            if len(self.cards.resources['faceup']) < 5:
                raise self.Error('Fewer than 5 faceup cards found')
        for _ in range(players):
            logging.debug('final round, player %d', self.turn)
            self.do_turn()
            self.next_turn()

        logging.debug('played %d rounds', self.round)

        logging.debug('points for tracks: %s', self.points.__str__())

        longest_road_winner = self.add_longest_road()
        self.points[longest_road_winner] += 10
        # logging.debug('player %d wins longest road (+10)', longest_road_winner)
        logging.debug('...not adding longest road...')

        goal_points = self.add_goal_points()
        self.points += np.array([goal_points[trn] for trn in range(players)])
        logging.debug('goal points: %s', goal_points.__str__())

        winner = np.argmax(self.points)
        # winning_points = self.points[winner]

        # for turn in range(players):
        #     self.points[turn] = self.points[turn]

        logging.debug('pieces at end: %s', self.pieces.__str__())
        logging.debug('points at end: %s', self.points.__str__())
        logging.debug('winner: %d', winner)

        if self.plot:
            self.map.plot_graph(winner)

        # end play_game

    def do_turn(self):
        turn = self.turn
        player_strategy = self.strategies[turn]
        finished = False
        cards_taken = 0
        while not finished:

            action_values = player_strategy.feedforward()
            action_values = self.action_values_zero(action_values, cards_taken)
            move, action_index, value = self.find_best_action(action_values)

            if move is None:  # change strategy?
                logging.info('No possible moves, skipping turn')
                logging.info('round %d, player %d', self.round, turn)
                logging.info('cards in hand: %d', len(self.cards.resources['hands'][turn]))
                logging.info('colors of hand cards: %s', self.cards.color_count('hands', turn=turn).__str__())
                logging.info('pieces remaining: %d', self.pieces[turn])
                edges_short_enough = self.map.subset_edges(feature='distance', value=self.pieces[turn], op=np.less_equal)
                logging.info('tracks short enough for pieces remaining: ')
                logging.info(list(edges_short_enough))
                logging.info('...and their taken status:')
                logging.info(
                    self.map.extract_feature([self.map.get_edge_index(e) for e in edges_short_enough], feature='turn'))
                logging.info('...and the values of laying a track:')
                logging.info(list(action_values['track']))
                logging.info('cards in deck: %d', len(self.cards.resources['deck']))
                logging.info('value of taking from deck: %s', action_values['deck'].__str__())
                logging.info('values of taking from faceups: %s', action_values['faceup'].__str__())
                logging.info('cards in discards: %d', len(self.cards.resources['discards']))
                logging.info('goal cards remaining: %d', len(self.cards.goals['deck']))
                logging.info('value of taking new goals: %s', action_values['goals'].__str__())
                finished = True

            if move == 'goals':
                [self.cards.pick_goal(turn) for _ in range(3)]
                self.strategies[turn].update_inputs('goals', self)
                finished = True
            elif move == 'faceup':
                cards_taken += 1
                if self.cards.resources['faceup'][action_index] == 0:
                    cards_taken += 1  # when take rainbow, as if taken 2 cards
                self.cards.pick_faceup(turn, action_index)
                [self.strategies[trn].update_inputs('resources', self) for trn in range(self.players)]
            elif move == 'deck':  # random card from deck
                cards_taken += 1
                self.cards.pick_deck(turn)
                [self.strategies[trn].update_inputs('resources', self) for trn in range(self.players)]
            elif move == 'track':  # laying track
                hand_indices = self.choose_resources(turn, action_index)
                self.lay_track(hand_indices, action_index)
                [self.strategies[trn].update_inputs('edges', self) for trn in range(self.players)]
                [self.strategies[trn].update_inputs('resources', self) for trn in range(self.players)]
                self.strategies[turn].update_inputs('goals', self)
                finished = True
            else:
                logging.info('No move')

            if cards_taken > 1:
                finished = True

        # end do_turn

    def lay_track(self, hand_indices, edge_index):
        turn = self.turn
        edge_name = self.map.get_edge_name(edge_index)
        edge_length = self.map.extract_feature(edge_index, 'distance')
        logging.debug('player %d lays track from %s to %s with track length %d using cards %s', turn, edge_name[0],
                      edge_name[1], edge_length,
                      [self.cards.resources['hands'][turn][ind] for ind in hand_indices].__str__())
        hand_indices.sort(reverse=True)
        [self.cards.spend_card(turn, card) for card in hand_indices]
        self.cards.cards_check()
        self.map.lay_track(turn, edge_index)
        self.points[turn] += self.distance_points[edge_length]
        self.pieces[turn] -= edge_length
        self.cards.cards_check()
        logging.debug('player %d now has %d points, with %d pieces and %d resources remaining', turn,
                      self.points[turn], self.pieces[turn], len(self.cards.resources['hands'][turn]))

        # end lay_track

    @staticmethod
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

    def action_values_zero(self, action_values_init, cards_taken):

        turn = self.turn

        action_values = {
            'goals': [-np.inf],
            'faceup': [-np.inf for _ in range(5)],
            'deck': [-np.inf],
            'track': [-np.inf for _ in range(self.NUM_EDGES)]
        }

        if cards_taken > 0:  # then required to take a second card, set all other values to 0
            action_values['deck'] = action_values_init['deck']
            for ind, val in enumerate(self.cards.resources['faceup']):
                if val > 0:
                    action_values['faceup'][ind] = action_values_init['faceup'][ind]
            return action_values

        if len(self.cards.resources['faceup']) >= 5 and ( # SHOULD JUST BE == ?
                cards_taken + len(self.cards.resources['deck']) + len(self.cards.resources['discards']) >= 2):
            action_values['deck'] = action_values_init['deck']
            action_values['faceup'] = action_values_init['faceup']

        if len(self.cards.goals['deck']) >= 3:
            action_values['goals'] = action_values_init['goals']

        # possible edges where there aren't enough cards of the color, or already taken, or not enough pieces
        edges_unavailable = self.map.subset_edges(feature='turn', value=-1, op=np.not_equal, dtype=int)
        if self.pieces[turn] >= 6:
            edges_not_short_enough = []
        else:
            edges_not_short_enough = self.map.subset_edges(feature='distance', value=self.pieces[turn],
                                                           op=np.greater, dtype=int)
        hand_colors = self.cards.color_count('hands', turn=turn)
        not_enough_color = [[] for _ in range(self.NUM_COLORS)]
        for c in range(self.NUM_COLORS):
            if c == 0:
                edges = [e for e in range(self.NUM_EDGES)]
                value = self.map.extract_feature(edges=edges, feature='distance')
                not_enough_color[c] = [edges[e] for e, val in enumerate(value) if
                                       val > hand_colors[c] + max(hand_colors[1:])]
            else:
                edges = self.map.subset_edges(feature='color', value=c, dtype=int)
                value = self.map.extract_feature(edges=edges, feature='distance')
                not_enough_color[c] = [edges[e] for e, val in enumerate(value) if val > hand_colors[c] + hand_colors[0]]
        cannot_lay_track = self.map.unique(
            edges=list(chain(*[edges_unavailable, edges_not_short_enough, list(chain(*not_enough_color))])))
        for e in range(self.NUM_EDGES):
            if e not in cannot_lay_track:
                action_values['track'][e] = action_values_init['track'][e]

        return action_values

    def choose_resources(self, turn, edge_index):
        edge_color = self.map.extract_feature(edge_index, 'color')
        edge_length = self.map.extract_feature(edge_index, 'distance')
        hand_colors = self.cards.color_count('hands', turn=turn)
        if edge_color == 0:
            possible_colors = []
            nrainbow = 0
            while len(possible_colors) == 0:
                possible_colors = [c for c in np.arange(1, self.NUM_COLORS, 1) if
                                   hand_colors[c] + nrainbow >= edge_length]
                nrainbow += 1
            edge_color = np.random.choice(possible_colors)
        possible_indices = [ind for ind, val in enumerate(self.cards.resources['hands'][turn]) if val == edge_color]
        possible_indices.extend([ind for ind, val in enumerate(self.cards.resources['hands'][turn]) if val == 0])
        indices = possible_indices[:edge_length]
        if len(indices) < edge_length:
            raise Error('Cards used is fewer than edge length')
        return indices

        # end choose_resources

    def add_goal_points(self):

        points = np.zeros(self.players, dtype=np.int16)
        for turn in range(self.players):
            subgraph = self.map.create_player_subgraph(turn)
            goals = self.cards.goals['hands'][turn]
            for _, row in goals.iterrows():
                if approx.local_node_connectivity(subgraph, row[0], row[1]) == 1:
                    logging.debug('goal for player %d: from %s to %s, +%d', turn, row[0], row[1], row[2])
                    points[turn] += row[2]
                    self.goals_completed[turn] += 1
                else:
                    logging.debug('goal for player %d: from %s to %s, -%d', turn, row[0], row[1], row[2])
                    points[turn] -= row[2]
        return points

    def add_longest_road(self):
        # addlongestroad.m
        return np.zeros(3, dtype=np.bool)  # rd.randint(0, self.map.players-1)

    def next_turn(self):
        self.turn += 1
        if self.turn == self.players:
            self.turn = 0
            self.round += 1

