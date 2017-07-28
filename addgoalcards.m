function points = addgoalcards(G, goals, players)

points = zeros([1, players]);
for turn = 1:players
    goalpoints = 0;
    H = G.taken;
    H = rmedge(H, find(H.Edges.Weight ~= turn));
    for i = 1:length(goals{turn})
        outcome = goals{turn}{i}{3};
        if isempty(shortestpath(H, goals{turn}{i}{1}, goals{turn}{i}{2}))
            outcome = -outcome;
        end
        goalpoints = goalpoints + outcome;
    end
    points(turn) = points(turn) + goalpoints;
end