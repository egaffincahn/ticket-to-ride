function [] = population

%#ok<*AGROW>

% rng(3)

individuals = 120;
generations = 5;
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

ages = zeros(individuals,1);

fid = fopen('log.csv', 'w');
fprintf(fid, 'generation,duration,mean_winner_points,max_winner_points,mean_parent_age,max_parent_age\n');

str = sprintf('Finished generation %d of %d (%.2f%%)\nEstimating time remaining...', 0, generations, 0);
tstart = tic;

for g = 1:generations
    ages = ages + 1;
    h = waitbar((g-1)/generations, h, str);
    t = tic;
    
    [winnerpoints, losers] = rungeneration(G, strategies, cards, info, numworkers);
    strategies(losers(:)) = [];
    strategies = multiply(strategies, players);
    
    ages(losers(:)) = [];
    ages = [ages; zeros(individuals * (players-1) / players, 1)];
    
    fprintf(fid, '%d,%.1f,%.1f,%d,%.1f,%d\n', ...
        g, toc(t), ...
        mean(winnerpoints), max(winnerpoints), ...
        mean(ages(1:individuals/players)), max(ages(1:individuals/players)));
    str = sprintf('Finished generation %d of %d (%.2f%%)\n%s', g, generations, 100*g/generations, timeremaining(g, generations, tstart, true));
    h = waitbar(g/generations, h, str);
end
delete(h)

% figure(1), plot(1:generations, durations, '-o'), xlabel('generation'), ylabel('generation time (s)')

% figure(2), clf
% subplot(2,1,1), plot(1:generations, mean(winnerpoints, 2), '-o'), xlabel('generation'), ylabel('average winner points')
% subplot(2,1,2), plot(1:generations, max(winnerpoints, [], 2), '-o'), xlabel('generation'), ylabel('max winner points')

% figure(3), clf
% subplot(2,1,1), plot(1:generations+1, mean(ages(:,1:individuals/players), 2), '-o'), xlabel('generation'), ylabel('average parent age')
% subplot(2,1,2), plot(1:generations+1, max(ages, [], 2), 'o'), xlabel('generation'), ylabel('max parent age')

fclose(fid);
save('strategies', 'strategies')

keyboard
