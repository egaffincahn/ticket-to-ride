function cards = movecards(turn, cards, from, to, ind)

switch from
    case 'faceup' % to hand, discards
        cards2move = cards.faceup(ind); % take card from faceup
        cards.faceup(ind) = [];
        cards = movecards(turn, cards, 'deck', 'faceup', 1:length(ind)); % replace it with one from deck
    case 'deck' % to hand, faceup
        cards2move = 99*ones(1,length(ind));
        for i = 1:length(ind) % just do one card at a time so we can shuffle discards back in
            if isempty(cards.deck)
                cards = movecards(turn, cards, 'discards', 'deck', 1:length(cards.discards));
            end
            cards2move(i) = cards.deck(1);
            cards.deck(1) = [];
        end
    case 'hand' % to discards
        cards2move = cards.hand{turn}(ind);
        cards.hand{turn}(ind) = [];
    case 'discards' % to deck
        cards2move = cards.discards(ind);
        cards.discards = [];
end

switch to
    case 'hand'
        cards.hand{turn} = [cards.hand{turn}, cards2move];
    case 'faceup'
        cards.faceup = [cards.faceup, cards2move];
        if sum(~cards.faceup) >= 3 % if there are too many
            cards = movecards(turn, cards, 'faceup', 'discards', 1:length(cards.faceup));
        end
    case 'discards'
        cards.discards = [cards.discards, cards2move];
    case 'deck'
        cards.deck = cards2move;
end

