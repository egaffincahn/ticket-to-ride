function [gamepoints, winner] = playsinglegame

players = 3;
doplot = true;

[G, cards, info] = setupgame(players);
for i = 1:players
    strategies(i) = strategy(G, cards); %#ok<AGROW>
end

[gamepoints, winner] = playgame(G, strategies, cards, info, doplot);
