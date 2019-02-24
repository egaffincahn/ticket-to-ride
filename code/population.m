function [] = population(players)

% rng(1)
rng('shuffle')

if nargin < 1 || isempty(players)
    players = 3;
end

individuals = 100;
iterations = 100;

S = strategy(individuals, players);
pointsmatrix = nan(iterations, individuals - rem(individuals, players)); % WHAT IS THIS?
for i = 1:iterations
    losers = []; % WHAT IS THIS?
    iterationpoints = []; % WHAT IS THIS?
    for j = 1:players:individuals
        if j + players > individuals; continue; end
        s = S(j:j+players-1); % choose this individual's strategies
        [points, winner] = ticket(s, players);
        losers = [losers, find(winner ~= 1:players) + j - 1]; %#ok<AGROW> % indices of individuals who lost
        iterationpoints = [iterationpoints; points]; %#ok<AGROW>
    end
    pointsmatrix(i,:) = iterationpoints(:)';
    S(losers) = []; % kill losers
    nkids = floor((individuals - length(S)) / 2);
    pairs = randperm(length(S));
    for j = 1:2:length(pairs)
        S(end+1:end+nkids) = multiply(S(pairs([j, j+1])), nkids, players);
    end
    S = S(randperm(length(S)));
    disp('finished iteration')
end

plot(pointsmatrix)

keyboard
