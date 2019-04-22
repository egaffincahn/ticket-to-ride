% During player number TURN, MOVECARDS re-allocates cards with FROM and TO,
% which can be 'deck', 'faceup', 'discards', 'hand'. The number of cards is
% given by IND.

function cards = movecards(turn, cards, from, to, ind)

% db = struct2cell(dbstack);
% if sum(ismember(db(2,:), 'movecards')) == 1
%     fprintf('\n\n~~~~~~\n\n')
% else
%     fprintf('\n')
% end
% fprintf('from %s to %s\n', from, to)
% fprintf('faceup %s\n', sprintf('%d ', cards.faceup))
% fprintf('deck %s\n', sprintf('%d ', cards.deck))
% fprintf('discards %s\n', sprintf('%d ', cards.discards))


switch from
    case 'faceup' % to hand, discards
        cards2move = cards.faceup(ind);
        cards.faceup(ind) = [];
    case 'deck' % to hand, faceup
        ind = 1:min([length(cards.deck), length(ind)]); % might not have enough in deck
        cards2move = cards.deck(ind);
        cards.deck(ind) = [];
    case 'hand' % to discards
        cards2move = cards.hand{turn}(ind);
        cards.hand{turn}(ind) = [];
    case 'discards' % to deck
        cards2move = Shuffle(cards.discards(ind));
        cards.discards = [];
end

switch to
    case 'hand'
        cards.hand{turn} = [cards.hand{turn}, cards2move];
    case 'faceup'
        cards.faceup = [cards.faceup, cards2move];
    case 'discards'
        cards.discards = [cards.discards, cards2move];
    case 'deck'
        cards.deck = [cards.deck, cards2move];
end

for i = 1:2
    if strcmp(to, 'faceup') && sum(cards.faceup == 0) >= 3 && sum([cards.faceup, cards.deck, cards.discards] > 0) >= 3 % if there are too many
        cards = movecards(turn, cards, 'faceup', 'discards', 1:length(cards.faceup));
    end
    if strcmp(from, 'faceup') && length(cards.faceup) < 5
        cards = movecards(turn, cards, 'deck', 'faceup', 1:(5-length(cards.faceup)));
    end
    if strcmp(from, 'deck') && isempty(cards.deck)
        cards = movecards(turn, cards, 'discards', 'deck', 1:length(cards.discards));
    end
    if isempty(cards.deck) && ~isempty(cards.discards)
        cards = movecards(turn, cards, 'discards', 'deck', 1:length(cards.discards));
    end
end

db = struct2cell(dbstack);
if sum(ismember(db(2,:), 'movecards')) == 1 && (... % when we're supposed to be done moving cards, do any conditions have problems?
        (length(cards.faceup) < 5 && ~isempty(cards.deck)) || ... % condition 1
        (length(cards.faceup) < 5 && ~isempty(cards.discards)) || ... % condition 2
        (isempty(cards.deck) && ~isempty(cards.discards)) || ...
        (110 ~= length(cards.deck) + length(cards.discards) + length(cards.faceup) + sum(cellfun(@length, cards.hand))))
    keyboard
end
