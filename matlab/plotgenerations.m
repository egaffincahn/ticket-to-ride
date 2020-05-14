function plotgenerations(durations, winnerpoints, ages)

generations = max([length(durations), size(winnerpoints,1), size(ages,1)]);

if nargin > 0 && ~isempty(durations)
    figure(1), plot(1:generations, durations, '-o'), xlabel('generation'), ylabel('generation time (s)')
end

if nargin > 1 && ~isempty(winnerpoints)
    figure(2), clf
    subplot(2,1,1), plot(1:generations, mean(winnerpoints, 2), '-o'), xlabel('generation'), ylabel('average winner points')
    subplot(2,1,2), plot(1:generations, max(winnerpoints, [], 2), '-o'), xlabel('generation'), ylabel('max winner points')
end

if nargin > 2 && ~isempty(ages)
    figure(3), clf
    subplot(2,1,1), plot(1:generations+1, mean(ages(:,1:individuals/players), 2), '-o'), xlabel('generation'), ylabel('average parent age')
    subplot(2,1,2), plot(1:generations+1, max(ages, [], 2), 'o'), xlabel('generation'), ylabel('max parent age')
end