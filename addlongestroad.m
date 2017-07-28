function points = addlongestroad(G, players)

best_dist = zeros([1, players]);
for turn = 1:players
    
    H = G.distance;
    H = rmedge(H, find(G.taken.Edges.Weight ~= turn));
    %h = plot(H); h.EdgeLabel = H.Edges.Weight;
    
    for i = 1:height(H.Nodes)
        search = H.Nodes.Name(dfsearch(H, H.Nodes.Name(i)));
        dist = 0;
        if length(search) == 1
            continue
        end
        for j = 1:length(search)
            if j == length(search) && length(search) == 2
                continue
            elseif j == length(search)
                wrap = 1;
            else
                wrap = j + 1;
            end
            ind = findedge(H, search{j}, search{wrap});
            if ind == 0
                continue
            end
            temp_dist = H.Edges.Weight(ind);
            if temp_dist == 0
                continue
            end
            dist = dist + temp_dist;
        end
        if dist > best_dist
            best_dist(turn) = dist;
        end
    end
end

[~, player] = max(best_dist);
points = zeros(size(best_dist));
points(player) = 10;