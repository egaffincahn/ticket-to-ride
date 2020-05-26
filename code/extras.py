from ticket.population import Population
from ticket.game import Game


def play_single_game(players=3):
    pop = Population(individuals=players)
    game = Game(pop.cohort)
    game.play_game()
    return game
