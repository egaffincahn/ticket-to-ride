function edgevals = valuateedges(turn, G, cards, info, s)


edgevals = zeros(height(G.taken.Edges),1);
H = G.distance;
H.Edges.Weight(find(all(G.taken.Edges.Weight ~= [0 turn], 2))) = Inf;
H.Edges.Weight(find(G.distance.Edges.Weight > info.pieces(turn))) = Inf;
% H = rmedge(H, find(G.taken.Edges.Weight | G.distance.Edges.Weight > info.pieces(turn))); % remove edges which are taken and where player doesn't have enough train pieces

for goal = 1:length(cards.playergoals{turn})
    [~, completed] = addgoalcards(G, cards, info); % check if the goal was completed
    if completed{turn}(goal)
        continue
    end

    % Computes the basic strategy. Logic is below in sub-function. Then add
    % value based on findings.
    [valueadditions, bestedgepath, success] = basicstrategy(turn, G, H, cards, goal);
    if ~success; continue; end
    edgevals = addvalue(edgevals, valueadditions, cards, turn, goal, s);
    
    % STRATEGY: Iteratively remove a possible edge from the best path, then
    % recompute the best path. If an edge is used in lots of best paths,
    % then it will be given a higher weight.
    if s(turn).valuation.iterativevaluation
        for i = 1:length(bestedgepath)
%             H_temp = rmedge(H, bestedgepath(i)); % make this edge impossible
            H_temp.Edges.Weight(bestedgepath(i)) = Inf; % make this edge impossible
            [valueadditions, ~, success] = basicstrategy(turn, G, H_temp, cards, goal); % repeat the strategy
            if ~success % when removing an edge, if no path can be found, then that edge is super important
                valueadditions(bestedgepath(i)) = 1; % so we re-add it to the valuation in the subfunction
            end
            edgevals = addvalue(edgevals, valueadditions, cards, turn, goal, s);
            
        end
    end
    
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


if s(turn).valuation.attemptoverlap % on or off
    % not sure how to write this algorithm. one way:
    % cluster the goals (with unknown k)
    % find important nodes in clusters
    % connect each city to its cluster center
    % find best route from any one in a cluster to any other
end


function [valueadditions, edges, success] = basicstrategy(turn, G, H, cards, goal)

% This will be one base strategy. Logic: For each city in the goal
% card, get all the cities connected to it. Then find the best route
% from any city on one side of the goal card to any city connected to
% the other side.
playergraph = rmedge(G.distance, find(G.taken.Edges.Weight ~= turn)); % get a smaller graph where the edges are the player's connected cities
valueadditions = zeros(height(G.taken.Edges),1);

for j = 1:2 % scroll through each city in the goal
    tree = shortestpathtree(playergraph, cards.playergoals{turn}{goal}{j}, 'OutputForm', 'cell'); % get all the cities the goal city is connected to
    connected{j} = findnode(H, unique([tree{:}])); %#ok<AGROW> % get the indices of the connected cities
end
numpossible = length(connected{1}) * length(connected{2}); %
connectionmatrix = distances(H); % get the connection matrix of all the cities with taken tracks as Inf
[bestdist, ind] = min(reshape(connectionmatrix(connected{1}, connected{2}), [1 numpossible])); % get the best route from any on one side to any on the other
success = ~isinf(bestdist); if ~success; edges = []; return; end
[closest1, closest2] = ind2sub([length(connected{1}) length(connected{2})], ind); % get the subscripts - the closest cities on each side
bestpath = shortestpath(H, connected{1}(closest1), connected{2}(closest2)); % get the best path
edges = findedge(H, bestpath(1:end-1), bestpath(2:end)); % the indices of the cities on that best path
valueadditions(edges) = 1; % get the indices of the edges to increase


function edgevals = addvalue(edgevals, valueadditions, cards, turn, goal, s)
% if ~success % if the goal can't be completed, just move on
%     return
% end
% increase the value additions by the points awarded to the goal
edgevals = edgevals + valueadditions * cards.playergoals{turn}{goal}{end};

% increase based on distance, or inverse of distance

