from datetime import datetime as dt
import logging
import pickle
import gzip
from ticket import utils
from ticket.population import Population


def main(new=True):

    if new:

        logging.basicConfig(filename=utils.log_file, filemode='w', format='%(message)s', level=logging.WARNING)
        logging.critical('started at %s', str(dt.now()))

        population = Population(generations=1, individuals=3)
        # population = Population(generations=1, individuals=30)

    else:

        logging.basicConfig(filename=utils.log_file, filemode='a', format='%(message)s', level=logging.WARNING)
        logging.critical('re-started at %s', str(dt.now()))
        with gzip.open(utils.output_file, 'rb') as f:
            population = pickle.load(f)

    population.go()
    population.save(save_memory=True)

    logging.critical('finished at %s', str(dt.now()))
    print('finished')


if __name__ == '__setup__':
    main(new=True)
