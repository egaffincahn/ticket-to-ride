function [G, hand, deck, faceup, discards, pieces, points] = laytrack(G, turn, pick, hand, deck, faceup, discards, ind, pieces, points)

pieces(turn) = pieces(turn) - G.distance.Edges.Weight(pick);
points(turn) = points(turn) + G.points.Edges.Weight(pick);
G.taken.Edges.Weight(pick) = turn;
[hand, deck, faceup, discards,] = movecards(turn, hand, deck, faceup, discards, 'hand', 'discards', ind);

