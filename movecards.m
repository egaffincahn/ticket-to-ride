function [hand, deck, faceup, discards] = movecards(turn, hand, deck, faceup, discards, from, to, ind)

switch from
    case 'faceup' % to hand, discards
        cards = faceup(ind); % take card from faceup
        faceup(ind) = [];
        [hand, deck, faceup, discards] = movecards(turn, hand, deck, faceup, discards, 'deck', 'faceup', 1:length(ind)); % replace it with one from deck
    case 'deck' % to hand, faceup
        cards = 99*ones(1,length(ind));
        for i = 1:length(ind) % just do one card at a time so we can shuffle discards back in
            if isempty(deck)
                [hand, deck, faceup, discards] = movecards(turn, hand, deck, faceup, discards, 'discards', 'deck', 1:length(discards));
            end
            cards(i) = deck(1);
            deck(1) = [];
        end
    case 'hand' % to discards
        cards = hand{turn}(ind);
        hand{turn}(ind) = [];
    case 'discards' % to deck
        cards = discards(ind);
        discards = [];
end

switch to
    case 'hand'
        hand{turn} = [hand{turn}, cards];
    case 'faceup'
        faceup = [faceup, cards];
        if sum(~faceup) >= 3 % if there are too many
            [hand, deck, faceup, discards] = movecards(turn, hand, deck, faceup, discards, 'faceup', 'discards', 1:length(faceup));
        end
    case 'discards'
        discards = [discards, cards];
    case 'deck'
        deck = cards;
end