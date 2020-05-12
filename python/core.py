import pandas as pd
from os.path import join


class TicketToRide:
    NUM_COLORS = 9
    NUM_PARALLEL = 2
    NUM_DISTANCES = 6
    goals_init = pd.read_csv('ticket_to_ride/data/goals.txt')
    NUM_GOALS = len(goals_init)
    NUM_EDGES = 100
    NUM_NODES = 36

    distance_points = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
    pieces_init = 45

    def __init__(self, number_of_cluster_reps=20, players=3, data_location=None):
        self.number_of_cluster_reps = number_of_cluster_reps
        self.players = players
        if data_location is None:
            data_location = join('ticket_to_ride', 'data', 'data.obj')
        self.data_location = data_location

    class Error(Exception):

        def __init__(self, *args):
            self.message = None
            if args:
                self.message = args[0]
