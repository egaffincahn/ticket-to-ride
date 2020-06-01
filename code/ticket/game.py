import numpy as np
import logging
from itertools import chain
from networkx.algorithms import approximation as approx
from ticket.core import TicketToRide
from ticket.board import Map, Cards


class Game(TicketToRide):

    def __init__(self, individuals, plot=False, **kwargs):
        super().__init__(**kwargs)
        self.map = Map(**kwargs)
        self.cards = Cards(**kwargs)
        self.individuals = individuals
        self.pieces = self.pieces_init * np.ones(self.players, dtype=np.int8)
        self.points = np.zeros(self.players, dtype=np.int16)
        self.turn = 0
        self.round = 0
        self.goals_completed = np.zeros(self.players, dtype=np.int8)
        self.longest_track = np.zeros(self.players, dtype=np.int8)
        self.plot = plot
        self.longest_track_winner = None
        self.longest_track_length = None

    def play_game(self):

        logging.info('starting game with individuals {}, parents {}'.format([ind.id_ for ind in self.individuals],
                                                                            [ind.parent for ind in self.individuals]))

        players = self.players
        self.cards.initialize_game()

        for turn in range(players):
            self.individuals[turn].strategy.set_game_turn(turn)
            self.individuals[turn].strategy.update_inputs('all', self)
            action_values = self.individuals[turn].strategy.feedforward()
            self.cards.pick_goals(turn, force_keep=2, action_values=action_values)

        while all([self.pieces[trn] > 2 for trn in range(players)]):
            logging.debug('round {}, player {}'.format(self.round, self.turn))
            self.do_turn()
            self.next_turn()
            if len(self.cards.resources['faceup']) < 5:
                raise self.Error('Fewer than 5 faceup cards found')
        for _ in range(players):
            logging.debug('final round, player {}'.format(self.turn))
            self.do_turn()
            self.next_turn()

        logging.info('played {} rounds'.format(self.round))
        logging.info('points for tracks: {}'.format(self.points))

        self.add_longest_track()
        self.add_goal_points()
        winner = np.argmax(self.points)

        logging.info('pieces at end: {}'.format(self.pieces))
        logging.info('points at end: {}'.format(self.points))
        logging.info('winner: player {}, id {}'.format(winner, self.individuals[winner].id_))

        if self.plot:
            self.map.plot_graph(winner)

        # end play_game

    def do_turn(self):
        turn = self.turn
        player_strategy = self.individuals[turn].strategy
        finished = False
        cards_taken = 0
        while not finished:

            action_values = player_strategy.feedforward()
            action_values = self.action_values_zero(action_values, cards_taken)
            move, action_index, value = self.find_best_action(action_values)

            if move is None:  # change strategy?
                logging.info('No possible moves, skipping turn')
                logging.info('round {}, player {}'.format(self.round, turn))
                logging.info('cards in hand: {}'.format(len(self.cards.resources['hands'][turn])))
                logging.info('colors of hand cards: {}'.format(self.cards.color_count('hands', turn=turn)))
                logging.info('pieces remaining: {}'.format(self.pieces[turn]))
                edges_short_enough = self.map.subset_edges(
                    feature='distance', value=self.pieces[turn], op=np.less_equal)
                logging.info('tracks short enough for pieces remaining: ')
                logging.info(list(edges_short_enough))
                logging.info('...and their taken status:')
                logging.info(
                    self.map.extract_feature([self.map.get_edge_index(e) for e in edges_short_enough], feature='turn'))
                logging.info('...and the values of laying a track:')
                logging.info(list(action_values['track']))
                logging.info('cards in deck: {}'.format(len(self.cards.resources['deck'])))
                logging.info('value of taking from deck: {}'.format(action_values['deck']))
                logging.info('values of taking from faceups: {}'.format(action_values['faceup']))
                logging.info('cards in discards: {}'.format(len(self.cards.resources['discards'])))
                logging.info('goal cards remaining: {}'.format(len(self.cards.goals['deck'])))
                logging.info('value of taking new goals: {}'.format(action_values['goals_take']))
                finished = True

            if move == 'goals_take':
                self.cards.pick_goals(turn, force_keep=1, action_values=action_values)
                self.individuals[turn].strategy.update_inputs('goals', self)
                finished = True
            elif move == 'faceup':
                cards_taken += 1
                if action_index == 0:
                    cards_taken += 1  # when take rainbow, as if taken 2 cards
                self.cards.pick_faceup(turn, action_index)
                [self.individuals[trn].strategy.update_inputs('resources', self) for trn in range(self.players)]
            elif move == 'deck':  # top card from deck
                cards_taken += 1
                self.cards.pick_deck(turn)
                [self.individuals[trn].strategy.update_inputs('resources', self) for trn in range(self.players)]
            elif move == 'track':  # laying track
                hand_indices = self.choose_resources(turn, action_index)
                self.lay_track(hand_indices, action_index)
                [self.individuals[trn].strategy.update_inputs('edges', self) for trn in range(self.players)]
                [self.individuals[trn].strategy.update_inputs('resources', self) for trn in range(self.players)]
                self.individuals[turn].strategy.update_inputs('goals', self)
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
        logging.debug('player {} lays track from {} to {} with track length {} using cards {}'.format(
            turn, edge_name[0], edge_name[1], edge_length,
            [self.cards.resources['hands'][turn][ind] for ind in hand_indices]))
        hand_indices.sort(reverse=True)
        [self.cards.spend_card(turn, card) for card in hand_indices]
        self.cards.cards_check()
        self.map.lay_track(turn, edge_index)
        self.points[turn] += self.distance_points[edge_length]
        self.pieces[turn] -= edge_length
        self.cards.cards_check()
        logging.debug('player {} now has {} points, with {} pieces and {} resources remaining'.format(turn,
                      self.points[turn], self.pieces[turn], len(self.cards.resources['hands'][turn])))

        # end lay_track

    @staticmethod
    def find_best_action(action_values):
        action_index = None
        move = None
        value = -np.inf
        for key, val in action_values.items():
            if key == 'goals_threshold' or key == 'goals_each':
                continue
            value_tmp = np.max(val)
            if value_tmp > value:
                move = key
                action_index = np.argmax(val)
                value = value_tmp
        return move, action_index, value

        # end find_best_action

    def action_values_zero(self, action_values_init, cards_taken):

        turn = self.turn

        action_values = dict(
            track=[-np.inf for _ in range(self.NUM_EDGES)],
            goals_take=[-np.inf],
            goals_threshold=[-np.inf],
            goals_each=np.array([-np.inf for _ in range(self.NUM_GOALS)]),
            deck=[-np.inf],
            faceup=[-np.inf for _ in range(self.NUM_COLORS)]
        )

        if len(self.cards.resources['faceup']) != 5:
            raise self.Error('incorrect number of faceup cards')

        enough_cards = (cards_taken + len(self.cards.resources['deck']) + len(self.cards.resources['discards'])) >= 2
        if enough_cards:
            action_values['deck'] = action_values_init['deck']
            faceup_colors = self.cards.color_count('faceup')
            for c in range(self.NUM_COLORS):
                if (cards_taken == 0 or c > 0) and (faceup_colors[c] > 0):
                    action_values['faceup'][c] = action_values_init['faceup'][c]
            if cards_taken > 0:
                return action_values

        if len(self.cards.goals['deck']) >= 1:
            action_values['goals_take'] = action_values_init['goals_take']
            action_values['goals_threshold'] = action_values_init['goals_threshold']
            action_values['goals_each'] = action_values_init['goals_each']

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
            num_rainbow = 0
            while len(possible_colors) == 0:
                possible_colors = [c for c in np.arange(1, self.NUM_COLORS, 1) if
                                   hand_colors[c] + num_rainbow >= edge_length]
                num_rainbow += 1
            edge_color = self.rng.choice(possible_colors)
        possible_indices = [ind for ind, val in enumerate(self.cards.resources['hands'][turn]) if val == edge_color]
        possible_indices.extend([ind for ind, val in enumerate(self.cards.resources['hands'][turn]) if val == 0])
        indices = possible_indices[:edge_length]
        if len(indices) < edge_length:
            raise self.Error('Cards used is fewer than edge length')
        return indices

        # end choose_resources

    def add_goal_points(self):
        points = np.zeros(self.players, dtype=np.int16)
        for turn in range(self.players):
            subgraph = self.map.create_player_subgraph(turn)
            goals = self.cards.goals['hands'][turn]
            for _, row in goals.iterrows():
                if approx.local_node_connectivity(subgraph, row[0], row[1]) == 1:
                    posneg = '+'
                    points[turn] += row[2]
                    self.goals_completed[turn] += 1
                else:
                    posneg = '-'
                    points[turn] -= row[2]
                logging.debug('goal for player {}: from {} to {}, {}{}'.format(turn, row[0], row[1], posneg, row[2]))
        logging.info('goal points: {}'.format(points))
        self.points += points

    def add_longest_track(self):
        overall_best = self.map.compare_paths(players=self.players)
        for turn in range(self.players):
            G = self.map.create_player_subgraph(turn, multi=False, incl_nodes=True)
            player_best = self.map.find_longest_path(G)
            overall_best = self.map.compare_paths(old=overall_best, new=player_best)
            self.longest_track[turn] = player_best['length']
        points = np.zeros(self.players, dtype=np.int16)
        points[overall_best['turn']] = 10  # ties go to both players
        self.longest_track_winner = overall_best['turn']
        self.longest_track_length = overall_best['length']
        logging.info('player(s) {} wins longest road (+10) with {}-track path'.format(self.longest_track_winner, self.longest_track_length))
        self.points += points

    def next_turn(self):
        self.turn += 1
        if self.turn == self.players:
            self.turn = 0
            self.round += 1
