function [] = population

%#ok<*AGROW>

rng(3)

individuals = 120;
generations = 2000;
players = 3; % players per game - 1 lives on

[G, cards, info] = setupgame(players);

h = waitbar(0, 'Testing parallel computing toolbox...');

ncores = feature('numcores');
if ncores > 2
    if isempty(gcp('nocreate'))
        parpool(ncores - 1);
        numworkers = ncores - 1;
    else
        pool = gcp;
        numworkers = pool.NumWorkers;
    end
else
    numworkers = 0;
end

h = waitbar(0, h, 'Randomizing network weights');

parfor (i = 1:individuals, numworkers)
    strategies(i) = strategy(G, cards);
end
% load('strategies', 'strategies')

winnerpoints = nan(generations,individuals/players);
durations = nan(generations,1);
ages = ones(generations,individuals);

str = sprintf('Finished generation %d of %d (%.2f%%)\nEstimating time remaining...', 0, generations, 0);
tstart = tic;

for i = 1:generations
    h = waitbar((i-1)/generations, h, str);
    t = tic;
    
    [winnerpoints(i,:), losers] = rungeneration(G, strategies, cards, info);
    strategies(losers(:)) = [];
    strategies = multiply(strategies, players);
    
    ages_temp = ages(i,:);
    ages_temp = ages_temp + 1;
    ages_temp(losers(:)) = [];
    ages_temp = [ages_temp, ones(1, individuals * (players-1) / players)];
    ages(i+1,:) = ages_temp;
    
    durations(i) = toc(t);
    str = sprintf('Finished generation %d of %d (%.2f%%)\n%s', i, generations, 100*i/generations, timeremaining(i, generations, tstart, true));
    h = waitbar(i/generations, h, str);
end
delete(h)

figure(1), plot(1:generations, durations, '-o'), xlabel('generation'), ylabel('generation time (s)')

figure(2), clf
subplot(2,1,1), plot(1:generations, mean(winnerpoints, 2), '-o'), xlabel('generation'), ylabel('average winner points')
subplot(2,1,2), plot(1:generations, max(winnerpoints, [], 2), '-o'), xlabel('generation'), ylabel('max winner points')

figure(3), clf
subplot(2,1,1), plot(1:generations+1, mean(ages(:,1:individuals/players), 2), '-o'), xlabel('generation'), ylabel('average parent age')
subplot(2,1,2), plot(1:generations+1, max(ages, [], 2), 'o'), xlabel('generation'), ylabel('max parent age')

save('strategies', 'strategies')

keyboard
