% Logic of this function: We take the graph of track distances and then
% only keep the ones where the current player has laid the track. Then we
% take the remaining connections and build a full adjacency matrix, which
% is a symmetric matrix (# cities x # cities) where there is a 1 at each
% (row,column) pair where the two cities are connected. Start with a column
% that has a connection, and then look down the column for connected
% cities. If there's only 1, remove that connection, then do the same for
% the connected city. If there are ever 2 or more cities connected,
% duplicate everything and keep going down each path.

%#ok<*AGROW>

function [points, bestdist] = addlongestroad(G, info)

bestdist = zeros([1, info.players]); % initialize each player's longest at 0

for turn = 1:info.players
    
    H = G.distance; % use the graph of track distances to calculate longest track
    H = rmedge(H, find(G.taken.Edges.Weight ~= turn)); % remove all the edges where this player didn't go

    fulladjmat = full(adjacency(H)); % create full adjacency matrix with 1s where two cities are connected by this player
    path = {}; % each cell is vector representing the route through each city index
    terminated = false(size(path)); % vector representing whether the path has been full searched
    trimadjmat = {}; % each cell is a full adjacency matrix but where the city connections looked at so far have been removed (trimmed) to disallow them from being used again
    playerdists = 0; % vector for this player where each index is the number of points in a path, only updated once it's terminated
    foundglobalbest = false; % tells us if there's a path that has used every connection - allows us to quit early
    
    for city = find(sum(fulladjmat, 1) > 0) % only look at the cities that have connections
        path{end+1} = city; % initialize a new path with the current city we start with
        terminated(end+1) = false; % this new path has not been finished
        currpath = length(path); % currpath indexes the current index of the path (and other) cell vector we are exploring
        trimadjmat{currpath} = fulladjmat; % initialize the current trimmed adjacency matrix
        while any(~terminated) && ~foundglobalbest % only stop when all paths are terminated or we found a path that uses all connections
            curr = path{currpath}(end); % current city index
            numconn = sum(trimadjmat{currpath}(:,curr)); % number of connected cities to the current
            if numconn == 1 % only 1 - easy case
                conn = find(trimadjmat{currpath}(:,curr), 1, 'first'); % find the connected city index
                path{currpath} = [path{currpath} conn]; % add the connected to the path vector
                trimadjmat{currpath}(curr,conn) = 0; % remove it from the trimmed adjacency matrix
                trimadjmat{currpath}(conn,curr) = 0; % and the symmetric (row,column) pair
            elseif numconn > 1 % more than 1 connected cities
                terminated(currpath) = []; % we remove a few of the current cells to be replaced by 2 or more (1 from each connected city)
                for next = find(trimadjmat{currpath}(:,curr))' % scroll through each connected city
                    path{end+1} = [path{currpath} next]; % create a new path and add the connected city to it
                    terminated(end+1) = false; % do the same as in the 1 connected city case
                    trimadjmat{end+1} = trimadjmat{currpath};
                    trimadjmat{end}(curr,next) = 0;
                    trimadjmat{end}(next,curr) = 0;
                end
                trimadjmat(currpath) = []; % remove some more of the current cells
                path(currpath) = [];
                currpath = length(path); % tell the algorithm which path to get started with after this fork
            elseif numconn == 0 % when there are no more connected cities on this path
                ind = findedge(H, path{currpath}(1:end-1), path{currpath}(2:end)); % gets the edge indices for the cities in the path
                playerdists(currpath) = sum(H.Edges.Weight(ind)); % adds up the distances
                if all(~trimadjmat{currpath}(:)) % all cities have been connected on this path (exciting!)
                    foundglobalbest = true;
                else
                    terminated(currpath) = true; % don't need to return to this path
                    currpath = find(~terminated, 1, 'last'); % get started on the last unfinished path (could choose any of them)
                end
            end
        end
        if foundglobalbest
            break
        end
    end
    bestdist(turn) = max(playerdists);
end

longest = max(bestdist); % find the value of the longest
points = 10 * (longest == bestdist); % get player(s) with longest, give them all 10!


