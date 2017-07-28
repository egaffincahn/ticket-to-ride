function [G, cards, pieces, points] = laytrack(G, turn, pick, cards, ind, pieces, points)

pieces(turn) = pieces(turn) - G.distance.Edges.Weight(pick);
points(turn) = points(turn) + G.points.Edges.Weight(pick);
G.taken.Edges.Weight(pick) = turn;
cards = movecards(turn, cards, 'hand', 'discards', ind);

