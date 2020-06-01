from datetime import datetime as dt
import logging
from ticket import utils
from ticket.population import Population


def main(new=True):

    if new:

        logging.basicConfig(filename=utils.log_file, filemode='w', format='%(message)s', level=logging.INFO)
        logging.critical('started at {}'.format(str(dt.now())))

        population = Population(generations=1, individuals=3)
        # population = Population(generations=1, individuals=30)

    else:

        logging.basicConfig(filename=utils.log_file, filemode='a', format='%(message)s', level=logging.WARNING)
        logging.critical('re-started at {}'.format(str(dt.now())))
        population = utils.read_population()

    population.go()
    population.save(reduce_file_size=True)

    logging.critical('finished at {}'.format(str(dt.now())))
    print('finished')


if __name__ == '__main__':
    main(new=True)
