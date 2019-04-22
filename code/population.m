function [] = population

%#ok<*AGROW>

rng(2)

individuals = 6;
generations = 15000;
players = 3; % players per game - 1 lives on

[G, cards, info] = setupgame(players);

for i = 1:individuals
    strategies(i) = strategy(G, cards);
end
% load('strategies', 'strategies')

ncores = feature('numcores');
if ncores > 2
    parpool(ncores - 1);
end

winnerpoints = nan(generations,individuals/players);
durations = nan(generations,1);
ages = ones(generations,individuals);
h = waitbar(0, 'Calculating time remaining...');
tstart = tic;
for i = 1:generations
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
    str = sprintf('generation %d of %d (%.2f%%)\n%s', i, generations, 100*i/generations, timeremaining(i, generations, tstart, true));
    waitbar(i/generations, h, str)
%     fprintf('finished generation %d - %.1f seconds\n', i, durations(i))
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
