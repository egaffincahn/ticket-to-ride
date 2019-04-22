# ticket-to-ride
A program that plays Ticket to Ride!

Call  
`population()` to run the algorithm, or
`playsinglegame(numplayers)` to play just a one game and visualize the gameplay.

The program can now compete (at least a little)! Each individual in the genetic algorithm is represented by one feed-forward neural network. The inputs are the cards in hand, the face-up cards, the player's goal cards, and a representation of the board and its tracks. The output is the player's action. There is no specific strategy, but over time the each generation should be better at playing than the previous.

If turned on, the `plotgraph` function allows you to visualize the gameplay.
