import numpy as np
from numpy import random as rd
import pickle
import copy
import logging
from os.path import join
from datetime import datetime as dt
from core import TicketToRide
from ticket_to_ride.strategy import Strategy
from ticket_to_ride.game import Game


class Population(TicketToRide):

    def __init__(self, generations=1, individuals=3, deaths=1, **kwargs):
        super().__init__(**kwargs)
        self.generations = generations
        self.individuals = individuals
        self.deaths = deaths
        self.epoch = 0

        self.alive_after_generation = np.int8(individuals * (self.players - deaths) / self.players)
        if np.mod(individuals, self.players) > 0:
            raise self.Error('Number of individuals must be multiple of number of players')

        self.graveyard = []
        self.cohort = np.array([Individual(epoch=self.epoch, **kwargs) for i in range(individuals)])
        for i in range(individuals):
            self.cohort[i].strategy.init_weights()

    def run_generation(self):
        players = self.players
        sets = np.int16(self.individuals / players)
        order = rd.permutation(self.individuals).reshape(players, sets)
        losers = np.empty(sets, dtype=np.int16)
        logging.info('generation %d', self.epoch)
        for s in range(sets):
            game = Game([self.cohort[order[turn, s]].strategy for turn in range(players)])
            game.play_game()
            losers[s] = order[np.argmin(game.points), s]
            [self.cohort[order[turn, s]].add_experience(game, turn) for turn in range(players)]
            logging.warning('game points: %s, ages: %s', game.points.__str__(),
                            [self.cohort[order[turn, s]].age for turn in range(players)].__str__())
        self.epoch += 1
        return losers

    def reproduce(self):
        parents = self.cohort
        individuals = len(parents)
        pairs = np.int16(individuals / 2)
        order = rd.permutation(individuals).reshape(2, pairs)
        children = [Individual(epoch=self.epoch, number_of_cluster_reps=self.number_of_cluster_reps) for _ in
                    range(pairs)]
        for p in range(pairs):
            children[p].strategy.init_weights(parents[order[0, p]].strategy, parents[order[1, p]].strategy)
        self.cohort = np.concatenate((parents, children))

    def kill_losers(self, losers, save_memory=True):
        if save_memory:
            for l in losers:
                self.cohort[l].strategy = None
        self.graveyard = np.concatenate((self.graveyard, self.cohort[losers]))
        self.cohort = np.delete(self.cohort, losers)

    def extract_data(self, feature, incl_dead=False, sort_by=None):
        cohort = self.cohort
        if incl_dead:
            cohort = np.concatenate((self.graveyard, cohort))
        if sort_by is not None:
            cohort = sorted(cohort, key=lambda i: i.__getattribute__(sort_by))
        values = [individual.__getattribute__(feature) for individual in cohort]
        return values

    def save(self, path='', filename=None, slim=True):
        if filename is None:
            filename = self.data_location
        population = copy.deepcopy(self)
        if slim:
            for individual in population.cohort:
                individual.strategy.weights = None
        with open(join(path, filename), 'wb') as f:
            pickle.dump(population, f)


class Individual(TicketToRide):

    def __init__(self, epoch=0, seed=dt.now().microsecond, **kwargs):
        super().__init__(**kwargs)
        self.age = 0
        self.birthday = epoch
        self.points = np.array([], dtype=np.int16)
        self.pieces_used = np.array([], dtype=np.int16)
        self.tracks = np.array([], dtype=np.int8)
        self.goals_taken = np.array([], dtype=np.int8)
        self.goals_completed = np.array([], dtype=np.int8)
        self.strategy = Strategy(seed=seed, **kwargs)

    def add_experience(self, game, turn):
        self.age += 1
        self.points = np.concatenate((self.points, [game.points[turn]]))
        self.pieces_used = np.concatenate((self.pieces_used, [45 - game.pieces[turn]]))
        self.tracks = np.concatenate((self.tracks, [len(game.map.subset_edges('turn', turn))]))
        self.goals_taken = np.concatenate((self.goals_taken, [game.cards.goals['hands'][turn].shape[0]]))
        self.goals_completed = np.concatenate((self.goals_completed, [game.goals_completed[turn]]))
