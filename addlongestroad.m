function points = addlongestroad(G, players)

best_dist = zeros([1, players]);
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
        if length(search) == 1 % city not connected to any others
            continue
        end
        for j = 1:length(search)
            if j == length(search) && length(search) == 2 % if only two cities, don't wrap around
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
            temp_dist = H.Edges.Weight(ind); % get the weight of the edge
            if temp_dist == 0 % if the weight is 0, not sure this ever happens...?
                continue
            end
            dist = dist + temp_dist; % increase the track length
        end
        if dist > best_dist % new best track length for this player
            best_dist(turn) = dist;
        end
    end
end

[~, player] = max(best_dist); % find the player with the best
points = zeros(size(best_dist));
points(player) = 10; % and give them 10 points!
