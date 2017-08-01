function [G, cards, info] = laytrack(G, turn, pick, cards, ind, info)

info.pieces(turn) = info.pieces(turn) - G.distance.Edges.Weight(pick);
info.points(turn) = info.points(turn) + G.points.Edges.Weight(pick);
G.taken.Edges.Weight(pick) = turn;
cards = movecards(turn, cards, 'hand', 'discards', ind);

% fprintf('\n\n\n')
% G.taken.Edges(pick,:)
% [info.pieces'; info.points]

plotgraph(turn, G, cards, info)