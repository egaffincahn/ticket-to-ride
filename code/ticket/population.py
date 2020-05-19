import numpy as np
import logging
import pickle
import copy
import gzip
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

        self.graveyard = []
        self.cohort = np.array([self.create_individual(**kwargs) for _ in range(self.individuals)])

    def go(self, generations=None, **kwargs):
        if generations is None:
            generations = self.generations
        while self.epoch < generations:
            winners, losers, rest = self.run_generation()
            self.extinction(losers)  # only losers die
            if self.epoch < self.generations:
                self.reproduce(winners, rest, **kwargs)  # only winners reproduce

    def run_generation(self):
        logging.warning('generation {}'.format(self.epoch))
        players = self.players
        sets = np.int16(self.individuals / players)
        order = self.rng.permutation(self.individuals).reshape(players, sets)
        winners = np.empty(sets, dtype=np.int16)
        losers = np.empty(sets, dtype=np.int16)

        for s in range(sets):
            game = Game([self.cohort[order[turn, s]] for turn in range(players)])
            game.play_game()
            winners[s] = order[np.argmax(game.points), s]
            losers[s] = order[np.argmin(game.points), s]
            [self.cohort[order[turn, s]].add_experience(game, turn) for turn in range(players)]
            logging.warning('game summary: points: {}, id: {}, parent: {}, ages: {}'.format(game.points, [self.cohort[order[turn, s]].id_ for turn in range(players)], [self.cohort[order[turn, s]].parent for turn in range(players)], [self.cohort[order[turn, s]].age for turn in range(players)]))
        self.epoch += 1
        ties = winners == losers
        winners = winners[np.logical_not(ties)]
        losers = losers[np.logical_not(ties)]
        middlers = order[np.logical_not(np.isin(order, np.concatenate((winners, losers))))]  # neither winners nor losers
        return self.cohort[winners], self.cohort[losers], self.cohort[middlers]

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

    def extract_data(self, feature, incl_dead=False, sort_by=None):
        cohort = self.cohort
        if incl_dead:
            cohort = np.concatenate((self.graveyard, cohort))
        if sort_by is not None:
            cohort = sorted(cohort, key=lambda i: i.__getattribute__(sort_by))
        values = [individual.__getattribute__(feature) for individual in cohort]
        return values

    def save(self, reduce_file_size=True):
        population = copy.deepcopy(self)
        if reduce_file_size:
            logging.critical('removing weights to save disk space')
            for individual in population.cohort:
                individual.strategy.weights = None
        with gzip.open(utils.get_output_file(), 'wb') as f:
            logging.critical('writing to {}'.format(utils.get_output_file()))
            pickle.dump(population, f)


class Individual(TicketToRide):

    def __init__(self, id_, epoch=0, parent=None, **kwargs):
        super().__init__(**kwargs)

        self.id_ = id_
        self.parent = parent if parent is None else parent.id_
        self.birthday = epoch
        self.age = 0
        self.points = np.array([], dtype=np.int16)
        self.pieces_used = np.array([], dtype=np.int16)
        self.tracks = np.array([], dtype=np.int8)
        self.goals_taken = np.array([], dtype=np.int8)
        self.goals_completed = np.array([], dtype=np.int8)
        self.rng_state = self.rng.bit_generator.state
        self.strategy = Strategy(self, **kwargs)

    def add_experience(self, game, turn):
        self.age += 1
        self.points = np.concatenate((self.points, [game.points[turn]]))
        self.pieces_used = np.concatenate((self.pieces_used, [45 - game.pieces[turn]]))
        self.tracks = np.concatenate((self.tracks, [len(game.map.subset_edges('turn', turn))]))
        self.goals_taken = np.concatenate((self.goals_taken, [game.cards.goals['hands'][turn].shape[0]]))
        self.goals_completed = np.concatenate((self.goals_completed, [game.goals_completed[turn]]))
