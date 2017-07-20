function [goals, goalcards] = pickgoals(turn, goals, goalcards, s)

if isempty(goals{turn})
    setup = true;
else
    setup = false;
end

for i = 1:3 % pick up 3 cards
    goals{turn}{i} = {char(goalcards.from(i)), char(goalcards.to(i)), goalcards.value(i)};
end

goalcards(1:3,:) = [];

if setup % must keep at least 2
    % add some aggressiveness strategy
else % must keep at least 1
    % add some aggressiveness strategy
end