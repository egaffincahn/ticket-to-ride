% Calculates the probability of doing some action based on a variable
% number of considerations (number of players, number of tracks, etc), and
% then depending on what we're calculating the probability of (laying down
% a new track, etc), pick the appropriate beta weights from the strategy
% matrix. Then use the logistic to get the probability.
function y = glm(s, turn, considerations, instance, link, intercept)



% build the design matrix including all interactions
X = [];
for i = 1:size(considerations, 1)
    X_row = [];
    for j = 1:size(considerations, 2)
        X_row = [X_row, prod(nchoosek(considerations(i,:), j), 2)']; %#ok<AGROW>
    end
    X = [X; X_row]; %#ok<AGROW>
end
if intercept
    X = [ones(size(X,1), 1), X];
end

% choose the appropriate weights from the strategy structure
beta = s(turn).(instance);

switch link
    case 'logistic'
        y = 1 ./ (1 + exp(-X * beta(:))); % get the probability from the logistic
    case 'linear'
        y = X * beta(:);
end