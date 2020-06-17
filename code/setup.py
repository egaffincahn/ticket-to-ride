from datetime import datetime as dt
import logging
from ticket import utils
from ticket.population import Population


def main(new=True, save_weights=False):

    filemode = 'w' if new else 'a'

    logging.basicConfig(filename=utils.log_file, filemode=filemode, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.WARNING)

    if new:

        population = Population(generations=1, individuals=3)
        logging.critical('started')
        # population = Population(generations=1, individuals=30)

    else:

        logging.critical('re-started')
        population = utils.read_population()
        if any([ind.strategy.weights is None for ind in population.cohort]):
            raise population.Error('did not save weights previously')

    population.go(generations=2)
    population.save(reduce_file_size=not save_weights)

    logging.critical('finished')
    print('finished')


if __name__ == '__main__':
    new = input('Start new process? (y/n) ') == 'y'
    save_weights = input('Save weights? (y/n) ') == 'y'
    main(new=new, save_weights=save_weights)
