function [gamepoints, tau] = rungeneration(G, cards, info, tau, numworkers)

players = info.players;
individuals = length(tau);%length(strategies);
order = randperm(individuals);

tau = reshape(tau(order), [individuals/players,players]);
if nargin < 5
    numworkers = 0;
end
parfor (i = 1:individuals/players, numworkers) % scroll through each matchup
    gamepoints(i,:) = playgame_tau(G, tau(i,:), cards, info);
end
