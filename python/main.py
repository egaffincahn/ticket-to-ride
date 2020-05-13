from datetime import datetime as dt
import logging
import pickle
from ticket_to_ride.population import Population
import utils


def main(new=True):

    if new:

        logging.basicConfig(filename=utils.log_file, filemode='w', format='%(message)s', level=logging.WARNING)
        logging.critical('started at %s', str(dt.now()))

        population = Population(generations=5, individuals=3, deaths=1, number_of_cluster_reps=25)
        # population = Population(generations=250, individuals=30, deaths=1, number_of_cluster_reps=25)

    else:

        logging.basicConfig(filename=utils.log_file, filemode='a', format='%(message)s', level=logging.WARNING)
        logging.critical('re-started at %s', str(dt.now()))
            population = pickle.load(f)

    population.go()
    population.save(save_memory=False)

    logging.critical('finished at %s', str(dt.now()))
    print('finished')


if __name__ == '__main__':
    main(new=False)
