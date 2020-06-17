from matplotlib import pyplot as plt
import numpy as np
from numpy import random as rd
from ticket import utils

# population = utils.read_population()
#
# rng = rd.default_rng()
#
# age = population.extract_data(feature='age', incl_dead=True)
# birthday = population.extract_data(feature='birthday', incl_dead=True)
# parents = population.extract_data(feature='parent', incl_dead=True)
# points = population.extract_data(feature='points', incl_dead=True)
# goals_taken = population.extract_data(feature='goals_taken', incl_dead=True)
# goals_completed = population.extract_data(feature='goals_completed', incl_dead=True)
# tracks = population.extract_data(feature='tracks', incl_dead=True)
# pieces_used = population.extract_data(feature='pieces_used', incl_dead=True)
#
#
# def jitter(x, frac=.1):
#     return [ind+rng.uniform(high=frac, size=ind.shape) for ind in iter(x)]
#
# num_individuals = len(population.graveyard) + len(population.cohort)
# epoch = [np.arange(birthday[i], birthday[i] + age[i]) for i in range(num_individuals)]
#
# fig, axs = plt.subplots(3, 2)
# axs[0][0].plot(birthday, age, '.')
# for i in range(num_individuals):
#     axs[1][0].plot(epoch[i], jitter(goals_taken[i]))
#     axs[2][0].plot(epoch[i], jitter(goals_completed[i]))
#     axs[0][1].plot(epoch[i], jitter(points[i]))
#     axs[1][1].plot(epoch[i], jitter(tracks[i]))
#     axs[2][1].plot(epoch[i], jitter(pieces_used[i]))
#
# axs[0][0].set_ylabel('Age')
# axs[1][0].set_ylabel('Goals Taken')
# axs[2][0].set_ylabel('Goals Completed')
# axs[0][1].set_ylabel('Points')
# axs[1][1].set_ylabel('Tracks Placed')
# axs[2][1].set_ylabel('Pieces Used')
#
# axs[2][0].set_xlabel('Epoch')
# axs[2][1].set_xlabel('Epoch')
#
# fig.show()
#
#
# population = utils.read_population()
# population.plot_feature('points', incl_dead=False)
# population.plot_feature('points', incl_dead=True)
# birthday = population.extract_data(feature='birthday', incl_dead=True)
# age = population.extract_data(feature='age', incl_dead=True)
# points = population.extract_data(feature='points', incl_dead=True)
# num_individuals = len(birthday)
# epoch = [np.arange(birthday[i], birthday[i] + age[i]) for i in range(num_individuals)]
# epoch_reshape = np.concatenate(epoch)
# points_reshape = np.concatenate(points)
# epoch_fun = np.mean
# epoch_smush = map(lambda x: epoch_fun(points_reshape[epoch_reshape == x]), range(population.epoch))


# import numpy as np
# from ticket import utils
population = utils.read_population()
population.plot_feature(feature='points', incl_dead=True)
population.plot_feature(feature='points', incl_dead=True, summary=np.mean)
# population.plot_feature(feature='age', incl_dead=True)
population.plot_feature(feature='age', incl_dead=True, summary=np.mean)

