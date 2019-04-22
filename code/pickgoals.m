function cards = pickgoals(turn, cards)

% adds a field which indicates who owns that goalcard
if ~any(ismember(cards.goalcards.Properties.VariableNames, 'player'))
    cards.goalcards.player = zeros(height(cards.goalcards),1);
end

for i = 1:2 % pick up 3 cards?
    if all(cards.goalcards.player ~= 0)
        break
    end
    ind = randi(height(cards.goalcards));
    while cards.goalcards.player(ind) ~= 0
        ind = randi(height(cards.goalcards));
    end
    cards.playergoals{turn}{end+1} = {char(cards.goalcards.from(ind)), char(cards.goalcards.to(ind)), cards.goalcards.value(ind)};
    cards.goalcards.player(ind) = turn;
end
