from datetime import datetime as dt
import logging
import pickle
from ticket_to_ride.population import Population


def main(new=True):

    if new:

        logging.basicConfig(filename='log.txt', filemode='w', format='%(message)s', level=logging.WARNING)
        logging.critical('started at %s', str(dt.now()))

        population = Population(generations=3, individuals=3, deaths=1, number_of_cluster_reps=25)
        # population = Population(generations=250, individuals=30, deaths=1, number_of_cluster_reps=25)

    else:

        logging.basicConfig(filename='log.txt', filemode='a', format='%(message)s', level=logging.WARNING)
        with open('ticket_to_ride/data/data.obj', 'rb') as f:
            population = pickle.load(f)

    run_program(population)

    logging.critical('finished at %s', str(dt.now()))
    print('finished')


def run_program(population):

    while population.epoch < population.generations:
        logging.warning('generation %d', population.epoch)
        losers = population.run_generation()
        population.kill_losers(losers)
        if population.epoch < population.generations:
            population.reproduce()
        population.save()


if __name__ == '__main__':
    main(new=True)
