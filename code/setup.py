from datetime import datetime as dt
import logging
from ticket import utils
from ticket.population import Population


def main(new=True):

    filemode = 'w' if new else 'a'

    logging.basicConfig(filename=utils.log_file, filemode=filemode, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.WARNING)

    if new:

        population = Population(generations=1, individuals=3)
        logging.critical('started')
        # population = Population(generations=1, individuals=30)

    else:

        logging.critical('re-started')
        population = utils.read_population()

    population.go()
    population.save(reduce_file_size=True)

    logging.critical('finished at {}'.format(str(dt.now())))
    print('finished')


if __name__ == '__main__':
    new = input('Load previous? (y/n) ') == 'n'
    main(new=new)
