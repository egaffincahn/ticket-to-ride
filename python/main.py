# raise exception
# new logging levels
# necessary:
    # add longest road

from datetime import datetime as dt
import logging
import numpy as np
from genetic import run_all

def main():

    individuals = 99
    generations = 500

    players = 3
    plot = False

    logging.basicConfig(filename='log.txt', filemode='w', format='%(message)s', level=logging.CRITICAL)
    logging.critical('started at %s', str(dt.now()))

    points = run_all(generations, individuals, players)
    logging.critical('finished generations, points:\n%s', np.array_str(points))
    logging.critical('finished at %s', str(dt.now()))
    print('finished')

if __name__ == '__main__':
    main()