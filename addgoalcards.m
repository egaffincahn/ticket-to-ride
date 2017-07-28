function points = addgoalcards(G, goals, players)

points = zeros([1, players]);
for turn = 1:players
    
    goalpoints = 0; % summation of points for completion of goals
    H = G.taken;
    H = rmedge(H, find(H.Edges.Weight ~= turn)); % remove all the edges where this player didn't go
    
    for i = 1:length(goals{turn}) % scroll through each of the player's cards
        outcome = goals{turn}{i}{3}; % get the number of points for completion (and assume they got it)
        if isempty(shortestpath(H, goals{turn}{i}{1}, goals{turn}{i}{2})) % find if there's any path connecting
            outcome = -outcome; % subtract the points if there's no path
        end
        goalpoints = goalpoints + outcome; % add them up!
    end
    points(turn) = points(turn) + goalpoints; % add them up!
end