function winner = ticket(players)

% rng(1)

s = struct();

if nargin < 1 || isempty(players) % assume 3 players in the game
    players = 3;
end
assert(players >= 3 && players <= 5, 'Must be between 3-5 players')

G = initializemap;

pieces = 45 * ones([players, 1]); % number of trains each player has
points = zeros([1, players]); % initialize everyone to 0 points
cards = struct();
cards.deck = Shuffle([zeros([1, 14]), repmat(1:8, [1, 12])]); % initialize and shuffle the deck!
cards.hand = cell(1, players); % initialize each players cards as empty cell
cards.faceup =  [];
cards.discards = [];
cards = movecards([], cards, 'deck', 'faceup', 1:5); % put first 5 face up
for turn = 1:players
    cards = movecards(turn, cards, 'deck', 'hand', 1:4);
end

goalcards = importgoals; % read goal cards in from the txt file
goalcards = goalcards(randperm(height(goalcards)),:); % randomize their order
% each player has a cell
% each player cell has a cell for each goal
% each goal cell has two city cells and a point value cell
goals = cellfun(@(x) {}, cell(1, players), 'UniformOutput', false);
for turn = 1:players
    [goals, goalcards] = pickgoals(turn, goals, goalcards, s);
end

turn = 1; % indicates player whose turn it is
while all(pieces > 2) % go until someone has 2 or fewer pieces
    [G, cards, goals, goalcards, pieces, points] = doturn(turn, G, cards, goals, goalcards, pieces, points, s);
    turn = turn + 1;
    if turn > players; turn = 1; end
end


for i = 1:players
    % they should lay down longest they have because it's almost over
    [G, cards, goals, goalcards, pieces, points] = doturn(turn, G, cards, goals, goalcards, pieces, points, s);
    turn = turn + 1;
    if turn > players; turn = 1; end % back around the table
end

% add up the points awarded for completing a goal card and longest road
points = points + addgoalcards(G, goals, players);
points = points + addlongestroad(G, players);

[~, winner] = max(points);
