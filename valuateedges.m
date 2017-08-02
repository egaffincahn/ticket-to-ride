function edgevals = valuateedges(turn, G, cards, info, s)


edgevals = zeros([size(G.distance.Edges, 1), 1]);
H = G.distance;
H.Edges.Weight(find(G.taken.Edges.Weight)) = Inf; %#ok<FNDSB>

for i = 1:length(cards.playergoals{turn})
    [~, completed] = addgoalcards(G, cards, info); % check if the goal was completed
    if completed{turn}(i)
        continue
    end

    % Will be one strategy. Logic: For each city in the goal card, get all
    % the cities connected to it. Then find the best route from any city on
    % one side of the goal card to any city connected to the other side.
    playergraph = rmedge(G.distance, find(G.taken.Edges.Weight ~= turn)); % get a smaller graph with only the cities connected
    for j = 1:2 % scroll through each city in the goal
        tree = shortestpathtree(playergraph, cards.playergoals{turn}{i}{j}, 'OutputForm', 'cell'); % get all the cities the goal city is connected to
        connected{j} = findnode(H, unique([tree{:}])); % get the indices of the connected cities
    end
    numpossible = length(connected{1}) * length(connected{2}); % 
    connectionmatrix = distances(H); % get the connection matrix of all the cities with taken tracks as Inf
    [~, ind] = min(reshape(connectionmatrix(connected{1}, connected{2}), [1 numpossible])); % get the best route from any on one side to any on the other
    [closest1, closest2] = ind2sub([length(connected{1}) length(connected{2})], ind); % get the subscripts - the closest cities on each side
    bestpath = shortestpath(H, connected{1}(closest1), connected{2}(closest2)); % get the best path
    edges = findedge(H, bestpath(1:end-1), bestpath(2:end)); % the indices of the cities on that best path
    edgevals(edges) = edgevals(edges) + 1; % increase the value of those edges
    
end

available = sum(~G.taken.Edges.Weight);
% urgency = 20 * sum(edgevals) / available;
urgency = 1 + 20 * log(numedges(H) / available);
edgevals = edgevals * urgency;

edgevals(find(G.taken.Edges.Weight)) = -1; %#ok<FNDSB>


% which goal to prioritize
switch s(turn).valuation.goalpriorities % must be one of these
    % consider chance of getting the goal in prioritizing it
    case 'distance'
        % prioritize longest
        % prioritize shortest
    case 'turns'
        % prioritize most number of turns
        % prioritize fewest number of turns
    case 'points'
        % prioritize most number of points per turn
        % prioritize fewest number of points per turn
    case 'equal'
        % all goals equally prioritized
    otherwise
        error('Invalid goal priorities in strategy')
end

% within a goal, which route to prioritize
switch s(turn).valuation.routeminimizer % must be one of these
    case 'distance'
        % prefer short distance
        % prefer longer distance
    case 'turns'
        % prefer more turns
        % prefer fewer turns
    case 'points'
        % prefer most points per turn
        % prefer fewest points per turn
    otherwise
        error('Invalid route minimizer in strategy')
end


if s(turn).valuation.iterativevaluation % on or off
    % for each goal
        % for each city connected to first city
            % for each city connected to second city
                % find shortest path
                    % add value to the edges in that path 
                    % for each edge in that path
                        % remove edge
                        % find shortest path again
                        % add value to each edge in that path
end

if s(turn).valuation.attemptoverlap % on or off
    % not sure how to write this algorithm. one way:
    % cluster the goals (with unknown k)
    % find important nodes in clusters
    % connect each city to its cluster center
    % find best route from any one in a cluster to any other
end