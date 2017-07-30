% should unit test this

function [points, bestdist] = addlongestroad(G, players)

bestdist = zeros([1, players]);
for turn = 1:players
    
    H = G.distance;
    H = rmedge(H, find(G.taken.Edges.Weight ~= turn)); % remove all the edges where this player didn't go
    %h = plot(H); h.EdgeLabel = H.Edges.Weight;
    
    for i = 1:height(H.Nodes) % scroll through each city
        % important: depth first search starting at the node
        % if there's a fork with two long branches, might choose the wrong
        % one
        search = H.Nodes.Name(dfsearch(H, H.Nodes.Name(i)));
        dist = 0; % total distance of this path so far
        if length(search) < -1 % city connected to fewer than X cities, don't even bother
            continue
        end
        for j = 1:length(search)
            if length(search) == 2 && j == length(search) % don't include the second the same reverse trip
                continue
            elseif j == length(search) % check if the first and last cities are connected
                wrap = 1;
            else % normal case - just the next city in the path
                wrap = j + 1;
            end
            ind = findedge(H, search{j}, search{wrap}); % get the graph's edge index for these two cities
            if ind == 0 % if they're not connected
                continue
            end
            dist = dist + H.Edges.Weight(ind); % increase the track length
        end
        if dist > bestdist(turn) % new best track length for this player
            bestdist(turn) = dist;
        end
    end
end

longest = max(bestdist); % find the value of the longest
points = 10 * (longest == bestdist); % get player(s) with longest, give them all 10!
