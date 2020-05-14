function [gamepoints, winner] = playsinglegame(players)

rng(1)

if ~nargin
    players = 3;
end
doplot = false;

[G, cards, info] = setupgame(players);
for i = 1:players
    strategies(i) = strategy(G, cards); %#ok<AGROW>
end

[gamepoints, winner] = playgame(G, strategies, cards, info, doplot);
