function [] = population(players)

rng(1)

if nargin < 1 || isempty(players)
    players = 3;
end

individuals = 10;
iterations = 100;

S = strategy(individuals);
pointsmatrix = nan(iterations, individuals - rem(individuals, players));
for i = 1:iterations
    losers = [];
    iterationpoints = [];
    for j = 1:players:individuals
        if j + players > individuals; continue; end
        s = S(j:j+players-1);
        [points, winner] = ticket(s);
        losers = [losers, find(winner ~= 1:players) + j - 1]; %#ok<AGROW> % indices of individuals who lost
        iterationpoints = [iterationpoints; points]; %#ok<AGROW>
    end
    pointsmatrix(i,:) = iterationpoints(:)';
    S(losers) = []; % kill losers
    nkids = floor((individuals - length(S)) / 2);
    pairs = randperm(length(S));
    for j = 1:2:length(pairs)
        S(end+1:end+nkids) = multiply(S(pairs([j, j+1])), nkids);
    end
    S = S(randperm(length(S)));
    disp('finished iteration')
end

plot(pointsmatrix)
