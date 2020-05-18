import numpy as np
import networkx as nx
import logging
from networkx.algorithms import approximation as approx
from ticket.core import TicketToRide
from ticket.board import Map


class Strategy(TicketToRide):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs, self.input_indices = self.init_inputs()
        blank_map = Map(**kwargs)
        self.reps = nx.diameter(blank_map.map) + 1
        self.weights = [[[] for _ in range(2)] for _ in range(self.reps + 1)]
        self.player_logical_index = None
        self.prob_mutation = None

    def set_game_turn(self, game_turn):
        self.player_logical_index = np.arange(self.players) == game_turn  # changes every game

    def init_weights(self, parent=None):

        logging.debug('Building strategy')
        self.weights = [[_rand_init(self.mask[rep][ind], self.rng) for ind in range(2)] for rep in range(self.reps + 1)]

        if parent is not None:
            self.prob_mutation = self.rng.beta(self.mutation_beta_params[0], self.mutation_beta_params[1], size=(self.reps + 1, 2))
            for rep in range(self.reps + 1):
                for ind in range(2):
                    mutation_mask = self.rng.uniform(size=self.mask[rep][ind].shape) > self.prob_mutation[rep,ind]
                    self.weights[rep][ind][mutation_mask] = parent.weights[rep][ind][mutation_mask]

    def init_inputs(self):

        inputs = np.concatenate((  # non-zero values in a row R of inputs map to row R of layer 1
            np.zeros(1),  # bias
            np.zeros(1) + self.pieces_init,
            np.zeros(self.players - 1) + self.pieces_init,
            np.zeros(1),
            np.zeros(self.players - 1),
            np.zeros(self.players - 1),
            np.zeros(self.NUM_COLORS),  # faceup
            np.zeros(self.NUM_COLORS),  # hand
            np.zeros(self.NUM_GOALS),
            np.zeros(self.NUM_EDGES)
        )).astype(dtype=np.float32)

        input_indices = dict()
        input_indices['bias'] = np.array([0])
        input_indices['turn_pieces'] = next_ind(input_indices)
        input_indices['opponent_pieces'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['turn_points'] = next_ind(input_indices)
        input_indices['opponent_points'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['opponent_hand_lengths'] = next_ind(input_indices) + np.arange(self.players - 1)
        input_indices['faceups'] = next_ind(input_indices) + np.arange(self.NUM_COLORS)
        input_indices['hand_colors'] = next_ind(input_indices) + np.arange(self.NUM_COLORS)
        input_indices['goals'] = next_ind(input_indices) + np.arange(self.NUM_GOALS)
        input_indices['edges'] = next_ind(input_indices) + np.arange(self.NUM_EDGES)

        return inputs, input_indices

    def update_inputs(self, input_type, game):

        turn = game.turn

        if input_type == 'all' or input_type == 'edges':
            self.inputs[self.input_indices['turn_pieces']] = self.norm(game.pieces[self.player_logical_index], 'pieces')
            self.inputs[self.input_indices['opponent_pieces']] = self.norm(
                game.pieces[np.logical_not(self.player_logical_index)], 'pieces')
            self.inputs[self.input_indices['turn_points']] = self.norm(game.points[self.player_logical_index], 'points')
            self.inputs[self.input_indices['opponent_points']] = self.norm(
                game.points[np.logical_not(self.player_logical_index)], 'points')
            self.inputs[self.input_indices['edges']] = game.map.extract_feature(range(self.NUM_EDGES), turn=turn)

        if input_type == 'all' or input_type == 'edges' or input_type == 'goal':
            goal_points = np.zeros(self.NUM_GOALS)
            subgraph = game.map.create_player_subgraph(turn)
            for g in range(game.cards.goals['hands'][turn].shape[0]):
                ind = game.cards.goals['hands'][turn].index[g]
                frm = game.cards.goals['hands'][turn].iloc[g, 0]
                to = game.cards.goals['hands'][turn].iloc[g, 1]
                points = game.cards.goals['hands'][turn].iloc[g, 2]
                if not approx.local_node_connectivity(subgraph, frm, to):
                    points = -points
                goal_points[ind] = points
            self.inputs[self.input_indices['goals']] = self.norm(goal_points, 'goals')

        if input_type == 'all' or input_type == 'resources':
            hand_lengths = np.array([len(game.cards.resources['hands'][trn]) for trn in range(self.players)])
            self.inputs[self.input_indices['opponent_hand_lengths']] = self.norm(
                hand_lengths[np.logical_not(self.player_logical_index)], 'hand_length')
            self.inputs[self.input_indices['faceups']] = self.norm(game.cards.color_count('faceup', dtype='array'),
                                                                   'faceups')
            self.inputs[self.input_indices['hand_colors']] = self.norm(
                game.cards.color_count('hands', turn=turn, dtype='array'), 'hand')

    def feedforward(self):
        y = self.inputs
        for rep in range(self.reps + 1):
            if rep > 0:
                y = _catbias(y)
            y = np.tanh(np.matmul(y, self.weights[rep][0]))  # onto 4 superclusters (final layer: just Edges, Colors)
            y = _relu(np.matmul(_catbias(y), self.weights[rep][1]))  # onto Edges (final layer: output valuation)
        action_values = {
            'track': list(y[range(self.NUM_EDGES)]),
            'goals': [y[self.NUM_EDGES]],
            'deck': [y[self.NUM_EDGES + 1]],
            'faceup': list(y[-5:])
        }
        if not isinstance(y[0], np.float32):
            raise self.Error('output is not float32')

        return action_values

    def norm(self, x, ntype):
        if ntype == 'points':
            return (x - 30) / 30
        elif ntype == 'pieces':
            return (x - 30) / 30
        elif ntype == 'goals':
            return x / 11
        elif ntype == 'faceups':
            return (x - .5) / .5
        elif ntype == 'hand':
            return (x - 3.5) / 3.5
        elif ntype == 'hand_length':
            return (x - 10) / 10
        elif ntype == 'distance':
            return (x - 3.5) / 3.5
        else:
            raise self.Error('invalid normalization type {}'.format(ntype))

    # end class Strategy


def next_ind(x):
    return np.max(np.concatenate((list(x.values()))), keepdims=True) + 1


def _catbias(x):
    return np.concatenate((np.ones(1, dtype=np.float32), x))


def _rand_init(m, rng):
    norms = m.sum(axis=1, dtype=np.int16)
    w = np.zeros(m.shape, dtype=np.float32)
    w[m] = rng.uniform(-.5, .5, size=norms.sum()).astype(np.float32)
    return (w.T / np.sqrt(norms)).T


def _relu(x):
    return np.maximum(x, 0)


def _lincomb(x, y, p):
    return p * x + (1 - p) * y
