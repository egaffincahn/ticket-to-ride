function cards = pickcards(turn, cards, s)

picked = 0;
colorvals = valuatecolors(); % returns values for each color 1-8
colorvals = colorvals / sum(colorvals);
while picked < 2
    [value, pick] = max(colorvals); % find the highest valued color
    onboard = find(cards.faceup == pick);
    if value < .15 % crappy value, take random
        cards = movecards(turn, cards, 'deck', 'hand', 1);
        picked = picked + 1;
        continue
    elseif any(onboard) % pick the good-valued color
        cards = movecards(turn, cards, 'faceup', 'hand', onboard(1));
        picked = picked + 1;
        continue
    elseif picked < 1 % want the color, but it's not on the board
        onboard = find(cards.faceup == 0); % check for wildcards
        if value > .5 && any(onboard) % only take wildcard if value is very high
            cards = movecards(turn, cards, 'faceup', 'hand', onboard(1));
            break % only allowed 1
        end
    end
    colorvals(pick) = 0; % best option is not on board but it's not urgent, so artificially keep value at 0
end
