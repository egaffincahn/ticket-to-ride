function [winnerpoints, losers] = rungeneration(G, strategies, cards, info)

players = info.players;
individuals = length(strategies);
order = randperm(individuals);
winnerpoints = nan(1,individuals/players);

losers = nan(individuals/players, players-1);
matchups = reshape(order, [individuals/players,players]);
strategies = reshape(strategies, [individuals/players,players]);
for i = 1:individuals/players % scroll through each matchup
    gameplayers = matchups(i,:); % choose first 3 of random perm
    [gamepoints, winner] = playgame(G, strategies(i,:), cards, info);
    losers(i,:) = gameplayers(1:players ~= winner);
    winnerpoints(i) = gamepoints(winner);
end

