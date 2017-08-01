function edgevals = valuateedges(turn, G, cards, info, s)

% IF BEST IS TAKEN, NEED TO FIND A NEW ROUTE

edgevals = zeros([size(G.distance.Edges, 1), 1]);
H = G.distance;
H.Edges.Weight(find(G.taken.Edges.Weight)) = Inf;
% H = rmedge(H, find(G.taken.Edges.Weight)); % remove all the edges where this player didn't go

for i = 1:length(cards.playergoals{turn})
    [~, completed] = addgoalcards(G, cards, info);
    if completed{turn}(i)
        continue
    end
    % shortest path needs to test from all cities that are connected to all
    % that are connected to both cities in the goal
    
    
    playergraph = rmedge(G.distance, find(G.taken.Edges.Weight ~= turn));
    connectionmatrix = distances(playergraph);
    ind1 = findnode(H, cards.playergoals{turn}{i}{1});
    connected1 = find(connectionmatrix(:,ind1) ~= 0 & ~isinf(connectionmatrix(:,ind1)))';
    ind2 = findnode(H, cards.playergoals{turn}{i}{2});
    connected2 = find(connectionmatrix(:,ind2) ~= 0 & ~isinf(connectionmatrix(:,ind2)))';
    availablegraph = rmedge(G.distance, find(G.taken.Edges.Weight ~= 0));
    % definitely a faster way to do this:
    bestdistance = Inf;
    for city1 = [ind1 connected1]
        for city2 = [ind2 connected2]
            [path, distance] = shortestpath(availablegraph, city1, city2);
            if distance < bestdistance
                bestpath = path;
                bestdistance = distance;
            end
        end
    end
    ind = findedge(H, bestpath(1:end-1), bestpath(2:end));
    edgevals(ind) = edgevals(ind) + 1;
    
end

available = sum(~G.taken.Edges.Weight);
% urgency = 20 * sum(edgevals) / available;
urgency = 1 + 20 * log(numedges(H) / available);
edgevals = edgevals * urgency;

edgevals(find(G.taken.Edges.Weight)) = 0; %#ok<FNDSB>


%%
return


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