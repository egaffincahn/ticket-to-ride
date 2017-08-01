function cards = pickgoals(turn, cards, s)

if isempty(cards.playergoals{turn})
    setup = true;
else
    setup = false;
end

for i = 1:2 % pick up 3 cards
    if height(cards.goalcards) == 0
        break
    end
    cards.playergoals{turn}{end+1} = {char(cards.goalcards.from(i)), char(cards.goalcards.to(i)), cards.goalcards.value(i)};
end

cards.goalcards(1:2,:) = [];

if setup % must keep at least 2
    % add some aggressiveness strategy
else % must keep at least 1
    % add some aggressiveness strategy
end

% % discard one of the cards
% cards.goalcards.from{end+1} = cards.playergoals{turn}{end}{1};
% cards.goalcards.to{end} = cards.playergoals{turn}{end}{2};
% cards.goalcards.value(end) = cards.playergoals{turn}{end}{3};
% cards.playergoals{turn}(end) = [];