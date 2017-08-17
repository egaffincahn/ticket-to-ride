% Calculates the probability of doing some action based on a variable
% number of considerations (number of players, number of tracks, etc), and
% then depending on what we're calculating the probability of (laying down
% a new track, etc), pick the appropriate beta weights from the strategy
% matrix. Then use the logistic to get the probability.
function p = logistic(s, considerations, instance)

% build the design matrix including all interactions
X = 1;
for i = 1:length(considerations)
    X = [X, prod(nchoosek(x, i), 2)']; %#ok<AGROW>
end

beta = s(turn).beta.(instance); % choose the appropriate weights from the strategy structure

p = 1 ./ (1 + exp(-X * beta)); % get the probability from the logistic
