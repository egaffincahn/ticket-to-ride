function [points, winner] = ticket(s, players)

rng(6)

if nargin < 2 || isempty(players) % assume 3 players in the game
    if nargin > 0 && ~isempty(s)
        players = length(s);
    else
        players = 3;
    end
end
if nargin < 1 || isempty(s)
    s = strategy(players, players, true);
end
assert(players >= 2 && players <= 5, 'Must be between 2-5 players')

G = initializemap;

% s = strategy(players);

info.pieces = 45 * ones([players, 1]); % number of trains each player has
info.points = zeros([1, players]); % initialize everyone to 0 points
info.players = players;
info.rounds = 0;

cards = struct();
cards.deck = Shuffle([zeros([1, 14]), repmat(1:8, [1, 12])]); % initialize and shuffle the deck!
cards.hand = cell(1, players); % initialize each players cards as empty cell
cards.faceup =  [];
cards.discards = [];
cards = movecards([], cards, 'deck', 'faceup', 1:5); % put first 5 face up
for turn = 1:players
    cards = movecards(turn, cards, 'deck', 'hand', 1:4); % give players their first cards
end

cards.goalcards = importgoals; % read goal cards in from the txt file
cards.goalcards = cards.goalcards(randperm(height(cards.goalcards)),:); % randomize their order
% each player has a cell
% each player cell has a cell for each goal
% each goal cell has two city cells and a point value cell
cards.playergoals = cellfun(@(x) {}, cell(1, players), 'UniformOutput', false);
for turn = 1:players
    cards = pickgoals(turn, cards, s);
end

turn = 1; % indicates player whose turn it is
memory = struct('taken', cellfun(@(x) G.taken, cell(1, players), 'UniformOutput', false)); % remembers what tracks the player took
% tic
while all(info.pieces > 2) % go until someone has 2 or fewer pieces
    [G, cards, info, memory] = doturn(turn, G, cards, info, memory, s);
    turn = turn + 1;
    if turn > players
        turn = 1;
        info.rounds = info.rounds + 1;
%         fprintf('%.2f s elapsed for round %d\n', toc, info.rounds), tic
    end
    if KbCheck
%         keyboard
    end
end


for i = 1:players
    % they should lay down longest they have because it's almost over
    [G, cards, info, memory] = doturn(turn, G, cards, info, memory, s);
    turn = turn + 1;
    if turn > players % back around the table
        turn = 1;
        info.rounds = info.rounds + 1;
    end
end

% add up the points awarded for completing a goal card and longest road
info.points = info.points + addgoalcards(G, cards, info);
info.points = info.points + addlongestroad(G, info);

[~, winner] = max(info.points);

for turn = 1:players
    assert(45 - sum(G.distance.Edges.Weight(G.taken.Edges.Weight == turn)) == info.pieces(turn), 'Incorrect pieces remaining')
end

plotgraph(0, G, cards, info)

points = info.points

% keyboard
