import numpy as np
import logging
import pickle
import copy
import gzip
from itertools import chain
from matplotlib import pyplot as plt
from ticket.core import TicketToRide
from ticket.strategy import Strategy
from ticket.game import Game
from ticket import utils


class Population(TicketToRide):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # defaults
        self.generations = 1
        self.individuals = 3
        self.deaths = 1

        # update defaults
        for key in kwargs:
            self.__setattr__(key, kwargs[key])

        self.total_individuals = 0
        self.epoch = 0
        self.alive_after_generation = np.int8(self.individuals * (self.players - self.deaths) / self.players)
        if np.mod(self.individuals, self.players) > 0:
            raise self.Error('Number of individuals must be multiple of number of players')

        self._order = None
        self.graveyard = []
        self.cohort = np.array([self.create_individual(**kwargs) for _ in range(self.individuals)])

    def go(self, generations=None, **kwargs):
        if generations is None:
            generations = self.generations
        else:
            self.generations = generations
        while self.epoch < generations:
            winners, losers, rest = self.run_generation()
            self.extinction(losers)  # only losers die
            if self.epoch < generations:
                self.reproduce(winners, rest, **kwargs)  # only winners reproduce

    def run_generation(self):
        logging.warning('generation {}'.format(self.epoch))
        players = self.players
        sets = np.int16(self.individuals / players)
        self._order = self.rng.permutation(self.individuals).reshape(players, sets)
        winners = np.empty(sets, dtype=np.int16)
        losers = np.empty(sets, dtype=np.int16)
        for s in range(sets):
            winners[s], losers[s] = self.play_game(s)
        self.epoch += 1
        ties = winners == losers
        winners = winners[np.logical_not(ties)]
        losers = losers[np.logical_not(ties)]
        middlers = self._order[np.logical_not(np.isin(self._order, np.concatenate((winners, losers))))]
        return self.cohort[winners], self.cohort[losers], self.cohort[middlers]

    def play_game(self, s):
        game_individuals = [self.cohort[self._order[turn, s]] for turn in range(self.players)]
        game = Game([self.cohort[self._order[turn, s]] for turn in range(self.players)])
        game.play_game()
        winner = self._order[np.argmax(game.points), s]
        loser = self._order[np.argmin(game.points), s]
        [self.cohort[self._order[turn, s]].add_experience(self.epoch, game, turn) for turn in range(self.players)]
        logging.warning('game summary: points: {}, id: {}, parent: {}, ages: {}'.format(
            game.points, [ind.id_ for ind in game_individuals], [ind.parent for ind in game_individuals],
            [ind.age for ind in game_individuals]))
        return winner, loser

    def create_individual(self, parent=None, **kwargs):
        id_ = self.total_individuals
        parent_id = None
        if parent is not None:
            parent_id = parent.id_
        logging.info('creating individual {} from parent {}'.format(id_, parent_id))
        individual = Individual(id_=id_, epoch=self.epoch, parent=parent, **kwargs)
        if parent is None:
            individual.strategy.init_weights()
        else:
            individual.strategy.init_weights(parent.strategy)
            individual.prob_mutation = individual.strategy.prob_mutation
        self.total_individuals += 1
        return individual

    def reproduce(self, parents, nonparents, **kwargs):
        parents_scrambled = self.rng.permutation(parents)
        children = [self.create_individual(parent=p, **kwargs) for p in parents_scrambled]
        self.cohort = np.concatenate((parents, children, nonparents))

    def extinction(self, losers, reduce_file_size=True):
        if reduce_file_size:
            for lsr in losers:
                lsr.strategy = None
        self.graveyard = np.concatenate((self.graveyard, losers))
        self.cohort = self.cohort[np.logical_not(np.isin(self.cohort, losers))]

    def extract_data(self, feature, incl_dead=False, sort_by=None, summary=None):
        def _extract(feature_):
            cohort = self.cohort
            if incl_dead:
                cohort = np.concatenate((self.graveyard, cohort))
            if sort_by is not None:
                cohort = sorted(cohort, key=lambda i: i.__getattribute__(sort_by))
            return [individual.__getattribute__(feature_) for individual in cohort]
        values_tmp = _extract(feature_=feature)
        epoch_tmp = _extract(feature_='epoch')

        if summary is None:
            epoch = epoch_tmp
            values = values_tmp
        elif is_nested(values_tmp):
            epoch_flat = np.concatenate(epoch_tmp)
            values_flat = np.concatenate(values_tmp)
            epoch = np.unique(epoch_flat)
            values = np.array(list(map(lambda x: summary(values_flat[epoch_flat == x]), epoch)))
        else:
            raise self.Error('"{}" feature cannot be used with summary statistic'.format(feature))
        return epoch, values

    def save(self, reduce_file_size=True):
        population = copy.deepcopy(self)
        if reduce_file_size:
            logging.critical('removing weights to save disk space')
            for individual in population.cohort:
                individual.strategy.weights = None
        with gzip.open(utils.get_output_file(), 'wb') as f:
            logging.critical('writing to {}'.format(utils.get_output_file()))
            pickle.dump(population, f)

    def plot_feature(self, feature, jitter_frac=None, **kwargs):

        def jitter(x_, frac=jitter_frac):
            if is_nested(x_):
                return [ind + self.rng.uniform(high=frac/2, low=-frac/2, size=ind.shape) for ind in iter(x_)]
            else:
                return x_ + self.rng.uniform(high=frac / 2, low=-frac / 2, size=np.array(x_).shape)

        epoch, plotting_data = self.extract_data(feature=feature, **kwargs)

        if jitter_frac is None:
            jitter_frac = 0
            if is_nested(plotting_data):
                unlisted = list(chain(*plotting_data))
            else:
                unlisted = plotting_data
            if len(np.unique(unlisted)) / len(unlisted) < .1:
                jitter_frac = .1

        if 'summary' in kwargs and kwargs['summary'] is not None:
            plt.plot(epoch, jitter(plotting_data, frac=jitter_frac))
        else:
            for x, y in zip(epoch, jitter(plotting_data, frac=jitter_frac)):
                plt.plot(x, y)

        plt.xlabel('Epoch')
        plt.ylabel(feature)
        plt.show()


class Individual(TicketToRide):

    def __init__(self, id_=None, epoch=0, parent=None, **kwargs):
        super().__init__(**kwargs)

        self.id_ = id_
        self.parent = parent if parent is None else parent.id_
        self.birthday = epoch
        self.age = 0
        self.instantaneous_age = np.array([], dtype=np.int16)
        self.epoch = np.array([], dtype=np.int32)
        self.points = np.array([], dtype=np.int16)
        self.pieces_used = np.array([], dtype=np.int16)
        self.tracks = np.array([], dtype=np.int8)
        self.longest_track = np.array([], dtype=np.int8)
        self.goals_taken = np.array([], dtype=np.int8)
        self.goals_completed = np.array([], dtype=np.int8)
        self.rng_state = self.rng.bit_generator.state
        self.strategy = Strategy(self, **kwargs)

    def add_experience(self, epoch, game, turn):
        self.age += 1
        self.instantaneous_age = np.concatenate((self.instantaneous_age, [self.age]))
        self.epoch = np.concatenate((self.epoch, [epoch]))
        self.points = np.concatenate((self.points, [game.points[turn]]))
        self.pieces_used = np.concatenate((self.pieces_used, [45 - game.pieces[turn]]))
        self.tracks = np.concatenate((self.tracks, [len(game.map.subset_edges('turn', turn))]))
        self.longest_track = np.concatenate((self.longest_track, [game.longest_track[turn]]))
        self.goals_taken = np.concatenate((self.goals_taken, [game.cards.goals['hands'][turn].shape[0]]))
        self.goals_completed = np.concatenate((self.goals_completed, [game.goals_completed[turn]]))


def is_nested(x):
    def is_list(x_):
        return isinstance(x_, list) or isinstance(x_, np.ndarray)
    if not is_list(x):
        return False
    are_nested = [is_list(x_) for x_ in x]
    if not np.any(are_nested):
        return False
    return True
