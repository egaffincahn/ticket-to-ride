from matplotlib import pyplot as plt
import numpy as np
import pickle
from numpy import random as rd

# exec(open("analysis.py").read())

with open('ticket_to_ride/data/data.obj', 'rb') as f:
    population = pickle.load(f)

rng = rd.default_rng()

age = population.extract_data(feature='age', incl_dead=True)
birthday = population.extract_data(feature='birthday', incl_dead=True)
points = population.extract_data(feature='points', incl_dead=True)
goals_taken = population.extract_data(feature='goals_taken', incl_dead=True)
goals_completed = population.extract_data(feature='goals_completed', incl_dead=True)
tracks = population.extract_data(feature='tracks', incl_dead=True)
pieces_used = population.extract_data(feature='pieces_used', incl_dead=True)

def jitter(x, frac=.1):
    return [ind+rng.uniform(high=frac, size=ind.shape) for ind in iter(x)]

num_individuals = len(population.graveyard) + len(population.cohort)
epoch = [np.arange(birthday[i], birthday[i] + age[i]) for i in range(num_individuals)]

fig, axs = plt.subplots(3, 2)
axs[0][0].plot(birthday, age, '.')
for i in range(num_individuals):
    axs[1][0].plot(epoch[i], jitter(goals_taken[i]))
    axs[2][0].plot(epoch[i], jitter(goals_completed[i]))
    axs[0][1].plot(epoch[i], jitter(points[i]))
    axs[1][1].plot(epoch[i], jitter(tracks[i]))
    axs[2][1].plot(epoch[i], jitter(pieces_used[i]))

axs[0][0].set_ylabel('Age')
axs[1][0].set_ylabel('Goals Taken')
axs[2][0].set_ylabel('Goals Completed')
axs[0][1].set_ylabel('Points')
axs[1][1].set_ylabel('Tracks Placed')
axs[2][1].set_ylabel('Pieces Used')

axs[2][0].set_xlabel('Epoch')
axs[2][1].set_xlabel('Epoch')

fig.show()
