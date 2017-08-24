function [G, cards, info, memory] = laytrack(G, turn, pick, cards, ind, info, memory)
if G.distance.Edges.Weight(pick) <= 0
    keyboard
end
info.pieces(turn) = info.pieces(turn) - G.distance.Edges.Weight(pick);
info.points(turn) = info.points(turn) + G.points.Edges.Weight(pick);
G.taken.Edges.Weight(pick) = turn;
cards = movecards(turn, cards, 'hand', 'discards', ind);
% memory.revaluate = num2cell(true(1, players));

% fprintf('\n\n')
% G.taken.Edges(pick,:)
% [info.pieces'; info.points]

% plotgraph(turn, G, cards, info)