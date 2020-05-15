import pandas as pd
from ticket import utils


class TicketToRide:
    NUM_COLORS = 9
    NUM_PARALLEL = 2
    NUM_DISTANCES = 6
    goals_init = pd.read_csv(utils.goals_file)
    NUM_GOALS = len(goals_init)
    NUM_EDGES = 100
    NUM_NODES = 36

    distance_points = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
    pieces_init = 45

    mask, _number_of_cluster_reps_tmp = utils.read_masks()  # only want to read in once

    def __init__(self, **kwargs):

        # defaults
        self.players = 3
        self.data_location = utils.data_location
        self.mutation_beta_params = [2, 200]

        # update defaults
        for key in kwargs:
            self.__setattr__(key, kwargs[key])

        if 'number_of_cluster_reps' in kwargs and self._number_of_cluster_reps_tmp != self.number_of_cluster_reps:
            raise self.Error('Incorrect number_of_cluster_reps, re-run write_masks()')

    class Error(Exception):

        def __init__(self, *args):
            self.message = None
            if args:
                self.message = args[0]
