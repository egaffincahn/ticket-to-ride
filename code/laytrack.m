function [G, cards, info, memory] = laytrack(G, turn, pick, cards, ind, info, memory)
if G.distance.Edges.Weight(pick) <= 0
    keyboard
end
info.pieces(turn) = info.pieces(turn) - G.distance.Edges.Weight(pick);
info.points(turn) = info.points(turn) + calcpoints(G.distance.Edges.Weight(pick));
G.taken.Edges.Weight(pick) = turn;
cards = movecards(turn, cards, 'hand', 'discards', ind);

function points = calcpoints(distances)

points = nan(size(distances));
points(distances == 6) = 15;
points(distances == 5) = 10;
points(distances == 4) = 7;
points(distances == 3) = 4;
points(distances == 2) = 2;
points(distances == 1) = 1;
