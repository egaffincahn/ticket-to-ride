function [points, completed] = addgoalcards(G, cards, info)

points = zeros([1, info.players]);
completed = cell([1, info.players]);
for turn = 1:info.players
    
    goalpoints = 0; % summation of points for completion of goals
    H = rmedge(G.taken, find(G.taken.Edges.Weight ~= turn)); % remove all the edges where this player didn't go
    
    completed{turn} = true([1, length(cards.playergoals{turn})]);
    for i = 1:length(cards.playergoals{turn}) % scroll through each of the player's cards
        outcome = cards.playergoals{turn}{i}{3}; % get the number of points for completion (and assume they got it)
        if isempty(shortestpath(H, cards.playergoals{turn}{i}{1}, cards.playergoals{turn}{i}{2})) % find if there's any path connecting
            outcome = -outcome; % subtract the points if there's no path
            completed{turn}(i) = false;
        end
        goalpoints = goalpoints + outcome; % add them up!
    end
    points(turn) = points(turn) + goalpoints; % add them up!
end